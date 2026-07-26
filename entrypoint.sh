#!/bin/sh
set -e

# Ensure static and media directories exist
mkdir -p /app/static /app/media

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec gunicorn --bind 0.0.0.0:8000 --workers 4 stock_project.wsgi:application
