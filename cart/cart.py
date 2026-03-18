from decimal import Decimal
from django.conf import settings
from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart_session_id')
        if not cart:
            cart = self.session['cart_session_id'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, size='', color=''):
        product_id = str(product.id)
        # Create a unique key for product + size + color combination
        item_id = f"{product_id}_{size}_{color}"

        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(product.price), 'product_id': product_id, 'size': size, 'color': color}
        
        if override_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, size='', color=''):
        product_id = str(product.id)
        item_id = f"{product_id}_{size}_{color}"
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def __iter__(self):
        # We need to fetch products by product_id
        product_ids = [item['product_id'] for item in self.cart.values() if 'product_id' in item]
        # Fallback for old carts
        if not product_ids:
            product_ids = self.cart.keys()
            
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        # Map products by ID for easy lookup
        product_map = {str(p.id): p for p in products}
        
        for item_id, item in cart.items():
            pid = item.get('product_id', item_id)
            if pid in product_map:
                item['product'] = product_map[pid]
                item['item_id'] = item_id # to use in templates for forms
                
        for item in cart.values():
            if 'product' not in item: continue
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart_session_id']
        self.save()
