from django.contrib import admin
from .models import UserProfile, PriceAlert, NotificationLog, Airport
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at', 'updated_at')
    search_fields = ('user__username', 'role')
    list_filter = ('role',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'origin', 'destination', 'threshold_price', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'origin', 'destination')
    list_filter = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('alert', 'triggered_price', 'message', 'notified_at')
    search_fields = ('alert__user__username', 'alert__origin', 'alert__destination', 'message')
    list_filter = ('alert__status',)
    date_hierarchy = 'notified_at'
    ordering = ('-notified_at',)

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country', 'timezone', 'created_at', 'updated_at')
    search_fields = ('code', 'name', 'city', 'country')
    list_filter = ('country',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


