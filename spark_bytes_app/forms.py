from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from spark_bytes_app.models import Event

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form extending Django's built-in UserCreationForm.
    Adds fields for email, BUID, and profile picture.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})  # Style email field with a custom class
    )
    buid = forms.CharField(
        label="BUID",
        max_length=8,
        widget=forms.TextInput(attrs={'class': 'form-control'})  # Style BUID field with a custom class
    )
    img = forms.ImageField(
        label="Profile Picture",
        required=True  # Make the profile picture mandatory
    )

    class Meta:
        """
        Meta class to specify model and fields to include in the form.
        """
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'buid', 'img']

    def __init__(self, *args, **kwargs):
        """
        Override the initializer to add consistent styling to all form fields.
        """
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form extending Django's AuthenticationForm.
    Adds styling to the username and password fields.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})  # Style username field
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})  # Style password field
    )

    class Meta:
        """
        Meta class to specify fields for authentication.
        """
        model = User
        fields = ['username', 'password']


class EventForm(forms.ModelForm):
    """
    Form for creating or updating Event instances.
    Extends Django's ModelForm to map form fields to the Event model.
    """
    class Meta:
        """
        Meta class to specify the model and fields to include, 
        along with custom widgets for styling.
        """
        model = Event
        fields = [
            'name', 'description', 'img', 'location', 'date', 
            'food_types', 'allergies', 'reservation_limit'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),  # Style name field
            'description': forms.Textarea(attrs={'class': 'form-control'}),  # Style description field
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Style image upload field
            'location': forms.TextInput(attrs={'class': 'form-control'}),  # Style location field
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control', 'type': 'datetime-local'  # Date and time picker
            }),
            'food_types': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for food types
            'allergies': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for allergies
            'reservation_limit': forms.NumberInput(attrs={'class': 'form-control'})  # Style reservation limit field
        }