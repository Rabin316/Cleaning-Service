from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.utils.text import slugify

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
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time')
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.service.name} - {self.preferred_date}"
    
    class Meta:
        ordering = ['-created_at']

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