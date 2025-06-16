# from celery import shared_task
# from django.utils import timezone
# from .models import Auctions, Inventory
# from datetime import timedelta
# import logging
# from django.db import transaction


# logger = logging.getLogger(__name__)

# @shared_task
# def update_auction_status():
#     now = timezone.now()
#     updated_count = 0

#     with transaction.atomic():
#         auctions = Auctions.objects.select_for_update().all()

#         for auction in auctions:
#             old_status = auction.status
#             new_status = None

#             logger.debug(
#                 f"[Auction {auction.id}] Time Check → now: {now}, "
#                 f"prebid_start_date: {auction.prebid_start_date}, "
#                 f"start_date: {auction.start_date}, "
#                 f"end_date: {auction.end_date}, "
#                 f"current status: {old_status}"
#             )

#             # Determine new status (matching model logic)
#             if auction.end_date and now >= auction.end_date:
#                 new_status = 'closed'
#                 logger.debug(f"Auction {auction.id}: now >= end_date, setting status to 'closed'")
#             elif auction.prebid_start_date and auction.prebid_start_date <= now:
#                 new_status = 'current'
#                 logger.debug(f"Auction {auction.id}: now >= prebid_start_date, setting status to 'current'")
#             elif auction.start_date and auction.start_date <= now:
#                 new_status = 'current'
#                 logger.debug(f"Auction {auction.id}: now >= start_date, setting status to 'current'")
#             else:
#                 new_status = 'next'  # Changed from 'upcoming' to 'next'
#                 logger.debug(f"Auction {auction.id}: setting status to 'next'")
        
#             # Update status if changed
#             if new_status and new_status != old_status:
#                 auction.status = new_status
#                 auction.save(update_fields=['status'])
#                 updated_count += 1

#                 logger.info(f"Auction {auction.id} status updated from '{old_status}' to '{new_status}'")

#                 if new_status == 'closed':
#                     logger.info(f"Auction {auction.id} closed - End date: {auction.end_date}, Current time: {now}")

#             # Recalculate lot times if auction is current
#             if auction.status == 'current' and auction.lots_time_duration:
#                 update_lot_times(auction)

#     logger.info(f"Updated {updated_count} auction statuses")
#     return f"Updated {updated_count} auctions"


# def update_lot_times(auction):
#     """Separate function to update lot times for current auctions"""
#     try:
#         inventories = auction.inventory_set.filter(
#             deleted_at__isnull=True
#         ).order_by('id')
        
#         for index, inv in enumerate(inventories):
#             lot_start = auction.start_date + timedelta(
#                 seconds=index * auction.lots_time_duration
#             )
#             lot_end = lot_start + timedelta(
#                 seconds=auction.lots_time_duration
#             )
            
#             # Only update if times have changed
#             if inv.lot_start_time != lot_start or inv.lot_end_time != lot_end:
#                 inv.lot_start_time = lot_start
#                 inv.lot_end_time = lot_end
#                 inv.save(update_fields=['lot_start_time', 'lot_end_time'])
                
#     except Exception as e:
#         logger.error(f"Error updating lot times for auction {auction.id}: {e}")

# # Additional task to specifically check and close expired auctions
# @shared_task
# def close_expired_auctions():
#     """Dedicated task to close expired auctions"""
#     now = timezone.now()
    
#     expired_auctions = Auctions.objects.filter(
#         end_date__lte=now,
#         status__in=['current', 'prebid']  # Only close active auctions
#     )
    
#     updated_count = 0
#     for auction in expired_auctions:
#         old_status = auction.status
#         auction.status = 'closed'
#         auction.save(update_fields=['status'])
#         updated_count += 1
        
#         logger.info(f"Force closed auction {auction.id} (was {old_status})")
    
#     return f"Force closed {updated_count} expired auctions"

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Q
from .models import Auctions, Inventory, Bid, Payment_History
from datetime import timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

