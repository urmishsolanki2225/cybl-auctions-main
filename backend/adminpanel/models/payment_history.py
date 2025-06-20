from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Inventory

class Payment_History(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
        REFUNDED = 'Refunded', 'Refunded'

    class PaymentMethod(models.TextChoices):
        ONLINE = 'Online', 'Online'
        OFFLINE = 'Offline', 'Offline'

    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_histories')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='payment_histories')
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def str(self):
        return f"{self.user.username} - {self.amount} - {self.status} - {self.payment_method}"

    @property
    def total_charges_amount(self):
        """Calculate total amount of all charges for this payment"""
        return self.charge_details.filter(deleted_at__isnull=True).aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
    
    @property
    def final_amount(self):
        """Calculate final amount including all charges"""
        return self.amount + self.total_charges_amount