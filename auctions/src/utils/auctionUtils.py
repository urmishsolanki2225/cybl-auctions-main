from django.db import transaction
from datetime import timedelta
from adminpanel.models import Inventory

def cascade_lot_timing_update(lot, extension_seconds):
    """
    Utility function to cascade timing updates to subsequent lots
    """
    with transaction.atomic():
        auction = lot.auction
        
        # Find all lots that start after the current lot's original end time
        subsequent_lots = Inventory.objects.filter(
            auction=auction,
            lot_start_time__gt=lot.lot_end_time - timedelta(seconds=extension_seconds),
            deleted_at__isnull=True
        ).order_by('lot_start_time')
        
        # Update each subsequent lot
        for subsequent_lot in subsequent_lots:
            subsequent_lot.lot_start_time += timedelta(seconds=extension_seconds)
            if subsequent_lot.lot_end_time:
                subsequent_lot.lot_end_time += timedelta(seconds=extension_seconds)
            subsequent_lot.save(update_fields=['lot_start_time', 'lot_end_time'])
        
        # Update auction end time
        auction.end_date += timedelta(seconds=extension_seconds)
        auction.save(update_fields=['end_date'], skip_auto_calculation=True)