from django.contrib import admin
from .models import Booking, Service, Review


# Register your models here.
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(Review)