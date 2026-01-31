# Generated migration for Carousel models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='carousel', to='hotel.hotel')),
            ],
            options={
                'verbose_name_plural': 'Carousels',
            },
        ),
        migrations.CreateModel(
            name='CarouselSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(upload_to='carousel/')),
                ('button_text', models.CharField(blank=True, default='View Rooms', max_length=50)),
                ('button_url', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0, help_text='Order of appearance in carousel')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('carousel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='hotel.carousel')),
            ],
            options={
                'verbose_name_plural': 'Carousel Slides',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
