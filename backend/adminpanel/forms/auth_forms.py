from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.core.exceptions import ValidationError
import re

# Login Page Validation
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254, required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        if not re.match(email_regex, username):
            raise ValidationError("Enter a valid email address.")
        
        return username

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254, required=True)

# Define the custom validator
class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.findall('[^A-Za-z0-9]', password):
            raise ValidationError(
                "This password must contain at least one special character.",
                code='password_no_special_char',
            )

    def get_help_text(self):
        return "Your password must contain at least one special character."

# Define the custom password reset confirm form
class CustomPasswordResetConfirmForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': 'The two password fields didn’t match. Please confirm your password.',
        'password_too_short': 'This password is too short. It must contain at least 8 characters.',
        'password_no_special_char': 'This password must contain at least one special character.',
        'required': 'This field is required.',
    }

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
            if len(password1) < 8:
                raise forms.ValidationError(self.error_messages['password_too_short'], code='password_too_short')
            # Custom special character validation
            special_char_validator = SpecialCharacterValidator()
            try:
                special_char_validator.validate(password1)
            except ValidationError:
                raise forms.ValidationError(self.error_messages['password_no_special_char'], code='password_no_special_char')

        return password2
