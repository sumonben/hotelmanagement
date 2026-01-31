from django.contrib import admin
from .models import Booking, Payment, CancellationPolicy, Amenity, BookingAmenity


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'hotel', 'room', 'status', 'payment_status', 'check_in_date', 'total_price']
    list_filter = ['status', 'payment_status', 'check_in_date', 'hotel']
    search_fields = ['booking_id', 'user__username', 'hotel__name', 'guest_name']
    readonly_fields = ['booking_id', 'created_at', 'updated_at', 'confirmed_at', 'checked_in_at', 'checked_out_at', 'cancelled_at']
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_id', 'user', 'hotel', 'room', 'status')
        }),
        ('Guest Info', {
            'fields': ('guest_name', 'guest_email', 'guest_phone', 'number_of_guests')
        }),
        ('Dates', {
            'fields': ('check_in_date', 'check_out_date', 'number_of_nights')
        }),
        ('Pricing', {
            'fields': ('room_price_per_night', 'subtotal', 'tax_amount', 'discount_amount', 'total_price')
        }),
        ('Payment', {
            'fields': ('payment_status',)
        }),
        ('Additional Info', {
            'fields': ('special_requests', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at', 'checked_in_at', 'checked_out_at', 'cancelled_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'booking', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'booking__booking_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']


@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'days_before_checkin', 'refund_percentage', 'is_active']
    list_filter = ['hotel', 'is_active']
    search_fields = ['name', 'hotel__name']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(BookingAmenity)
class BookingAmenityAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amenity', 'price']
    list_filter = ['amenity']
    search_fields = ['booking__booking_id', 'amenity__name']
