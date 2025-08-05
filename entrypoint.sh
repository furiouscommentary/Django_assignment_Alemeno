#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$DJANGO_DB_HOST" "$DJANGO_DB_PORT"; do
  sleep 1
done
echo "PostgreSQL is available"

echo "Running Django migrations..."
python manage.py migrate

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is available"

echo "Waiting for Celery worker to be ready..."

sleep 5

echo "Triggering data ingestion task..."
python manage.py shell -c "from core.tasks import ingest_data; ingest_data.delay()"

echo "Starting Django server..."
exec "$@"