@shared_task
def update_auction_status():
    """
    Comprehensive auction status management including:
    - Status updates (next -> current -> closed)
    - Lot timing calculations with auto-extend
    - Winner determination
    - Inventory status updates
    - Payment transaction creation
    """
    now = timezone.now()
    updated_count = 0

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

                # Handle auction closure
                if new_status == 'closed':
                    close_auction_and_process_results(auction)
                    logger.info(f"Auction {auction.id} closed and processed - End date: {auction.end_date}")

            # Update lot times and handle auto-extend for current auctions
            if auction.status == 'current':
                update_lot_times_with_auto_extend(auction)

    logger.info(f"Updated {updated_count} auction statuses")
    return f"Updated {updated_count} auctions"


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


def update_lot_times_with_auto_extend(auction):
    """Update lot times and handle auto-extend functionality"""
    try:
        now = timezone.now()
        inventories = auction.inventory_set.filter(
            deleted_at__isnull=True
        ).order_by('id')
        
        auction_extended = False
        
        for index, inv in enumerate(inventories):
            # Calculate base lot times
            lot_start = auction.start_date + timedelta(
                seconds=index * auction.lots_time_duration
            )
            lot_end = lot_start + timedelta(
                seconds=auction.lots_time_duration
            )
            
            # Check for auto-extend if enabled
            if auction.auto_extend_time and auction.auto_extend_duration:
                # Get the last bid for this inventory
                last_bid = inv.bids.filter(
                    deleted_at__isnull=True
                ).order_by('-created_at').first()
                
                if last_bid:
                    # Check if bid was placed in the last few seconds (configurable threshold)
                    extend_threshold = 30  # seconds - you can make this configurable
                    time_since_bid = (now - last_bid.created_at).total_seconds()
                    time_until_lot_end = (lot_end - now).total_seconds()
                    
                    # If bid was recent and lot is about to end, extend it
                    if (time_since_bid <= extend_threshold and 
                        0 <= time_until_lot_end <= extend_threshold):
                        
                        lot_end = lot_end + timedelta(seconds=auction.auto_extend_duration)
                        auction_extended = True
                        
                        logger.info(f"Auto-extended lot {inv.id} by {auction.auto_extend_duration}s "
                                   f"due to recent bid by {last_bid.user.username}")
            
            # Update lot times if changed
            if inv.lot_start_time != lot_start or inv.lot_end_time != lot_end:
                inv.lot_start_time = lot_start
                inv.lot_end_time = lot_end
                inv.save(update_fields=['lot_start_time', 'lot_end_time'])
        
        # If any lot was extended, recalculate auction end date
        if auction_extended:
            # Find the latest lot end time
            latest_lot_end = inventories.aggregate(
                latest_end=Max('lot_end_time')
            )['latest_end']
            
            if latest_lot_end and latest_lot_end > auction.end_date:
                auction.end_date = latest_lot_end
                auction.save(update_fields=['end_date'])
                logger.info(f"Auction {auction.id} end date extended to {auction.end_date}")
                
    except Exception as e:
        logger.error(f"Error updating lot times for auction {auction.id}: {e}")


