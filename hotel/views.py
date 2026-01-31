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


class HomeView(TemplateView):
    """Home page for single hotel"""
    template_name = 'hotel/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = get_default_hotel()
        
        context['hotel'] = hotel
        context['room_types'] = hotel.room_types.all()
        context['facilities'] = hotel.facilities.filter(is_available=True)
        context['reviews'] = hotel.reviews.all()[:10]
        context['average_rating'] = hotel.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['search_form'] = HotelSearchForm()
        
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



class HotelDetailView(TemplateView):
    """Detailed hotel view for single hotel"""
    template_name = 'hotel/hotel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = get_default_hotel()
        
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


class RoomDetailView(DetailView):
    """Detailed room view"""
    model = Room
    template_name = 'hotel/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        
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

