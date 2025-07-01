from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from adminpanel.models import Category, Auctions
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class Inventory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('auction', 'In Auction'),
        ('sold', 'Sold'),
        ('unsold', 'Unsold'),
    ]

    IN_TRANSIT_STATUS_CHOICES = [
        ('awaiting_dispatch', 'Awaiting Dispatch'),
        ('awaiting_pickup', 'Awaiting Pick Up'),
        ('awaiting_arrival', 'Awaiting Arrival'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('old', 'Old'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    inventory_number = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    in_transit_status = models.CharField(max_length=20, choices=IN_TRANSIT_STATUS_CHOICES, null=True, blank=True)
    auction = models.ForeignKey(Auctions, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    lot_start_time = models.DateTimeField(null=True, blank=True)
    lot_end_time = models.DateTimeField(null=True, blank=True)

    winning_bid = models.ForeignKey('Bid', null=True, blank=True, on_delete=models.SET_NULL, related_name='winning_bid_for_inventory')
    winning_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='winning_inventory')
    youtube_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        super().clean()  # Call the parent's clean method

        # Add your custom validation logic
        if self.reserve_price is not None and self.starting_bid is not None:
            if self.reserve_price < self.starting_bid:
                raise ValidationError(_('Reserve price must be greater than or equal to starting bid.'))

        # Handle None comparisons
        if self.reserve_price is None and self.starting_bid is None:
            raise ValidationError(_('Both reserve price and starting bid cannot be None.'))

        # Add more validations as needed

    def calculate_lot_timings(self):
        if self.auction and self.auction.start_date and self.auction.lots_time_duration:
            inventories = list(
                self.auction.inventory_set.filter(deleted_at__isnull=True).order_by('id')
            )
            index = inventories.index(self)
            start_offset = timedelta(seconds=index * self.auction.lots_time_duration)
            self.lot_start_time = self.auction.start_date + start_offset
            self.lot_end_time = self.lot_start_time + timedelta(seconds=self.auction.lots_time_duration)