import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pharmarcy_Prescription_Tracker.settings')
django.setup()

from accounts.models import User, Customer

# Create Customer profiles for all users with role="customer" who don't have one
for user in User.objects.filter(role="customer"):
    customer, created = Customer.objects.get_or_create(user=user)
    if created:
        print(f"Created new profile for {user.username}")
    else:
        print(f"Profile already exists for {user.username}")