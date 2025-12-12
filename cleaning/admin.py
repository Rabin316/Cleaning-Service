from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from .models import Service, Booking, Testimonial, TeamMember

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_starting', 'duration', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'preferred_date', 'preferred_time', 
                    'frequency', 'status', 'created_at']
    list_filter = ['status', 'frequency', 'preferred_date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'address']
    list_editable = ['status']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Service Details', {
            'fields': ('service', 'frequency', 'preferred_date', 'preferred_time')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['name', 'content']
    list_editable = ['is_approved']
    ordering = ['-created_at']

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'position', 'bio']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'name']