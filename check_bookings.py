from cleaning.models import Booking
from django.contrib.auth.models import User

# Check recent bookings and their user assignments
bookings = Booking.objects.all().order_by('-created_at')[:10]

print("Recent bookings:")
print(f"{'ID':<5} {'Service':<20} {'User':<20} {'Status':<12} {'Created':<20}")
print("-" * 80)

for booking in bookings:
    user_name = booking.user.username if booking.user else "None (anonymous)"
    print(f"{booking.id:<5} {booking.service.name:<20} {user_name:<20} {booking.status:<12} {booking.created_at}")

print(f"\nTotal bookings: {Booking.objects.count()}")
print(f"Bookings with user_id: {Booking.objects.filter(user__isnull=False).count()}")
print(f"Bookings without user_id: {Booking.objects.filter(user__isnull=True).count()}")
