#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cleaning.models import Service

# Better icon mapping with valid FontAwesome 6.4.0 icons
icons_map = {
    'Deep Cleaning': 'wand-magic-sparkles',  # Valid FA6 icon for sparkle/magic effect
    'House Cleaning': 'house',  # Changed from house-chimney (may not exist)
    'Office Cleaning': 'building',
}

print('Updating service icons with valid FontAwesome 6.4.0 icons...\n')
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
print('\n' + '='*60)
print('All services with valid icons:')
print('='*60)
for s in Service.objects.all().order_by('name'):
    from cleaning.templatetags.icon_utils import normalize_icon
    normalized = normalize_icon(s.icon)
    print(f'  • {s.name}')
    print(f'    DB value: {s.icon}')
    print(f'    Normalized: {normalized}')
    print()
