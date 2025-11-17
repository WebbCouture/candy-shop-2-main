from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm
from .models import Product, Order, GiftCertificate, Coupon, OrderItem

from decimal import Decimal, ROUND_HALF_UP
import time
import stripe

# Configure Stripe once using settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def to_cents(amount) -> int:
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((d * 100).to_integral_value())


# Product list + search
def product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    no_results = bool(query) and not products.exists()
    return render(request, 'main/product_list.html', {
        'products': products,
        'search_query': query,
        'no_results': no_results,
    })


# --- Coupons & Promotions page ---
def coupons(request):
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        if not code:
            messages.error(request, "Please enter a code.")
            return redirect("coupons")

        try:
            promo = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            messages.error(request, f"Code '{code}' is invalid or expired.")
            return redirect("coupons")

        if not promo.is_valid_now(timezone.now()):
            messages.error(request, f"Code '{code}' is not active right now.")
            return redirect("coupons")

        request.session["promo"] = {
            "code": promo.code,
            "type": promo.type,
            "value": float(promo.value),
            "label": promo.label or "",
        }
        request.session.modified = True
        messages.success(request, f"Applied: {promo.label or promo.code} (code {promo.code}).")
        return redirect("cart")

    current = request.session.get("promo")
    return render(request, "main/coupons.html", {"current_promo": current})


@require_POST
def apply_coupon(request):
    code = (request.POST.get("promo_code") or "").strip().upper()
    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect("cart")

    try:
        promo = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        messages.error(request, f"Code '{code}' is invalid or expired.")
        return redirect("cart")

    if not promo.is_valid_now(timezone.now()):
        messages.error(request, f"Code '{code}' is not active right now.")
        return redirect("cart")

    request.session["promo"] = {
        "code": promo.code,
        "type": promo.type,
        "value": float(promo.value),
        "label": promo.label or "",
    }
    request.session.modified = True
    messages.success(request, f"Applied: {promo.label or promo.code} (code {promo.code}).")
    return redirect("cart")


def reviews(request):
    return render(request, 'main/reviews.html')


def blog(request):
    return render(request, 'main/blog.html')


def recipes(request):
    return render(request, 'main/recipes.html')


@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_id_str = str(product_id)

    item = cart.get(product_id_str, {
        "name": product.name,
        "image_url": product.image_url,
        "quantity": 0,
    })
    item["quantity"] += 1
    cart[product_id_str] = item

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, f'"{product.name}" was added to your cart')
    return redirect("cart")


