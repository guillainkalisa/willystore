from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from store.models import Product
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', False)
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    cart.add(product=product, quantity=quantity, override_quantity=override, size=size, color=color)
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'success',
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price()),
            'message': f"{product.title} added to cart."
        })
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    cart.remove(product, size=size, color=color)
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'success',
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price())
        })
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_drawer(request):
    cart = Cart(request)
    return render(request, 'cart/cart_drawer.html', {'cart': cart})
