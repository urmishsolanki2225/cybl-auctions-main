from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

class Country(models.Model):
    name = models.CharField(max_length=255)
    topLevelDomain = models.CharField(max_length=10, blank=True, null=True)
    alpha2Code = models.CharField(max_length=2, blank=True, null=True)
    alpha3Code = models.CharField(max_length=3, blank=True, null=True)
    callingCodes = models.CharField(max_length=10, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    altSpellings = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)
    adminCode1 = models.CharField(max_length=10)
    lat = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    population = models.IntegerField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class Profile(models.Model):
    TITLE_CHOICES = [
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('other', 'Other'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    SELLER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', unique=True)
    company = models.ForeignKey('company', on_delete=models.CASCADE, related_name='profiles', blank=True, null=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True, related_name='profiles')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True, related_name='profiles')
    city = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    seller_type = models.CharField(max_length=10, choices=SELLER_TYPE_CHOICES, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_permissions(self):
        try:
            group = Group.objects.get(name=self.role.title)
            return group.permissions.all()
        except Group.DoesNotExist:
            return None

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if the profile already exists
    profile, created = Profile.objects.get_or_create(user=instance)
    if not created:
        profile.save()
