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

# Create superuser if it doesn't exist
echo "Ensuring superuser exists..."
python manage.py shell << END
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created.")
else:
    print(f"Superuser {username} already exists.")
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Django with Gunicorn..."
# exec gunicorn docker_django.wsgi:application --bind 0.0.0.0:8000 --workers 3
exec daphne -b 0.0.0.0 -p 8000 docker_django.asgi:application

