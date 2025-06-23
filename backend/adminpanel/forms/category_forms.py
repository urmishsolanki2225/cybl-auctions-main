from django import forms
from django.core.validators import MaxLengthValidator
from adminpanel.models import Category
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        validators=[MaxLengthValidator(255)],
        widget=forms.TextInput(attrs={'maxlength': 255})
    )

    image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/jpeg, image/png, image/webp'})
    )

    class Meta:
        model = Category
        fields = ['name', 'parent', 'image']        

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        parent = cleaned_data.get('parent')             

        if name and parent:
            # Check if a subcategory with the same name already exists under the parent category
            if Category.objects.filter(name=name, parent=parent).exists():
                self.add_error('name', "A subcategory with this name already exists under the selected parent category.")
        elif name:
            # Check if a category with the same name already exists at the top level
            if Category.objects.filter(name=name, parent__isnull=True).exists():
                self.add_error('name', "A category with this name already exists.")

        return cleaned_data
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Skip validation if no new image is provided during update
            if hasattr(image, 'name'):
                valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                extension = image.name.lower().split('.')[-1]
                
                if f'.{extension}' not in valid_extensions:
                    raise ValidationError(
                        "Unsupported file format. Only JPG, JPEG, PNG, and WEBP images are allowed."
                    )
                
                # Optional: Validate file size (e.g., 5MB limit)
                if image.size > 5 * 1024 * 1024:  # 5MB
                    raise ValidationError("Image size should be less than 5MB.")
        return image
