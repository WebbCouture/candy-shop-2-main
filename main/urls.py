from django.contrib.auth.views import LoginView  # optional; fine to keep
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Home, Products, About, Contact pages
    path('products/', views.product_list, name='product_list'),
    path('shipping/', views.shipping, name='shipping'),
    path('coupons/', views.coupons, name='coupons'),
    path('reviews/', views.reviews, name='reviews'),
    path('blog/', views.blog, name='blog'),
    path('recipes/', views.recipes, name='recipes'), 
    
    # Cart-related URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),

    # Cart item quantity management URLs
    path('cart/increase/<path:item_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<path:item_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/delete/<path:item_id>/', views.cart_delete, name='cart_delete'),

    # Apply coupon (for the cart page form)
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),

    # Accounts-related URL (Login + Registration combined page)
    path('account/', views.account, name='account'),  # Changed from 'accounts/' to 'account/'

    # Custom logout route
    path('logout/', views.logout_view, name='logout'),

    # Redirect any visit to /account/login/ to your combined /account/ page
    path('account/login/', RedirectView.as_view(pattern_name='account', permanent=False)),  # Changed from 'accounts/login/'

    # Gift Certificates page
    path('gift-certificates/', views.gift_certificates, name='gift_certificates'),

    # Purchase history page (under 'account' section)
    path('account/purchase-history/', views.purchase_history, name='purchase_history'),
]

# Static files handling when DEBUG is False
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
