from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account/', views.user_account, name='account'),
    
    # Password
    path('change-password/', views.change_password, name='change_password'),
    
    # Preferences
    path('notification-preferences/', views.notification_preferences, name='notification_preferences'),
]
