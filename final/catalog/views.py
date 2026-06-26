from django.shortcuts import render
from .models import Item
from django.http import HttpResponse

def catalog(request):
    # Grab items currently in database table
    all_items = Item.objects.all()
    
    # Pass db items into HTML 
    context = {
        'items': all_items
    }
    return render(request, 'catalog/catalog.html', context)