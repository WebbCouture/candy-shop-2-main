from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon = models.ForeignKey("Coupon", null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gift_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gift_recipient = models.CharField(max_length=200, blank=True, default='')
    gift_code = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def recalculate_total(self):
        subtotal = sum((item.line_total() for item in self.items.all()), Decimal('0.00'))
        discount = Decimal('0.00')

        if self.coupon and self.coupon.is_valid_now():
            if self.coupon.type == "percent":
                discount = subtotal * (self.coupon.value / Decimal('100'))
            elif self.coupon.type == "amount":
                discount = min(self.coupon.value, subtotal)
            elif self.coupon.type == "freeship":
                discount = Decimal('5.00')

        self.discount_amount = discount
        self.total = subtotal - discount
        self.save(update_fields=['total', 'discount_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    def line_total(self):
        return (self.price or Decimal('0.00')) * Decimal(self.quantity)


class GiftCertificate(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("issued", "Issued"),
        ("redeemed", "Redeemed"),
        ("canceled", "Canceled"),
    ]
    code = models.CharField(max_length=20, unique=True, blank=True)
    recipient_name = models.CharField(max_length=120)
    recipient_email = models.EmailField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"GiftCertificate {self.code or '(pending)'} • ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.code:
            import secrets
            self.code = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)


# --- NEW: Coupon ---
class Coupon(models.Model):
    TYPE_CHOICES = [
        ("percent", "Percent"),
        ("amount", "Amount"),
        ("freeship", "Free Shipping"),
    ]
    code = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    label = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.label or self.type})"

    def is_valid_now(self, now=None):
        from django.utils import timezone
        now = now or timezone.now()
        if not self.active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True
