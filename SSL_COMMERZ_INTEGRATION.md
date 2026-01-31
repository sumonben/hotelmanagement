# SSL Commerz Payment Integration Guide

## Overview
This guide explains how to integrate SSL Commerz payment gateway into the RHMS Django application.

## Installation

### 1. Install the SSL Commerz Library
The library has been added to `requirements.txt`. Install it using:

```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install sslcommerz-lib
```

## Configuration

### 2. Add SSL Commerz Credentials to settings.py

Update `rhms_config/settings.py` with your SSL Commerz credentials:

```python
# SSL Commerz Payment Gateway Configuration
SSLCOMMERZ_STORE_ID = 'your_store_id'  # Get from SSL Commerz dashboard
SSLCOMMERZ_STORE_PASSWORD = 'your_store_password'  # Get from SSL Commerz dashboard
SSLCOMMERZ_IS_SANDBOX = True  # Set to False for production
```

### 3. Get SSL Commerz Credentials

1. Visit [SSL Commerz](https://www.sslcommerz.com/)
2. Create a merchant account
3. Log in to your dashboard
4. Find your Store ID and Store Password
5. Add them to your settings.py

## Implementation

### Files Added

1. **booking/ssl_commerz.py** - SSL Commerz payment gateway handler
   - `SSLCommerczPaymentGateway` class for managing payments
   - Functions for initializing and validating payments

2. **booking/ssl_commerz_views_example.py** - Example views for payment handling
   - Payment initiation view
   - Payment success handler
   - Payment failure handler
   - Payment cancellation handler

### Basic Usage

#### 1. Initialize Payment

```python
from booking.ssl_commerz import initiate_sslcommerz_payment

# In your payment view
response = initiate_sslcommerz_payment(booking, request)

if response.get('status') == 'success':
    gateway_url = response.get('GatewayPageURL')
    # Redirect user to gateway_url
```

#### 2. Validate Payment Response

```python
from booking.ssl_commerz import validate_sslcommerz_response

# After user returns from SSL Commerz
validation_response = validate_sslcommerz_response(request.POST)

if validation_response['status']:
    # Payment is valid, update booking status
    booking.payment_status = 'completed'
    booking.status = 'confirmed'
    booking.save()
```

#### 3. Update Payment Model (Optional)

To track SSL Commerz transactions, you may want to add a field to the Payment model:

```python
# In booking/models.py, update Payment class
payment_gateway = models.CharField(
    max_length=50,
    choices=[
        ('sslcommerz', 'SSL Commerz'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ],
    default='credit_card'
)
```

### Integration Steps

1. **Update payment.html template** to add SSL Commerz option:
```html
<div class="form-check">
    <input class="form-check-input" type="radio" name="payment_method" id="sslcommerz" value="sslcommerz">
    <label class="form-check-label" for="sslcommerz">
        SSL Commerz (Bkash, Nagad, Card, Bank)
    </label>
</div>
```

2. **Update booking/urls.py** to add payment endpoints:
```python
from . import views

urlpatterns = [
    # ... existing patterns ...
    
    # SSL Commerz Payment URLs
    path('payment/<int:booking_id>/initiate/', 
         views.SSLCommerczInitiateView.as_view(), 
         name='payment_initiate'),
    path('payment/success/', 
         views.SSLCommerczSuccessView.as_view(), 
         name='payment_success'),
    path('payment/failed/', 
         views.SSLCommerczFailedView.as_view(), 
         name='payment_failed'),
    path('payment/cancelled/', 
         views.SSLCommerczCancelledView.as_view(), 
         name='payment_cancelled'),
]
```

3. **Update booking/views.py** to include the example view classes from `ssl_commerz_views_example.py`

4. **Update payment form** to handle SSL Commerz:
```python
# In booking/forms.py
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(choices=[
                ('credit_card', 'Credit Card'),
                ('debit_card', 'Debit Card'),
                ('paypal', 'PayPal'),
                ('bank_transfer', 'Bank Transfer'),
                ('sslcommerz', 'SSL Commerz'),
            ])
        }
```

## Testing

### Sandbox Mode

SSL Commerz provides test cards for sandbox testing:

- **Card Number**: 4111111111111111
- **Expiry**: Any future date
- **CVV**: Any 3 digits

Set `SSLCOMMERZ_IS_SANDBOX = True` in settings.py to test in sandbox mode.

### Production Mode

1. Set `SSLCOMMERZ_IS_SANDBOX = False` in settings.py
2. Update Store ID and Store Password with production credentials
3. Ensure HTTPS is enabled on your server
4. Set `SECURE_SSL_REDIRECT = True` in settings.py

## Security Considerations

1. **Never hardcode credentials** - Use environment variables:
```python
import os

SSLCOMMERZ_STORE_ID = os.getenv('SSLCOMMERZ_STORE_ID')
SSLCOMMERZ_STORE_PASSWORD = os.getenv('SSLCOMMERZ_STORE_PASSWORD')
SSLCOMMERZ_IS_SANDBOX = os.getenv('SSLCOMMERZ_IS_SANDBOX', True)
```

2. **Use HTTPS** in production
3. **Validate all payments** on the server side
4. **Store payment records** for audit trails
5. **Implement proper error handling** and logging

## Troubleshooting

### Common Issues

1. **"Store ID is invalid"**
   - Check your SSLCOMMERZ_STORE_ID is correct
   - Ensure credentials are in correct settings.py

2. **"Payment validation failed"**
   - Verify the Validation ID is being received correctly
   - Check SSL Commerz server logs

3. **"GatewayPageURL is empty"**
   - Ensure all required fields are populated
   - Check that the store is active on SSL Commerz

## References

- [SSL Commerz Official Documentation](https://developer.sslcommerz.com/)
- [sslcommerz-lib GitHub](https://github.com/sslcommerz/sslcommerz-lib)
- [SSL Commerz Integration Guide](https://www.sslcommerz.com/developer/doc/)

## Support

For issues or questions:
1. Check SSL Commerz documentation
2. Review the example views in `ssl_commerz_views_example.py`
3. Check Django logs for detailed error messages
4. Contact SSL Commerz support with merchant ID
