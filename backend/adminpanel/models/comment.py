from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Auctions, Inventory

class Comment(models.Model):
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name='comments')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # latest comments first

    def __str__(self):
        return f"Comment by {self.user.username} on Lot {self.lot.id} in Auction {self.auction.id}"
