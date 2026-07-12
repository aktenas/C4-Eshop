from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Item, Category, Review
from .cart import Cart
from home.models import Booking

def catalog(request):
    categories = Category.objects.all()
    return render(request, 'catalog/catalog.html', {'categories': categories})

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
    cart.add(item=item, quantity=1)
    return redirect('cart_detail')

def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'catalog/cart_detail.html', {'cart': cart})

@login_required
@require_POST
def add_review_ajax(request):
    try:
        item_id = request.POST.get('item_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not all([item_id, rating, comment]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Selected catalog item does not exist.'}, status=404)

        rating_val = int(rating)
        if not (1 <= rating_val <= 5):
            return JsonResponse({'success': False, 'error': 'Invalid rating numerical range value.'}, status=400)

        review = Review.objects.create(
            item=item,
            user=request.user,
            rating=rating_val,
            comment=comment
        )

        return JsonResponse({
            'success': True,
            'username': request.user.username,
            'item_title': item.title,
            'rating': review.rating,
            'comment': review.comment,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
