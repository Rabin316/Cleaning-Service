"""
Cleaning Service Admin - Production-Ready Admin Dashboard

This module provides a comprehensive admin interface for managing:
- Bookings (with team assignment, status tracking, bulk operations)
- Team Members (availability, assignments, performance)
- Services (pricing, scheduling, add-ons)
- Customers (profiles, history, communication)
- Reporting & Analytics
"""

import csv
import json
from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Service,
    Booking,
    Testimonial,
    TeamMember,
    CustomerProfile,
    SavedAddress,
    FavoriteService,
    Notification,
)


# ============================================
# FORMS
# ============================================

class BulkAssignTeamForm(forms.Form):
    """Form for bulk assigning team members to bookings."""

    team_member = forms.ModelChoiceField(
        queryset=TeamMember.objects.filter(is_active=True),
        required=True,
        label="Assign to Team Member",
    )

    send_notification = forms.BooleanField(
        required=False,
        initial=True,
        label="Send notification to team member",
    )


class BookingStatusForm(forms.Form):
    """Form for bulk status updates."""

    STATUS_CHOICES = Booking.STATUS_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
    )

    send_notification = forms.BooleanField(
        required=False,
        initial=True,
    )


# ============================================
# INLINE ADMINS
# ============================================

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = "Customer Profile"

    fields = [
        "phone",
        "address",
        "city",
        "state",
        "zip_code",
        "preferred_time",
        "email_notifications",
        "sms_notifications",
        "total_bookings",
        "total_spent",
    ]

    readonly_fields = [
        "total_bookings",
        "total_spent",
        "created_at",
        "updated_at",
    ]


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0

    readonly_fields = [
        "id",
        "service",
        "preferred_date",
        "preferred_time",
        "status",
        "payment_status",
        "amount",
        "created_at",
    ]

    fields = [
        "id",
        "service",
        "preferred_date",
        "preferred_time",
        "status",
        "payment_status",
        "amount",
    ]

    ordering = ["-preferred_date"]
    can_delete = False
    max_num = 0


# ============================================
# CUSTOM USER ADMIN
# ============================================

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerProfileInline,)

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_total_bookings",
        "get_is_customer",
    ]

    list_filter = [
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "date_joined",
    ]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "customer_profile__phone",
    ]

    ordering = ["-date_joined"]

    def get_total_bookings(self, obj):
        if hasattr(obj, "customer_profile"):
            return obj.customer_profile.total_bookings
        return 0

    get_total_bookings.short_description = "Total Bookings"
    get_total_bookings.admin_order_field = "customer_profile__total_bookings"

    def get_is_customer(self, obj):
        return hasattr(obj, "customer_profile")

    get_is_customer.boolean = True
    get_is_customer.short_description = "Is Customer"


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)


