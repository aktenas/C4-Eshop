from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'), 
    path('category/<int:category_id>/', views.category, name='category'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('book/', views.book_appointment, name='book_appointment'),
]