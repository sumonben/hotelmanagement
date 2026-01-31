"""
Auto-generated migration to add SSL Commerz to payment method choices.
This updates the Payment model's PAYMENT_METHOD_CHOICES.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('sslcommerz', 'SSL Commerz (Bkash, Nagad, Card, Bank)'),
                    ('credit_card', 'Credit Card'),
                    ('debit_card', 'Debit Card'),
                    ('paypal', 'PayPal'),
                    ('bank_transfer', 'Bank Transfer'),
                    ('wallet', 'Wallet'),
                ],
                max_length=20
            ),
        ),
    ]
