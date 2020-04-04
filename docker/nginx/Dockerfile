FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
ADD conf.d /etc/nginx/conf.d

# Non-root user to run the site
RUN adduser -D -s /bin/false -G www-data www-data

# Create directory for caching
RUN mkdir -p /data/nginx/cache
