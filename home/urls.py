from django.urls import path
from . import views

urlpatterns = [
    # Home, Products, About, Contact pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),

    # Team members page
    path('team/', views.team, name='team'),
]