#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}

if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser \
    --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null || true
fi

exec gunicorn core.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
