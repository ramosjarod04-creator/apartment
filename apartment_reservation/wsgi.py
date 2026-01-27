"""
WSGI config for apartment_reservation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apartment_reservation.settings')

application = get_wsgi_application()

app = application

# This is the "Magic Fix": It runs migrations whenever the app starts
try:
    print("Running migrations...")
    call_command('migrate', interactive=False)
    print("Migrations completed successfully!")
except Exception as e:
    print(f"Migration failed: {e}")