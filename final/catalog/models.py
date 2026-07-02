from django.db import models
from django.contrib.auth.models import User  # Django's built-in user system

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"  # Fixes Django's automatic "Categorys" typo in admin

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # NEW FILTERABLE ATTRIBUTES
    material = models.CharField(max_length=50, default="Titanium")  # e.g., Titanium, Surgical Steel, Gold
    color = models.CharField(max_length=50, default="Silver")       # e.g., Silver, Gold, Black, Rose Gold
    size = models.CharField(max_length=50, default="1.2mm (16g)")    # e.g., 1.2mm, 8mm, 10mm

    def __str__(self):
        return self.title


class Review(models.Model):
    # Connects the review to a single Item
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    
    # Connects the review to a single User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 Stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.title} ({self.rating}★)"