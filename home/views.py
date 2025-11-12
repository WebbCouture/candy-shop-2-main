from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .forms import ContactForm
from .models import TeamMember, Message
from  main.models import Product


# Home page - shows latest products
def home(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    latest_products = Product.objects.all().order_by('-id')[:3]
    return render(request, 'home/home.html', {
        'cart_count': cart_count,
        'latest_products': latest_products,
    })


# About page
def about(request):
    team = TeamMember.objects.all()
    return render(request, 'home/about.html', {"team": team})


def team(request):
    team_members = TeamMember.objects.all()
    return render(request, 'home/team.html', {'team_members': team_members})

# Contact form
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to DB (Message model) manually
            msg_obj = Message.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
            )

            # Send notification to admin
            send_mail(
                f'New contact form submission: {msg_obj.subject}',
                f'From: {msg_obj.name} <{msg_obj.email}>\n\n{msg_obj.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            # Send confirmation to the user
            send_mail(
                'Thank you for contacting us',
                f'Hi {msg_obj.name},\n\nThank you for your message. We will get back to you shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [msg_obj.email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'home/contact.html', {'form': form})


# --- Static pages ---
def privacy(request):
    return render(request, 'home/privacy.html')

def terms(request):
    return render(request, 'home/terms.html')

