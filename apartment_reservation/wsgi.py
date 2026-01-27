import os
import django
from django.core.wsgi import get_wsgi_application

# 1. Set environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apartment_reservation.settings')

# 2. Manually trigger Django setup to allow model access
django.setup()

# 3. Now it is safe to import models and management commands
from django.core.management import call_command
from django.contrib.auth import get_user_model

# 4. Initialize the WSGI application
application = get_wsgi_application()
app = application # Required for Vercel

# 5. Failsafe Startup Logic
try:
    # Run migrations
    print("Running migrations...")
    call_command('migrate', interactive=False)

    # Create Superuser
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
        print("Superuser created successfully!")

    # Load Apartment Data
    # Ensure apartments.json is in your root directory
    if os.path.exists('apartments.json'):
        print("Loading apartment data...")
        call_command('loaddata', 'apartments.json')
        print("Data loaded successfully!")
    else:
        print("apartments.json not found, skipping loaddata.")

except Exception as e:
    # We print to the Vercel logs so you can see if something fails
    print(f"Startup script error: {e}")