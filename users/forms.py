from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

#User Registration Form
class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta():
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1','password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

#client side profile update where we project two forms as one on the web interface
class UserUpdateForm(ModelForm):
    email = forms.EmailField()
    
    class Meta():
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(ModelForm):
    class Meta():
        model = Profile
        fields = ['image']
