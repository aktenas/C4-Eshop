from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    material = models.CharField(max_length=50, default="Titanium")
    color = models.CharField(max_length=50, default="Silver") 
    size = models.CharField(max_length=50, default="1.2mm (16g)")
    
    def __str__(self):
        return self.title


class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.title} ({self.rating}★)"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # if a catalog item is deleted, the purchase history stays alive
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Snapshot fields to lock in the values exactly as they were during checkout
    item_title = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_material = models.CharField(max_length=50)
    item_color = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.item_title} inside Order #{self.order.id}"