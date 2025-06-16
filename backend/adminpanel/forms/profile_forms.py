# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User, Group
# from adminpanel.models import Profile, Company

# class UserProfileForm(forms.ModelForm):
#     title = forms.ChoiceField(choices=[
#         ('mr', 'Mr.'),
#         ('ms', 'Ms.'),
#         ('other', 'Other'),
#     ], required=True)

#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
#     phone_no = forms.CharField(max_length=15, required=True)
#     gender = forms.CharField(max_length=15, required=True)
#     address = forms.CharField(max_length=255, required=True)
#     country = forms.CharField(max_length=100, required=True)
#     state = forms.CharField(max_length=100, required=True)
#     city = forms.CharField(max_length=100, required=True)
#     zipcode = forms.CharField(max_length=10, required=True)
#     photo = forms.ImageField(required=False)
#     group = forms.ModelChoiceField(
#         queryset=Group.objects.all(),
#         required=True,
#         label="Role",
#         to_field_name="id"  # Explicitly use the id field
#     )
#     seller_type = forms.ChoiceField(choices=[
#         ('Individual', 'Individual'), 
#         ('Company', 'Company')
#     ], required=False)
#     company_name = forms.CharField(max_length=255, required=False)
#     company_phone = forms.CharField(max_length=15, required=False)
#     company_address = forms.CharField(widget=forms.Textarea, required=False)
#     company_logo = forms.ImageField(required=False)

#     class Meta:
#         model = User
#         fields = (
#             'title', 'email', 'first_name', 'last_name', 'phone_no', 
#             'gender', 'address', 'country', 'state', 'city', 
#             'zipcode', 'photo', 'group', 'seller_type', 
#             'company_name', 'company_phone', 'company_address', 
#             'company_logo'
#         )

#     def clean(self):
#         cleaned_data = super().clean()
#         group = cleaned_data.get('group')        
#         seller_type = cleaned_data.get('seller_type')

#         # Check if the profile has a company
#         profile = getattr(self.instance, 'profile', None)
#         company_exists = profile.company if profile else None

#         if group and group.id == 3:
#             if not seller_type:
#                 self.add_error('seller_type', 'Seller Type is required for sellers.')
#             if seller_type == 'Company':
#                 if not cleaned_data.get('company_name'):
#                     self.add_error('company_name', 'This field is required.')
#                 if not cleaned_data.get('company_phone'):
#                     self.add_error('company_phone', 'This field is required.')
#                 if not cleaned_data.get('company_address'):
#                     self.add_error('company_address', 'This field is required.')
#                 # Validate company_logo only if no company exists
#                 if not cleaned_data.get('company_logo') and not company_exists:
#                     self.add_error('company_logo', 'This field is required.')
#         return cleaned_data

#     def save_profile(self, user, commit=True):
#         profile = Profile.objects.update_or_create(
#             user=user,
#             defaults={
#                 'title': self.cleaned_data['title'],
#                 'gender': self.cleaned_data['gender'],
#                 'phone_no': self.cleaned_data['phone_no'],
#                 'address': self.cleaned_data['address'],
#                 'country': self.cleaned_data['country'],
#                 'state': self.cleaned_data['state'],
#                 'city': self.cleaned_data['city'],
#                 'zipcode': self.cleaned_data['zipcode'],
#                 'photo': self.cleaned_data['photo']
#             }
#         )
#         return profile

#     def save_company(self, profile, commit=True):
#     # Update existing company or create a new one
#         company_data = {
#             'name': self.cleaned_data.get('company_name'),
#             'phone_no': self.cleaned_data.get('company_phone'),
#             'address': self.cleaned_data.get('company_address'),
#             'company_logo': self.cleaned_data.get('company_logo')
#         }

#         if profile.company:  # Check if the profile already has a linked company
#             for key, value in company_data.items():
#                 if value:  # Update only if a new value is provided
#                     setattr(profile.company, key, value)
#             if commit:
#                 profile.company.save()
#         else:
#             # Create a new company if none exists
#             Company.objects.create(profile=profile, **company_data)


# class SignUpForm(UserCreationForm, UserProfileForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = UserCreationForm.Meta.fields + (
#             'title', 'first_name', 'last_name', 'email', 'phone_no', 
#             'gender', 'address', 'country', 'state', 'city', 
#             'zipcode', 'photo', 'group', 'seller_type', 
#             'company_name', 'company_phone', 'company_address'
#         )

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("This email is already registered.")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if commit:
#             user.save()
#             profile = self.save_profile(user, commit)
#             user.groups.clear()
#             user.groups.add(self.cleaned_data['group'])
#             if self.cleaned_data['group'].id == 3 and self.cleaned_data['seller_type'] == 'Company':
#                 self.save_company(profile, commit)  # Ensure to save company details
#         return user

# class UserAndProfileForm(UserProfileForm):
#     class Meta(UserProfileForm.Meta):
#         fields = UserProfileForm.Meta.fields

