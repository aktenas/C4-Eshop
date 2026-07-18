from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    # Defining the field explicitly here guarantees Django forces the max_length constraint onto the HTML element
    username = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'placeholder': 'Username (Max 20 chars)'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Create Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Required. 20 characters max. Letters, digits and @/./+/-/_ only."

    def clean_username(self):
        username = self.cleaned_data.get("username")
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