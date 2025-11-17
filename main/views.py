from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm
from .models import Product, Order, GiftCertificate, OrderItem

from decimal import Decimal
import time
import stripe

# Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def to_cents(amount) -> int:
    d = Decimal(str(amount)).quantize(Decimal("0.01"))
    return int(d * 100)


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

    messages.success(request, f'"{product.name}" lades till i korgen')
    return redirect("cart")


def cart_view(request):
    # BETALNING KLAR – SPARA ORDER + TÖM KUNDVAGN
    if request.GET.get('success') == '1':
        cart = request.session.get('cart', {})

        if request.user.is_authenticated and cart:
            order = Order.objects.create(
                user=request.user,
                total=Decimal('0.00'),
            )

            gift_total = Decimal('0.00')

            for key, item in cart.items():
                # PRESENTKORT
                if str(key).startswith("gift:") or item.get("type") == "gift_certificate":
                    amount = Decimal(item.get("amount", "0") or "0")
                    recipient_name = item.get("recipient_name") or "Okänd mottagare"
                    recipient_email = item.get("recipient_email") or "no@email"

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
            order.save()

        # TÖM KUNDVAGNEN HELT
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        messages.success(request, "Betalningen lyckades! Din order är sparad.")
        return redirect('account')

    # AVBRUTEN BETALNING
    if request.GET.get('canceled') == '1':
        messages.warning(request, "Betalningen avbröts. Dina varor finns kvar i korgen.")
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
                "name": item.get("name", "Presentkort"),
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

    total = subtotal.quantize(Decimal('0.01'))

    return render(request, 'main/cart.html', {
        'cart': cart,
        'STRIPE_PUBLIC_KEY': public_key,
        'items': items,
        'has_items': bool(items),
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'total': total,
        'currency': currency,
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
                    "product_data": {"name": item.get("name", "Presentkort")},
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
            success_url=request.build_absolute_uri("/account/"),
            cancel_url=request.build_absolute_uri("/cart/"),
        )
    except Exception as e:
        messages.error(request, f"Betalningsfel: {e}")
        return redirect('cart')

    return redirect(session.url, code=303)


def cart_increase(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        cart[item_id]['quantity'] += 1
        request.session['cart'] = cart
        messages.success(request, f"Ökade antal av {cart[item_id]['name']}.")
    return redirect('cart')


def cart_decrease(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        if cart[item_id]['quantity'] > 1:
            cart[item_id]['quantity'] -= 1
            messages.success(request, f"Minskade antal av {cart[item_id]['name']}.")
        else:
            name = cart[item_id]['name']
            del cart[item_id]
            messages.success(request, f"Tog bort {name} från korgen.")
        request.session['cart'] = cart
    return redirect('cart')


def cart_delete(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    if item_id in cart:
        name = cart[item_id]['name']
        del cart[item_id]
        request.session['cart'] = cart
        messages.success(request, f"Tog bort {name} från korgen.")
    return redirect('cart')


def logout_view(request):
    logout(request)
    messages.success(request, "Du är nu utloggad.")
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
                messages.success(request, "Inloggning lyckades!")
                return redirect('account')
        elif 'signup' in request.POST:
            signup_form = RegistrationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, "Registrering klar! Du är inloggad.")
                return redirect('account')

    return render(request, 'registration/account.html', {
        'login_form': login_form or AuthenticationForm(),
        'signup_form': signup_form or RegistrationForm(),
        'dashboard': False,
        'active_tab': 'login' if 'login' in request.POST else 'signup',
    })


def gift_certificates(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        amount_str = (request.POST.get('amount') or '').strip()

        if not all([name, email, amount_str]):
            messages.error(request, "Fyll i alla fält.")
            return redirect('gift_certificates')

        try:
            amount = Decimal(amount_str)
        except Exception:
            messages.error(request, "Beloppet måste vara ett giltigt nummer.")
            return redirect('gift_certificates')

        if amount < 1:
            messages.error(request, "Minsta belopp är 1 kr.")
            return redirect('gift_certificates')

        cart = request.session.get("cart", {})
        gc_key = f"gift:{int(time.time())}"
        cart[gc_key] = {
            "type": "gift_certificate",
            "name": f"Presentkort till {name} ({amount} kr)",
            "image_url": "",
            "quantity": 1,
            "amount": str(amount),
            "recipient_email": email,
        }
        request.session["cart"] = cart
        request.session.modified = True

        GiftCertificate.objects.create(
            recipient_name=name,
            recipient_email=email,
            amount=amount,
            message="",
            status="pending",
        )

        messages.success(request, f"Presentkort ({amount} kr) tillagt i korgen!")
        return redirect('cart')

    return render(request, 'main/gift_certificates.html')


@login_required(login_url='account')
def purchase_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-date').prefetch_related('items__product')
    return render(request, 'main/purchase_history.html', {'orders': orders})


def shipping(request):
    return render(request, 'main/shipping.html')