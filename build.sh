#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3.12 manage.py migrate --noinput

# Collect static files (if you use WhiteNoise)
python3.12 manage.py collectstatic --noinput