from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='catalog'), 
    path('category/<int:category_id>/', views.category, name='category'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('item/<str:slug>/', views.item_detail, name='item_detail'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # ADMIN ITEM EDIT

    path('manage/piercings/', views.admin_piercing_dashboard, name='admin_piercing_dashboard'),
    path('manage/piercings/edit/<int:item_id>/', views.admin_edit_piercing, name='admin_edit_piercing'),
]