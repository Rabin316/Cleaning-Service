import os
import sys
import pathlib
import django

# ensure project root on path
PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

from django.contrib.auth.models import User
from cleaning.models import Booking, CustomerProfile
from django.db.models import Sum
from decimal import Decimal

print('Backfilling CustomerProfile totals...')
for u in User.objects.all():
    profile, _ = CustomerProfile.objects.get_or_create(user=u)
    total_bookings = Booking.objects.filter(user=u).count()
    total_spent = Booking.objects.filter(user=u, payment_status='paid').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    profile.total_bookings = total_bookings
    profile.total_spent = total_spent
    # loyalty_points removed; only update totals
    profile.save()
    print(f'Updated {u.username}: bookings={total_bookings}, spent={total_spent}')

print('Backfill complete.')
