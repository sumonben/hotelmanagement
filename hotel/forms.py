from django import forms
from django.core.exceptions import ValidationError
from .models import Hotel, Room, HotelReview, RoomType
from django.utils import timezone

class HotelSearchForm(forms.Form):
    """Form for searching room availability at the single hotel"""
    check_in_date = forms.DateField(
        label="Check-in",
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().strftime('%Y-%m-%d')
        })
    )
    check_out_date = forms.DateField(
        label="Check-out",
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    guests = forms.IntegerField(
        min_value=1,
        initial=1,
        required=True,
        label="Number of Guests",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError("Check-out date must be after check-in date.")
        
        return cleaned_data


class HotelReviewForm(forms.ModelForm):
    """Form for creating hotel reviews"""
    class Meta:
        model = HotelReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title...',
                'maxlength': '200'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience...',
                'rows': 5
            }),
        }


class HotelFilterForm(forms.Form):
    """Form for filtering hotels"""
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest'),
            ('rating', 'Highest Rated'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    facilities = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import HotelFacility
        self.fields['facilities'].choices = [
            (f.id, f.name) for f in HotelFacility.objects.values_list('id', 'name').distinct()
        ]


class RoomFilterForm(forms.Form):
    """Form for filtering rooms"""
    room_type = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Room Type"
    )
    price_range = forms.ChoiceField(
        required=False,
        choices=[
            ('all', 'All Prices'),
            ('budget', '$0 - $50'),
            ('mid_range', '$50 - $150'),
            ('premium', '$150+'),
        ],
        widget=forms.RadioSelect()
    )
    
    def __init__(self, hotel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_type'].choices = [
            (rt.id, rt.name) for rt in hotel.room_types.all()
        ]