#     def save(self, commit=True):
#         user = super(UserAndProfileForm, self).save(commit=False)
#         if commit:
#             user.save()
#             profile = self.save_profile(user, commit)
#             user.groups.clear()
#             user.groups.add(self.cleaned_data['group'])
#             if self.cleaned_data['group'].id == 3:
#                 if self.cleaned_data['seller_type'] == 'Company':
#                     self.save_company(profile, commit)
#                 elif profile.companies.exists():
#                     profile.companies.first().delete()  # Ensure the company is deleted if seller type changes
#         return user

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from adminpanel.models import Profile, Company

class UserProfileForm(forms.ModelForm):
    title = forms.ChoiceField(choices=[
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('other', 'Other'),
    ], required=True)

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    phone_no = forms.CharField(max_length=15, required=True)
    gender = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=True)
    country = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    zipcode = forms.CharField(max_length=10, required=True)
    photo = forms.ImageField(required=False)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Role",
        to_field_name="id"
    )
    seller_type = forms.ChoiceField(choices=[
        ('Individual', 'Individual'), 
        ('Company', 'Company')
    ], required=False)
    company_name = forms.CharField(max_length=255, required=False)
    company_phone = forms.CharField(max_length=15, required=False)
    company_address = forms.CharField(widget=forms.Textarea, required=False)
    company_logo = forms.ImageField(required=False)
    
    # Add new company location fields
    company_country = forms.CharField(max_length=100, required=False)
    company_state = forms.CharField(max_length=100, required=False)
    company_city = forms.CharField(max_length=100, required=False)
    company_zipcode = forms.CharField(max_length=10, required=False)

    class Meta:
        model = User
        fields = (
            'title', 'email', 'first_name', 'last_name', 'phone_no', 
            'gender', 'address', 'country', 'state', 'city', 
            'zipcode', 'photo', 'group', 'seller_type', 
            'company_name', 'company_phone', 'company_address', 
            'company_logo', 'company_country', 'company_state',
            'company_city', 'company_zipcode'
        )

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')        
        seller_type = cleaned_data.get('seller_type')

        # Check if the profile has a company
        profile = getattr(self.instance, 'profile', None)
        company_exists = profile.company if profile else None

        if group and group.id == 3:
            if not seller_type:
                self.add_error('seller_type', 'Seller Type is required for sellers.')
            
            if seller_type == 'Company':
                # Validate company basic info
                company_fields = [
                    'company_name', 'company_phone', 'company_address',
                    'company_country', 'company_state', 'company_city',
                    'company_zipcode'
                ]
                
                for field in company_fields:
                    if not cleaned_data.get(field):
                        self.add_error(field, 'This field is required for company sellers.')
                
                # Validate company logo only if no company exists
                if not cleaned_data.get('company_logo') and not company_exists:
                    self.add_error('company_logo', 'Company logo is required for new company sellers.')
        
        return cleaned_data

    def save_profile(self, user, commit=True):
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                'title': self.cleaned_data['title'],
                'gender': self.cleaned_data['gender'],
                'phone_no': self.cleaned_data['phone_no'],
                'address': self.cleaned_data['address'],
                'country': self.cleaned_data['country'],
                'state': self.cleaned_data['state'],
                'city': self.cleaned_data['city'],
                'zipcode': self.cleaned_data['zipcode'],
                'photo': self.cleaned_data['photo']
            }
        )
        return profile

    def save_company(self, profile, commit=True):
        company_data = {
            'name': self.cleaned_data.get('company_name'),
            'phone_no': self.cleaned_data.get('company_phone'),
            'address': self.cleaned_data.get('company_address'),
            'company_logo': self.cleaned_data.get('company_logo'),
            'country': self.cleaned_data.get('company_country'),
            'state': self.cleaned_data.get('company_state'),
            'city': self.cleaned_data.get('company_city'),
            'zipcode': self.cleaned_data.get('company_zipcode')
        }

        if profile.company:  # Update existing company
            for key, value in company_data.items():
                if value:  # Update only if a new value is provided
                    setattr(profile.company, key, value)
            if commit:
                profile.company.save()
        else:
            # Create new company
            Company.objects.create(profile=profile, **company_data)


class SignUpForm(UserCreationForm, UserProfileForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'title', 'first_name', 'last_name', 'email', 'phone_no', 
            'gender', 'address', 'country', 'state', 'city', 
            'zipcode', 'photo', 'group', 'seller_type', 
            'company_name', 'company_phone', 'company_address',
            'company_logo', 'company_country', 'company_state',
            'company_city', 'company_zipcode'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = self.save_profile(user, commit)
            user.groups.clear()
            user.groups.add(self.cleaned_data['group'])
            if self.cleaned_data['group'].id == 3 and self.cleaned_data['seller_type'] == 'Company':
                self.save_company(profile, commit)
        return user


class UserAndProfileForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = UserProfileForm.Meta.fields

    def save(self, commit=True):
        user = super(UserAndProfileForm, self).save(commit=False)
        if commit:
            user.save()
            profile = self.save_profile(user, commit)
            user.groups.clear()
            user.groups.add(self.cleaned_data['group'])
            if self.cleaned_data['group'].id == 3:
                if self.cleaned_data['seller_type'] == 'Company':
                    self.save_company(profile, commit)
                elif profile.companies.exists():
                    profile.companies.first().delete()
        return user
