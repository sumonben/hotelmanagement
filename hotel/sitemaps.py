from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Hotel, Room, HotelReview


class HotelSitemap(Sitemap):
    """Sitemap for hotels"""
    changefreq = 'weekly'
    priority = 1.0
    
    def items(self):
        return Hotel.objects.filter(status='active')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('hotel:hotel_detail')


class RoomSitemap(Sitemap):
    """Sitemap for rooms"""
    changefreq = 'daily'
    priority = 0.8
    
    def items(self):
        return Room.objects.filter(hotel__status='active', is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return reverse('hotel:room_detail', kwargs={'pk': obj.id})


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 0.9
    
    def items(self):
        return ['hotel:home', 'hotel:hotel_detail']
    
    def location(self, item):
        return reverse(item)


sitemaps = {
    'hotels': HotelSitemap,
    'rooms': RoomSitemap,
    'static': StaticViewSitemap,
}
