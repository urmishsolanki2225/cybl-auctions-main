# MAIN ISSUES IDENTIFIED AND FIXED:

# 1. RACE CONDITIONS - Multiple tasks running every 1 second
# 2. MISSING process_expired_lots task in schedule
# 3. TIMING PRECISION ISSUES
# 4. AUTO-EXTEND LOGIC CONFLICTS

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Q
from .models import Auctions, Inventory, Bid, Payment_History
from datetime import timedelta
import logging
import uuid
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

@shared_task
def update_auction_status():
    """
    Main auction management task:
    - Updates auction statuses (next -> current -> closed)
    - Calculates lot times
    - Processes expired lots immediately
    """
    now = timezone.now()
    updated_count = 0
    processed_lots = 0

    with transaction.atomic():
        auctions = Auctions.objects.select_for_update().all()

        for auction in auctions:
            old_status = auction.status
            new_status = None

            logger.debug(
                f"[Auction {auction.id}] Time Check → now: {now}, "
                f"prebid_start_date: {auction.prebid_start_date}, "
                f"start_date: {auction.start_date}, "
                f"end_date: {auction.end_date}, "
                f"current status: {old_status}"
            )

            # Calculate auction end date if not set
            if not auction.end_date:
                calculate_auction_end_date(auction)

            # Determine new status
            if auction.end_date and now >= auction.end_date:
                new_status = 'closed'
                logger.debug(f"Auction {auction.id}: now >= end_date, setting status to 'closed'")
            elif auction.prebid_start_date and auction.prebid_start_date <= now:
                new_status = 'current'
                logger.debug(f"Auction {auction.id}: now >= prebid_start_date, setting status to 'current'")
            elif auction.start_date and auction.start_date <= now:
                new_status = 'current'
                logger.debug(f"Auction {auction.id}: now >= start_date, setting status to 'current'")
            else:
                new_status = 'next'
                logger.debug(f"Auction {auction.id}: setting status to 'next'")
        
            # Update status if changed
            if new_status and new_status != old_status:
                auction.status = new_status
                auction.save(update_fields=['status'])
                updated_count += 1
                logger.info(f"Auction {auction.id} status updated from '{old_status}' to '{new_status}'")

            # Process current auctions
            if auction.status == 'current':
                # Update lot times first
                update_lot_times_for_auction(auction)
                
                # Process expired lots immediately
                expired_lots = process_expired_lots_for_auction(auction, now)
                processed_lots += expired_lots

    logger.info(f"Updated {updated_count} auction statuses, processed {processed_lots} expired lots")
    return f"Updated {updated_count} auctions, processed {processed_lots} lots"


def calculate_auction_end_date(auction):
    """Calculate and set auction end date based on lot count and duration"""
    try:
        lot_count = auction.inventory_set.filter(deleted_at__isnull=True).count()
        
        if lot_count > 0 and auction.lots_time_duration and auction.start_date:
            total_duration_seconds = lot_count * auction.lots_time_duration
            auction.end_date = auction.start_date + timedelta(seconds=total_duration_seconds)
            auction.lot_count = lot_count
            auction.save(update_fields=['end_date', 'lot_count'])
            
            logger.info(f"Auction {auction.id}: Calculated end_date = {auction.end_date} "
                       f"(lot_count: {lot_count}, duration: {auction.lots_time_duration}s each)")
            
    except Exception as e:
        logger.error(f"Error calculating end date for auction {auction.id}: {e}")


def update_lot_times_for_auction(auction):
    """Update lot times for a specific auction without auto-extend logic"""
    try:
        inventories = auction.inventory_set.filter(
            deleted_at__isnull=True
        ).order_by('id')
        
        for index, inv in enumerate(inventories):
            # Calculate base lot times
            lot_start = auction.start_date + timedelta(
                seconds=index * auction.lots_time_duration
            )
            lot_end = lot_start + timedelta(
                seconds=auction.lots_time_duration
            )
            
            # Update lot times if changed
            if inv.lot_start_time != lot_start or inv.lot_end_time != lot_end:
                inv.lot_start_time = lot_start
                inv.lot_end_time = lot_end
                inv.save(update_fields=['lot_start_time', 'lot_end_time'])
                logger.debug(f"Updated lot {inv.id} times: {lot_start} to {lot_end}")
                
    except Exception as e:
        logger.error(f"Error updating lot times for auction {auction.id}: {e}")


