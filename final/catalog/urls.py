from django.urls import path
from . import views

urlpatterns = [
    # Matches: /catalog/
    path('', views.catalog, name='catalog'), 
    
    # Matches: /catalog/category/1/, /catalog/category/2/, etc.
    path('category/<int:category_id>/', views.category, name='category'),
    # Cart Operations
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    
    # Scheduling Operations
    path('book/', views.book_appointment, name='book_appointment'),
]