# Single Hotel Setup Guide

This project has been converted to work with a single specific hotel instead of a multi-hotel system.

## Key Changes Made

### 1. **Configuration Settings** ([rhms_config/settings.py](rhms_config/settings.py))
- Added `DEFAULT_HOTEL_ID` setting at the end of the file
- Change this to match your hotel's database ID

```python
# Single Hotel Configuration
DEFAULT_HOTEL_ID = 1  # Change this to your hotel's ID
```

### 2. **Hotel Views** ([hotel/views.py](hotel/views.py))
- **HomeView**: Now displays the single hotel's details, rooms, facilities, and reviews
- **HotelDetailView**: Also shows the single hotel's full details
- **HotelListView**: Redirects to home (maintained for backward compatibility)
- **HotelReviewCreateView**: Creates reviews for the default hotel only
- **save_hotel()**: Saves/removes the single hotel from user's wishlist
- **search_availability()**: Searches for available rooms in the single hotel
- Added helper function `get_default_hotel()` to retrieve the configured hotel

### 3. **Hotel URLs** ([hotel/urls.py](hotel/urls.py))
Updated URL patterns to remove slug-based routing:
- ❌ Removed: `path('hotels/<slug:slug>/', ...)`
- ✅ Updated: `path('hotel/', ...)` - for hotel detail view
- ✅ Updated: `path('hotel/review/', ...)` - for creating reviews
- ✅ Updated: `path('hotel/save/', ...)` - for wishlist toggle

### 4. **Hotel Templates** ([templates/hotel/home.html](templates/hotel/home.html))
- Complete redesign to showcase a single hotel
- Displays:
  - Hotel banner and hero section
  - Hotel details (contact, check-in/out times, rating)
  - Simplified search form (date + guests only)
  - Room types offered
  - Available rooms
  - Guest reviews and ratings
  - Add/Remove from wishlist button
  - Write a review link (for logged-in users)

### 5. **Search Forms** ([hotel/forms.py](hotel/forms.py))
- **HotelSearchForm**: Simplified to only include:
  - Check-in date
  - Check-out date
  - Number of guests
- Removed: city search, hotel search, price filters (not needed for single hotel)

## Setup Instructions

### Step 1: Create Your Hotel
1. Go to Django admin panel (`/admin/`)
2. Add a new Hotel entry with:
   - Name, description, contact info
   - Address (city, state, country, postal code)
   - Check-in/check-out times
   - Upload hotel image and banner

### Step 2: Configure Settings
Edit [rhms_config/settings.py](rhms_config/settings.py):
```python
DEFAULT_HOTEL_ID = <your_hotel_id>  # Replace with your hotel's actual ID
```

### Step 3: Add Rooms
1. In Django admin, add room types for your hotel
2. Add individual rooms with pricing and details

### Step 4: Add Amenities (Optional)
Add hotel facilities and amenities through Django admin

## URL Changes Reference

### Before (Multi-Hotel)
```
/                           → List featured hotels
/hotels/                    → List all hotels
/hotels/hotel-name/         → Hotel detail
/hotels/hotel-name/save/    → Save hotel
/hotels/hotel-name/review/  → Create review
```

### After (Single Hotel)
```
/                           → Show the hotel home page
/hotel/                     → Hotel detail (same as home)
/hotel/save/                → Save hotel to wishlist
/hotel/review/              → Create review
/room/<id>/                 → Room detail (unchanged)
/booking/                   → Booking management (unchanged)
```

## Database Notes

- **No migration needed**: All existing hotel, room, and booking data remains intact
- The `Hotel` model still exists and supports multiple hotels in the database
- Only the UI/views are restricted to show one hotel at a time
- You can easily revert to multi-hotel setup by changing views back

## Views Workflow

```
User visits "/" → HomeView displays hotel + rooms + reviews
                 ↓
            Search for dates + guests
                 ↓
            HotelSearchForm submission
                 ↓
            Display available rooms
                 ↓
            Click room → RoomDetailView
                 ↓
            Create booking → BookingCreateView
```

## Features Available

✅ **Users can:**
- View the single hotel's details, rooms, and amenities
- Check room availability for date ranges
- Book rooms
- Manage their bookings
- Leave and view reviews
- Add/remove hotel from wishlist

✅ **Admin can:**
- Manage rooms and pricing
- View and manage bookings
- Manage facility/amenities
- View guest reviews
- Change the default hotel anytime via settings

## Troubleshooting

### "Hotel matching query does not exist"
- Check that `DEFAULT_HOTEL_ID` in settings matches an actual hotel in database
- Verify hotel's status is "active"

### Hotel not showing on homepage
- Ensure at least one hotel exists in database with ID matching `DEFAULT_HOTEL_ID`
- Check hotel status = 'active'

### Rooms not displaying
- Add rooms to the hotel through Django admin
- Ensure rooms have status='available' and is_active=True

## Reverting to Multi-Hotel Setup

If you need to go back to a multi-hotel system:
1. Restore original views from git history
2. Restore original URLs
3. Restore original templates
4. Remove `DEFAULT_HOTEL_ID` from settings

All database records remain intact for easy restoration.
