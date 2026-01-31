from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Create missing user profiles for existing users'

    def handle(self, *args, **options):
        """Create profiles for all users that don't have one"""
        
        created_count = 0
        existing_count = 0
        
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(f'Created profile for user: {user.username}')
            else:
                existing_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProfile creation complete!\n'
                f'  - Created: {created_count} new profiles\n'
                f'  - Already existed: {existing_count} profiles'
            )
        )