# ============================================
# SERVICE ADMIN
# ============================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "price_starting",
        "duration",
        "get_bookings_count",
        "get_revenue",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "is_active",
        "created_at",
    ]

    search_fields = [
        "name",
        "description",
        "short_description",
    ]

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = [
        "is_active",
        "price_starting",
    ]

    ordering = ["name"]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "short_description",
                    "icon",
                    "image",
                )
            },
        ),
        (
            "Pricing & Duration",
            {
                "fields": (
                    "price_starting",
                    "duration",
                    "features",
                )
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_bookings_count(self, obj):
        return obj.booking_set.count()

    get_bookings_count.short_description = "Total Bookings"

    def get_revenue(self, obj):
        total = (
            obj.booking_set
            .filter(payment_status="paid")
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        return f"${total:,.2f}"

    get_revenue.short_description = "Revenue (Paid)"


# ============================================
# TEAM MEMBER ADMIN
# ============================================

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "position",
        "get_assigned_count",
        "get_upcoming_count",
        "is_active",
        "order",
        "get_quick_actions",
    ]

    list_filter = [
        "is_active",
        "position",
    ]

    search_fields = [
        "name",
        "position",
        "bio",
        "email",
        "phone",
    ]

    list_editable = [
        "is_active",
        "order",
    ]

    ordering = [
        "order",
        "name",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "position",
                    "bio",
                    "image",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "is_active",
                    "order",
                )
            },
        ),
    )

    def get_assigned_count(self, obj):
        count = obj.assigned_bookings.count()

        url = (
            reverse("admin:cleaning_booking_changelist")
            + f"?assigned_to__id={obj.id}"
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            count,
        )

    get_assigned_count.short_description = "Total Assigned"

    def get_upcoming_count(self, obj):
        today = timezone.now().date()

        count = obj.assigned_bookings.filter(
            status__in=["pending", "confirmed"],
            preferred_date__gte=today,
        ).count()

        url = (
            reverse("admin:cleaning_booking_changelist")
            + f"?assigned_to__id={obj.id}"
            + f"&status__in=pending,confirmed"
            + f"&preferred_date__gte={today}"
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            count,
        )

    get_upcoming_count.short_description = "Upcoming Jobs"

    def get_quick_actions(self, obj):
        url = (
            reverse("admin:cleaning_booking_changelist")
            + f"?assigned_to__id={obj.id}"
        )

        return format_html(
            '<a class="button" href="{}">View Jobs</a>',
            url,
        )

    get_quick_actions.short_description = "Actions"


