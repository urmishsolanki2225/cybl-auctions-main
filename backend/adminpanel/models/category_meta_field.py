from django.db import models
from django.core.exceptions import ValidationError
from adminpanel.models import Category

class CategoryMetaField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('input', 'Input Box'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('textarea', 'Textarea'),
        ('toggle', 'Toggle'),
        ('select', 'Select Box'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='meta_fields')
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='input')
    field_options = models.TextField(blank=True, null=True, help_text="Comma-separated values for radio, checkbox, and select fields")
    is_filter = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        # Validate field_options for specific field types
        if self.field_type in ['radio', 'checkbox', 'select']:
            if not self.field_options or not self.field_options.strip():
                raise ValidationError({
                    'field_options': f'Field options are required for {self.get_field_type_display()} field type.'
                })
            
            # Check if options contain only commas or empty values
            options = [opt.strip() for opt in self.field_options.split(',')]
            valid_options = [opt for opt in options if opt]
            
            if len(valid_options) < 2:
                raise ValidationError({
                    'field_options': f'At least 2 options are required for {self.get_field_type_display()} field type.'
                })
            
            # Check for duplicate options
            if len(valid_options) != len(set(valid_options)):
                raise ValidationError({
                    'field_options': 'Duplicate options are not allowed.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_options_list(self):
        """Return field options as a list"""
        if self.field_options:
            return [opt.strip() for opt in self.field_options.split(',') if opt.strip()]
        return []
    
    def __str__(self):
        return f"{self.category.name} - {self.name} ({self.get_field_type_display()})"
    
    class Meta:
        unique_together = ['category', 'name']
        ordering = ['-created_at']