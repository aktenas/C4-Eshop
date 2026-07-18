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

@never_cache
def catalog(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')
    
    selected_category = None
    items = None
    
    # 1. Grab the search input from the URL query params (?search=septum)
    search_query = request.GET.get('search', '')
    
    if selected_category_id:
        selected_category = get_object_or_404(Category, id=selected_category_id)
        
        # Start with all items in the chosen category
        items = Item.objects.filter(category=selected_category)
        
        # 2. If the user typed something in the search bar, filter the queryset
        if search_query:
            items = items.filter(title__icontains=search_query)
            
        # Default sorting by creation date
        items = items.order_by('-created_at')
        
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'items': items,
        'search_query': search_query, # Send it back so the search box stays filled
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
    
    # 1. Capture the form quantity integer safely (defaults to 1 if missing)
    try:
        qty_modifier = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        qty_modifier = 1

    # 2. Pass the dynamic modifier (1 or -1)
    cart.add(item=item, quantity=qty_modifier)
    
    # 3. Clean up the cart row session if the quantity drops to 0 or less
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

# Verifies user is an authorized staff member
def is_studio_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_studio_admin, login_url='login')
def admin_piercing_dashboard(request):
    """Fetch all database items for management"""
    # Grab everything so it populates the dashboard instantly
    piercing_items = Item.objects.all().order_by('category', 'title')
    #cache
    return render(request, 'catalog/admin_piercings.html', {'items': piercing_items})


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
        
        if not card_name or not card_number or not card_expiry or not card_cvv:
            messages.error(request, "GATEWAY WARNING: Invalid payment parameters provided.")
            return redirect('catalog:checkout')
        
        # Wrapping database actions inside an atomic block to ensure complete rollbacks in case of errors
        with transaction.atomic():
            # 1. Create the master Order record row
            order = Order.objects.create(
                user=request.user,
                grand_total=cart.get_total_price()
            )
            
            # 2. Loop through session items, record snapshots, and deduct physical stock limits
            for item_data in cart:
                catalog_item = item_data['item']
                
                # Check stock availability
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
                
                # REDUCE STOCK VALUE
                catalog_item.stock -= item_data['quantity']
                catalog_item.save()
            
            # 3. Securely empty out the session cookies
            cart.clear()
            
        messages.success(request, "ORDER SUCCESSFUL! Your studio items have been secured.")
        return redirect('accounts:dashboard')

    return render(request, 'catalog/checkout.html', {'cart': cart})

@login_required
@require_POST
def cancel_order(request, order_id):
    """
    Cancels an order, deletes it from the records, and refunds the items back to active stock.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    with transaction.atomic():
        for order_item in order.items.all():
            if order_item.item:
                order_item.item.stock += order_item.quantity
                order_item.item.save()
        
        # Delete the order record
        order.delete()
        
        messages.success(request, "ORDER ANNULLED: Order deleted and items returned to stock.")
        
    return redirect('accounts:dashboard')

@never_cache
def item_detail(request, slug):
    """
    Renders a single catalog piercing item based on its title-slug.
    """
    all_items = Item.objects.all()
    item = None
    
    from django.utils.text import slugify
    for i in all_items:
        if slugify(i.title) == slug:
            item = i
            break
            
    if item is None:
        from django.http import Http404
        raise Http404("Item specification does not exist.")
        
    return render(request, 'catalog/item_detail.html', {'item': item})