def cart_view(request):
    # BETALNING KLAR – SPARA ORDER + PRESENTKORT
    if request.GET.get('success') == '1':
        promo_obj = None
        promo = request.session.pop('promo', None)
        if promo:
            try:
                c = Coupon.objects.get(code=promo.get('code'))
                c.used_count = (c.used_count or 0) + 1
                c.save(update_fields=['used_count'])
                coupon_obj = c
            except Coupon.DoesNotExist:
                pass

        cart = request.session.get('cart', {})

        if request.user.is_authenticated and cart:
            order = Order.objects.create(
                user=request.user,
                total=Decimal('0.00'),
                coupon=coupon_obj,
                discount_amount=Decimal('0.00'),
            )

            gift_total = Decimal('0.00')

            for key, item in cart.items():
                # PRESENTKORT
                if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
                    amount = Decimal(item.get("amount", "0") or "0")
                    recipient_name = item.get("recipient_name") or item.get("name", "Okänd").split(" for ")[-1].split(" ($")[0]
                    recipient_email = item.get("recipient_email", "no@email")

                    gift_cert = GiftCertificate.objects.create(
                        recipient_name=recipient_name,
                        recipient_email=recipient_email,
                        amount=amount,
                        message=item.get("message", ""),
                        status="issued",
                    )

                    order.gift_amount = amount
                    order.gift_recipient = f"{gift_cert.recipient_name} ({gift_cert.recipient_email})"
                    order.gift_code = gift_cert.code
                    order.save(update_fields=['gift_amount', 'gift_recipient', 'gift_code'])

                    gift_total += amount
                    continue

                # VANLIGA PRODUKTER
                try:
                    product = Product.objects.get(id=int(key))
                except (ValueError, Product.DoesNotExist):
                    continue

                qty = int(item.get("quantity", 1))
                price = Decimal(product.price or 0)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price,
                )

            order.recalculate_total()
            if gift_total > 0:
                order.total += gift_total
                order.save(update_fields=['total'])

        # TÖM KUNDVAGNEN
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        messages.success(request, "Payment successful! Your order is confirmed.")
        return redirect('cart')

    if request.GET.get('canceled') == '1':
        messages.warning(request, "Payment canceled. Your items are still in the cart.")
        return redirect('cart')

    # VANLIG KUNDVAGN
    cart = request.session.get('cart', {})
    public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    items = []
    subtotal = Decimal('0.00')
    currency = getattr(settings, 'STRIPE_CURRENCY', 'usd').upper()

    for key, item in cart.items():
        if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
            qty = int(item.get("quantity", 1))
            unit_price = Decimal(item.get("amount", "0") or "0")
            line_total = unit_price * qty
            items.append({
                "id": key,
                "name": item.get("name", "Gift Certificate"),
                "description": item.get("description", ""),
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "is_gift": True,
            })
            subtotal += line_total
        else:
            try:
                product = Product.objects.get(id=int(key))
            except (ValueError, Product.DoesNotExist):
                continue
            qty = int(item.get("quantity", 1))
            unit_price = Decimal(product.price or 0)
            line_total = unit_price * qty
            items.append({
                "id": key,
                "name": product.name,
                "description": getattr(product, "description", ""),
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "is_gift": False,
            })
            subtotal += line_total

    promo = request.session.get("promo")
    discount = Decimal('0.00')
    shipping = Decimal('0.00')

    if promo:
        ptype = promo.get("type")
        pval = promo.get("value", 0)
        if ptype == "percent":
            discount = (subtotal * Decimal(pval) / Decimal('100')).quantize(Decimal('0.01'))
        elif ptype == "amount":
            discount = Decimal(str(pval))
        elif ptype == "freeship":
            shipping = Decimal('0.00')

    if discount > subtotal:
        discount = subtotal

    total = (subtotal - discount + shipping).quantize(Decimal('0.01'))

    return render(request, 'main/cart.html', {
        'cart': cart,
        'STRIPE_PUBLIC_KEY': public_key,
        "items": items,
        "has_items": bool(items),
        "subtotal": subtotal.quantize(Decimal('0.01')),
        "discount": discount.quantize(Decimal('0.01')),
        "shipping": shipping.quantize(Decimal('0.01')),
        "total": total,
        "currency": currency,
        "promo": promo,
    })


@login_required(login_url='account')
@require_POST
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    line_items = []
    currency = getattr(settings, "STRIPE_CURRENCY", "usd")

    for key, item in cart.items():
        if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
            amt_cents = to_cents(item.get("amount", "0"))
            if amt_cents <= 0:
                continue
            line_items.append({
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": item.get("name", "Gift Certificate")},
                    "unit_amount": amt_cents,
                },
                "quantity": 1,
            })
        else:
            try:
                product = Product.objects.get(id=int(key))
            except (ValueError, Product.DoesNotExist):
                continue

            qty = int(item.get("quantity", 1))
            unit_price = getattr(product, "price", 0)
            unit_cents = to_cents(unit_price)
            if unit_cents <= 0 or qty <= 0:
                continue

            line_items.append({
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": product.name},
                    "unit_amount": unit_cents,
                },
                "quantity": qty,
            })

    if not line_items:
        return redirect('cart')

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=request.build_absolute_uri("/cart/?success=1"),
            cancel_url=request.build_absolute_uri("/cart/?canceled=1"),
        )
    except Exception as e:
        messages.error(request, f"Payment error: {e}")
        return redirect('cart')

    return redirect(session.url, code=303)


