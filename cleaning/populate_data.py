from cleaning.models import Service, TeamMember, Testimonial

# Create sample services
services_data = [
    {
        'name': 'House Cleaning',
        'short_description': 'Complete home cleaning service for your peace of mind',
        'description': 'Our house cleaning service covers all areas of your home...',
        'price_starting': 89.99,
        'duration': '2-3 hours',
        'icon': 'fa-home',
        'features': '''Dusting all surfaces
Vacuuming and mopping floors
Kitchen cleaning and sanitizing
Bathroom deep cleaning
Trash removal'''
    },
    {
        'name': 'Office Cleaning',
        'short_description': 'Professional cleaning for productive workspaces',
        'description': 'Keep your office environment clean and professional...',
        'price_starting': 129.99,
        'duration': '3-4 hours',
        'icon': 'fa-building',
        'features': '''Desk and workstation cleaning
Common area sanitization
Kitchen and break room
Restroom maintenance
Trash and recycling'''
    },
    {
        'name': 'Deep Cleaning',
        'short_description': 'Thorough cleaning for a spotless home',
        'description': 'Our deep cleaning service goes beyond regular cleaning...',
        'price_starting': 199.99,
        'duration': '4-6 hours',
        'icon': 'fa-broom',
        'features': '''All regular cleaning tasks
Appliance cleaning (inside/out)
Baseboards and trim
Window cleaning
Carpet deep cleaning'''
    },
]

for service_data in services_data:
    Service.objects.create(**service_data)

print("Sample data created successfully!")