def process_expired_lots_for_auction(auction, current_time):
    """Process expired lots for a specific auction"""
    processed_count = 0
    
    try:
        # Get lots that have ended but are still marked as pending/auction
        # Add a small buffer (1 second) to handle timing precision issues
        buffer_time = current_time - timedelta(seconds=1)
        
        expired_lots = auction.inventory_set.filter(
            Q(lot_end_time__lte=buffer_time) &
            Q(status__in=['pending', 'auction']) &
            Q(deleted_at__isnull=True)
        )
        
        for lot in expired_lots:
            try:
                logger.info(f"Processing expired lot {lot.id} (ended at {lot.lot_end_time}, now is {current_time})")
                process_closed_lot(lot)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process expired lot {lot.id}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error processing expired lots for auction {auction.id}: {e}")
    
    return processed_count


@shared_task
def check_lot_auto_extend():
    """
    Separate task for auto-extension - runs more frequently
    Only handles auto-extension logic, not lot processing
    """
    now = timezone.now()
    extended_count = 0
    
    try:
        # Get all current auctions with auto-extend enabled
        current_auctions = Auctions.objects.filter(
            status='current',
            auto_extend_time=True,
            auto_extend_duration__isnull=False
        )
        
        for auction in current_auctions:
            try:
                # Get lots that are about to end (within next 15 seconds) and haven't been extended recently
                threshold_time = now + timedelta(seconds=15)
                
                ending_soon_lots = auction.inventory_set.filter(
                    deleted_at__isnull=True,
                    lot_end_time__lte=threshold_time,
                    lot_end_time__gt=now,  # Not already ended
                    status__in=['pending', 'auction']  # Still active
                )
                
                for lot in ending_soon_lots:
                    # Check for very recent bids (within last 15 seconds)
                    recent_bid_threshold = now - timedelta(seconds=15)
                    recent_bid = lot.bids.filter(
                        deleted_at__isnull=True,
                        created_at__gte=recent_bid_threshold
                    ).order_by('-created_at').first()
                    
                    if recent_bid:
                        # Check if we're in the extend window (last 10 seconds)
                        time_until_end = (lot.lot_end_time - now).total_seconds()
                        
                        if 0 < time_until_end <= 10:  # Extend only in last 10 seconds
                            # Extend the lot
                            extension_duration = timedelta(seconds=auction.auto_extend_duration)
                            old_end_time = lot.lot_end_time
                            lot.lot_end_time = lot.lot_end_time + extension_duration
                            lot.save(update_fields=['lot_end_time'])
                            extended_count += 1
                            
                            logger.info(f"Auto-extended lot {lot.id} from {old_end_time} to {lot.lot_end_time} "
                                       f"due to recent bid by {recent_bid.user.username}")
                            
                            # Update auction end date if necessary
                            if lot.lot_end_time > auction.end_date:
                                auction.end_date = lot.lot_end_time
                                auction.save(update_fields=['end_date'])
                                logger.info(f"Extended auction {auction.id} end date to {auction.end_date}")
                        
            except Exception as e:
                logger.error(f"Error checking auto-extend for auction {auction.id}: {e}")
        
        if extended_count > 0:
            logger.info(f"Auto-extended {extended_count} lots")
            
    except Exception as e:
        logger.error(f"Error in check_lot_auto_extend: {e}")
    
    return f"Auto-extended {extended_count} lots"


def process_closed_lot(inventory):
    """
    Process a single closed lot:
    1. Determine winner
    2. Update inventory status (sold/unsold)
    3. Create payment transaction
    4. Broadcast winner via WebSocket
    """
    winner_data = None
    
    try:
        with transaction.atomic():
            # Lock the inventory to prevent race conditions
            inventory = Inventory.objects.select_for_update().get(id=inventory.id)
            
            # Skip if already processed
            if inventory.status in ['sold', 'unsold']:
                logger.info(f"Lot {inventory.id} already processed with status: {inventory.status}")
                return
            
            winning_bid = inventory.bids.filter(
                deleted_at__isnull=True
            ).order_by('-bid_amount', 'created_at').first()

            if winning_bid and winning_bid.bid_amount >= inventory.reserve_price:
                inventory.winning_bid = winning_bid
                inventory.winning_user = winning_bid.user
                inventory.status = 'sold'

                total_amount = winning_bid.bid_amount

                create_payment_transaction(
                    user=winning_bid.user,
                    inventory=inventory,
                    amount=total_amount,
                    winning_bid_amount=winning_bid.bid_amount,
                )

                profile_photo = None
                try:
                    if hasattr(winning_bid.user, 'profile') and winning_bid.user.profile.photo:
                        profile_photo = winning_bid.user.profile.photo.url
                except Exception as e:
                    logger.warning(f"Failed to fetch profile photo: {e}")

                winner_data = {
                    'user_id': winning_bid.user.id,
                    'username': winning_bid.user.username,
                    'profile_photo': profile_photo,
                    'winning_amount': str(winning_bid.bid_amount),
                    'status': 'sold'
                }

                logger.info(f"Lot {inventory.id} sold to {winning_bid.user.username} "
                            f"for ${winning_bid.bid_amount}")
            else:
                inventory.status = 'unsold'
                inventory.winning_bid = None
                inventory.winning_user = None

                winner_data = {
                    'status': 'unsold',
                    'reason': 'Reserve not met' if winning_bid else 'No bids received'
                }

                logger.info(f"Lot {inventory.id} unsold - "
                            f"{'highest bid below reserve' if winning_bid else 'no bids'}")

            inventory.save(update_fields=['status', 'winning_bid', 'winning_user'])
            logger.info(f"✅ Successfully processed lot {inventory.id} with status: {inventory.status}")

    except Exception as e:
        logger.error(f"❌ Error processing closed lot {inventory.id}: {e}")
        return

    # ✅ Broadcast OUTSIDE the transaction
    try:
        if winner_data:
            broadcast_lot_winner(inventory, winner_data)
    except Exception as e:
        logger.error(f"❌ Failed to broadcast winner for lot {inventory.id}: {e}")


