from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('tattoo', 'Tattoo'),
        ('piercing', 'Piercing'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    notes = models.TextField(blank=True)
    deposit = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_service_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"