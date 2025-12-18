#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cleaning.models import Service

# Update icons with better FontAwesome icons
icons_map = {
    'Deep Cleaning': 'sparkles',
    'House Cleaning': 'house-chimney',
    'Office Cleaning': 'building',
}

print('Updating service icons...\n')
for name, icon in icons_map.items():
    service = Service.objects.filter(name=name).first()
    if service:
        old_icon = service.icon
        service.icon = icon
        service.save()
        print(f'✓ Updated "{name}": {old_icon} → {icon}')
    else:
        print(f'✗ Service "{name}" not found')

# List all services and their icons
print('\n' + '='*50)
print('All services with updated icons:')
print('='*50)
for s in Service.objects.all().order_by('name'):
    print(f'  • {s.name}: {s.icon}')
