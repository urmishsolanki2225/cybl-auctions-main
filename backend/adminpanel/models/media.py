from django.db import models
from adminpanel.models import Inventory
class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('FILE', 'File'),
    ]
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='media_items', null=True, blank=True)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    entity = models.CharField(max_length=255)
    type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES)
    is_feature = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.path