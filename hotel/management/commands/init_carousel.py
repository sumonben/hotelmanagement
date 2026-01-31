"""
Management command to initialize carousel for the default hotel.
Usage: python manage.py init_carousel
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from hotel.models import Hotel, Carousel, CarouselSlide


class Command(BaseCommand):
    help = 'Initialize carousel for the default hotel with sample slides'

    def handle(self, *args, **options):
        try:
            hotel = Hotel.objects.get(id=settings.DEFAULT_HOTEL_ID)
        except Hotel.DoesNotExist:
            raise CommandError(f'Hotel with ID {settings.DEFAULT_HOTEL_ID} does not exist')

        # Create carousel if it doesn't exist
        carousel, created = Carousel.objects.get_or_create(hotel=hotel)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created carousel for {hotel.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Carousel already exists for {hotel.name}')
            )

        # Create sample slides if carousel is empty
        if carousel.slides.count() == 0:
            sample_slides = [
                {
                    'title': f'Welcome to {hotel.name}',
                    'subtitle': 'Experience Luxury and Comfort',
                    'description': 'Discover world-class hospitality and exceptional service',
                    'button_text': 'Book Now',
                    'button_url': '#',
                    'order': 1,
                },
                {
                    'title': 'Premium Rooms & Suites',
                    'subtitle': 'Your Perfect Stay Awaits',
                    'description': 'Choose from our selection of elegantly designed rooms',
                    'button_text': 'View Rooms',
                    'button_url': '#',
                    'order': 2,
                },
                {
                    'title': 'World-Class Amenities',
                    'subtitle': 'Everything You Need',
                    'description': 'Enjoy our state-of-the-art facilities and services',
                    'button_text': 'Learn More',
                    'button_url': '#',
                    'order': 3,
                },
            ]

            for slide_data in sample_slides:
                slide = CarouselSlide.objects.create(carousel=carousel, **slide_data)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created slide: {slide.title}')
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Carousel initialized with {len(sample_slides)} sample slides'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\nℹ Note: Please upload actual images for the carousel slides in the Django admin.'
                )
            )
        else:
            self.stdout.write(
                self.style.INFO(f'Carousel already has {carousel.slides.count()} slides')
            )
