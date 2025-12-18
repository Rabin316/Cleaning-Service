# cleaning/models.py - Complete models file

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models import Sum
from decimal import Decimal


# ============================================
# CUSTOMER PROFILE & RELATED MODELS
# ============================================

class CustomerProfile(models.Model):
    """Extended user profile for customers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Preferences
    preferred_time = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'Morning (8AM-12PM)'),
            ('afternoon', 'Afternoon (12PM-5PM)'),
            ('evening', 'Evening (5PM-8PM)'),
        ],
        blank=True
    )
    special_instructions = models.TextField(blank=True, help_text="Any special cleaning requirements")
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    # Loyalty
    total_bookings = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email}"
    


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        CustomerProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()


class SavedAddress(models.Model):
    """Saved addresses for quick booking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_addresses')
    label = models.CharField(max_length=50, help_text="e.g., Home, Office")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Saved Addresses"
    
    def __str__(self):
        return f"{self.user.username} - {self.label}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses to non-default
            SavedAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Notification(models.Model):
    """In-app notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('booking', 'Booking Update'),
            ('promotion', 'Promotion'),
            ('reminder', 'Reminder'),
            ('system', 'System'),
        ]
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ============================================
# SERVICE MODELS
# ============================================

class Service(models.Model):
    """Service model for different cleaning services"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    price_starting = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100, help_text="e.g., 2-3 hours")
    icon = models.CharField(max_length=100, default="fa-broom", help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    features = models.TextField(help_text="One feature per line")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class FavoriteService(models.Model):
    """User's favorite services for quick booking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'service']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name}"


# ============================================
# TEAM MEMBER MODEL
# ============================================

class TeamMember(models.Model):
    """Team members"""
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    
    class Meta:
        ordering = ['order', 'name']


# ============================================
# BOOKING MODEL
# ============================================

class Booking(models.Model):
    """Booking model for service appointments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FREQUENCY_CHOICES = [
        ('one_time', 'One Time'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    # Link to user (for authenticated customers)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    
    # Service and basic info
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Scheduling
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time')
    
    # Additional info
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    payment_intent_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Ratings & Review
    customer_rating = models.IntegerField(
        null=True, 
        blank=True,
        choices=[(i, i) for i in range(1, 6)]
    )
    customer_review = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        TeamMember, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_bookings'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.service.name} - {self.preferred_date}"
    
    class Meta:
        ordering = ['-created_at']


# ============================================
# TESTIMONIAL MODEL
# ============================================

# LoyaltyRedemption model removed


class Testimonial(models.Model):
    """Customer testimonials"""
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']


# Keep CustomerProfile totals in sync with bookings
@receiver([post_save, post_delete], sender=Booking)
def update_customer_profile_totals(sender, instance, **kwargs):
    user = instance.user
    if not user:
        return
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    total_bookings = Booking.objects.filter(user=user).count()
    total_spent_agg = Booking.objects.filter(user=user, payment_status='paid').aggregate(Sum('amount'))
    total_spent = total_spent_agg['amount__sum'] or Decimal('0')

    profile.total_bookings = total_bookings
    profile.total_spent = total_spent
    # Loyalty points removed; no calculations
    profile.save()