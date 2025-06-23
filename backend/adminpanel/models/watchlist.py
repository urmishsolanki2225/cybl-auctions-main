from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Inventory

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='watchlisted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'inventory')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.inventory.title}"