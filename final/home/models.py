from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('Tattoo Sessions', 'Tattoo Sessions'),
        ('Facial Piercing', 'Facial Piercing'),
        ('Nose Piercing', 'Nose Piercing'),
        ('Ears Piercing', 'Ears Piercing'),
        ('LIP/MOUTH PIERCING', 'LIP/MOUTH PIERCING'),
        ('Checkup', 'Checkup'),
    ]

    title = models.CharField(max_length=100) # This acts as your service type
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, default="Professional sterile procedure.")
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.title} - €{self.price}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # RELATIONAL LINK: Inherits price and service type directly from the Service table row
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments', null=True, blank=True)
    
    # CAPTURED FROM WIZARD FLOW: Gathered dynamically during the user booking process
    artist = models.CharField(max_length=100, default="Any Artist")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.title} (€{self.service.price})"
    
class Review(models.Model):
    # Added unique related_name to resolve the User property clash!
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews')
    
    # Linked to our new Service model relation column row cleanly
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews') 
    
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.title} ({self.rating}★)"