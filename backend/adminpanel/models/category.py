from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'parent', 'order')
