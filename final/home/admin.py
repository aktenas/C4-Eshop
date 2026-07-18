from django.contrib import admin
from .models import Booking, Service


# Register your models here.
admin.site.register(Service)
admin.site.register(Booking)