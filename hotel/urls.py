from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    # Home and single hotel
    path('', views.HomeView.as_view(), name='home'),
    path('hotel/', views.HotelDetailView.as_view(), name='hotel_detail'),
    path('hotel/save/', views.save_hotel, name='save_hotel'),
    
    # Rooms
    path('room/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    
    # Reviews
    path('hotel/review/', views.HotelReviewCreateView.as_view(), name='review_create'),
    
    # Wishlist
    path('saved-hotels/', views.saved_hotels, name='saved_hotels'),
    
    # Search
    path('search-availability/', views.search_availability, name='search_availability'),
]
