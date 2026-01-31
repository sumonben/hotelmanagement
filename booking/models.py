from django.db import models
from django.contrib.auth.models import User
from hotel.models import Room, Hotel
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Booking(models.Model):
    """Room booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField(default=1)
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    
    room_price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_nights = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    special_requests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_id']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Generate booking ID if not exists
        if not self.booking_id:
            import uuid
            self.booking_id = f"BK{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate number of nights and prices if not set
        if self.check_in_date and self.check_out_date:
            self.number_of_nights = (self.check_out_date - self.check_in_date).days
            if self.room_price_per_night and not self.subtotal:
                self.subtotal = Decimal(str(self.room_price_per_night)) * self.number_of_nights
        
        # Calculate total price if components are set
        if self.subtotal:
            self.total_price = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    def get_days_until_checkin(self):
        return (self.check_in_date - timezone.now().date()).days
    
    def can_cancel(self):
        return self.status in ['pending', 'confirmed']
    
    def confirm_booking(self):
        self.status = 'confirmed'
        self.payment_status = 'completed'
        self.confirmed_at = timezone.now()
        self.save()
    
    def check_in(self):
        self.status = 'checked_in'
        self.checked_in_at = timezone.now()
        self.save()
    
    def check_out(self):
        self.status = 'checked_out'
        self.checked_out_at = timezone.now()
        self.save()


class Payment(models.Model):
    """Payment records for bookings"""
    PAYMENT_METHOD_CHOICES = [
        ('sslcommerz', 'SSL Commerz (Bkash, Nagad, Card, Bank)'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for {self.booking.booking_id} - {self.amount}"


class CancellationPolicy(models.Model):
    """Cancellation policies for bookings"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='cancellation_policies')
    name = models.CharField(max_length=100)
    days_before_checkin = models.IntegerField(help_text="Days before check-in")
    refund_percentage = models.IntegerField(help_text="Percentage of refund (0-100)")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Cancellation Policies"
        ordering = ['-days_before_checkin']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class Amenity(models.Model):
    """Additional amenities for rooms"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BookingAmenity(models.Model):
    """Track amenities added to bookings"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['booking', 'amenity']
    
    def __str__(self):
        return f"{self.booking.booking_id} - {self.amenity.name}"
