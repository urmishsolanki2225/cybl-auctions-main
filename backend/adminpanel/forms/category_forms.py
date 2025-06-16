from django import forms
from django.core.validators import MaxLengthValidator
from adminpanel.models import Category

class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        validators=[MaxLengthValidator(50)],
        widget=forms.TextInput(attrs={'maxlength': 50})
    )

    class Meta:
        model = Category
        fields = ['name', 'parent']

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
