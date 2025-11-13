from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# --- Registration Form ---
class RegistrationForm(UserCreationForm):
    """
    A registration form for creating new user accounts, extending Django's
    built-in UserCreationForm — with all help texts forced to English.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'form-input rounded-md border-gray-300',
        })
    )

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-input rounded-md border-gray-300',
        })
    )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-input rounded-md border-gray-300',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        help_texts = {
            'username': "Required. Letters, digits and @/./+/-/_ only.",
            'password1': (
                "Your password must contain at least 8 characters and should be secure. "
                "Avoid using common words or personal information."
            ),
            'password2': "Enter the same password again for verification.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Force the English help texts (Django defaults might be localised)
        self.fields['password1'].help_text = (
            "Your password must contain at least 8 characters and must be secure."
        )
        self.fields['password2'].help_text = "Enter the same password as before."

    def clean_email(self):
        """
        Ensure the email is unique for each user.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        """
        Override save method to handle user creation.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
