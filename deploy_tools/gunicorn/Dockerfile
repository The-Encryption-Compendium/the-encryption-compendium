FROM alpine:3.11

# Create a non-root user to run the site
RUN adduser -s /bin/false -D www-data

# Install dependencies
RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
        libffi-dev \
        musl-dev \
        postgresql-dev \
        python3 \
        python3-dev

# Install pip packages. The packages we install will vary based
# on whether we're running in production mode or development
# mode.
ARG DEVELOPMENT="yes"
RUN if [ ! "${DEVELOPMENT}" = "yes" ] && [ ! "${DEVELOPMENT}" = "no" ]; \
    then \
        echo "Error: DEVELOPMENT must be yes or no, not \"${DEVELOPMENT}\"." \
            >/dev/stderr; \
        exit 1; \
    fi



COPY requirements.txt /tmp/requirements.txt
COPY requirements.dev.txt /tmp/requirements.dev.txt
COPY deploy_tools/gunicorn/setup.sh /tmp/setup.sh

RUN /tmp/setup.sh

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
ENV DEVELOPMENT="${DEVELOPMENT}"

CMD [ "/bin/sh", "/run.sh" ]
