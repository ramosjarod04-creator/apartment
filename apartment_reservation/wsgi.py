import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apartment_reservation.settings')

application = get_wsgi_application()
app = application # Required for Vercel

# Failsafe Startup Logic
try:
    # 1. Run migrations to ensure tables exist
    print("Running migrations...")
    call_command('migrate', interactive=False)

    # 2. Create Superuser if it doesn't exist
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
        print("Superuser created successfully!")

    # 3. Load Apartment Data from apartments.json
    # Note: Make sure apartments.json is in your root folder (same as manage.py)
    print("Loading apartment data...")
    call_command('loaddata', 'apartments.json')
    print("Data loaded successfully!")

except Exception as e:
    print(f"Startup script error: {e}")