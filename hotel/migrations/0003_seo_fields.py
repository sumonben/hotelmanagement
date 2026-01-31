from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0002_carousel'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='meta_description',
            field=models.CharField(blank=True, help_text='SEO meta description (max 160 chars)', max_length=160),
        ),
        migrations.AddField(
            model_name='hotel',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Comma-separated keywords', max_length=200),
        ),
        migrations.AddField(
            model_name='roomtype',
            name='slug',
            field=models.SlugField(blank=True, help_text='Auto-generated from name'),
        ),
        migrations.AddField(
            model_name='roomtype',
            name='image_alt_text',
            field=models.CharField(blank=True, help_text='Alt text for SEO', max_length=200),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='alt_text',
            field=models.CharField(blank=True, help_text='Alt text for accessibility and SEO', max_length=200),
        ),
    ]
