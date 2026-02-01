from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import uuid

from .models import Booking, Payment, CancellationPolicy
from .forms import BookingForm, PaymentForm, BookingSearchForm, CancellationForm
from .ssl_commerz import SSLCommerczPaymentGateway
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
    
    def post(self, request, *args, **kwargs):
        """Handle POST request"""
        print(f"POST Data: {request.POST}")
        print(f"Payment method: {request.POST.get('payment_method')}")
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form):
        """Handle form invalid"""
        print(f"Form Invalid - Errors: {form.errors}")
        print(f"Non-field errors: {form.non_field_errors()}")
        return self.render_to_response(self.get_context_data(form=form))
    
    def form_valid(self, form):
        payment_method = form.cleaned_data.get('payment_method')
        print(f"Form Valid - Payment Method: {payment_method}")
        
        # If SSL Commerz is selected, redirect to payment gateway
        if payment_method == 'sslcommerz':  # Note: the value is 'sslcommerz', not 'ssl_commerz'
            print("SSL Commerz method selected")
            try:
                gateway = SSLCommerczPaymentGateway()
                response = gateway.init_payment(self.booking, self.request)
                
                # Debug: Print response
                import json
                print(f"SSL Commerz Response: {json.dumps(response, indent=2, default=str) if isinstance(response, dict) else response}")
                
                # Check if response has success status
                status = response.get('status') if isinstance(response, dict) else None
                
                # Get gateway URL - try multiple possible key names
                gateway_url = None
                if isinstance(response, dict):
                    gateway_url = (response.get('GatewayPageURL') or 
                                 response.get('redirectGatewayURL') or
                                 response.get('gatewayPageURL') or
                                 response.get('redirect_url') or
                                 response.get('redirect_gateway_url'))
                
                print(f"Gateway URL: {gateway_url}")
                print(f"Response status: {status}")
                
                # Check for success - status could be 'success', 'SUCCESS', etc.
                is_success = status and str(status).upper() == 'SUCCESS'
                
                if is_success and gateway_url:
                    print(f"✓ Gateway URL found: {gateway_url}")
                    # Save payment record as pending
                    Payment.objects.create(
                        booking=self.booking,
                        amount=self.booking.total_price,
                        payment_method=payment_method,
                        transaction_id=response.get('sessionkey', response.get('session_id', '')),
                        status='pending'
                    )
                    # Redirect to SSL Commerz payment page
                    return redirect(gateway_url)
                else:
                    error_msg = response.get('failedreason') or response.get('message') or 'Failed to initialize payment. Please check credentials.'
                    print(f"✗ SSL Commerz failed: {error_msg}")
                    messages.error(self.request, f'Payment initialization failed: {error_msg}')
                    return redirect('booking:payment', booking_id=self.booking.id)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"✗ Payment Exception: {error_trace}")
                messages.error(self.request, f'Payment error: {str(e)}')
                return redirect('booking:payment', booking_id=self.booking.id)
        
        # For other payment methods, process locally
        print(f"Processing payment method: {payment_method}")
        payment = form.save(commit=False)
        payment.booking = self.booking
        payment.amount = self.booking.total_price
        payment.payment_method = payment_method
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


