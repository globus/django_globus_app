#!/bin/bash
python /backend/manage.py makemigrations
python /backend/manage.py migrate
python /backend/manage.py collectstatic --settings=$DJANGO_SETTINGS_MODULE --noinput

exec /usr/local/bin/gunicorn django_globus_app.wsgi \
    --env DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    --name globus-django-app \
    --bind 0.0.0.0:80 \
    --workers 2 \
    --log-level info \
    --log-file /srv/logs/gunicorn.log \
    --access-logfile /srv/logs/access.log \
    --chdir /backend
