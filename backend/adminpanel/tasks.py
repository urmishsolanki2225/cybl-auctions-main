# Enhanced tasks.py with comprehensive logging and fixes

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

# Enhanced logging setup
logger = logging.getLogger(__name__)

@shared_task
def update_auction_status():
    """
    Main auction management task with enhanced logging
    """
    now = timezone.now()
    updated_count = 0
    processed_lots = 0

    logger.info(f"🚀 Starting update_auction_status at {now}")

    with transaction.atomic():
        auctions = Auctions.objects.select_for_update().all()
        logger.info(f"📊 Found {auctions.count()} auctions to check")

        for auction in auctions:
            old_status = auction.status
            new_status = None

            logger.debug(
                f"[Auction {auction.id}] Status Check:\n"
                f"  - Current time: {now}\n"
                f"  - Prebid start: {auction.prebid_start_date}\n"
                f"  - Start date: {auction.start_date}\n"
                f"  - End date: {auction.end_date}\n"
                f"  - Current status: {old_status}"
            )

            # Calculate auction end date if not set
            if not auction.end_date:
                logger.warning(f"⚠️ Auction {auction.id} has no end_date, calculating...")
                calculate_auction_end_date(auction)

            # Determine new status with detailed logging
            if auction.end_date and now >= auction.end_date:
                new_status = 'closed'
                logger.info(f"🔴 Auction {auction.id}: CLOSING (now >= end_date)")
            elif auction.start_date and auction.start_date <= now:
                new_status = 'current'
                logger.info(f"🟢 Auction {auction.id}: CURRENT (now >= start_date)")
            elif auction.prebid_start_date and auction.prebid_start_date <= now:
                new_status = 'current'
                logger.info(f"🟡 Auction {auction.id}: CURRENT (now >= prebid_start_date)")
            else:
                new_status = 'next'
                logger.debug(f"⚪ Auction {auction.id}: NEXT (waiting for start)")
        
            # Update status if changed
            if new_status and new_status != old_status:
                auction.status = new_status
                auction.save(update_fields=['status'])
                updated_count += 1
                logger.info(f"✅ Auction {auction.id} status: '{old_status}' → '{new_status}'")

            # Process current auctions
            if auction.status == 'current':
                logger.info(f"🔄 Processing current auction {auction.id}")
                
                # Update lot times first
                update_lot_times_for_auction(auction)
                
                # Process expired lots immediately with detailed logging
                expired_lots = process_expired_lots_for_auction(auction, now)
                processed_lots += expired_lots
                
                if expired_lots > 0:
                    logger.info(f"🏁 Processed {expired_lots} expired lots in auction {auction.id}")

    logger.info(f"✅ Task completed: Updated {updated_count} auction statuses, processed {processed_lots} expired lots")
    return f"Updated {updated_count} auctions, processed {processed_lots} lots"


def calculate_auction_end_date(auction):
    """Calculate and set auction end date with enhanced logging"""
    try:
        lot_count = auction.inventory_set.filter(deleted_at__isnull=True).count()
        logger.info(f"📊 Auction {auction.id} has {lot_count} active lots")
        
        if lot_count > 0 and auction.lots_time_duration and auction.start_date:
            total_duration_seconds = lot_count * auction.lots_time_duration
            auction.end_date = auction.start_date + timedelta(seconds=total_duration_seconds)
            auction.lot_count = lot_count
            auction.save(update_fields=['end_date', 'lot_count'])
            
            logger.info(f"✅ Auction {auction.id}: Calculated end_date = {auction.end_date} "
                       f"(lots: {lot_count}, duration: {auction.lots_time_duration}s each)")
        else:
            logger.warning(f"⚠️ Cannot calculate end_date for auction {auction.id}: "
                          f"lot_count={lot_count}, duration={auction.lots_time_duration}, "
                          f"start_date={auction.start_date}")
            
    except Exception as e:
        logger.error(f"❌ Error calculating end date for auction {auction.id}: {e}")


def update_lot_times_for_auction(auction):
    """Update lot times with detailed logging"""
    try:
        inventories = auction.inventory_set.filter(
            deleted_at__isnull=True
        ).order_by('id')
        
        logger.debug(f"🔄 Updating times for {inventories.count()} lots in auction {auction.id}")
        
        updated_count = 0
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
                old_start = inv.lot_start_time
                old_end = inv.lot_end_time
                
                inv.lot_start_time = lot_start
                inv.lot_end_time = lot_end
                inv.save(update_fields=['lot_start_time', 'lot_end_time'])
                updated_count += 1
                
                logger.debug(f"📅 Lot {inv.id} times updated:\n"
                           f"  Start: {old_start} → {lot_start}\n"
                           f"  End: {old_end} → {lot_end}")
        
        if updated_count > 0:
            logger.info(f"✅ Updated {updated_count} lot times in auction {auction.id}")
                
    except Exception as e:
        logger.error(f"❌ Error updating lot times for auction {auction.id}: {e}")


