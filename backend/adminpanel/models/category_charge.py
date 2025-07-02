# models.py
from django.db import models
from adminpanel.models import Category

class ChargeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CategoryCharge(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="charges")
    charge_type = models.ForeignKey(ChargeType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('category', 'charge_type')

    def __str__(self):
        return f"{self.charge_type.name} for {self.category.name} - ₹{self.amount}"