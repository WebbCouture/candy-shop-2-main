from django.contrib import admin
from .models import Coupon, Cart, CartItem, GiftCertificate


@admin.register(GiftCertificate)
class GiftCertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "recipient_name", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "recipient_name", "recipient_email")
    readonly_fields = ("code", "created_at")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "value", "label", "active", "starts_at", "ends_at", "used_count")
    list_filter = ("active", "type", "starts_at", "ends_at")
    search_fields = ("code", "label")
    readonly_fields = ("used_count",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price")
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("cart", "product", "quantity", "total_price")