def process_expired_lots_for_auction(auction, current_time):
    """Process expired lots with comprehensive logging"""
    processed_count = 0
    
    try:
        # Add buffer to handle timing precision issues
        buffer_time = current_time - timedelta(seconds=2)  # Reduced buffer
        
        logger.debug(f"🔍 Checking for expired lots in auction {auction.id}:\n"
                    f"  Current time: {current_time}\n"
                    f"  Buffer time: {buffer_time}")
        
        expired_lots = auction.inventory_set.filter(
            Q(lot_end_time__lte=current_time) &  # Use current_time instead of buffer_time
            Q(status__in=['pending', 'auction']) &
            Q(deleted_at__isnull=True)
        ).order_by('lot_end_time')
        
        logger.info(f"🔍 Found {expired_lots.count()} expired lots in auction {auction.id}")
        
        for lot in expired_lots:
            try:
                time_expired = current_time - lot.lot_end_time
                logger.info(f"🏁 Processing expired lot {lot.id}:\n"
                           f"  Title: {lot.title}\n"
                           f"  End time: {lot.lot_end_time}\n"
                           f"  Current time: {current_time}\n"
                           f"  Expired by: {time_expired.total_seconds()} seconds\n"
                           f"  Current status: {lot.status}")
                
                # Check if lot has any bids
                bid_count = lot.bids.filter(deleted_at__isnull=True).count()
                highest_bid = lot.bids.filter(deleted_at__isnull=True).order_by('-bid_amount').first()
                
                logger.info(f"📊 Lot {lot.id} bid analysis:\n"
                           f"  Total bids: {bid_count}\n"
                           f"  Highest bid: {highest_bid.bid_amount if highest_bid else 'None'}\n"
                           f"  Reserve price: {lot.reserve_price}\n"
                           f"  Reserve met: {highest_bid.bid_amount >= lot.reserve_price if highest_bid else False}")
                
                process_closed_lot(lot)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to process expired lot {lot.id}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Error processing expired lots for auction {auction.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    return processed_count


def process_closed_lot(inventory):
    """
    Process a single closed lot with comprehensive logging
    """
    winner_data = None
    
    try:
        logger.info(f"🔒 Starting to process closed lot {inventory.id}")
        
        with transaction.atomic():
            # Lock the inventory to prevent race conditions
            inventory = Inventory.objects.select_for_update().get(id=inventory.id)
            
            # Skip if already processed
            if inventory.status in ['sold', 'unsold']:
                logger.warning(f"⚠️ Lot {inventory.id} already processed with status: {inventory.status}")
                return
            
            logger.info(f"🔍 Analyzing bids for lot {inventory.id}")
            
            # Get all bids for analysis
            all_bids = inventory.bids.filter(deleted_at__isnull=True).order_by('-bid_amount', 'created_at')
            logger.info(f"📊 Found {all_bids.count()} total bids for lot {inventory.id}")
            
            # Log all bids for debugging
            for i, bid in enumerate(all_bids[:5]):  # Show top 5 bids
                logger.info(f"  Bid {i+1}: ${bid.bid_amount} by {bid.user.username} at {bid.created_at}")
            
            winning_bid = all_bids.first()  # Highest bid
            
            logger.info(f"🏆 Lot {inventory.id} analysis:\n"
                       f"  Winning bid: ${winning_bid.bid_amount if winning_bid else 'None'}\n"
                       f"  Winner: {winning_bid.user.username if winning_bid else 'None'}\n"
                       f"  Reserve price: ${inventory.reserve_price}\n"
                       f"  Reserve met: {winning_bid.bid_amount >= inventory.reserve_price if winning_bid else False}")

            if winning_bid and winning_bid.bid_amount >= inventory.reserve_price:
                # SOLD - Process winning bid
                inventory.winning_bid = winning_bid
                inventory.winning_user = winning_bid.user
                inventory.status = 'sold'

                total_amount = winning_bid.bid_amount

                logger.info(f"✅ Lot {inventory.id} SOLD to {winning_bid.user.username} for ${winning_bid.bid_amount}")

                # Create payment transaction
                payment = create_payment_transaction(
                    user=winning_bid.user,
                    inventory=inventory,
                    amount=total_amount,
                    winning_bid_amount=winning_bid.bid_amount,
                )
                
                if payment:
                    logger.info(f"💰 Payment transaction created: {payment.transaction_id}")
                else:
                    logger.error(f"❌ Failed to create payment transaction for lot {inventory.id}")

                # Get profile photo safely
                profile_photo = None
                try:
                    if hasattr(winning_bid.user, 'profile') and winning_bid.user.profile.photo:
                        profile_photo = winning_bid.user.profile.photo.url
                        logger.debug(f"📸 Profile photo found for winner: {profile_photo}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch profile photo: {e}")

                winner_data = {
                    'user_id': winning_bid.user.id,
                    'username': winning_bid.user.username,
                    'profile_photo': profile_photo,
                    'winning_amount': str(winning_bid.bid_amount),
                    'status': 'sold'
                }

            else:
                # UNSOLD - No winning bid or reserve not met
                inventory.status = 'unsold'
                inventory.winning_bid = None
                inventory.winning_user = None

                reason = 'Reserve not met' if winning_bid else 'No bids received'
                logger.info(f"❌ Lot {inventory.id} UNSOLD - {reason}")

                winner_data = {
                    'status': 'unsold',
                    'reason': reason
                }

            # Save inventory changes
            inventory.save(update_fields=['status', 'winning_bid', 'winning_user'])
            logger.info(f"💾 Lot {inventory.id} saved with status: {inventory.status}")

    except Exception as e:
        logger.error(f"❌ Error processing closed lot {inventory.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return

    # Broadcast OUTSIDE the transaction
    try:
        if winner_data:
            logger.info(f"📡 Broadcasting winner data for lot {inventory.id}")
            broadcast_lot_winner(inventory, winner_data)
        else:
            logger.warning(f"⚠️ No winner data to broadcast for lot {inventory.id}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast winner for lot {inventory.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


def broadcast_lot_winner(inventory, winner_data):
    """Broadcast lot winner with enhanced logging"""
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.error("❌ Channel layer is not configured - cannot broadcast!")
            return

        room_group_name = f'lot_{inventory.id}'
        auction_group_name = f'auction_{inventory.auction.id}'
        
        logger.info(f"📡 Broadcasting to rooms: {room_group_name}, {auction_group_name}")

        message_data = {
            'lot_id': inventory.id,
            'lot_title': inventory.title,
            'winner': winner_data,
            'ended_at': timezone.now().isoformat()
        }
        
        logger.debug(f"📦 Broadcast message data: {message_data}")

        # Send to lot-specific room
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'lot_ended',
                'data': message_data
            }
        )
        logger.info(f"✅ Sent to lot room: {room_group_name}")

        # Send to auction-wide room
        async_to_sync(channel_layer.group_send)(
            auction_group_name,
            {
                'type': 'lot_ended', 
                'data': message_data
            }
        )
        logger.info(f"✅ Sent to auction room: {auction_group_name}")

        logger.info(f"🎉 Successfully broadcasted winner for lot {inventory.id}")

    except Exception as e:
        logger.error(f"❌ Error broadcasting winner for lot {inventory.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


def create_payment_transaction(user, inventory, amount, winning_bid_amount):
    """Create payment transaction with logging"""
    try:
        # Generate unique transaction ID
        transaction_id = f"TXN-{inventory.auction.id}-{inventory.id}-{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"💰 Creating payment transaction:\n"
                   f"  Transaction ID: {transaction_id}\n"
                   f"  User: {user.username}\n"
                   f"  Amount: ${amount}\n"
                   f"  Lot: {inventory.title}")
        
        payment = Payment_History.objects.create(
            transaction_id=transaction_id,
            amount=amount,
            user=user,
            inventory=inventory,
            status=Payment_History.PaymentStatus.PENDING,
            payment_method=Payment_History.PaymentMethod.ONLINE
        )
        
        logger.info(f"✅ Payment transaction created successfully: {transaction_id}")
        return payment
        
    except Exception as e:
        logger.error(f"❌ Error creating payment transaction for inventory {inventory.id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


@shared_task
def process_expired_lots():
    """
    Standalone task to process expired lots with enhanced logging
    """
    now = timezone.now()
    processed_count = 0
    
    logger.info(f"🔍 Starting process_expired_lots at {now}")
    
    try:
        # Use current time instead of buffer for more accurate processing
        expired_lots = Inventory.objects.filter(
            Q(lot_end_time__lte=now) &
            Q(status__in=['pending', 'auction']) &
            Q(deleted_at__isnull=True)
        ).order_by('lot_end_time')
        
        logger.info(f"📊 Found {expired_lots.count()} expired lots across all auctions")
        
        for lot in expired_lots:
            try:
                time_expired = now - lot.lot_end_time
                logger.info(f"🏁 Processing standalone expired lot {lot.id} "
                           f"(expired {time_expired.total_seconds()} seconds ago)")
                
                process_closed_lot(lot)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to process expired lot {lot.id}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"✅ Standalone task completed: Processed {processed_count} expired lots")
        
    except Exception as e:
        logger.error(f"❌ Error in process_expired_lots: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    return f"Processed {processed_count} expired lots"


@shared_task
def cleanup_expired_auctions():
    """Clean up old closed auctions with logging"""
    logger.info("🧹 Starting cleanup of expired auctions")
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_closed_auctions = Auctions.objects.filter(
        status='closed',
        end_date__lt=cutoff_date
    )
    
    logger.info(f"📊 Found {old_closed_auctions.count()} old closed auctions to clean up")
    
    cleanup_count = 0
    for auction in old_closed_auctions:
        try:
            logger.info(f"🧹 Processing old auction {auction.id} (ended {auction.end_date})")
            # Additional cleanup logic can go here
            cleanup_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up auction {auction.id}: {e}")
    
    logger.info(f"✅ Cleanup completed: Processed {cleanup_count} old auctions")
    return f"Processed {cleanup_count} old auctions"