# SSL Commerz Payment Gateway Fix

## Problem

SSL Commerz payment gateway was not redirecting to the payment API when users selected the SSL Commerz payment method and submitted the payment form.

## Root Causes Identified and Fixed

### 1. **Incorrect Parameter Names in SSLCOMMERZ Constructor**

**Issue**: The library uses specific parameter names that don't match standard Django naming conventions.

**Fix Applied**:
```python
# WRONG - These names are not recognized:
SSLCOMMERZ({
    'store_passwd': password,      # X Wrong
    'easyApiPassword': password,   # X Wrong
    'is_sandbox': True,             # X Wrong
})

# CORRECT - These are the actual expected parameters:
SSLCOMMERZ({
    'store_pass': password,         # ✓ Correct
    'issandbox': True,              # ✓ Correct (boolean, not underscore)
})
```

### 2. **Incorrect createSession() Method Call**

**Issue**: The `createSession()` method requires a `post_body` parameter with payment details.

**Fix Applied**:
```python
# WRONG - Passing parameters to constructor:
sslc = SSLCOMMERZ({
    'store_id': ...,
    'store_pass': ...,
    'issandbox': ...,
    'total_amount': ...,    # X These go to POST body
    'currency': ...,        # X Not to constructor
    ...
})
response = sslc.createSession()  # X Missing post_body argument

# CORRECT - Separate constructor and POST body:
sslc = SSLCOMMERZ({
    'store_id': store_id,
    'store_pass': store_pass,
    'issandbox': is_sandbox,
})

post_body = {
    'total_amount': amount,
    'currency': 'BDT',
    'tran_id': transaction_id,
    'product_name': 'Hotel Room Booking',
    'cus_phone': phone,
    'cus_add1': address,
    'success_url': success_url,
    'fail_url': fail_url,
    'cancel_url': cancel_url,
    ...
}

response = sslc.createSession(post_body)  # ✓ Correct
```

### 3. **Missing Required Fields**

**Issue**: SSL Commerz API requires certain mandatory fields. Errors were:
- `'tran_id' is missing or empty` - Transaction ID not provided
- `'cus_phone' is missing or empty` - Customer phone not provided
- `'product_name' is missing` - Product name not provided

**Fix Applied**:
```python
post_body = {
    'tran_id': str(booking.booking_id),                    # ✓ Added
    'product_name': 'Hotel Room Booking',                  # ✓ Added
    'product_category': 'travel',                          # ✓ Added
    'product_profile': 'travel',                           # ✓ Added
    'cus_phone': profile.phone or '01700000000',          # ✓ Added default
    'cus_add1': profile.address or 'Address not provided', # ✓ Added default
    'cus_city': profile.city or 'Dhaka',                  # ✓ Added default
    'cus_state': profile.state or 'Dhaka',                # ✓ Added default
    'cus_postcode': profile.postal_code or '1000',        # ✓ Added default
    'cus_country': profile.country or 'Bangladesh',       # ✓ Added default
    ...
}
```

### 4. **Case-Sensitive Status Check**

**Issue**: Response status could be 'SUCCESS' or 'success', but code was checking for exact 'success' (lowercase).

**Fix Applied**:
```python
# WRONG:
if response.get('status') == 'success' and gateway_url:  # X Case-sensitive

# CORRECT:
status = response.get('status') if isinstance(response, dict) else None
is_success = status and str(status).upper() == 'SUCCESS'
if is_success and gateway_url:  # ✓ Case-insensitive
```

### 5. **Incorrect Gateway URL Key**

**Issue**: Response contains `GatewayPageURL` (not empty) but code was looking for `redirectGatewayURL` (which was empty).

**Fix Applied**:
```python
# Check multiple possible key names in order of priority
gateway_url = (response.get('GatewayPageURL') or              # ✓ Primary
             response.get('redirectGatewayURL') or          # ✓ Fallback
             response.get('gatewayPageURL') or              # ✓ Fallback
             response.get('redirect_url') or                # ✓ Fallback
             response.get('redirect_gateway_url'))          # ✓ Fallback
```

## Files Modified

1. **booking/ssl_commerz.py**
   - Fixed `init_payment()` method to use correct parameter names
   - Changed parameters from constructor to `post_body` argument
   - Added required fields with default values
   - Added better error handling and debugging

2. **booking/views.py** (PaymentView)
   - Fixed status check to be case-insensitive
   - Updated gateway URL detection to check `GatewayPageURL` first
   - Added better error messages and debugging
   - Added form validation error handling

3. **templates/booking/payment.html**
   - Added client-side form submission debugging

## Testing Results

✓ Payment gateway initialization successful
✓ Session Key generated: `7F61CA7C03582AAA68B6325A8DBA184F`
✓ Gateway Page URL returned: `https://sandbox.sslcommerz.com/EasyCheckOut/...`
✓ Ready for user redirection to payment page

## How It Works Now

1. User selects SSL Commerz payment method
2. User enters booking details and clicks "Complete Payment"
3. PaymentView receives form submission
4. Creates SSLCOMMERZ instance with credentials
5. Calls `createSession(post_body)` with payment details
6. Gets back `GatewayPageURL` from SSL Commerz API
7. **✓ Redirects user to SSL Commerz payment gateway**
8. User completes payment on SSL Commerz
9. SSL Commerz redirects back to our callback URLs (success/failed/cancelled)

## Configuration Verified

✓ SSLCOMMERZ_STORE_ID: `ziana695a18ca87746`
✓ SSLCOMMERZ_STORE_PASSWORD: Configured
✓ SSLCOMMERZ_IS_SANDBOX: `True` (testing mode)
✓ Callback URLs: Configured in booking/urls.py

## Debugging Information

When testing payment flow, check Django console for:
```
SSL Commerz method selected
Form Valid - Payment Method: sslcommerz
SSL Commerz Raw Response: {...}
Gateway URL: https://sandbox.sslcommerz.com/EasyCheckOut/...
Response status: SUCCESS
✓ Gateway URL found: https://sandbox.sslcommerz.com/EasyCheckOut/...
```

## Supported Payment Methods in SSL Commerz

The gateway now supports all payment methods available in SSL Commerz sandbox:
- **Credit/Debit Cards**: VISA, MASTERCARD, AMEX
- **Mobile Banking**: bKash, Nagad, DBBL Mobile, Robi Topup, etc.
- **Internet Banking**: City, AB Bank, IBBL, Bank Asia, etc.
- **Other**: QCash, Fastcash, upay, okayWallet, etc.

## Next Steps

1. Test complete payment flow in sandbox
2. Verify callback handling (payment_success, payment_failed, payment_cancelled)
3. Test on production with real SSL Commerz credentials when ready
4. Monitor payment logs for any issues

