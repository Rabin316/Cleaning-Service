from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Service, Booking, Testimonial, TeamMember
from .forms import BookingForm, ContactForm
from datetime import datetime

def home(request):
    """Home page view"""
    services = Service.objects.filter(is_active=True)[:6]
    testimonials = Testimonial.objects.filter(is_approved=True)[:3]
    team_members = TeamMember.objects.filter(is_active=True)[:4]
    
    context = {
        'services': services,
        'testimonials': testimonials,
        'team_members': team_members,
    }
    return render(request, 'cleaning/home.html', context)

def services(request):
    """Services listing page"""
    all_services = Service.objects.filter(is_active=True)
    context = {'services': all_services}
    return render(request, 'cleaning/services.html', context)

def service_detail(request, slug):
    """Individual service detail page"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(is_active=True).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'cleaning/service_detail.html', context)

def booking(request):
    """Booking page"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Enforce authenticated user's details when available
            if request.user.is_authenticated:
                booking.user = request.user
                booking.name = request.user.get_full_name() or request.user.username
                booking.email = request.user.email
                profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
                if profile and profile.phone:
                    booking.phone = profile.phone

            # In DEBUG mode, mark booking as paid and set amount from service for easy testing
            if settings.DEBUG:
                try:
                    if not booking.amount and booking.service:
                        booking.amount = booking.service.price_starting
                except Exception:
                    pass
                booking.payment_status = 'paid'

            booking.save()

            # Send confirmation email
            try:
                send_mail(
                    'Booking Confirmation - Clean Pro',
                    f'Thank you for booking with us! Your booking ID is {booking.id}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.email],
                    fail_silently=True,
                )
            except:
                pass

            messages.success(request, 'Your booking has been received! We will contact you shortly.')
            return redirect('booking_success')
    else:
        # Pre-fill form for authenticated users
        if request.user.is_authenticated:
            profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': getattr(profile, 'phone', ''),
            }
            form = BookingForm(initial=initial)
        else:
            form = BookingForm()
    
    services = Service.objects.filter(is_active=True)
    context = {
        'form': form,
        'services': services,
    }
    return render(request, 'cleaning/booking.html', context)

def booking_success(request):
    """Booking success page"""
    return render(request, 'cleaning/booking_success.html')

def about(request):
    """About page"""
    team_members = TeamMember.objects.filter(is_active=True)
    context = {'team_members': team_members}
    return render(request, 'cleaning/about.html', context)

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process contact form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            try:
                send_mail(
                    f'Contact Form: {subject}',
                    f'From: {name} ({email})\n\n{message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
                return redirect('contact')
            except:
                messages.error(request, 'There was an error sending your message. Please try again.')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'cleaning/contact.html', context)



# cleaning/customer_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import (
    Booking, CustomerProfile, SavedAddress, 
    FavoriteService, Notification, Service
)
from .forms import (
    CustomerRegistrationForm, CustomerLoginForm,
    ProfileUpdateForm, CustomerProfileForm,
    SavedAddressForm, BookingReviewForm, BookingForm
)
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.views.decorators.http import require_POST



# Authentication Views
def customer_register(request):
    """Customer registration"""
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created successfully.')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'cleaning/customer/register.html', {'form': form})


def customer_login(request):
    """Customer login"""
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'customer_dashboard')
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect(next_url)
    else:
        form = CustomerLoginForm()
    
    return render(request, 'cleaning/customer/login.html', {'form': form})