def cart_increase(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        cart[item_id]['quantity'] += 1
        request.session['cart'] = cart
        messages.success(request, f"Increased quantity of {cart[item_id]['name']}.")
    return redirect('cart')


def cart_decrease(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        if cart[item_id]['quantity'] > 1:
            cart[item_id]['quantity'] -= 1
            messages.success(request, f"Decreased quantity of {cart[item_id]['name']}.")
        else:
            name = cart[item_id]['name']
            del cart[item_id]
            messages.success(request, f"Removed {name} from cart.")
        request.session['cart'] = cart
    return redirect('cart')


def cart_delete(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        name = cart[item_id]['name']
        del cart[item_id]
        request.session['cart'] = cart
        messages.success(request, f"Removed {name} from cart.")
    return redirect('cart')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('account')


def account(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        return render(request, 'registration/account.html', {
            'dashboard': True,
            'orders': orders
        })

    login_form = AuthenticationForm()
    signup_form = RegistrationForm()

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('account')
            else:
                return render(request, 'registration/account.html', {
                    'login_form': login_form,
                    'signup_form': RegistrationForm(),
                    'dashboard': False,
                    'active_tab': 'login',
                })

        elif 'signup' in request.POST:
            signup_form = RegistrationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect('account')
            else:
                return render(request, 'registration/account.html', {
                    'login_form': AuthenticationForm(),
                    'signup_form': signup_form,
                    'dashboard': False,
                    'active_tab': 'signup',
                })

    return render(request, 'registration/account.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'dashboard': False,
        'active_tab': 'login',
    })


def gift_certificates(request):
    TEST_CODES = {
        "12345": {"balance": "50.00", "expires": "2026-12-31"},
        "00000": {"balance": "0.00",  "expires": "2026-12-31"},
        "777777": {"balance": "25.00", "expires": "2026-06-30"},
    }

    if request.method == 'POST':
        if "code" in request.POST:
            code = (request.POST.get("code") or "").strip()
            if not code.isdigit():
                messages.error(request, "Please enter numbers only.")
                return redirect('gift_certificates')

            info = TEST_CODES.get(code)
            if info:
                messages.success(request, f"Code {code} is valid. Balance: ${info['balance']} — Expires: {info['expires']} (demo)")
            else:
                messages.error(request, f"Code {code} is invalid or not found (demo).")
            return redirect('gift_certificates')

        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        amount_str = (request.POST.get('amount') or '').strip()

        if not name or not email or not amount_str:
            messages.error(request, "Please fill out all fields before submitting.")
            return redirect('gift_certificates')

        try:
            amount = Decimal(amount_str)
        except Exception:
            messages.error(request, "Amount must be a valid number.")
            return redirect('gift_certificates')

        if amount < 1:
            messages.error(request, "Minimum amount is $1.")
            return redirect('gift_certificates')

        cart = request.session.get("cart", {})
        gc_key = f"gift:{int(time.time())}"
        cart[gc_key] = {
            "type": "gift_certificate",
            "name": f"Gift Certificate for {name} (${amount})",
            "image_url": "",
            "quantity": 1,
            "amount": str(amount),
            "recipient_email": email,
        }
        request.session["cart"] = cart

        GiftCertificate.objects.create(
            recipient_name=name,
            recipient_email=email,
            amount=amount,
            message="",
            status="pending",
        )

        messages.success(request, f"Added gift certificate (${amount}) to your cart.")
        return redirect('cart')

    return render(request, 'main/gift_certificates.html')


@login_required(login_url='account')
def purchase_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by('-date')
        .prefetch_related('items__product')
    )

    return render(request, 'main/purchase_history.html', {
        'orders': orders,
    })


def shipping(request):
    return render(request, 'main/shipping.html')