FROM alpine:3.11

# Create a non-root user to run the site
RUN adduser -s /bin/false -D www-data

# Install dependencies
RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
        libffi-dev \
        musl-dev \
        python3 \
        python3-dev

COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache gcc \
    && python3 -m pip install \
        -r /tmp/requirements.txt \
        --no-cache-dir \
#
# Clean up
    && apk del gcc \
    && rm /tmp/requirements.txt

# Development purposes -- if the /var/src directory is non-empty, then we
# assume that the code has been mounted there and run the code from there
# instead.
VOLUME /var/src

# Install code
ENV WWW_DIR="/var/www"
RUN mkdir -p "${WWW_DIR}" \
    && chown -R www-data:www-data "${WWW_DIR}"
ADD --chown=www-data:www-data src "${WWW_DIR}"

# Install script to be run as the www-data user
COPY --chown=root:www-data deploy_tools/gunicorn/run.sh /run.sh

USER www-data
WORKDIR "${WWW_DIR}"

# Set additional configuration options
ENV DEVELOPMENT="yes"

CMD [ "/bin/sh", "/run.sh" ]
