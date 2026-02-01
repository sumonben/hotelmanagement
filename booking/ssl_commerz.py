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
        
        try:
            # Create SSLCOMMERZ instance with only required parameters
            sslc = SSLCOMMERZ({
                'store_id': self.store_id,
                'store_pass': self.store_password,
                'issandbox': self.is_sandbox,
            })
            
            # Prepare post body with payment details
            post_body = {
                'tran_id': str(booking.booking_id),  # Transaction ID - REQUIRED
                'total_amount': float(booking.total_price),
                'currency': 'BDT',
                'product_name': 'Hotel Room Booking',  # REQUIRED
                'product_category': 'travel',
                'product_profile': 'travel',
                'order_num': str(booking.booking_id),
                'desc': f'Booking {booking.booking_id} - {booking.room.hotel.name}',
                'success_url': request.build_absolute_uri(reverse('booking:payment_success')),
                'fail_url': request.build_absolute_uri(reverse('booking:payment_failed')),
                'cancel_url': request.build_absolute_uri(reverse('booking:payment_cancelled')),
                'emi_option': 0,
                'cus_name': request.user.get_full_name() or request.user.username,
                'cus_email': request.user.email,
                'cus_phone': profile.phone or '01700000000',  # Default phone if not set
                'cus_add1': profile.address or 'Address not provided',
                'cus_add2': '',
                'cus_city': profile.city or 'Dhaka',
                'cus_state': profile.state or 'Dhaka',
                'cus_postcode': profile.postal_code or '1000',
                'cus_country': profile.country or 'Bangladesh',
                'shipping_method': 'NO',
                'multi_card_name': '',
                'allowed_bin': '',
            }
            
            # Call createSession with post_body
            response = sslc.createSession(post_body)
            
            # Debug logging
            import json
            print(f"SSL Commerz Raw Response: {json.dumps(response, indent=2, default=str)}")
            
            # Check response type
            if isinstance(response, str):
                print(f"Response is string: {response}")
                # Try to parse as JSON
                try:
                    response = json.loads(response)
                except:
                    print("Could not parse response as JSON")
                    return {'status': 'error', 'message': response}
            
            print(f"Response type: {type(response)}")
            print(f"Response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
            
            return response
            
        except Exception as e:
            import traceback
            print(f"Error initializing SSL Commerz payment: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {'status': 'error', 'message': str(e)}
    
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
            'store_pass': self.store_password,
            'issandbox': self.is_sandbox,
        })
        
        validation_id = data.get('val_id')
        
        if not validation_id:
            return {
                'status': False,
                'message': 'Invalid validation ID'
            }
        
        response = sslc.validationTransactionOrder(validation_id)
        
        if response and response.get('status') == 'VALID':
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
