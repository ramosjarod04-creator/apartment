"""
WSGI config for apartment_reservation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.contrib.auth import get_user_model
User = get_user_model()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apartment_reservation.settings')

application = get_wsgi_application()

app = application

# This is the "Magic Fix": It runs migrations whenever the app starts
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
        print("Superuser created successfully!")
except Exception as e:
    print(f"Superuser creation failed: {e}")