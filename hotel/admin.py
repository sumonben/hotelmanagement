from django.contrib import admin
from .models import Hotel, Room, RoomType, HotelFacility, HotelReview, RoomImage, Carousel, CarouselSlide


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'status', 'is_featured', 'rating', 'created_at']
    list_filter = ['status', 'is_featured', 'city', 'created_at']
    search_fields = ['name', 'city', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude')
        }),
        ('Images', {
            'fields': ('image', 'banner')
        }),
        ('Timing', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Status & Rating', {
            'fields': ('status', 'is_featured', 'rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'max_guests']
    list_filter = ['hotel', 'max_guests']
    search_fields = ['name', 'hotel__name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'floor', 'status', 'price_per_night']
    list_filter = ['status', 'hotel', 'floor']
    search_fields = ['room_number', 'hotel__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HotelFacility)
class HotelFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'is_available']
    list_filter = ['hotel', 'is_available']
    search_fields = ['name', 'hotel__name']


@admin.register(HotelReview)
class HotelReviewAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'rating', 'verified_guest', 'created_at']
    list_filter = ['rating', 'verified_guest', 'hotel', 'created_at']
    search_fields = ['hotel__name', 'user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'alt_text', 'created_at']
    list_filter = ['room__hotel', 'created_at']
    search_fields = ['room__room_number', 'alt_text']

class CarouselSlideInline(admin.TabularInline):
    """Inline admin for carousel slides"""
    model = CarouselSlide
    extra = 1
    fields = ['title', 'subtitle', 'image', 'button_text', 'button_url', 'order', 'is_active']
    ordering = ['order']


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'is_active', 'slide_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['hotel__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CarouselSlideInline]
    
    def slide_count(self, obj):
        return obj.slides.count()
    slide_count.short_description = "Number of Slides"


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'carousel', 'order', 'is_active', 'created_at']
    list_filter = ['carousel__hotel', 'is_active', 'order', 'created_at']
    search_fields = ['title', 'subtitle', 'carousel__hotel__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['carousel', 'order']
    fieldsets = (
        ('Carousel Information', {
            'fields': ('carousel', 'order')
        }),
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Button', {
            'fields': ('button_text', 'button_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )