# Residential Hotel Management System (RHMS)

A comprehensive Django-based online hotel management system for residential hotels with complete booking, payment, and user management features.

## Features

### Hotel Management
- Multiple hotel listings with detailed information
- Room management with different room types
- Facility and amenity tracking
- Hotel reviews and ratings system
- Featured hotels section
- Image gallery for hotels and rooms

### Room Management
- Room types and categorization
- Pricing management (regular and discount prices)
- Room availability checking
- Room status tracking (available, occupied, maintenance, unavailable)
- Image management for rooms

### Booking System
- Real-time room availability search
- Advanced booking form with date and guest validation
- Booking confirmation and tracking
- Booking history and management
- Check-in and check-out functionality
- Booking cancellation with refund policies

### Payment Processing
- Multiple payment methods support (Credit Card, Debit Card, PayPal, Bank Transfer)
- Secure payment processing
- Payment history tracking
- Invoice and receipt generation
- Tax calculation and discount management

### User Management
- User registration and authentication
- User profiles with personal information
- Booking history and management
- Saved hotels/wishlist functionality
- Notification preferences
- Loyalty points system
- Payment method management

### Admin Features
- Django admin interface with customized models
- Hotel and room management
- Booking and payment tracking
- User and review management
- Comprehensive filtering and search

## Project Structure

```
rhms/
├── manage.py
├── requirements.txt
├── rhms_config/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── hotel/                    # Hotel app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── booking/                  # Booking app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── users/                    # Users app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── templates/               # HTML templates
│   ├── base.html
│   ├── hotel/
│   │   ├── home.html
│   │   ├── hotel_list.html
│   │   ├── hotel_detail.html
│   │   └── ...
│   ├── booking/
│   │   ├── booking_list.html
│   │   ├── booking_form.html
│   │   └── ...
│   └── users/
│       ├── register.html
│       ├── login.html
│       └── ...
├── static/                  # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── img/
└── media/                   # User uploaded files
    ├── hotels/
    ├── rooms/
    └── profile_pictures/
```

## Installation

### Prerequisites
- Python 3.8+
- Django 4.2+
- pip

### Setup Steps

1. **Clone or download the project**
```bash
cd rhms
```

2. **Create a virtual environment**
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Create static directories**
```bash
mkdir -p static/css static/js
mkdir -p media/hotels media/rooms media/profile_pictures
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**
```bash
python manage.py runserver
```

9. **Access the application**
- Frontend: http://localhost:8000/
- Admin: http://localhost:8000/admin/

## Database Models

### Hotel App
- **Hotel**: Main hotel information and details
- **RoomType**: Different room categories
- **Room**: Individual rooms in the hotel
- **HotelFacility**: Facilities available at the hotel
- **HotelReview**: Guest reviews and ratings
- **RoomImage**: Additional images for rooms

### Booking App
- **Booking**: Room booking records
- **Payment**: Payment transactions
- **CancellationPolicy**: Hotel cancellation policies
- **Amenity**: Available amenities
- **BookingAmenity**: Track amenities added to bookings

### Users App
- **UserProfile**: Extended user information
- **SavedHotel**: Saved hotels/wishlist
- **PaymentMethod**: Saved payment methods
- **NotificationPreference**: User notification preferences

## Usage

### For Guests
1. Register or login to your account
2. Search for hotels by city, date range, and price
3. View hotel details, rooms, and reviews
4. Book a room with your preferred dates
5. Proceed to payment
6. Check-in and check-out at the hotel
7. Leave reviews and manage your bookings

### For Admin
1. Login to Django admin (http://localhost:8000/admin/)
2. Manage hotels, rooms, and facilities
3. View and manage bookings
4. Process payments and refunds
5. Manage users and their profiles
6. View and moderate reviews

## Configuration

Edit `rhms_config/settings.py` for:
- Database settings
- Email configuration for notifications
- Payment gateway settings (future)
- Media and static files paths
- Security settings

## Features Roadmap

- Payment gateway integration (Stripe, PayPal)
- Email notifications
- SMS notifications
- Multi-language support
- Mobile app
- Advanced analytics and reporting
- API for third-party integrations
- Real-time notifications

## Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Password hashing
- User authentication and authorization
- Secure payment processing

## Support

For issues, questions, or suggestions, please create an issue in the project repository.

## License

This project is licensed under the MIT License.

## Author

Developed as a comprehensive hotel management system for educational and commercial purposes.

## Version

Version 1.0 - Full Phase Implementation
