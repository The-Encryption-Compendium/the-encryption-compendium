#!/bin/sh

# Generate self-signed TLS certificates
if [ ! -f /tls/fullchain.pem ]
then
    openssl req \
        -x509 \
        -newkey rsa:4096 \
        -keyout /tls/privkey.pem \
        -out /tls/fullchain.pem \
        -days 30 \
        -nodes \
        -subj "/CN=${SERVER_NAME}"
fi

nginx -g 'daemon off;'
