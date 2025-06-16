from django import forms
from django.core.exceptions import ValidationError
from adminpanel.models import Inventory, Category, Auctions 

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['category', 'title', 'description', 'status', 'in_transit_status', 'auction', 'condition', 'starting_bid', 'reserve_price', 'youtube_url']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        in_transit_status = cleaned_data.get('in_transit_status')
        auction = cleaned_data.get('auction')
        starting_bid = cleaned_data.get('starting_bid')
        reserve_price = cleaned_data.get('reserve_price')


        # Validation based on the status
        if status == 'pending':
            if auction is not None:
                self.add_error('auction', 'Auction should not be set for pending status.')
            if in_transit_status is not None:
                self.add_error('in_transit_status', 'In Transit Status should not be set for pending status.')

        elif status == 'in_transit':
            if not in_transit_status:
                self.add_error('in_transit_status', 'Select In Transit Status is required.')
            if auction is not None:
                self.add_error('auction', 'Auction should not be set for in transit status.')

        elif status == 'auction':
            if auction is None:
                self.add_error('auction', 'Auction Name is required for auction status.')
            if in_transit_status is not None:
                self.add_error('in_transit_status', 'In Transit Status should not be set for auction status.')
                
        if starting_bid and reserve_price:
            if float(reserve_price) < float(starting_bid):
                self.add_error('reserve_price', 'Reserve price must be greater than or equal to starting bid.')

        return cleaned_data
