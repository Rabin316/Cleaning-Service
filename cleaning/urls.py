# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('booking/', views.booking, name='booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    
    # Customer Dashboard
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/bookings/', views.customer_bookings, name='customer_bookings'),
    path('dashboard/booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('dashboard/booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('dashboard/booking/<int:booking_id>/rebook/', views.rebook, name='rebook'),
    
    # Profile Management
    path('dashboard/profile/', views.customer_profile, name='customer_profile'),
    
    # Addresses
    path('dashboard/addresses/', views.saved_addresses, name='saved_addresses'),
    path('dashboard/addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('dashboard/addresses/<int:address_id>/set-default/', views.set_default_address, name='set_default_address'),
    
    # Favorites
    path('dashboard/favorites/', views.favorite_services, name='favorite_services'),
    path('services/<int:service_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Notifications
    path('dashboard/notifications/', views.notifications, name='notifications'),
    path('dashboard/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('dashboard/notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # Payments
    path('dashboard/payments/', views.payment_history, name='payment_history'),
    
    # Quick Booking
    path('quick-booking/<int:service_id>/', views.quick_booking, name='quick_booking'),
]