#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run migrations - THIS IS WHAT FIXES YOUR ERROR
python3.12 manage.py migrate --noinput

# Collect static files
python3.12 manage.py collectstatic --noinput