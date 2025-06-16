from django.db import models
from adminpanel.models import Country, State 

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_no = models.CharField(max_length=15)
    company_logo = models.ImageField(upload_to='company_logo/', blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies') 
    city = models.CharField(max_length=100, blank=True, null=True)    
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


    def __str__(self):
        return self.name