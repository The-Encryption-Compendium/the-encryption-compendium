#!/bin/sh

# Enable more verbose logging in development mode
if [ "${DEVELOPMENT}" = "yes" ]
then
    ADDTL_OPTS="--reload --log-level debug"
else
    ADDTL_OPTS="--log-level info"
fi

# Initialize the database
python3 manage.py migrate

# Collect static files into /var/www/static
python3 manage.py collectstatic --noinput

gunicorn encryption_compendium.wsgi \
    --config "${GUNICORN_CONFIG}" \
    ${ADDTL_OPTS}
