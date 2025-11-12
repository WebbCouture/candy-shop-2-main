from django import forms
from .models import Message  # added


class ContactForm(forms.ModelForm):
    """
    A contact form for users to send messages including their name,
    email, subject, and message body.
    """
    class Meta:
        model = Message
        fields = ["name", "email", "subject", "message"]
        labels = {
            "name": "Your Name",
            "email": "Your Email",
            "subject": "Subject",
            "message": "Message",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "email": forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "subject": forms.TextInput(attrs={
                'placeholder': 'Subject',
                'class': 'form-input rounded-md border-gray-300',
            }),
            "message": forms.Textarea(attrs={
                'placeholder': 'Your message here...',
                'rows': 5,
                'class': 'form-textarea rounded-md border-gray-300',
            }),
        }

