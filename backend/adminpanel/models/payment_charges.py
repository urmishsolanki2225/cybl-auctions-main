# adminpanel/models/payment_charges.py
from django.db import models
from django.utils import timezone

class PaymentChargeDetail(models.Model):
    class ChargeType(models.TextChoices):
        STORAGE = 'Storage', 'Storage Charge'
        LABEL = 'Label', 'Labeling Charge'

    payment = models.ForeignKey('Payment_History', on_delete=models.CASCADE, related_name='charge_details')
    charge_type = models.CharField(max_length=50, choices=ChargeType.choices)
    description = models.TextField(blank=True, null=True)
    per_day_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    days = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.per_day_amount and self.days:
            self.total_amount = self.per_day_amount * self.days
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def __str__(self):
        return f"{self.charge_type} - ₹{self.total_amount} for {self.days} days"

    class Meta:
        db_table = 'payment_charge_details'