#!/usr/bin/env bash
set -e

APP_MODULE="assured_farming.wsgi:application"
WORKERS=3
MAX_ATTEMPTS=5

echo "$(date) | start.sh running"

# ------- DATABASE WAIT (works with Render DATABASE_URL) -------
if [ -n "$DATABASE_URL" ]; then
  echo "$(date) | DATABASE_URL found, parsing host/port"

  DB_HOST=$(python - <<'PY'
import os, urllib.parse as u
p = u.urlparse(os.environ.get("DATABASE_URL",""))
print(p.hostname or "")
PY
)

  DB_PORT=$(python - <<'PY'
import os, urllib.parse as u
p = u.urlparse(os.environ.get("DATABASE_URL",""))
print(p.port or 5432)
PY
)

  if [ -n "$DB_HOST" ]; then
    echo "$(date) | Waiting for Postgres at $DB_HOST:$DB_PORT"
    ATTEMPT=0
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
      if nc -z "$DB_HOST" "$DB_PORT"; then
        echo "$(date) | Postgres is ready!"
        break
      fi
      ATTEMPT=$((ATTEMPT+1))
      echo "$(date) | Attempt $ATTEMPT/$MAX_ATTEMPTS failed..."
      sleep 2
    done
  fi
fi

echo "$(date) | Running migrations and collectstatic"
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

echo "$(date) | Starting Gunicorn"
exec gunicorn $APP_MODULE --bind 0.0.0.0:$PORT --workers $WORKERS
