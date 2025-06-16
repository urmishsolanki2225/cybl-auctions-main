from django.contrib import admin
from adminpanel.models import Category, Profile, Country, State, Company, Auctions, Inventory, Media, Bid, Payment_History  # Import the models

# Register your models here.
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Company)
admin.site.register(Auctions)
admin.site.register(Inventory)
admin.site.register(Media)
admin.site.register(Bid)
admin.site.register(Payment_History)
