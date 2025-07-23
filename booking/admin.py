from django.contrib import admin
from .models import Location, Booking

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'price', 'capacity', 'is_active', 'image_preview')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" style="border-radius: 4px;" />'
        return "Немає зображення"
    image_preview.allow_tags = True
    image_preview.short_description = "Зображення"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'start_date', 'end_date', 'is_confirmed')
    list_filter = ('is_confirmed', 'start_date', 'location')
    search_fields = ('user__username', 'location__title')
