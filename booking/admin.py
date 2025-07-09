from django.contrib import admin
from .models import Location, Booking

# Register your models here.

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display =( 'title', 'price', 'is_active')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'is_confirmed')
