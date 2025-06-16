from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Auctions, Inventory

class Bid(models.Model):
    BID_TYPE_CHOICES = [
        ('Pre Bid', 'Pre Bid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE)
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='bids'  # ✅ Important for reverse access
    )
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=BID_TYPE_CHOICES) 

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Bid {self.bid_amount} by {self.user} on {self.inventory}"

    def delete(self, using=None, keep_parents=False):
        """Soft delete the bid by setting deleted_at instead of removing the object."""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted bid."""
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """Check if the bid is soft deleted."""
        return self.deleted_at is not None