# ============================================
# BOOKING ADMIN
# ============================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    # IMPORTANT:
    # "status" must be directly inside list_display
    # because it is used in list_editable.
    list_display = [
        "id",
        "get_customer_link",
        "service",
        "preferred_date",
        "preferred_time",
        "frequency",
        "status",
        "get_payment_badge",
        "assigned_to",
        "amount",
        "created_at",
    ]

    list_filter = [
        "status",
        "payment_status",
        "frequency",
        "preferred_date",
        "created_at",
        "service",
        "assigned_to",
    ]

    search_fields = [
        "name",
        "email",
        "phone",
        "address",
        "user__username",
        "user__email",
        "service__name",
        "payment_intent_id",
        "special_instructions",
    ]

    list_editable = [
        "status",
        "assigned_to",
    ]

    ordering = [
        "-created_at",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "payment_intent_id",
    ]

    date_hierarchy = "preferred_date"

    list_per_page = 50

    actions = [
        "mark_as_confirmed",
        "mark_as_completed",
        "mark_as_cancelled",
        "assign_team_member",
        "send_reminder_emails",
        "export_selected_bookings",
    ]

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "user",
                    "name",
                    "email",
                    "phone",
                    "address",
                )
            },
        ),
        (
            "Service Details",
            {
                "fields": (
                    "service",
                    "frequency",
                    "preferred_date",
                    "preferred_time",
                )
            },
        ),
        (
            "Assignment & Status",
            {
                "fields": (
                    "special_instructions",
                    "status",
                    "assigned_to",
                )
            },
        ),
        (
            "Payment",
            {
                "fields": (
                    "payment_status",
                    "payment_intent_id",
                    "amount",
                )
            },
        ),
        (
            "Review",
            {
                "fields": (
                    "customer_rating",
                    "customer_review",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    change_form_template = (
        "admin/cleaning/booking/change_form.html"
    )

    def get_customer_link(self, obj):
        if obj.user:
            url = reverse(
                "admin:auth_user_change",
                args=[obj.user.id],
            )

            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.name,
                obj.user.username,
            )

        return obj.name

    get_customer_link.short_description = "Customer"
    get_customer_link.admin_order_field = "name"

    def get_status_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "confirmed": "#17a2b8",
            "completed": "#28a745",
            "cancelled": "#dc3545",
        }

        color = colors.get(
            obj.status,
            "#6c757d",
        )

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 12px; '
            'font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    get_status_badge.short_description = "Status"
    get_status_badge.admin_order_field = "status"

    def get_payment_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "paid": "#28a745",
            "failed": "#dc3545",
            "refunded": "#6c757d",
        }

        color = colors.get(
            obj.payment_status,
            "#6c757d",
        )

        amount = (
            f" ${obj.amount}"
            if obj.amount
            else ""
        )

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 12px; '
            'font-size: 11px; font-weight: bold;">{}{}</span>',
            color,
            obj.get_payment_status_display(),
            amount,
        )

    get_payment_badge.short_description = "Payment"
    get_payment_badge.admin_order_field = "payment_status"

    # ========================================
    # CUSTOM ACTIONS
    # ========================================

    @admin.action(
        description="Mark selected bookings as confirmed"
    )
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(
            status="confirmed"
        )

        self.message_user(
            request,
            f"{updated} booking(s) marked as confirmed.",
        )

        for booking in queryset.filter(
            user__isnull=False
        ):
            Notification.objects.create(
                user=booking.user,
                title="Booking Confirmed",
                message=(
                    f"Your booking for "
                    f"{booking.service.name} on "
                    f"{booking.preferred_date} has been confirmed."
                ),
                notification_type="booking",
                link=reverse(
                    "booking_detail",
                    args=[booking.id],
                ),
            )

    @admin.action(
        description="Mark selected bookings as completed"
    )
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(
            status="completed"
        )

        self.message_user(
            request,
            f"{updated} booking(s) marked as completed.",
        )

    @admin.action(
        description="Mark selected bookings as cancelled"
    )
    def mark_as_cancelled(self, request, queryset):

        cancellable = queryset.filter(
            status__in=[
                "pending",
                "confirmed",
            ]
        )

        updated = cancellable.update(
            status="cancelled"
        )

        self.message_user(
            request,
            f"{updated} booking(s) marked as cancelled.",
        )

        for booking in cancellable.filter(
            user__isnull=False
        ):
            Notification.objects.create(
                user=booking.user,
                title="Booking Cancelled",
                message=(
                    f"Your booking for "
                    f"{booking.service.name} on "
                    f"{booking.preferred_date} has been cancelled."
                ),
                notification_type="booking",
            )

    @admin.action(
        description="Assign team member to selected bookings"
    )
    def assign_team_member(self, request, queryset):

        if "apply" in request.POST:
            form = BulkAssignTeamForm(
                request.POST
            )

            if form.is_valid():

                team_member = (
                    form.cleaned_data["team_member"]
                )

                send_notification = (
                    form.cleaned_data[
                        "send_notification"
                    ]
                )

                updated = queryset.update(
                    assigned_to=team_member
                )

                if send_notification:

                    for booking in queryset.filter(
                        user__isnull=False
                    ):
                        Notification.objects.create(
                            user=booking.user,
                            title="Team Assigned",
                            message=(
                                f"{team_member.name} has been assigned "
                                f"to your {booking.service.name} "
                                f"booking on {booking.preferred_date}."
                            ),
                            notification_type="booking",
                            link=reverse(
                                "booking_detail",
                                args=[booking.id],
                            ),
                        )

                self.message_user(
                    request,
                    f"{updated} booking(s) assigned to "
                    f"{team_member.name}.",
                )

                return HttpResponseRedirect(
                    request.get_full_path()
                )

        else:
            form = BulkAssignTeamForm()

        return render(
            request,
            "admin/cleaning/booking/bulk_assign.html",
            {
                "form": form,
                "bookings": queryset,
                "title": "Assign Team Member",
                "action_checkbox_name": (
                    admin.ACTION_CHECKBOX_NAME
                ),
            },
        )

    @admin.action(
        description="Send reminder emails for selected bookings"
    )
    def send_reminder_emails(self, request, queryset):

        from django.conf import settings
        from django.core.mail import send_mail

        sent = 0

        bookings = queryset.filter(
            status__in=[
                "pending",
                "confirmed",
            ],
            preferred_date__gte=timezone.now().date(),
        )

        for booking in bookings:

            try:

                send_mail(
                    f"Reminder: Your {booking.service.name} booking tomorrow",

                    (
                        f"Hi {booking.name},\n\n"
                        f"This is a reminder about your booking:\n"
                        f"Service: {booking.service.name}\n"
                        f"Date: {booking.preferred_date}\n"
                        f"Time: {booking.preferred_time}\n"
                        f"Address: {booking.address}\n\n"
                        f"If you need to make changes, please contact us.\n\n"
                        f"Thank you,\n"
                        f"Clean Pro Team"
                    ),

                    settings.DEFAULT_FROM_EMAIL,

                    [booking.email],

                    fail_silently=False,
                )

                sent += 1

            except Exception as e:

                self.message_user(
                    request,
                    f"Failed to send to "
                    f"{booking.email}: {e}",
                    level=messages.ERROR,
                )

        self.message_user(
            request,
            f"{sent} reminder email(s) sent successfully.",
        )

    @admin.action(
        description="Export selected bookings to CSV"
    )
    def export_selected_bookings(
        self,
        request,
        queryset,
    ):

        response = HttpResponse(
            content_type="text/csv"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="bookings_export.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "ID",
            "Customer",
            "Email",
            "Phone",
            "Service",
            "Date",
            "Time",
            "Frequency",
            "Address",
            "Status",
            "Payment Status",
            "Amount",
            "Assigned To",
            "Created At",
        ])

        bookings = queryset.select_related(
            "service",
            "assigned_to",
            "user",
        )

        for booking in bookings:

            writer.writerow([
                booking.id,
                booking.name,
                booking.email,
                booking.phone,
                booking.service.name,
                booking.preferred_date,
                booking.preferred_time,
                booking.get_frequency_display(),
                booking.address,
                booking.get_status_display(),
                booking.get_payment_status_display(),
                booking.amount or "",
                (
                    booking.assigned_to.name
                    if booking.assigned_to
                    else ""
                ),
                booking.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                ),
            ])

        return response


