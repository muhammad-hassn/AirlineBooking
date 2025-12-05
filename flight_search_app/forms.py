from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    country = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Country'}))
    postal_code = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Postal Code'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'country', 'postal_code')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                country=self.cleaned_data['country'],
                postal_code=self.cleaned_data['postal_code']
            )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
