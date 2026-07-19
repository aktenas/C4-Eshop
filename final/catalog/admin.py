from django.contrib import admin
from .models import Category, Item, Review

# editable database elements by the admin
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Review)