# ============================================
# CUSTOMER PROFILE ADMIN
# ============================================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = [
        "user_link",
        "phone",
        "city",
        "state",
        "get_preferred_time_display",
        "total_bookings",
        "total_spent",
        "get_last_booking",
    ]

    list_filter = [
        "preferred_time",
        "email_notifications",
        "sms_notifications",
        "city",
        "state",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "address",
        "city",
    ]

    readonly_fields = [
        "total_bookings",
        "total_spent",
        "created_at",
        "updated_at",
    ]

    list_per_page = 50

    fieldsets = (
        (
            "User",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                )
            },
        ),
        (
            "Preferences",
            {
                "fields": (
                    "preferred_time",
                    "special_instructions",
                    "email_notifications",
                    "sms_notifications",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "total_bookings",
                    "total_spent",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional",
            {
                "fields": (
                    "profile_picture",
                    "date_of_birth",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def user_link(self, obj):

        url = reverse(
            "admin:auth_user_change",
            args=[obj.user.id],
        )

        return format_html(
            '<a href="{}">{} ({})</a>',
            url,
            obj.user.get_full_name()
            or obj.user.username,
            obj.user.email,
        )

    user_link.short_description = "Customer"
    user_link.admin_order_field = "user__username"

    def get_preferred_time_display(self, obj):
        return (
            obj.get_preferred_time_display()
            if obj.preferred_time
            else "-"
        )

    get_preferred_time_display.short_description = (
        "Preferred Time"
    )

    def get_last_booking(self, obj):

        last = (
            Booking.objects
            .filter(user=obj.user)
            .order_by("-created_at")
            .first()
        )

        if last:

            url = reverse(
                "admin:cleaning_booking_change",
                args=[last.id],
            )

            return format_html(
                '<a href="{}">{} - {}</a>',
                url,
                last.service.name,
                last.preferred_date,
            )

        return "-"

    get_last_booking.short_description = "Last Booking"


# ============================================
# SAVED ADDRESS ADMIN
# ============================================

@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):

    list_display = [
        "user_link",
        "label",
        "city",
        "state",
        "is_default",
        "created_at",
    ]

    list_filter = [
        "is_default",
        "state",
        "created_at",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "label",
        "address",
        "city",
    ]

    list_editable = [
        "is_default",
    ]

    readonly_fields = [
        "created_at",
    ]

    def user_link(self, obj):

        url = reverse(
            "admin:auth_user_change",
            args=[obj.user.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name()
            or obj.user.username,
        )

    user_link.short_description = "Customer"


# ============================================
# FAVORITE SERVICE ADMIN
# ============================================

@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):

    list_display = [
        "user_link",
        "service_link",
        "added_at",
    ]

    list_filter = [
        "service",
        "added_at",
    ]

    search_fields = [
        "user__username",
        "service__name",
    ]

    date_hierarchy = "added_at"

    raw_id_fields = [
        "user",
        "service",
    ]

    def user_link(self, obj):

        url = reverse(
            "admin:auth_user_change",
            args=[obj.user.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name()
            or obj.user.username,
        )

    user_link.short_description = "Customer"

    def service_link(self, obj):

        url = reverse(
            "admin:cleaning_service_change",
            args=[obj.service.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.service.name,
        )

    service_link.short_description = "Service"


# ============================================
# NOTIFICATION ADMIN
# ============================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = [
        "user_link",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "is_read",
        "created_at",
    ]

    search_fields = [
        "user__username",
        "title",
        "message",
    ]

    list_editable = [
        "is_read",
    ]

    date_hierarchy = "created_at"

    actions = [
        "mark_as_read",
        "mark_as_unread",
        "send_test_notification",
    ]

    readonly_fields = [
        "created_at",
    ]

    def user_link(self, obj):

        url = reverse(
            "admin:auth_user_change",
            args=[obj.user.id],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name()
            or obj.user.username,
        )

    user_link.short_description = "Customer"

    @admin.action(
        description="Mark selected as read"
    )
    def mark_as_read(self, request, queryset):

        updated = queryset.update(
            is_read=True
        )

        self.message_user(
            request,
            f"{updated} notification(s) marked as read.",
        )

    @admin.action(
        description="Mark selected as unread"
    )
    def mark_as_unread(self, request, queryset):

        updated = queryset.update(
            is_read=False
        )

        self.message_user(
            request,
            f"{updated} notification(s) marked as unread.",
        )

    @admin.action(
        description="Send test notification to selected users"
    )
    def send_test_notification(
        self,
        request,
        queryset,
    ):

        users = User.objects.filter(
            id__in=queryset.values_list(
                "user_id",
                flat=True,
            )
        )

        count = 0

        for user in users:

            Notification.objects.create(
                user=user,
                title="Test Notification from Admin",
                message=(
                    "This is a test notification "
                    "sent from the admin panel."
                ),
                notification_type="system",
            )

            count += 1

        self.message_user(
            request,
            f"{count} test notification(s) created.",
        )


# ============================================
# TESTIMONIAL ADMIN
# ============================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "role",
        "rating",
        "is_approved",
        "created_at",
    ]

    list_filter = [
        "is_approved",
        "rating",
        "created_at",
    ]

    search_fields = [
        "name",
        "role",
        "content",
    ]

    list_editable = [
        "is_approved",
    ]

    ordering = [
        "-created_at",
    ]

    readonly_fields = [
        "created_at",
    ]

    actions = [
        "approve_testimonials",
        "reject_testimonials",
    ]

    @admin.action(
        description="Approve selected testimonials"
    )
    def approve_testimonials(
        self,
        request,
        queryset,
    ):

        updated = queryset.update(
            is_approved=True
        )

        self.message_user(
            request,
            f"{updated} testimonial(s) approved.",
        )

    @admin.action(
        description="Reject selected testimonials"
    )
    def reject_testimonials(
        self,
        request,
        queryset,
    ):

        updated = queryset.update(
            is_approved=False
        )

        self.message_user(
            request,
            f"{updated} testimonial(s) rejected.",
        )


# ============================================
# ADMIN SITE CONFIGURATION
# ============================================

admin.site.site_header = "Clean Pro Administration"
admin.site.site_title = "Clean Pro Admin"
admin.site.index_title = "Welcome to Clean Pro Admin Panel"


class AdminMedia:
    css = {
        "all": (
            "admin/css/custom_admin.css",
        )
    }

    js = (
        "admin/js/custom_admin.js",
    )


# ============================================
# CUSTOM ADMIN SITE
# ============================================

class CleanProAdminSite(admin.AdminSite):
    """Custom admin site with additional views."""

    site_header = "Clean Pro Administration"
    site_title = "Clean Pro Admin"
    index_title = "Operations Dashboard"

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "dashboard/",
                self.admin_view(self.dashboard_view),
                name="dashboard",
            ),
            path(
                "dashboard/booking-stats/",
                self.admin_view(self.booking_stats_api),
                name="booking_stats_api",
            ),
            path(
                "dashboard/team-schedule/",
                self.admin_view(self.team_schedule_view),
                name="dashboard_team_schedule",
            ),
            path(
                "dashboard/revenue/",
                self.admin_view(self.revenue_report),
                name="dashboard_revenue",
            ),
        ]

        return custom_urls + urls

    def dashboard_view(self, request):

        today = timezone.now().date()

        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        total_bookings = Booking.objects.count()

        pending_bookings = Booking.objects.filter(
            status="pending"
        ).count()

        confirmed_bookings = Booking.objects.filter(
            status="confirmed"
        ).count()

        upcoming_bookings = Booking.objects.filter(
            status__in=[
                "pending",
                "confirmed",
            ],
            preferred_date__gte=today,
        ).count()

        today_bookings = Booking.objects.filter(
            status__in=[
                "pending",
                "confirmed",
            ],
            preferred_date=today,
        ).select_related(
            "service",
            "assigned_to",
        )

        this_week_bookings = Booking.objects.filter(
            preferred_date__range=[
                week_ago,
                today,
            ]
        ).count()

        total_revenue = (
            Booking.objects
            .filter(payment_status="paid")
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        this_month_revenue = (
            Booking.objects
            .filter(
                payment_status="paid",
                created_at__date__gte=month_ago,
            )
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        active_team = TeamMember.objects.filter(
            is_active=True
        ).count()

        team_with_jobs = (
            TeamMember.objects
            .filter(
                assigned_bookings__status__in=[
                    "pending",
                    "confirmed",
                ],
                assigned_bookings__preferred_date__gte=today,
            )
            .distinct()
            .count()
        )

        recent_bookings = (
            Booking.objects
            .select_related(
                "service",
                "assigned_to",
                "user",
            )
            .order_by("-created_at")[:10]
        )

        popular_services = (
            Service.objects
            .filter(is_active=True)
            .annotate(
                booking_count=Count("booking")
            )
            .order_by("-booking_count")[:5]
        )

        context = {
            **self.each_context(request),
            "title": "Operations Dashboard",
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "upcoming_bookings": upcoming_bookings,
            "today_bookings": today_bookings,
            "this_week_bookings": this_week_bookings,
            "total_revenue": total_revenue,
            "this_month_revenue": this_month_revenue,
            "active_team": active_team,
            "team_with_jobs": team_with_jobs,
            "recent_bookings": recent_bookings,
            "popular_services": popular_services,
        }

        return render(
            request,
            "admin/cleaning/dashboard.html",
            context,
        )

    def booking_stats_api(self, request):

        days = int(
            request.GET.get(
                "days",
                30,
            )
        )

        end_date = timezone.now().date()

        start_date = (
            end_date
            - timedelta(days=days)
        )

        daily_data = []

        for i in range(days):

            day = (
                start_date
                + timedelta(days=i)
            )

            count = Booking.objects.filter(
                preferred_date=day,
                status__in=[
                    "pending",
                    "confirmed",
                    "completed",
                ],
            ).count()

            daily_data.append({
                "date": day.isoformat(),
                "count": count,
            })

        status_data = list(
            Booking.objects
            .filter(
                preferred_date__gte=start_date
            )
            .values("status")
            .annotate(
                count=Count("id")
            )
        )

        service_data = list(
            Booking.objects
            .filter(
                preferred_date__gte=start_date
            )
            .values("service__name")
            .annotate(
                count=Count("id")
            )
            .order_by("-count")[:10]
        )

        return JsonResponse({
            "daily_bookings": daily_data,
            "status_distribution": status_data,
            "service_distribution": service_data,
        })

    def team_schedule_view(self, request):

        today = timezone.now().date()

        end_date = (
            today
            + timedelta(days=7)
        )

        team_members = (
            TeamMember.objects
            .filter(is_active=True)
            .prefetch_related(
                "assigned_bookings__service"
            )
        )

        schedule = []

        for member in team_members:

            bookings = (
                member.assigned_bookings
                .filter(
                    preferred_date__range=[
                        today,
                        end_date,
                    ],
                    status__in=[
                        "pending",
                        "confirmed",
                    ],
                )
                .select_related("service")
                .order_by(
                    "preferred_date",
                    "preferred_time",
                )
            )

            member_schedule = []

            for booking in bookings:

                address = booking.address or ""

                member_schedule.append({
                    "date": booking.preferred_date,
                    "time": booking.preferred_time,
                    "service": booking.service.name,
                    "customer": booking.name,
                    "address": (
                        address[:50] + "..."
                        if len(address) > 50
                        else address
                    ),
                    "status": booking.status,
                    "booking_id": booking.id,
                })

            schedule.append({
                "member": member,
                "bookings": member_schedule,
            })

        context = {
            **self.each_context(request),
            "title": "Team Schedule (Next 7 Days)",
            "schedule": schedule,
            "today": today,
            "end_date": end_date,
        }

        return render(
            request,
            "admin/cleaning/team_schedule.html",
            context,
        )

    def revenue_report(self, request):

        days = int(
            request.GET.get(
                "days",
                30,
            )
        )

        end_date = timezone.now().date()

        start_date = (
            end_date
            - timedelta(days=days)
        )

        daily_revenue = []

        for i in range(days):

            day = (
                start_date
                + timedelta(days=i)
            )

            revenue = (
                Booking.objects
                .filter(
                    payment_status="paid",
                    created_at__date=day,
                )
                .aggregate(
                    Sum("amount")
                )["amount__sum"]
                or 0
            )

            daily_revenue.append({
                "date": day.isoformat(),
                "revenue": float(revenue),
            })

        service_revenue = list(
            Booking.objects
            .filter(
                payment_status="paid",
                created_at__date__gte=start_date,
            )
            .values("service__name")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
            .order_by("-total")
        )

        payment_summary = list(
            Booking.objects
            .filter(
                created_at__date__gte=start_date
            )
            .values("payment_status")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
        )

        context = {
            **self.each_context(request),
            "title": "Revenue Report",
            "days": days,
            "start_date": start_date,
            "end_date": end_date,
            "daily_revenue": json.dumps(
                daily_revenue
            ),
            "service_revenue": service_revenue,
            "payment_summary": payment_summary,
            "total_revenue": sum(
                item["total"] or 0
                for item in service_revenue
            ),
        }

        return render(
            request,
            "admin/cleaning/revenue_report.html",
            context,
        )


# ============================================
# CUSTOM ADMIN SITE INSTANCE
# ============================================

admin_site = CleanProAdminSite(
    name="admin"
)


# ============================================
# REGISTER MODELS
# ============================================

admin_site.register(
    User,
    UserAdmin,
)

admin_site.register(
    Service,
    ServiceAdmin,
)

admin_site.register(
    Booking,
    BookingAdmin,
)

admin_site.register(
    CustomerProfile,
    CustomerProfileAdmin,
)

admin_site.register(
    SavedAddress,
    SavedAddressAdmin,
)

admin_site.register(
    FavoriteService,
    FavoriteServiceAdmin,
)

admin_site.register(
    Notification,
    NotificationAdmin,
)

admin_site.register(
    Testimonial,
    TestimonialAdmin,
)

admin_site.register(
    TeamMember,
    TeamMemberAdmin,
)