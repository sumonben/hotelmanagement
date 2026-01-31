"""
SSL Commerz Payment Gateway Integration
Handles payment processing with SSL Commerz
"""

from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
from django.urls import reverse
import json


class SSLCommerczPaymentGateway:
    """
    SSL Commerz Payment Gateway Handler
    Manages payment initialization and validation
    """
    
    def __init__(self):
        self.store_id = settings.SSLCOMMERZ_STORE_ID
        self.store_password = settings.SSLCOMMERZ_STORE_PASSWORD
        self.is_sandbox = settings.SSLCOMMERZ_IS_SANDBOX
    
    def init_payment(self, booking, request):
        """
        Initialize SSL Commerz payment session
        
        Args:
            booking: Booking instance
            request: HTTP request object
            
        Returns:
            dict: Payment initialization response
        """
        
        # Get or create user profile to ensure it exists
        from users.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        sslc = SSLCOMMERZ({
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'easyApiPassword': self.store_password,
            'total_amount': float(booking.total_price),
            'currency': 'BDT',
            'order_num': str(booking.booking_id),
            'desc': f'Booking {booking.booking_id} - {booking.room.hotel.name}',
            'success_url': request.build_absolute_uri(reverse('booking:payment_success')),
            'fail_url': request.build_absolute_uri(reverse('booking:payment_failed')),
            'cancel_url': request.build_absolute_uri(reverse('booking:payment_cancelled')),
            'emi_option': 0,
            'cus_name': request.user.get_full_name() or request.user.username,
            'cus_email': request.user.email,
            'cus_phone': profile.phone or '',
            'cus_add1': profile.address or '',
            'cus_add2': '',
            'cus_city': profile.city or '',
            'cus_state': profile.state or '',
            'cus_postcode': profile.postal_code or '',
            'cus_country': profile.country or 'Bangladesh',
            'shipping_method': 'NO',
            'multi_card_name': '',
            'allowed_bin': '',
        })
        
        response = sslc.createSession()
        return response
    
    def validate_response(self, data):
        """
        Validate SSL Commerz payment response
        
        Args:
            data: Payment response data from SSL Commerz
            
        Returns:
            dict: Validation response
        """
        
        sslc = SSLCOMMERZ({
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'easyApiPassword': self.store_password,
        })
        
        validation_id = data.get('val_id')
        
        if not validation_id:
            return {
                'status': False,
                'message': 'Invalid validation ID'
            }
        
        response = sslc.transaction_query_request(validation_id)
        
        if response and response.get('status') == 'success':
            return {
                'status': True,
                'message': 'Payment validated successfully',
                'data': response
            }
        
        return {
            'status': False,
            'message': 'Payment validation failed',
            'data': response
        }
    
    def get_payment_status(self, booking_id):
        """
        Get payment status for a booking
        
        Args:
            booking_id: Booking ID
            
        Returns:
            str: Payment status
        """
        
        from .models import Payment
        
        try:
            payment = Payment.objects.filter(
                booking__booking_id=booking_id
            ).latest('created_at')
            return payment.status
        except Payment.DoesNotExist:
            return 'pending'


def initiate_sslcommerz_payment(booking, request):
    """
    Convenience function to initiate SSL Commerz payment
    
    Args:
        booking: Booking instance
        request: HTTP request object
        
    Returns:
        dict: Payment initialization response
    """
    
    gateway = SSLCommerczPaymentGateway()
    return gateway.init_payment(booking, request)


def validate_sslcommerz_response(data):
    """
    Convenience function to validate SSL Commerz payment response
    
    Args:
        data: Payment response data
        
    Returns:
        dict: Validation response
    """
    
    gateway = SSLCommerczPaymentGateway()
    return gateway.validate_response(data)
