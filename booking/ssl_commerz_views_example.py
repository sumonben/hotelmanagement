"""
Example views for SSL Commerz payment integration
Add these views to your booking/views.py or create a new file

This is a guide showing how to integrate SSL Commerz into your payment flow.
"""

# Example implementation for booking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from .models import Booking, Payment
from .ssl_commerz import initiate_sslcommerz_payment, validate_sslcommerz_response


class SSLCommerczInitiateView(LoginRequiredMixin, View):
    """
    Initiate SSL Commerz payment
    """
    
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Initiate payment
        response = initiate_sslcommerz_payment(booking, request)
        
        if response.get('status') == 'success':
            # Store the GatewayPageURL for redirect
            gateway_page_url = response.get('GatewayPageURL')
            
            # Create pending payment record
            Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                payment_method='sslcommerz',
                transaction_id=response.get('sessionkey', ''),
                status='pending'
            )
            
            # Redirect to SSL Commerz payment page
            return redirect(gateway_page_url)
        else:
            messages.error(request, 'Failed to initiate payment. Please try again.')
            return redirect('booking:payment', booking.id)


class SSLCommerczSuccessView(LoginRequiredMixin, View):
    """
    Handle successful SSL Commerz payment
    """
    
    def post(self, request):
        # Get validation ID from SSL Commerz response
        validation_id = request.POST.get('val_id')
        order_id = request.POST.get('order_num')
        
        if not validation_id or not order_id:
            messages.error(request, 'Invalid payment response.')
            return redirect('hotel:home')
        
        # Validate payment with SSL Commerz
        validation_response = validate_sslcommerz_response(request.POST)
        
        if validation_response['status']:
            # Get booking
            try:
                booking = Booking.objects.get(booking_id=order_id)
            except Booking.DoesNotExist:
                messages.error(request, 'Booking not found.')
                return redirect('hotel:home')
            
            # Update payment status
            payment = Payment.objects.filter(
                booking=booking,
                status='pending'
            ).first()
            
            if payment:
                payment.status = 'completed'
                payment.transaction_id = validation_id
                payment.save()
            
            # Update booking status
            booking.payment_status = 'completed'
            booking.status = 'confirmed'
            booking.save()
            
            messages.success(request, 'Payment successful! Your booking is confirmed.')
            return redirect('booking:detail', booking.id)
        else:
            messages.error(request, 'Payment validation failed.')
            return redirect('hotel:home')


class SSLCommerczFailedView(LoginRequiredMixin, View):
    """
    Handle failed SSL Commerz payment
    """
    
    def post(self, request):
        order_id = request.POST.get('order_num')
        
        try:
            booking = Booking.objects.get(booking_id=order_id)
            
            # Update payment status
            payment = Payment.objects.filter(
                booking=booking,
                status='pending'
            ).first()
            
            if payment:
                payment.status = 'failed'
                payment.save()
            
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('booking:payment', booking.id)
        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found.')
            return redirect('hotel:home')


class SSLCommerczCancelledView(LoginRequiredMixin, View):
    """
    Handle cancelled SSL Commerz payment
    """
    
    def post(self, request):
        order_id = request.POST.get('order_num')
        
        try:
            booking = Booking.objects.get(booking_id=order_id)
            messages.warning(request, 'Payment was cancelled.')
            return redirect('booking:payment', booking.id)
        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found.')
            return redirect('hotel:home')


# Add to your booking/urls.py:
# 
# from . import views
# 
# urlpatterns = [
#     ...
#     # SSL Commerz Payment URLs
#     path('payment/<int:booking_id>/initiate/', 
#          views.SSLCommerczInitiateView.as_view(), 
#          name='payment_initiate'),
#     path('payment/success/', 
#          views.SSLCommerczSuccessView.as_view(), 
#          name='payment_success'),
#     path('payment/failed/', 
#          views.SSLCommerczFailedView.as_view(), 
#          name='payment_failed'),
#     path('payment/cancelled/', 
#          views.SSLCommerczCancelledView.as_view(), 
#          name='payment_cancelled'),
#     ...
# ]
