def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = 0

    if isinstance(cart, dict):
        for item in cart.values():
            if isinstance(item, dict) and 'quantity' in item:
                count += item['quantity']
            else:
                count += 1  # fallback if item is not a dict
    elif isinstance(cart, list):
        count = len(cart)
    
    return {'cart_item_count': count}
