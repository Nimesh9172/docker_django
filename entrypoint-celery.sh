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

# Start Celery worker
echo "Starting Celery worker..."
exec celery -A docker_django worker --loglevel=info
