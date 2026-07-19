from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.db import transaction
from catalog.models import Item, Category, Review
from .cart import Cart
from .models import Order, OrderItem
from django.contrib import messages

# a fresh page is booted each time so the catalog is up to date
@never_cache
def catalog(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')
    
    selected_category = None
    items = None
    
    search_query = request.GET.get('search', '')
    
    if selected_category_id:
        selected_category = get_object_or_404(Category, id=selected_category_id)
        items = Item.objects.filter(category=selected_category)
        
        if search_query:
            items = items.filter(title__icontains=search_query)
            
        items = items.order_by('-created_at')
        
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'items': items,
        'search_query': search_query,
    }
    return render(request, 'catalog/catalog.html', context)

def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = Item.objects.filter(category=category)

    search_query = request.GET.get('search', '')
    material_filter = request.GET.get('material', '')
    color_filter = request.GET.get('color', '')
    sort_by = request.GET.get('sort', '')

    if search_query:
        items = items.filter(title__icontains=search_query)
    if material_filter:
        items = items.filter(material=material_filter)
    if color_filter:
        items = items.filter(color=color_filter)
        
    if sort_by == 'price_low':
        items = items.order_by('price')
    elif sort_by == 'price_high':
        items = items.order_by('-price')

    context = {
        'category': category,
        'items': items,
        'search_query': search_query,
        'selected_material': material_filter,
        'selected_color': color_filter,
        'selected_sort': sort_by,
    }
    return render(request, 'catalog/category.html', context)

@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    
    try:
        qty_modifier = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        qty_modifier = 1

    # Find out how many items are inside the session cart
    current_qty_in_cart = 0
    for cart_item in cart:
        if cart_item['item'].id == item.id:
            current_qty_in_cart = cart_item['quantity']
            break

    # calculate what the total would be
    projected_total = current_qty_in_cart + qty_modifier

    # block addition if it exceeds inventory limits
    if projected_total > item.stock:
        messages.error(request, f"CANNOT ADD MORE: Only {item.stock} units of '{item.title}' are available in stock.")
        return redirect('catalog:cart_detail')

    cart.add(item=item, quantity=qty_modifier)
    
    for cart_item in cart:
        if cart_item['item'].id == item.id and cart_item['quantity'] <= 0:
            cart.remove(item)
            
    return redirect('catalog:cart_detail')

def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('catalog:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'catalog/cart_detail.html', {'cart': cart})

def is_studio_admin(user):
    return user.is_authenticated and user.is_staff
# only admins can access the item edit board
@user_passes_test(is_studio_admin, login_url='login')
def admin_piercing_dashboard(request):
    piercing_items = Item.objects.all().order_by('category', 'title')
    return render(request, 'catalog/admin_piercings.html', {'items': piercing_items})
# admin can edit the piercing attrs
@user_passes_test(is_studio_admin, login_url='login')
def admin_edit_piercing(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item.title = request.POST.get('title')
        item.price = request.POST.get('price')
        item.material = request.POST.get('material')
        item.color = request.POST.get('color')
        item.save()
        return redirect('catalog:admin_piercing_dashboard')

    return render(request, 'catalog/admin_edit_piercing.html', {'item': item})

@login_required
def checkout(request):
    cart = Cart(request) 
    
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('catalog:catalog')
        
    if request.method == 'POST':
        card_name = request.POST.get('payment_name')
        card_number = request.POST.get('payment_card')
        card_expiry = request.POST.get('payment_expiry')
        card_cvv = request.POST.get('payment_cvv')
        # card validation
        if not card_name or not card_number or not card_expiry or not card_cvv:
            messages.error(request, "GATEWAY WARNING: Invalid payment parameters provided.")
            return redirect('catalog:checkout')
        
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                grand_total=cart.get_total_price()
            )
            
            for item_data in cart:
                catalog_item = item_data['item']
                
                if catalog_item.stock < item_data['quantity']:
                    messages.error(request, f"INSUFFICIENT STOCK: '{catalog_item.title}' is sold out.")
                    return redirect('catalog:cart_detail')
                
                OrderItem.objects.create(
                    order=order,
                    item=catalog_item,
                    item_title=catalog_item.title,
                    item_price=item_data['price'],
                    item_material=catalog_item.material,
                    item_color=catalog_item.color,
                    quantity=item_data['quantity']
                )
                # reduce stock after payment
                catalog_item.stock -= item_data['quantity']
                catalog_item.save()
            
            cart.clear()
            
        messages.success(request, "ORDER SUCCESSFUL! Your items have been secured.")
        return redirect('accounts:dashboard')

    return render(request, 'catalog/checkout.html', {'cart': cart})

@login_required
@require_POST
def cancel_order(request, order_id):
    # the user id is crucial , attackers cannot delete someone elses order by its ID
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    with transaction.atomic():
        for order_item in order.items.all():
            if order_item.item:
                # increase the item quantity after order deletion
                order_item.item.stock += order_item.quantity
                order_item.item.save()
        
        order.delete()
        messages.success(request, "ORDER ANNULLED: Order deleted and items returned to stock.")
        
    return redirect('accounts:dashboard')

@never_cache
def item_detail(request, slug):
    # every databse item is requested
    all_items = Item.objects.all()
    item = None
    # loop through the items to find the one the user clicked on
    from django.utils.text import slugify
    for i in all_items:
        # slugify converts items titles to search friendly text, example: Industrial Cat Holo -> industrial-cat-holo
        if slugify(i.title) == slug:
            item = i
            break
            
    if item is None:
        from django.http import Http404
        raise Http404("Item specification does not exist.")
        
    return render(request, 'catalog/item_detail.html', {'item': item})