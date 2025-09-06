#!/bin/sh

set -e

echo "Waiting for Postgres..."
until nc -z db 5432; do
  sleep 2
done
echo "Postgres is up!"

echo "Waiting for Redis..."
until nc -z redis 6379; do
  sleep 2
done
echo "Redis is up!"

# Start Celery beat
echo "Starting Celery beat..."
exec celery -A docker_django beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
