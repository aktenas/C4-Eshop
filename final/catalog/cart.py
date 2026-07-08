from decimal import Decimal
from .models import Item

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, item, quantity=1, override_quantity=False):
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(item.price)}
        
        if override_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        self.save()

    def remove(self, item):
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def __iter__(self):
        item_ids = self.cart.keys()
        items = Item.objects.filter(id__in=item_ids)
        cart = self.cart.copy()
        
        for item in items:
            cart[str(item.id)]['item'] = item

        for item_data in cart.values():
            item_data['price'] = Decimal(item_data['price'])
            item_data['total_price'] = item_data['price'] * item_data['quantity']
            yield item_data

    def __len__(self):
        return sum(item_data['quantity'] for item_data in self.cart.values())

    def get_total_price(self):
        # Base cost of jewelry products
        base_total = sum(Decimal(item_data['price']) * item_data['quantity'] for item_data in self.cart.values())
        
        booking = self.session.get('active_booking')
        if booking:
            base_total += Decimal(booking['deposit'])
            
        return base_total

    def clear(self):
        del self.session['cart']
        if 'active_booking' in self.session:
            del self.session['active_booking']
        self.save()

    def save(self):
        self.session.modified = True