@csrf_exempt
def payment_success(request):
    """SSL Commerz payment success callback"""
    try:
        # Get payment data
        data = request.POST
        
        print(f"\n{'='*80}")
        print(f"Payment Success Callback Data:")
        print(f"{'='*80}")
        print(f"All POST data: {dict(data)}")
        print(f"Callback Keys: {list(data.keys())}")
        
        # Get session key (transaction ID from SSL Commerz)
        session_key = data.get('sessionkey') or data.get('SESSIONKEY') or data.get('session_key')
        print(f"Session Key: {session_key}")
        
        # Get various order/transaction identifiers
        tran_id = data.get('tran_id') or data.get('TRAN_ID') or data.get('tranId')
        order_num = data.get('order_num') or data.get('order_number') or data.get('ORDER_NUM') or data.get('orderNum')
        val_id = data.get('val_id') or data.get('VAL_ID')
        
        print(f"Tran ID: {tran_id}")
        print(f"Order Num: {order_num}")
        print(f"Val ID: {val_id}")
        
        booking = None
        payment = None
        
        # Strategy 1: Try to find payment by session key
        if session_key:
            try:
                payment = Payment.objects.get(transaction_id=session_key)
                booking = payment.booking
                print(f"[SUCCESS] Found payment by session_key: {payment.id}, Booking: {booking.booking_id}")
            except Payment.DoesNotExist:
                print(f"[FALLBACK] No payment found with session_key: {session_key}")
        
        # Strategy 2: Try to find payment by tran_id
        if not payment and tran_id:
            try:
                payment = Payment.objects.get(transaction_id=tran_id)
                booking = payment.booking
                print(f"[SUCCESS] Found payment by tran_id: {payment.id}, Booking: {booking.booking_id}")
            except Payment.DoesNotExist:
                print(f"[FALLBACK] No payment found with tran_id: {tran_id}")
        
        # Strategy 3: Try to find booking by order_num
        if not booking and order_num:
            try:
                booking = Booking.objects.get(booking_id=order_num)
                print(f"[SUCCESS] Found booking by order_num: {booking.booking_id}")
                
                # Try to find or create payment
                if not payment:
                    try:
                        payment = Payment.objects.get(booking=booking, status='pending')
                        print(f"[SUCCESS] Found pending payment for booking: {payment.id}")
                    except Payment.DoesNotExist:
                        # Create payment record
                        payment = Payment.objects.create(
                            booking=booking,
                            amount=booking.total_price,
                            payment_method='sslcommerz',
                            transaction_id=session_key or tran_id or val_id or order_num,
                            status='pending'
                        )
                        print(f"[CREATED] New payment record: {payment.id}")
            except Booking.DoesNotExist:
                print(f"[FALLBACK] No booking found with order_num: {order_num}")
        
        # Strategy 4: Check if there's a recent pending payment (last resort)
        if not payment and not booking:
            try:
                # Get the most recent pending payment for sslcommerz
                payment = Payment.objects.filter(
                    payment_method='sslcommerz',
                    status='pending'
                ).order_by('-created_at').first()
                
                if payment:
                    booking = payment.booking
                    print(f"[FALLBACK] Found recent pending payment: {payment.id}, Booking: {booking.booking_id}")
                else:
                    print(f"[FALLBACK] No pending sslcommerz payments found")
            except Exception as e:
                print(f"[ERROR] Error checking recent payments: {e}")
        
        # If we still don't have booking info, log more details and fail
        if not booking or not payment:
            print(f"[CRITICAL] Could not find booking information!")
            print(f"Payment: {payment}")
            print(f"Booking: {booking}")
            print(f"Callback data keys: {list(data.keys())}")
            print(f"Callback data: {dict(data)}")
            
            messages.error(request, 'Could not find booking information in payment response. Please contact support.')
            return redirect('booking:booking_list')
        
        # Validate the payment with SSL Commerz
        print(f"\nValidating payment with SSL Commerz...")
        gateway = SSLCommerczPaymentGateway()
        validation_response = gateway.validate_response(data)
        print(f"Validation Response: {validation_response}")
        
        # Check validation status
        validation_status = validation_response.get('status')
        if validation_status and str(validation_status).upper() in ['TRUE', 'VALID', 'SUCCESS']:
            print(f"[VALID] Payment validation successful")
            
            # Update payment status to completed
            payment.status = 'completed'
            payment.transaction_id = session_key or tran_id or val_id or payment.transaction_id
            payment.save()
            print(f"[SAVED] Payment status updated to completed")
            
            # Confirm booking
            booking.confirm_booking()
            print(f"[CONFIRMED] Booking confirmed")
            
            messages.success(request, 'Payment successful! Your booking is confirmed.')
            print(f"[COMPLETE] Payment completed for booking: {booking.booking_id}")
            print(f"{'='*80}\n")
            return redirect('booking:booking_detail', booking_id=booking.id)
        else:
            error_msg = validation_response.get('message', 'Payment validation failed.')
            print(f"[INVALID] Validation failed: {error_msg}")
            messages.error(request, f'Payment validation error: {error_msg}')
            print(f"{'='*80}\n")
            return redirect('booking:booking_list')
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[EXCEPTION] Payment Success Exception:")
        print(error_trace)
        print(f"{'='*80}\n")
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('booking:booking_list')


@csrf_exempt
def payment_failed(request):
    """SSL Commerz payment failure callback"""
    try:
        data = request.POST
        print(f"Payment Failed Callback Data: {dict(data)}")
        
        # Get session key or order number
        session_key = data.get('sessionkey') or data.get('SESSIONKEY')
        order_num = data.get('order_num') or data.get('order_number')
        
        # Try to find payment by session key first
        booking = None
        try:
            payment = Payment.objects.get(transaction_id=session_key)
            booking = payment.booking
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            # Try to find by order number
            if order_num:
                try:
                    booking = Booking.objects.get(booking_id=order_num)
                    Payment.objects.filter(booking=booking, status='pending').update(status='failed')
                except Booking.DoesNotExist:
                    print(f"Booking not found: {order_num}")
            else:
                print(f"No session key or order number in callback")
        
        if booking:
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('booking:payment', booking_id=booking.id)
        else:
            messages.error(request, 'Payment failed. Could not find booking information.')
            return redirect('booking:booking_list')
    except Exception as e:
        print(f"Payment Failed Exception: {str(e)}")
        messages.error(request, 'Error processing payment failure.')
        return redirect('booking:booking_list')


@csrf_exempt
def payment_cancelled(request):
    """SSL Commerz payment cancelled callback"""
    try:
        data = request.POST
        print(f"Payment Cancelled Callback Data: {dict(data)}")
        
        # Get session key or order number
        session_key = data.get('sessionkey') or data.get('SESSIONKEY')
        order_num = data.get('order_num') or data.get('order_number')
        
        # Try to find payment by session key first
        booking = None
        try:
            payment = Payment.objects.get(transaction_id=session_key)
            booking = payment.booking
            payment.status = 'failed'  # Mark as failed when cancelled
            payment.save()
        except Payment.DoesNotExist:
            # Try to find by order number
            if order_num:
                try:
                    booking = Booking.objects.get(booking_id=order_num)
                    Payment.objects.filter(booking=booking, status='pending').update(status='failed')
                except Booking.DoesNotExist:
                    print(f"Booking not found: {order_num}")
            else:
                print(f"No session key or order number in callback")
        
        if booking:
            messages.warning(request, 'Payment cancelled. You can retry payment anytime.')
            return redirect('booking:payment', booking_id=booking.id)
        else:
            messages.warning(request, 'Payment cancelled.')
            return redirect('booking:booking_list')
    except Exception as e:
        print(f"Payment Cancelled Exception: {str(e)}")
        messages.error(request, 'Error processing payment cancellation.')
        return redirect('booking:booking_list')
