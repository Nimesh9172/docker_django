#!/bin/sh

set -e

echo "Waiting for Postgres..."
until nc -z db 5432; do
  sleep 2
done
echo "Postgres is up!"

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Django with Gunicorn..."
# exec gunicorn docker_django.wsgi:application --bind 0.0.0.0:8000 --workers 3
exec daphne -b 0.0.0.0 -p 8000 docker_django.asgi:application

