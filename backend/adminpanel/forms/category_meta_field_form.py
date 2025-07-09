from django import forms
from django.core.exceptions import ValidationError
from adminpanel.models import CategoryMetaField

class CategoryMetaFieldForm(forms.ModelForm):
    class Meta:
        model = CategoryMetaField
        fields = ['name', 'field_type', 'field_options', 'is_filter', 'is_required']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter field name'
            }),
            'field_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'fieldType'
            }),
            'field_options': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter comma-separated options (e.g., Option1, Option2, Option3)',
                'id': 'fieldOptions'
            }),
            'is_filter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError('Name cannot be empty.')
        
        name = name.strip()
        if len(name) > 255:
            raise ValidationError('Name is too long (max 255 characters).')
        
        return name
    
    def clean_field_options(self):
        field_type = self.cleaned_data.get('field_type')
        field_options = self.cleaned_data.get('field_options')
        
        # Check if options are required for specific field types
        if field_type in ['radio', 'checkbox', 'select']:
            if not field_options or not field_options.strip():
                raise ValidationError(f'Field options are required for {dict(CategoryMetaField.FIELD_TYPE_CHOICES)[field_type]} field type.')
            
            # Parse and validate options
            options = [opt.strip() for opt in field_options.split(',')]
            valid_options = [opt for opt in options if opt]
            
            if len(valid_options) < 2:
                raise ValidationError(f'At least 2 options are required for {dict(CategoryMetaField.FIELD_TYPE_CHOICES)[field_type]} field type.')
            
            # Check for duplicate options
            if len(valid_options) != len(set(valid_options)):
                raise ValidationError('Duplicate options are not allowed.')
            
            # Return cleaned comma-separated options
            return ', '.join(valid_options)
        
        # For other field types, options should be empty
        elif field_type in ['input', 'textarea', 'toggle']:
            return ''
        
        return field_options
    
    def clean(self):
        cleaned_data = super().clean()
        category = self.instance.category if self.instance.pk else None
        name = cleaned_data.get('name')
        
        # Check for unique name within category
        if category and name:
            existing = CategoryMetaField.objects.filter(
                category=category, 
                name=name
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing.exists():
                raise ValidationError({
                    'name': 'A field with this name already exists in this category.'
                })
        
        return cleaned_data