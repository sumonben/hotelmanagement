from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Hotel(models.Model):
    """Main hotel model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='hotels/')
    banner = models.ImageField(upload_to='hotels/banners/')
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.IntegerField(default=0)
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    
    # SEO Fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description (max 160 chars)")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated keywords")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        if self.total_reviews > 0:
            return round(self.rating / self.total_reviews, 1)
        return 0


class RoomType(models.Model):
    """Room types available at hotels"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)  # Single, Double, Suite, etc.
    slug = models.SlugField(blank=True, help_text="Auto-generated from name")
    description = models.TextField()
    max_guests = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    beds = models.CharField(max_length=100)  # Single bed, Double bed, etc.
    amenities = models.TextField(help_text="Comma-separated list of amenities")
    image = models.ImageField(upload_to='room_types/')
    image_alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for SEO")
    
    class Meta:
        unique_together = ['hotel', 'name']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class Room(models.Model):
    """Individual rooms in the hotel"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('unavailable', 'Unavailable'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price after discount"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['hotel', 'status']),
        ]
    
    def __str__(self):
        return f"Room {self.room_number} - {self.hotel.name}"
    
    def get_price(self):
        """Get current price (discount or regular)"""
        return self.discount_price if self.discount_price else self.price_per_night
    
    def is_available(self, check_in, check_out):
        """Check if room is available for given dates"""
        from booking.models import Booking
        bookings = Booking.objects.filter(
            room=self,
            status__in=['confirmed', 'checked_in']
        ).exclude(check_out_date__lte=check_in).exclude(check_in_date__gte=check_out)
        return not bookings.exists()


class HotelFacility(models.Model):
    """Facilities available at the hotel"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=100)  # WiFi, Parking, Pool, etc.
    icon = models.CharField(max_length=50, blank=True)  # For font-awesome icons
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['hotel', 'name']
        verbose_name_plural = "Hotel Facilities"
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class HotelReview(models.Model):
    """Reviews for hotels"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    verified_guest = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.user.username} ({self.rating}★)"


class RoomImage(models.Model):
    """Additional images for rooms"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility and SEO")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.room}"

class Carousel(models.Model):
    """Carousel slides for homepage"""
    hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE, related_name='carousel')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Carousels"
    
    def __str__(self):
        return f"Carousel for {self.hotel.name}"
    
    def get_active_slides(self):
        """Get all active carousel slides"""
        return self.slides.filter(is_active=True).order_by('order')


class CarouselSlide(models.Model):
    """Individual carousel slides"""
    carousel = models.ForeignKey(Carousel, on_delete=models.CASCADE, related_name='slides')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='carousel/')
    button_text = models.CharField(max_length=50, blank=True, default='View Rooms')
    button_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Order of appearance in carousel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Carousel Slides"
    
    def __str__(self):
        return f"{self.carousel.hotel.name} - {self.title}"