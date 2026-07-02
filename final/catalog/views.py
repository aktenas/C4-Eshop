from .models import Item
from django.http import HttpResponse
from .models import Item, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .cart import Cart

# This handles the main landing page at /catalog/
def catalog(request):
    categories = Category.objects.all()
    return render(request, 'catalog/catalog.html', {'categories': categories})


# This handles the specific department view at /catalog/category/<id>/
def category(request, category_id):
    # Grab the selected category, or show a 404 page if it doesn't exist
    category = get_object_or_404(Category, id=category_id)
    
    # Filter items so we ONLY grab pieces belonging to this specific collection
    items = Item.objects.filter(category=category)

    # Grab filter inputs from the URL query parameters
    search_query = request.GET.get('search', '')
    material_filter = request.GET.get('material', '')
    color_filter = request.GET.get('color', '')
    sort_by = request.GET.get('sort', '')

    # Apply Filters dynamically if the user selects them
    if search_query:
        items = items.filter(title__icontains=search_query)
    if material_filter:
        items = items.filter(material=material_filter)
    if color_filter:
        items = items.filter(color=color_filter)
        
    # Apply Price Sorting
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
    cart.add(item=item, quantity=1)
    return redirect('cart_detail')

def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    booking = request.session.get('active_booking')
    return render(request, 'catalog/cart_detail.html', {'cart': cart, 'booking': booking})

def book_appointment(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        notes = request.POST.get('notes', '')
        
        request.session['active_booking'] = {
            'service': service_type,
            'notes': notes,
            'deposit': '50.00'
        }
        return redirect('cart_detail')
    return render(request, 'catalog/book_service.html')