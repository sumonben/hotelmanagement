from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Payment
from hotel.models import Room

class BookingForm(forms.ModelForm):
    """Form for creating room bookings"""
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'number_of_guests', 
                  'guest_name', 'guest_email', 'guest_phone', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().strftime('%Y-%m-%d')
            }),
            'check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Special requests (optional)'
            }),
        }
    
    def __init__(self, room=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room
        if room:
            self.fields['number_of_guests'].max_value = room.room_type.max_guests
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        guests = cleaned_data.get('number_of_guests')
        
        # Validate dates
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError("Check-out date must be after check-in date.")
            
            min_stay = timezone.now().date() + timedelta(days=1)
            if check_in < min_stay:
                raise ValidationError("Check-in date must be at least tomorrow.")
        
        # Validate guest count
        if self.room and guests and guests > self.room.room_type.max_guests:
            raise ValidationError(
                f"Maximum guests for this room type is {self.room.room_type.max_guests}."
            )
        
        # Check room availability
        if self.room and check_in and check_out:
            if not self.room.is_available(check_in, check_out):
                raise ValidationError("This room is not available for selected dates.")
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    """Form for payment processing"""
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
        }
    
    # Additional card fields for UI
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'id': 'cardNumber'
        })
    )
    card_holder = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on card',
            'id': 'cardHolder'
        })
    )
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'id': 'expiryDate'
        })
    )
    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
            'id': 'cvv'
        })
    )
    
    # PayPal email
    paypal_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'PayPal email',
            'id': 'paypalEmail'
        })
    )
    
    # Bank transfer agreement
    agree_terms = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')
            card_holder = cleaned_data.get('card_holder')
            
            if not all([card_number, expiry_date, cvv, card_holder]):
                raise ValidationError("All card fields are required.")
            
            # Basic validation
            if not card_number.replace(' ', '').isdigit() or len(card_number.replace(' ', '')) != 16:
                raise ValidationError("Invalid card number.")
            
            if len(cvv) not in [3, 4]:
                raise ValidationError("Invalid CVV.")
        
        elif payment_method == 'paypal':
            paypal_email = cleaned_data.get('paypal_email')
            if not paypal_email:
                raise ValidationError("PayPal email is required.")
        
        return cleaned_data


class BookingSearchForm(forms.Form):
    """Form for searching existing bookings"""
    booking_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Booking ID'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )


class CancellationForm(forms.Form):
    """Form for cancellation request"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Reason for cancellation (optional)'
        }),
        required=False
    )
    agree = forms.BooleanField(
        label='I understand the cancellation policy',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
