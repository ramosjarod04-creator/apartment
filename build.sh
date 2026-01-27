#!/bin/bash

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Database Migrations (This fixes your error!)
python manage.py migrate --noinput

# 3. Collect Static Files
python manage.py collectstatic --noinput