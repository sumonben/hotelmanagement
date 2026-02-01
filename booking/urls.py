from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    # Booking management
    path('create/<int:room_id>/', views.BookingCreateView.as_view(), name='create_booking'),
    path('<int:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('my-bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('search/', views.booking_search, name='booking_search'),
    
    # Payment
    path('<int:booking_id>/payment/', views.PaymentView.as_view(), name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    
    # Check-in/out
    path('<int:booking_id>/checkin/', views.booking_checkin, name='checkin'),
    path('<int:booking_id>/checkout/', views.booking_checkout, name='checkout'),
    
    # Cancellation
    path('<int:booking_id>/cancel/', views.booking_cancel, name='cancel'),
]
