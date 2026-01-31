from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from datetime import timedelta
from django.core.paginator import Paginator

from .models import Hotel, Room, RoomType, HotelReview, HotelFacility, RoomImage
from .forms import HotelSearchForm, HotelReviewForm, HotelFilterForm, RoomFilterForm
from booking.models import Booking
from users.models import SavedHotel


def get_default_hotel():
    """Get the default hotel for this single-hotel setup"""
    return get_object_or_404(Hotel, id=settings.DEFAULT_HOTEL_ID)


class SEOContextMixin:
    """Mixin to add SEO meta tags to context"""
    
    def get_seo_context(self, title, description, keywords="", image_url=""):
        """Generate SEO context data"""
        return {
            'page_title': title,
            'meta_description': description,
            'meta_keywords': keywords,
            'meta_image': image_url,
            'canonical_url': self.request.build_absolute_uri(),
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'seo_data'):
            context.update(self.seo_data)
        return context


class HomeView(SEOContextMixin, TemplateView):
    """Home page for single hotel"""
    template_name = 'hotel/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = get_default_hotel()
        
        # Set SEO data
        self.seo_data = self.get_seo_context(
            title=f"{hotel.name} | Luxury Hotel Booking",
            description=hotel.meta_description or f"Book rooms at {hotel.name} in {hotel.city}. Best rates and amenities.",
            keywords=hotel.meta_keywords or f"{hotel.name}, hotel, booking, {hotel.city}",
            image_url=hotel.banner.url if hotel.banner else ""
        )
        context.update(self.seo_data)
        
        context['hotel'] = hotel
        context['room_types'] = hotel.room_types.all()
        context['facilities'] = hotel.facilities.filter(is_available=True)
        context['reviews'] = hotel.reviews.all()[:10]
        context['average_rating'] = hotel.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['search_form'] = HotelSearchForm()
        
        # Check if user has saved this hotel
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedHotel.objects.filter(
                user=self.request.user,
                hotel=hotel
            ).exists()
        else:
            context['is_saved'] = False
        
        # Available rooms
        rooms = hotel.rooms.filter(status='available', is_active=True)
        context['rooms'] = rooms[:6]
        
        # Carousel
        try:
            carousel = hotel.carousel
            if carousel.is_active:
                context['carousel'] = carousel
                context['carousel_slides'] = carousel.get_active_slides()
        except:
            pass
        
        return context


class HotelListView(TemplateView):
    """Redirect to home for single hotel setup"""
    template_name = 'hotel/home.html'
    
    def get(self, request, *args, **kwargs):
        # Redirect to home since we only have one hotel
        return redirect('hotel:home')



class HotelDetailView(SEOContextMixin, TemplateView):
    """Detailed hotel view for single hotel"""
    template_name = 'hotel/hotel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = get_default_hotel()
        
        # Set SEO data
        self.seo_data = self.get_seo_context(
            title=f"{hotel.name} - {hotel.city} | Hotel Rooms & Rates",
            description=hotel.meta_description or f"Explore rooms at {hotel.name}. {hotel.address}, {hotel.city}. Book now!",
            keywords=hotel.meta_keywords or f"{hotel.name}, {hotel.city}, hotel rooms, accommodation",
            image_url=hotel.image.url if hotel.image else ""
        )
        context.update(self.seo_data)
        
        context['hotel'] = hotel
        context['room_types'] = hotel.room_types.all()
        context['facilities'] = hotel.facilities.filter(is_available=True)
        context['reviews'] = hotel.reviews.all()[:10]
        context['average_rating'] = hotel.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Check if user has saved this hotel
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedHotel.objects.filter(
                user=self.request.user,
                hotel=hotel
            ).exists()
        
        # Room filter
        room_type_id = self.request.GET.get('room_type')
        rooms = hotel.rooms.filter(status='available', is_active=True)
        
        if room_type_id:
            rooms = rooms.filter(room_type_id=room_type_id)
        
        context['rooms'] = rooms
        
        return context


