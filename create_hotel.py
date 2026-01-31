#!/usr/bin/env python
"""Script to create a sample hotel"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhms_config.settings')
django.setup()

from hotel.models import Hotel

# Check if hotel already exists
if Hotel.objects.filter(id=1).exists():
    print("Hotel with ID 1 already exists!")
    hotel = Hotel.objects.get(id=1)
else:
    # Create a sample hotel
    hotel = Hotel.objects.create(
        name="Grand Hotel",
        slug="grand-hotel",
        description="A luxurious 5-star hotel offering world-class amenities and exceptional service",
        email="info@grandhotel.com",
        phone="+1-800-GRAND-01",
        address="123 Main Street",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001",
        check_in_time="14:00",
        check_out_time="11:00",
        status="active",
        is_featured=True
    )
    print("✓ Hotel created successfully!")

print(f"  - ID: {hotel.id}")
print(f"  - Name: {hotel.name}")
print(f"  - Email: {hotel.email}")
print(f"  - Status: {hotel.status}")
print(f"\nYour DEFAULT_HOTEL_ID in settings.py is set to: 1")
print("The hotel is now ready to use!")
