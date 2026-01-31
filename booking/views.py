from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
import uuid

from .models import Booking, Payment, CancellationPolicy
from .forms import BookingForm, PaymentForm, BookingSearchForm, CancellationForm
from hotel.models import Room, Hotel


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Create new booking"""
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.room = get_object_or_404(Room, id=kwargs['room_id'])
        self.hotel = self.room.hotel
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['room'] = self.room
        
        # Pre-fill dates from GET parameters if provided
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        
        if check_in and check_out and 'data' not in kwargs:
            # Initialize with GET data
            from datetime import datetime
            try:
                ci = datetime.strptime(check_in, '%Y-%m-%d').date()
                co = datetime.strptime(check_out, '%Y-%m-%d').date()
                kwargs['initial'] = {
                    'check_in_date': ci,
                    'check_out_date': co,
                }
            except ValueError:
                # If date parsing fails, just ignore
                pass
        
        return kwargs
    
    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.room = self.room
        booking.hotel = self.hotel
        
        # Set pricing
        booking.room_price_per_night = self.room.get_price()
        booking.number_of_nights = (booking.check_out_date - booking.check_in_date).days
        booking.subtotal = Decimal(str(booking.room_price_per_night)) * booking.number_of_nights
        
        # Calculate tax (10%)
        booking.tax_amount = booking.subtotal * Decimal('0.10')
        booking.total_price = booking.subtotal + booking.tax_amount
        
        booking.status = 'pending'
        booking.save()
        
        # Update user profile
        from users.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        profile.total_bookings += 1
        profile.save()
        
        return redirect('booking:booking_detail', booking_id=booking.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self.room
        context['hotel'] = self.hotel
        
        # Calculate estimated prices
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        
        if check_in and check_out:
            from datetime import datetime
            try:
                ci = datetime.strptime(check_in, '%Y-%m-%d').date()
                co = datetime.strptime(check_out, '%Y-%m-%d').date()
                nights = (co - ci).days
                
                if nights > 0:
                    subtotal = Decimal(str(self.room.get_price())) * nights
                    tax = subtotal * Decimal('0.10')
                    total = subtotal + tax
                    
                    context['estimated_subtotal'] = subtotal
                    context['estimated_tax'] = tax
                    context['estimated_total'] = total
                    context['nights'] = nights
            except (ValueError, TypeError):
                # If date parsing fails, just skip price calculation
                pass
        
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """View booking details"""
    model = Booking
    template_name = 'booking/booking_detail.html'
    context_object_name = 'booking'
    
    def get_object(self):
        return get_object_or_404(Booking, id=self.kwargs['booking_id'], user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        
        context['room'] = booking.room
        context['hotel'] = booking.hotel
        context['can_cancel'] = booking.can_cancel()
        context['can_checkout'] = booking.status in ['confirmed', 'checked_in']
        context['can_checkin'] = booking.status == 'confirmed'
        
        # Check cancellation policy
        if booking.can_cancel():
            policies = booking.hotel.cancellation_policies.filter(is_active=True).order_by('-days_before_checkin')
            if policies.exists():
                refund_policy = None
                for policy in policies:
                    days_until = booking.get_days_until_checkin()
                    if days_until >= policy.days_before_checkin:
                        refund_policy = policy
                        break
                context['cancellation_policy'] = refund_policy
        
        return context


class BookingListView(LoginRequiredMixin, ListView):
    """List user's bookings"""
    model = Booking
    template_name = 'booking/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('hotel', 'room')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get booking stats
        context['total_bookings'] = self.get_queryset().count()
        context['confirmed_bookings'] = self.get_queryset().filter(status='confirmed').count()
        context['completed_bookings'] = self.get_queryset().filter(status='checked_out').count()
        
        return context


class PaymentView(LoginRequiredMixin, CreateView):
    """Process payment for booking"""
    model = Payment
    form_class = PaymentForm
    template_name = 'booking/payment.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(Booking, id=kwargs['booking_id'], user=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.booking = self.booking
        payment.amount = self.booking.total_price
        payment.payment_method = form.cleaned_data['payment_method']
        payment.transaction_id = f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        payment.status = 'completed'
        
        payment.save()
        
        # Update booking status
        self.booking.confirm_booking()
        
        messages.success(self.request, 'Payment processed successfully!')
        return redirect('booking:booking_detail', booking_id=self.booking.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.booking
        return context


def booking_checkin(request, booking_id):
    """Check in to a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'confirmed':
        booking.check_in()
        booking.room.status = 'occupied'
        booking.room.save()
        messages.success(request, 'Successfully checked in!')
    else:
        messages.error(request, 'Invalid booking status for check-in.')
    
    return redirect('booking:booking_detail', booking_id=booking.id)


def booking_checkout(request, booking_id):
    """Check out from a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status in ['confirmed', 'checked_in']:
        booking.check_out()
        booking.room.status = 'available'
        booking.room.save()
        messages.success(request, 'Successfully checked out!')
    else:
        messages.error(request, 'Invalid booking status for check-out.')
    
    return redirect('booking:booking_detail', booking_id=booking.id)


def booking_cancel(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.can_cancel():
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            
            # Calculate refund
            policies = booking.hotel.cancellation_policies.filter(is_active=True)
            refund_percentage = 0
            
            for policy in policies:
                if booking.get_days_until_checkin() >= policy.days_before_checkin:
                    refund_percentage = policy.refund_percentage
                    break
            
            refund_amount = booking.total_price * Decimal(str(refund_percentage)) / 100
            
            # Create refund payment
            Payment.objects.create(
                booking=booking,
                amount=refund_amount,
                payment_method='refund',
                transaction_id=f"REFUND{uuid.uuid4().hex[:10].upper()}",
                status='completed'
            )
            
            booking.save()
            messages.success(request, f'Booking cancelled. Refund amount: {refund_amount}')
            return redirect('booking:booking_list')
    else:
        form = CancellationForm()
    
    return render(request, 'booking/cancel_form.html', {
        'booking': booking,
        'form': form
    })


def booking_search(request):
    """Search for booking by ID or email"""
    form = BookingSearchForm()
    bookings = None
    
    if request.method == 'POST':
        form = BookingSearchForm(request.POST)
        if form.is_valid():
            booking_id = form.cleaned_data.get('booking_id')
            email = form.cleaned_data.get('email')
            
            if booking_id:
                bookings = Booking.objects.filter(booking_id=booking_id)
            elif email:
                bookings = Booking.objects.filter(guest_email=email)
    
    return render(request, 'booking/search.html', {
        'form': form,
        'bookings': bookings
    })
