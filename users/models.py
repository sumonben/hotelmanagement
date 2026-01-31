from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from PIL import Image
import os

class UserProfile(models.Model):
    """Extended user profile"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    loyalty_points = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.profile_picture.path)


class SavedHotel(models.Model):
    """Saved/Wishlist hotels by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_hotels')
    hotel = models.ForeignKey('hotel.Hotel', on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'hotel']
        verbose_name_plural = "Saved Hotels"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"


class PaymentMethod(models.Model):
    """Saved payment methods for users"""
    PAYMENT_TYPE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal Account'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    card_number_last_4 = models.CharField(max_length=4, blank=True)
    card_holder_name = models.CharField(max_length=100, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    paypal_email = models.EmailField(blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Payment Methods"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.payment_type == 'paypal':
            return f"{self.user.username} - PayPal ({self.paypal_email})"
        return f"{self.user.username} - {self.payment_type.upper()} ****{self.card_number_last_4}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    
    email_booking_confirmation = models.BooleanField(default=True)
    email_booking_reminder = models.BooleanField(default=True)
    email_promotional = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    
    sms_booking_confirmation = models.BooleanField(default=False)
    sms_booking_reminder = models.BooleanField(default=False)
    
    in_app_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
