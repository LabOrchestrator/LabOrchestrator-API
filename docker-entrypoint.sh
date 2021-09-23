#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --run-syncdb

# Create superuser
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_FIRST_NAME" ] ; then
    echo "Creating superuser"
    python manage.py createsuperuser --no-input
fi

# Start server
echo "Starting server"
#chown -R www-data:www-data /opt/app/volumes # otherwise the database is not accessible from the workers; only needed when we add volumes
(gunicorn lab_orchestrator.wsgi --user www-data --bind 0.0.0.0:8010 --workers "$AMOUNT_WORKERS") &
nginx -g "daemon off;" # needed for static files

