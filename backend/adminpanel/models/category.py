from django.db import models
from django.utils import timezone

def category_image_path(instance, filename):
    # Generates path like: category/categoryname_id.ext
    ext = filename.split('.')[-1]
    if instance.parent:
        # For subcategories: category/parentname_id.ext
        return f'category/{instance.parent.name}_{instance.id}.{ext}'
    else:
        # For main categories: category/categoryname_id.ext
        return f'category/{instance.name}_{instance.id}.{ext}'

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to=category_image_path, null=True, blank=True)
    is_active = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other categories
            Category.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'parent', 'order')
