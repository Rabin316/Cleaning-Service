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
            booking = form.save()
            
            # Send confirmation email
            try:
                send_mail(
                    'Booking Confirmation - Clean Pro Services',
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