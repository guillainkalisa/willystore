from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import OrderItem, Order
from cart.cart import Cart
from .momo_api import momo_provider

def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('store:product_list')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        district = request.POST.get('district')
        payment_method = request.POST.get('payment_method', 'cash')
        transaction_id = request.POST.get('transaction_id', '')

        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            district=district,
            payment_method=payment_method,
            transaction_id=transaction_id,
            paid=False
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
                size=item.get('size', ''),
                color=item.get('color', '')
            )

        if payment_method == 'momo':
            amount = cart.get_total_price()
            ref_id, success = momo_provider.request_to_pay(
                amount=amount, 
                phone_number=phone, 
                external_id=order.id
            )
            
            if success and ref_id:
                order.transaction_id = ref_id
                order.save()
                cart.clear()
                return redirect('orders:order_processing', order_id=order.id)
            else:
                order.transaction_id = "API_FAILED"
                order.save()
                cart.clear()
                return render(request, 'orders/created.html', {'order': order, 'error': 'API push failed. We entered fallback.'})

        cart.clear()
        return render(request, 'orders/created.html', {'order': order})
    else:
        return render(request, 'orders/create.html', {'cart': cart})

def order_processing(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/processing.html', {'order': order})

def check_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not order.transaction_id or order.transaction_id == "API_FAILED":
        return JsonResponse({'status': 'FAILED'})
        
    status = momo_provider.get_transaction_status(order.transaction_id)
    
    if status == 'SUCCESSFUL' and not order.paid:
        order.paid = True
        order.save()
        
    return JsonResponse({'status': status})