@login_required
def customer_logout(request):
    """Customer logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# Dashboard Views
@login_required
def customer_dashboard(request):
    """Customer dashboard overview"""
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    
    # Get bookings
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status__in=['pending', 'confirmed'],
        preferred_date__gte=timezone.now().date()
    ).select_related('service').order_by('preferred_date')[:5]
    
    recent_bookings = Booking.objects.filter(
        user=request.user
    ).select_related('service').order_by('-created_at')[:5]
    
    # Get statistics
    stats = {
        'total_bookings': Booking.objects.filter(user=request.user).count(),
        'upcoming_count': upcoming_bookings.count(),
        'completed_count': Booking.objects.filter(user=request.user, status='completed').count(),
        'total_spent': Booking.objects.filter(
            user=request.user, 
            payment_status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Get favorite services
    favorite_services = FavoriteService.objects.filter(
        user=request.user
    ).select_related('service')[:4]
    
    context = {
        'profile': profile,
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,
        'stats': stats,
        'notifications': unread_notifications,
        'favorite_services': favorite_services,
    }
    
    return render(request, 'cleaning/customer/dashboard.html', context)


@login_required
def customer_bookings(request):
    """View all customer bookings"""
    status_filter = request.GET.get('status', 'all')
    
    bookings = Booking.objects.filter(user=request.user).select_related('service')
    
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    # Separate into categories
    upcoming = bookings.filter(
        status__in=['pending', 'confirmed'],
        preferred_date__gte=timezone.now().date()
    ).order_by('preferred_date')
    
    past = bookings.filter(
        Q(status='completed') | Q(status='cancelled') |
        Q(preferred_date__lt=timezone.now().date())
    ).order_by('-preferred_date')
    
    context = {
        'upcoming_bookings': upcoming,
        'past_bookings': past,
        'status_filter': status_filter,
    }
    
    return render(request, 'cleaning/customer/bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """View individual booking details"""
    booking = get_object_or_404(
        Booking.objects.select_related('service', 'assigned_to'),
        id=booking_id,
        user=request.user
    )
    
    # Handle review submission
    if request.method == 'POST' and booking.status == 'completed':
        review_form = BookingReviewForm(request.POST, instance=booking)
        if review_form.is_valid():
            review_form.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        review_form = BookingReviewForm(instance=booking)
    
    context = {
        'booking': booking,
        'review_form': review_form,
        'can_cancel': booking.status in ['pending', 'confirmed'] and booking.preferred_date >= timezone.now().date(),
        'can_review': booking.status == 'completed' and not booking.customer_rating,
    }
    
    return render(request, 'cleaning/customer/booking_detail.html', context)


@login_required
@require_POST
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if booking can be cancelled
    days_until = (booking.preferred_date - timezone.now().date()).days
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
    elif days_until < 1:
        messages.error(request, 'Bookings cannot be cancelled less than 24 hours before the scheduled time.')
    else:
        booking.status = 'cancelled'
        booking.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            title='Booking Cancelled',
            message=f'Your booking for {booking.service.name} on {booking.preferred_date} has been cancelled.',
            notification_type='booking'
        )
        
        messages.success(request, 'Your booking has been cancelled successfully.')
    
    return redirect('booking_detail', booking_id=booking.id)


@login_required
@require_POST
def rebook(request, booking_id):
    """Rebook a previous service"""
    old_booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Pre-fill booking form with old booking data
    request.session['rebook_data'] = {
        'service': old_booking.service.id,
        'address': old_booking.address,
        'special_instructions': old_booking.special_instructions,
        'frequency': old_booking.frequency,
    }
    
    messages.info(request, 'Please select a new date and time for your booking.')
    return redirect('booking')


# Profile Management
@login_required
def customer_profile(request):
    """View and edit customer profile"""
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('customer_profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    
    return render(request, 'cleaning/customer/profile.html', context)


# Saved Addresses
@login_required
def saved_addresses(request):
    """Manage saved addresses"""
    addresses = SavedAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        form = SavedAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address saved successfully!')
            return redirect('saved_addresses')
    else:
        form = SavedAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    
    return render(request, 'cleaning/customer/addresses.html', context)


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete a saved address"""
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('saved_addresses')


@login_required
@require_POST
@login_required
@require_POST
def set_default_address(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    SavedAddress.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated.')
    return redirect('saved_addresses')


# Favorite Services
@login_required
def favorite_services(request):
    """View favorite services"""
    favorites = FavoriteService.objects.filter(
        user=request.user
    ).select_related('service')
    
    context = {'favorites': favorites}
    return render(request, 'cleaning/customer/favorites.html', context)


@login_required
@require_POST
def toggle_favorite(request, service_id):
    """Add or remove service from favorites"""
    service = get_object_or_404(Service, id=service_id)
    favorite, created = FavoriteService.objects.get_or_create(
        user=request.user,
        service=service
    )
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from favorites'})
    else:
        return JsonResponse({'status': 'added', 'message': 'Added to favorites'})


# Notifications
@login_required
def notifications(request):
    """View all notifications"""
    all_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Mark as read when viewed
    all_notifications.filter(is_read=False).update(is_read=True)
    
    context = {'notifications': all_notifications}
    return render(request, 'cleaning/customer/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'status': 'success'})




# Payment History
@login_required
def payment_history(request):
    """View payment history"""
    payments = Booking.objects.filter(
        user=request.user,
        payment_status='paid'
    ).select_related('service').order_by('-created_at')
    
    total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': payments,
        'total_paid': total_paid,
    }
    
    return render(request, 'cleaning/customer/payments.html', context)


# Quick Booking (for logged-in users)
@login_required
def quick_booking(request, service_id):
    """Quick booking with pre-filled information"""
    service = get_object_or_404(Service, id=service_id)
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    default_address = SavedAddress.objects.filter(user=request.user, is_default=True).first()
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.name = request.user.get_full_name()
            booking.email = request.user.email
            booking.phone = profile.phone
            booking.save()
            
            # Update profile stats
            profile.total_bookings += 1
            profile.save()
            
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        initial_data = {
            'service': service,
            'name': request.user.get_full_name(),
            'email': request.user.email,
            'phone': profile.phone,
        }
        
        if default_address:
            initial_data['address'] = f"{default_address.address}, {default_address.city}, {default_address.state} {default_address.zip_code}"
        
        form = BookingForm(initial=initial_data)
    
    context = {
        'form': form,
        'service': service,
    }
    
    return render(request, 'cleaning/customer/quick_booking.html', context)