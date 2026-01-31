from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (UserRegistrationForm, UserLoginForm, UserProfileForm, 
                   ChangePasswordForm, NotificationPreferenceForm)
from .models import UserProfile, NotificationPreference
from booking.models import Booking


class UserRegistrationView(CreateView):
    """Register new user"""
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        
        # Create user profile
        UserProfile.objects.get_or_create(user=user)
        
        # Create notification preferences
        NotificationPreference.objects.get_or_create(user=user)
        
        messages.success(self.request, 'Account created successfully! Please login.')
        return response


class UserLoginView(LoginView):
    """Login user"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('hotel:home')


class UserLogoutView(LogoutView):
    """Logout user"""
    next_page = reverse_lazy('hotel:home')


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        profile = form.save()
        
        # Update user info
        user = self.request.user
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


def dashboard(request):
    """User dashboard"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    profile = request.user.profile
    recent_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]
    stats = {
        'total_bookings': profile.total_bookings,
        'loyalty_points': profile.loyalty_points,
        'upcoming_bookings': Booking.objects.filter(
            user=request.user,
            status__in=['pending', 'confirmed'],
            check_in_date__gte=timezone.now().date()
        ).count(),
        'completed_bookings': Booking.objects.filter(
            user=request.user,
            status='checked_out'
        ).count(),
    }
    
    return render(request, 'users/dashboard.html', {
        'profile': profile,
        'recent_bookings': recent_bookings,
        'stats': stats
    })


def change_password(request):
    """Change user password"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(form.cleaned_data['old_password']):
                messages.error(request, 'Current password is incorrect.')
            else:
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('users:profile')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'users/change_password.html', {'form': form})


def notification_preferences(request):
    """Manage notification preferences"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    pref, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=pref)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated!')
            return redirect('users:profile')
    else:
        form = NotificationPreferenceForm(instance=pref)
    
    return render(request, 'users/notification_preferences.html', {'form': form})


def user_account(request):
    """User account settings"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    return render(request, 'users/account.html', {
        'user': request.user,
        'profile': request.user.profile
    })
