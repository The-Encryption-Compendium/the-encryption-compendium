#!/bin/sh

if [ "${DEVELOPMENT}" = "yes" ]
then
    LOG_LEVEL="debug"
else
    LOG_LEVEL="info"
fi

if [ -d /var/src ]
then
    echo "----------------------------------------------"
    echo "Changing directory into /var/src"
    echo "----------------------------------------------"
    cd /var/src
fi

gunicorn encryption_compendium.wsgi \
    --bind 0.0.0.0:5000 \
    --access-logfile /dev/stdout \
    --error-logfile /dev/stderr \
    --log-level "${LOG_LEVEL}"
