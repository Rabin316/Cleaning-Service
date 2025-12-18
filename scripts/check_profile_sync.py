import os
import sys
import pathlib
import django
# Ensure project root is on path
PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.contrib.auth.models import User
from cleaning.models import Booking, CustomerProfile
from django.db.models import Sum

for u in User.objects.all():
    profile, _ = CustomerProfile.objects.get_or_create(user=u)
    total_bookings = Booking.objects.filter(user=u).count()
    total_spent = Booking.objects.filter(user=u, payment_status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    print(u.username, '-> profile:', profile.total_bookings, profile.total_spent, '| computed:', total_bookings, total_spent)
