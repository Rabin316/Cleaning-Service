import os, sys, pathlib, django
from datetime import date, timedelta, time

PROJECT_ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

from django.contrib.auth.models import User
from cleaning.models import Service, Booking

user = User.objects.first()
service = Service.objects.first()
if not user or not service:
    print('Need at least one User and one Service in DB')
    raise SystemExit(1)

b = Booking(
    user=user,
    service=service,
    name=user.get_full_name() or user.username,
    email=user.email,
    phone=getattr(user, 'phone', '0000000000'),
    address='Test address',
    preferred_date=date.today() + timedelta(days=2),
    preferred_time=time(10,0),
    frequency='one_time',
)
# leave amount blank so DEBUG logic in view would set it; but we'll set paid here to simulate
b.amount = service.price_starting
b.payment_status = 'paid'
b.save()
print('Created booking id', b.id, 'amount', b.amount, 'payment_status', b.payment_status)
