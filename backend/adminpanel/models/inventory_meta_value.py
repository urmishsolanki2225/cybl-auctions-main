from django.db import models
from adminpanel.models import Inventory, CategoryMetaField

class InventoryMetaValue(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='meta_values')
    meta_field = models.ForeignKey(CategoryMetaField, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.inventory.title} - {self.meta_field.name}: {self.value}"