def close_auction_and_process_results(auction):
    """
    Process auction closure:
    1. Determine winners for each lot
    2. Update inventory status (sold/unsold)
    3. Create payment transactions
    """
    try:
        with transaction.atomic():
            inventories = auction.inventory_set.filter(deleted_at__isnull=True)
            total_lots = inventories.count()
            sold_lots = 0
            unsold_lots = 0
            
            for inventory in inventories:
                # Get the highest bid for this inventory
                winning_bid = inventory.bids.filter(
                    deleted_at__isnull=True
                ).order_by('-bid_amount', 'created_at').first()
                
                if winning_bid and winning_bid.bid_amount >= inventory.reserve_price:
                    # Item sold - winner found
                    inventory.winning_bid = winning_bid
                    inventory.winning_user = winning_bid.user
                    inventory.status = 'sold'
                    sold_lots += 1
                    
                    # Calculate total amount (bid + buyer's premium)
                    total_amount = winning_bid.bid_amount
                    if auction.buyers_premium:
                        premium_amount = (winning_bid.bid_amount * auction.buyers_premium) / 100
                        total_amount += premium_amount
                    
                    # Create pending payment transaction
                    create_payment_transaction(
                        user=winning_bid.user,
                        inventory=inventory,
                        amount=total_amount,
                        winning_bid_amount=winning_bid.bid_amount,
                        buyers_premium=auction.buyers_premium
                    )
                    
                    logger.info(f"Lot {inventory.id} sold to {winning_bid.user.username} "
                               f"for ${winning_bid.bid_amount} (Total: ${total_amount})")
                    
                else:
                    # Item unsold - no winning bid or bid below reserve
                    inventory.status = 'unsold'
                    inventory.winning_bid = None
                    inventory.winning_user = None
                    unsold_lots += 1
                    
                    if winning_bid:
                        logger.info(f"Lot {inventory.id} unsold - highest bid ${winning_bid.bid_amount} "
                                   f"below reserve ${inventory.reserve_price}")
                    else:
                        logger.info(f"Lot {inventory.id} unsold - no bids received")
                
                inventory.save(update_fields=['status', 'winning_bid', 'winning_user'])
            
            logger.info(f"Auction {auction.id} processing complete: "
                       f"{sold_lots} sold, {unsold_lots} unsold out of {total_lots} lots")
            
    except Exception as e:
        logger.error(f"Error processing auction {auction.id} closure: {e}")


def create_payment_transaction(user, inventory, amount, winning_bid_amount, buyers_premium):
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
            payment_method=Payment_History.PaymentMethod.ONLINE  # Default, can be updated later
        )
        
        logger.info(f"Created payment transaction {transaction_id} for user {user.username} "
                   f"- Amount: ${amount} (Bid: ${winning_bid_amount}, Premium: {buyers_premium}%)")
        
        return payment
        
    except Exception as e:
        logger.error(f"Error creating payment transaction for inventory {inventory.id}: {e}")
        return None


@shared_task
def check_lot_auto_extend():
    """
    Separate task to specifically handle lot auto-extension
    This can run more frequently (every 5-10 seconds) for better responsiveness
    """
    now = timezone.now()
    extended_count = 0
    
    # Get all current auctions with auto-extend enabled
    current_auctions = Auctions.objects.filter(
        status='current',
        auto_extend_time=True,
        auto_extend_duration__isnull=False
    )
    
    for auction in current_auctions:
        try:
            # Get lots that are about to end (within next 30 seconds)
            ending_soon_lots = auction.inventory_set.filter(
                deleted_at__isnull=True,
                lot_end_time__lte=now + timedelta(seconds=30),
                lot_end_time__gt=now
            )
            
            for lot in ending_soon_lots:
                # Check for recent bids (within last 30 seconds)
                recent_bid = lot.bids.filter(
                    deleted_at__isnull=True,
                    created_at__gte=now - timedelta(seconds=30)
                ).order_by('-created_at').first()
                
                if recent_bid:
                    # Extend the lot
                    lot.lot_end_time = lot.lot_end_time + timedelta(seconds=auction.auto_extend_duration)
                    lot.save(update_fields=['lot_end_time'])
                    extended_count += 1
                    
                    logger.info(f"Auto-extended lot {lot.id} by {auction.auto_extend_duration}s "
                               f"due to recent bid by {recent_bid.user.username}")
                    
                    # Update auction end date if necessary
                    if lot.lot_end_time > auction.end_date:
                        auction.end_date = lot.lot_end_time
                        auction.save(update_fields=['end_date'])
                        
        except Exception as e:
            logger.error(f"Error checking auto-extend for auction {auction.id}: {e}")
    
    if extended_count > 0:
        logger.info(f"Auto-extended {extended_count} lots")
    
    return f"Auto-extended {extended_count} lots"


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
            # For now, just log the old auctions
            logger.info(f"Old closed auction found: {auction.id} (ended {auction.end_date})")
            cleanup_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning up auction {auction.id}: {e}")
    
    return f"Processed {cleanup_count} old auctions"