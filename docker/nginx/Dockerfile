FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
ADD conf.d /etc/nginx/conf.d

# Non-root user to run the site
RUN adduser -D -s /bin/false -G www-data www-data

# Create directory for caching
RUN mkdir -p /data/nginx/cache

RUN apk update \
    && apk add --no-cache openssl apache2-utils \
    && mkdir -p /tls/encryptioncompendium.org/

# Create an empty .htpasswd file for authentication
RUN touch /etc/nginx/.htpasswd

# Add a custom run script
COPY run.sh /run.sh
CMD [ "/run.sh" ]
