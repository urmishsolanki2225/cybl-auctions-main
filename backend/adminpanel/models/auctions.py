from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from adminpanel.models import Country, State
from datetime import timedelta


class Auctions(models.Model):
    TIME_DURATION_CHOICES = [
        (5, "5 Seconds"),
        (10, "10 Seconds"),
        (20, "20 Seconds"),
        (30, "30 Seconds"),
        (40, "40 Seconds"),
        (50, "50 Seconds"),
        (60, "1 Minute"),
        (120, "2 Minutes"),
        (180, "3 Minutes"),
        (240, "4 Minutes"),
        (300, "5 Minutes"),
    ]

    # Auction Status Choices
    AUCTION_STATUS_CHOICES = [
        ('next', 'Next'),
        ('current', 'Current'),
        ('closed', 'Closed'),
    ]

    # Auction Basic Details
    is_featured = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    # Dates
    prebid_start_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    # Lot Timing & Auto Extend
    lots_time_duration = models.PositiveIntegerField(choices=TIME_DURATION_CHOICES)
    auto_extend_time = models.BooleanField(default=False)
    auto_extend_duration = models.PositiveIntegerField(choices=TIME_DURATION_CHOICES, null=True, blank=True)

    bid_increment = models.DecimalField(
        null=True, blank=True,
        max_digits=10, decimal_places=2, default=100.00,
        help_text="Minimum bid increment in currency units"
    )
    lot_count = models.PositiveIntegerField(default=0, editable=False)

    # Financials
    buyers_premium = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage (e.g., 15.00 = 15%)"
    )

    # User Linking
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    
    # Seller Location Type
    SELLER_LOCATION_CHOICES = [
        ("onsite", "Onsite"),
        ("offsite", "Offsite"),
    ]
    seller_location = models.CharField(max_length=10, choices=SELLER_LOCATION_CHOICES, null=True, blank=True)

    # Address Details (only for offsite)
    address = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


    # Auction Status
    status = models.CharField(
        max_length=10, choices=AUCTION_STATUS_CHOICES, null=True, blank=True, default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        current_time = timezone.now()

        # Updated status logic to include prebid_start_date
        if self.end_date and current_time >= self.end_date:
            self.status = 'closed'
        elif self.prebid_start_date and self.prebid_start_date <= current_time:
            self.status = 'current'  # Prebid period starts -> current
        elif self.start_date and self.start_date <= current_time:
            self.status = 'current'  # Main auction starts -> current
        else:
            self.status = 'next'  # Before prebid/start -> next

        # Save the instance first to ensure it has a PK
        is_new = self.pk is None
        super(Auctions, self).save(*args, **kwargs)

        # Now we can safely access related inventory items
        lot_count = self.inventory_set.filter(deleted_at__isnull=True).count()

        # Update lot count if changed or new
        if is_new or self.lot_count != lot_count:
            self.lot_count = lot_count

            if self.lots_time_duration:
                total_duration_seconds = lot_count * self.lots_time_duration
                self.end_date = self.start_date + timedelta(seconds=total_duration_seconds)

            # Save again to persist updated fields
            super(Auctions, self).save(update_fields=['lot_count', 'end_date'])

