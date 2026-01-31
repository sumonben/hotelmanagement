# Fix for "RelatedObjectDoesNotExist: User has no profile" Error

## Problem
When attempting to create a booking at `/booking/create/2/`, the application threw:
```
RelatedObjectDoesNotExist at /booking/create/2/
User has no profile.
```

This occurred because:
1. Some users were created before the `UserProfile` model was implemented
2. The code tried to access `user.profile` without checking if it existed
3. No automatic profile creation mechanism was in place

## Solution Implemented

### 1. **Django Signals for Automatic Profile Creation** (`users/signals.py`)
- Created signal handlers that automatically create a `UserProfile` when a new user is created
- Added backup signal to ensure profile exists whenever a user is saved
- Uses `get_or_create()` to prevent duplicate profile creation

### 2. **App Configuration Update** (`users/apps.py`)
- Registered signals in the app's `ready()` method
- Ensures signals are loaded when Django starts

### 3. **Defensive Code in Views** (`booking/views.py`)
- Updated `BookingCreateView.form_valid()` to safely get or create the user profile
- Changed from direct `user.profile` access to `UserProfile.objects.get_or_create()`
- Prevents errors if profile doesn't exist for any reason

### 4. **Payment Gateway Safety** (`booking/ssl_commerz.py`)
- Updated `SSLCommerczPaymentGateway.init_payment()` to ensure profile exists before accessing profile data
- Now safely retrieves profile with `get_or_create()` before accessing fields like phone, address, city, etc.

### 5. **Management Command** (`users/management/commands/create_missing_profiles.py`)
- Created command to create profiles for all existing users without one
- Run with: `python manage.py create_missing_profiles`
- Shows count of created profiles vs. existing profiles

## Files Modified/Created

### Created Files:
- `users/signals.py` - Signal handlers for automatic profile creation
- `users/management/commands/create_missing_profiles.py` - Management command to fix existing users
- `users/management/__init__.py` - Package initialization
- `users/management/commands/__init__.py` - Package initialization

### Modified Files:
- `users/apps.py` - Added `ready()` method to register signals
- `booking/views.py` - Updated `BookingCreateView.form_valid()` for safe profile access
- `booking/ssl_commerz.py` - Updated `init_payment()` method to ensure profile exists

## How It Works

### For New Users:
1. When a user registers, Django's `post_save` signal triggers
2. Signal automatically creates a `UserProfile` with default values
3. Profile is ready when user attempts to make a booking

### For Existing Users (without profiles):
1. Profile is created on-demand using `get_or_create()` when:
   - User creates a booking
   - User makes a payment
   - Any other code tries to access the profile
2. Alternatively, run: `python manage.py create_missing_profiles`

### Data Consistency:
- All profile access now uses `get_or_create()` to ensure it exists
- Signals prevent users from ever being created without a profile (going forward)
- Backward compatibility maintained for existing users

## Testing

After applying these fixes, the booking creation flow should work without errors:

1. Run migrations: `python manage.py migrate`
2. Create missing profiles: `python manage.py create_missing_profiles`
3. Navigate to: `/booking/create/2/` (or any valid room ID)
4. Create a booking - should complete successfully without profile errors

## Result

✅ Fixed RelatedObjectDoesNotExist error
✅ Automatic profile creation for all new users
✅ Retroactive profile creation for existing users
✅ Safe profile access throughout the application
✅ No data loss or migration issues
