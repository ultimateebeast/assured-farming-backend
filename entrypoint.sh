#!/usr/bin/env bash
set -e

echo "Waiting for Postgres..."
until nc -z -v -w30 $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for database..."
  sleep 1
done

echo "Apply database migrations"
python manage.py migrate --noinput

echo "Collect static"
python manage.py collectstatic --noinput || true

exec "$@"
