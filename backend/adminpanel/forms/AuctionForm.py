from django import forms
from django.utils import timezone
from adminpanel.models import Auctions

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auctions
        exclude = ['latitude', 'longitude']  # Don't include these in form.cleaned_data
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'prebid_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Extract values
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        start_date = cleaned_data.get('start_date')
        prebid_start_date = cleaned_data.get('prebid_start_date')
        lots_time_duration = cleaned_data.get('lots_time_duration')
        user = cleaned_data.get('user')
        seller_location = cleaned_data.get('seller_location')

        address = cleaned_data.get('address')
        country = cleaned_data.get('country')
        state = cleaned_data.get('state')
        city = cleaned_data.get('city')
        zipcode = cleaned_data.get('zipcode')

        auto_extend_time = cleaned_data.get('auto_extend_time')
        auto_extend_duration = cleaned_data.get('auto_extend_duration')
        buyers_premium = cleaned_data.get('buyers_premium')

        # 1. Required base fields
        base_required_fields = {
            'name': name,
            'description': description,
            'start_date': start_date,
            'lots_time_duration': lots_time_duration,
            'user': user,
        }
        for field, value in base_required_fields.items():
            if not value and not self.errors.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")

        # 2. Conditionally required seller_location if user exists
        if user and not seller_location:
            self.add_error('seller_location', "Seller location is required when a seller is selected.")

        # 3. Offsite address fields if seller_location is 'offsite'
        if seller_location == 'offsite':
            offsite_fields = {
                'address': address,
                'country': country,
                'state': state,
                'city': city,
                'zipcode': zipcode,
            }
            
            for field, value in offsite_fields.items():
                if not value and not self.errors.get(field):
                    self.add_error(field, f"{field.replace('_', ' ').title()} is required.")

        # 4. Start date must be in the future
        if start_date and start_date <= timezone.now():
            self.add_error('start_date', "Start datetime must be in the future.")

        # 5. Prebid date must be before start date
        if prebid_start_date:
            if not start_date:
                self.add_error('start_date', "Start datetime is required when using Prebid Start Date.")
            elif prebid_start_date >= start_date:
                self.add_error('prebid_start_date', "Prebid start datetime must be before auction start date.")

        # 6. Auto extend logic
        if auto_extend_time and not auto_extend_duration:
            self.add_error('auto_extend_duration', "This field is required if Auto Extend Time is enabled.")

        # 7. Buyer’s premium logic
        if user:
            if buyers_premium is None:
                self.add_error('buyers_premium', "Buyer's premium is required when a seller is selected.")
            elif buyers_premium < 5:
                self.add_error('buyers_premium', "Buyer's premium must be at least 5%.")

                
