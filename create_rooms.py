#!/usr/bin/env python
"""Script to create sample rooms and room types"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhms_config.settings')
django.setup()

from hotel.models import Hotel, RoomType, Room

hotel = Hotel.objects.get(id=1)

# Create room types
room_types_data = [
    {
        'name': 'Standard Room',
        'description': 'Comfortable room with essential amenities',
        'max_guests': 2,
        'beds': 'Queen bed',
        'amenities': 'TV, WiFi, Air conditioning, Private bathroom, Mini fridge',
    },
    {
        'name': 'Deluxe Room',
        'description': 'Spacious room with modern amenities and city view',
        'max_guests': 3,
        'beds': 'King bed',
        'amenities': 'Smart TV, High-speed WiFi, Air conditioning, Luxury bathroom, Mini bar, Work desk',
    },
    {
        'name': 'Suite',
        'description': 'Premium suite with living area and premium services',
        'max_guests': 4,
        'beds': 'King bed + Sofa bed',
        'amenities': 'Smart TV, Premium WiFi, Climate control, Luxury bathroom with jacuzzi, Mini bar, Living area',
    }
]

room_types = []
for rt_data in room_types_data:
    rt, created = RoomType.objects.get_or_create(
        hotel=hotel,
        name=rt_data['name'],
        defaults={
            'description': rt_data['description'],
            'max_guests': rt_data['max_guests'],
            'beds': rt_data['beds'],
            'amenities': rt_data['amenities'],
        }
    )
    room_types.append(rt)
    if created:
        print(f"✓ Created room type: {rt.name}")
    else:
        print(f"  Room type already exists: {rt.name}")

# Create sample rooms
rooms_data = [
    {'room_number': '101', 'floor': 1, 'room_type': room_types[0], 'price': Decimal('99.99')},
    {'room_number': '102', 'floor': 1, 'room_type': room_types[0], 'price': Decimal('99.99')},
    {'room_number': '103', 'floor': 1, 'room_type': room_types[1], 'price': Decimal('149.99')},
    {'room_number': '104', 'floor': 1, 'room_type': room_types[1], 'price': Decimal('149.99')},
    {'room_number': '201', 'floor': 2, 'room_type': room_types[0], 'price': Decimal('99.99')},
    {'room_number': '202', 'floor': 2, 'room_type': room_types[0], 'price': Decimal('99.99')},
    {'room_number': '203', 'floor': 2, 'room_type': room_types[1], 'price': Decimal('149.99')},
    {'room_number': '301', 'floor': 3, 'room_type': room_types[2], 'price': Decimal('249.99')},
]

for room_data in rooms_data:
    room, created = Room.objects.get_or_create(
        hotel=hotel,
        room_number=room_data['room_number'],
        defaults={
            'floor': room_data['floor'],
            'room_type': room_data['room_type'],
            'price_per_night': room_data['price'],
            'status': 'available',
            'is_active': True,
        }
    )
    if created:
        print(f"✓ Created room {room.room_number} ({room.room_type.name}) - ${room.price_per_night}/night")
    else:
        print(f"  Room already exists: {room.room_number}")

print(f"\n✓ Hotel setup complete!")
print(f"  - Hotel: {hotel.name}")
print(f"  - Room types: {len(room_types)}")
print(f"  - Rooms: {hotel.rooms.count()}")
