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

gunicorn encryption_compendium.wsgi \
    --config "${GUNICORN_CONFIG}" \
    ${ADDTL_OPTS}
