from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Create Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            # 'maxlength': '20' stops users from physically typing more than 20 characters in the browser field
            'username': forms.TextInput(attrs={'placeholder': 'Username (Max 20 chars)', 'maxlength': '20'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # Secure backend check: rejects registration if the string somehow exceeds 20 characters
        if username and len(username) > 20:
            raise forms.ValidationError("Username cannot be longer than 20 characters.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']