#!/bin/sh

set -e

echo "Waiting for Kafka..."
while ! nc -z kafka 9092; do
  sleep 1
done
echo "Kafka is up!"
python manage.py consumers
