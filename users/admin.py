from django.contrib import admin
from .models import UserProfile, SavedHotel, PaymentMethod, NotificationPreference


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'total_bookings', 'loyalty_points', 'is_email_verified']
    list_filter = ['is_email_verified', 'is_phone_verified', 'country']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SavedHotel)
class SavedHotelAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'created_at']
    list_filter = ['hotel', 'created_at']
    search_fields = ['user__username', 'hotel__name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'card_holder_name', 'is_default', 'is_active']
    list_filter = ['payment_type', 'is_default', 'is_active']
    search_fields = ['user__username', 'card_holder_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_booking_confirmation', 'in_app_notifications']
    list_filter = ['email_booking_confirmation', 'email_promotional', 'in_app_notifications']
    search_fields = ['user__username', 'user__email']