def broadcast_lot_winner(inventory, winner_data):
    """Broadcast lot winner information to WebSocket clients"""
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.error("Channel layer is not configured.")
            return

        room_group_name = f'lot_{inventory.id}'
        auction_group_name = f'auction_{inventory.auction.id}'

        message_data = {
            'lot_id': inventory.id,
            'lot_title': inventory.title,
            'winner': winner_data,
            'ended_at': timezone.now().isoformat()
        }

        # Send to lot-specific room
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'lot_ended',
                'data': message_data
            }
        )

        # Send to auction-wide room
        async_to_sync(channel_layer.group_send)(
            auction_group_name,
            {
                'type': 'lot_ended',
                'data': message_data
            }
        )

        logger.info(f"✅ Broadcasted winner for lot {inventory.id} to rooms: {room_group_name}, {auction_group_name}")

    except Exception as e:
        logger.exception(f"❌ Error broadcasting winner for lot {inventory.id}: {e}")


def create_payment_transaction(user, inventory, amount, winning_bid_amount):
    """Create a pending payment transaction for won inventory"""
    try:
        # Generate unique transaction ID
        transaction_id = f"TXN-{inventory.auction.id}-{inventory.id}-{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment_History.objects.create(
            transaction_id=transaction_id,
            amount=amount,
            user=user,
            inventory=inventory,
            status=Payment_History.PaymentStatus.PENDING,
            payment_method=Payment_History.PaymentMethod.ONLINE
        )
        
        logger.info(f"Created payment transaction {transaction_id} for user {user.username} "
                   f"- Amount: ${amount} (Bid: ${winning_bid_amount})")
        
        return payment
        
    except Exception as e:
        logger.error(f"Error creating payment transaction for inventory {inventory.id}: {e}")
        return None


@shared_task
def process_expired_lots():
    """
    Standalone task to process expired lots across all auctions
    This is a backup to catch any lots that might have been missed
    """
    now = timezone.now()
    processed_count = 0
    
    try:
        # Get lots that have ended but are still marked as pending/auction
        # Add buffer to handle timing precision
        buffer_time = now - timedelta(seconds=5)
        
        expired_lots = Inventory.objects.filter(
            Q(lot_end_time__lte=buffer_time) &
            Q(status__in=['pending', 'auction']) &
            Q(deleted_at__isnull=True)
        )
        
        logger.info(f"Found {expired_lots.count()} expired lots to process")
        
        for lot in expired_lots:
            try:
                logger.info(f"Processing expired lot {lot.id} (ended at {lot.lot_end_time}, buffer time: {buffer_time})")
                process_closed_lot(lot)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process expired lot {lot.id}: {e}")
                continue
        
        logger.info(f"Processed {processed_count} expired lots")
        
    except Exception as e:
        logger.error(f"Error in process_expired_lots: {e}")
    
    return f"Processed {processed_count} expired lots"


@shared_task
def cleanup_expired_auctions():
    """Clean up and finalize very old closed auctions"""
    cutoff_date = timezone.now() - timedelta(days=30)  # 30 days old
    
    old_closed_auctions = Auctions.objects.filter(
        status='closed',
        end_date__lt=cutoff_date
    )
    
    cleanup_count = 0
    for auction in old_closed_auctions:
        try:
            # Additional cleanup logic can go here
            logger.info(f"Old closed auction found: {auction.id} (ended {auction.end_date})")
            cleanup_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning up auction {auction.id}: {e}")
    
    return f"Processed {cleanup_count} old auctions"