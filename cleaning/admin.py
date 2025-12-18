# cleaning/admin.py - Complete admin configuration

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe

# Import all models
from .models import (
    Service, Booking, Testimonial, TeamMember,
    CustomerProfile, SavedAddress, FavoriteService, Notification
)

# First, unregister any existing registrations to avoid conflicts
try:
    admin.site.unregister(Service)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Booking)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Testimonial)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(TeamMember)
except admin.sites.NotRegistered:
    pass

# Inline admin for CustomerProfile
class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fields = [
        'phone', 'address', 'city', 'state', 'zip_code',
        'preferred_time', 'email_notifications', 'sms_notifications',
        'total_bookings', 'total_spent'
    ]
    readonly_fields = ['total_bookings', 'total_spent']


# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_total_bookings']
    
    def get_total_bookings(self, obj):
        if hasattr(obj, 'customer_profile'):
            return obj.customer_profile.total_bookings
        return 0
    get_total_bookings.short_description = 'Total Bookings'

# Unregister the original User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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
    list_display = [
        'id', 'user', 'name', 'service', 'preferred_date', 
        'preferred_time', 'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'frequency', 'preferred_date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'address', 'user__username']
    list_editable = ['status']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'name', 'email', 'phone', 'address')
        }),
        ('Service Details', {
            'fields': ('service', 'frequency', 'preferred_date', 'preferred_time')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'status', 'assigned_to')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_intent_id', 'amount')
        }),
        ('Review', {
            'fields': ('customer_rating', 'customer_review'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected bookings as confirmed'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected bookings as completed'


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'phone', 'city', 'state', 
        'total_bookings', 'total_spent'
    ]
    list_filter = ['preferred_time', 'email_notifications', 'sms_notifications']
    search_fields = ['user__username', 'user__email', 'phone', 'address', 'city']
    readonly_fields = ['total_bookings', 'total_spent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'state', 'zip_code')
        }),
        ('Preferences', {
            'fields': ('preferred_time', 'special_instructions', 'email_notifications', 'sms_notifications')
        }),
        ('Stats', {
                'fields': ('total_bookings', 'total_spent'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('profile_picture', 'date_of_birth', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'state', 'is_default', 'created_at']
    list_filter = ['is_default', 'state', 'created_at']
    search_fields = ['user__username', 'label', 'address', 'city']
    list_editable = ['is_default']


@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'added_at']
    list_filter = ['service', 'added_at']
    search_fields = ['user__username', 'service__name']
    date_hierarchy = 'added_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'


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


# Customize admin site
admin.site.site_header = 'Clean Pro Administration'
admin.site.site_title = 'Clean Pro Admin'
admin.site.index_title = 'Welcome to Clean Pro Admin Panel'