class RoomDetailView(SEOContextMixin, DetailView):
    """Detailed room view"""
    model = Room
    template_name = 'hotel/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        
        # Set SEO data
        self.seo_data = self.get_seo_context(
            title=f"Room {room.room_number} - {room.hotel.name} | Book Now",
            description=f"{room.room_type.name} with {room.room_type.max_guests} guests. ${room.get_price()}/night at {room.hotel.name}",
            keywords=f"{room.room_type.name}, {room.hotel.name}, hotel room, booking",
            image_url=room.room_type.image.url if room.room_type.image else ""
        )
        context.update(self.seo_data)
        
        context['images'] = room.images.all()
        context['hotel'] = room.hotel
        context['room_type'] = room.room_type
        
        # Check availability for date range
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        
        if check_in and check_out:
            context['available'] = room.is_available(check_in, check_out)
        
        return context

class HotelReviewCreateView(LoginRequiredMixin, CreateView):
    """Create hotel review"""
    model = HotelReview
    form_class = HotelReviewForm
    template_name = 'hotel/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_default_hotel()
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        review = form.save(commit=False)
        review.hotel = self.hotel
        review.user = self.request.user
        
        # Check if user already reviewed
        if HotelReview.objects.filter(hotel=self.hotel, user=self.request.user).exists():
            messages.error(self.request, 'You have already reviewed this hotel.')
            return redirect('hotel:hotel_detail')
        
        review.save()
        
        # Update hotel rating
        avg_rating = self.hotel.reviews.aggregate(Avg('rating'))['rating__avg']
        self.hotel.rating = avg_rating * self.hotel.reviews.count()
        self.hotel.total_reviews = self.hotel.reviews.count()
        self.hotel.save()
        
        messages.success(self.request, 'Review submitted successfully!')
        return redirect('hotel:hotel_detail')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hotel'] = self.hotel
        return context


def save_hotel(request):
    """Toggle save hotel to wishlist"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to save hotels.')
        return redirect('users:login')
    
    hotel = get_default_hotel()
    
    saved_hotel, created = SavedHotel.objects.get_or_create(
        user=request.user,
        hotel=hotel
    )
    
    if not created:
        saved_hotel.delete()
        messages.success(request, f'{hotel.name} removed from saved hotels.')
    else:
        messages.success(request, f'{hotel.name} saved to your wishlist!')
    
    return redirect('hotel:hotel_detail')


def saved_hotels(request):
    """View saved hotels"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view saved hotels.')
        return redirect('users:login')
    
    # Since we only have one hotel, show if it's saved by the user
    hotel = get_default_hotel()
    saved = SavedHotel.objects.filter(user=request.user, hotel=hotel).exists()
    
    return render(request, 'hotel/saved_hotels.html', {
        'hotel': hotel,
        'is_saved': saved
    })


def search_availability(request):
    """Search room availability for the single hotel"""
    form = HotelSearchForm()
    hotel = get_default_hotel()
    
    if request.method == 'POST':
        form = HotelSearchForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data.get('check_in_date')
            check_out = form.cleaned_data.get('check_out_date')
            guests = form.cleaned_data.get('guests', 1)
            
            # Get available rooms for the date range
            # Filter rooms that don't have conflicting bookings
            from booking.models import Booking
            
            booked_rooms = Booking.objects.filter(
                hotel=hotel,
                status__in=['confirmed', 'checked_in']
            ).filter(
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).values_list('room_id', flat=True)
            
            available_rooms = hotel.rooms.filter(
                status='available',
                is_active=True,
                room_type__max_guests__gte=guests
            ).exclude(id__in=booked_rooms)
            
            return render(request, 'hotel/search_results.html', {
                'hotel': hotel,
                'rooms': available_rooms,
                'check_in': check_in,
                'check_out': check_out,
                'guests': guests,
            })
    
    return render(request, 'hotel/search_form.html', {'form': form})

