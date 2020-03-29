FROM solr:8.4
ARG POSTGRES_JDBC_VERSION
ENV CONFIG_DIR="/opt/solr/server/solr/configsets/_default/conf"

USER root

RUN mkdir -p ./contrib/dataimporthandler/lib \
#
# Install the PostgreSQL JDBC driver
    && wget \
        "https://jdbc.postgresql.org/download/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
        -O ./contrib/dataimporthandler/lib/postgresql.jar \
        --progress=bar:force \
#
# Give ownership of the config directory to solr so that we can
# generate the data-config.xml file at runtime.
    && chown -R solr:solr "${CONFIG_DIR}"

ADD --chown=solr:solr conf "${CONFIG_DIR}"

# Add a script to run prior to starting Solr
COPY setup.sh /docker-entrypoint-initdb.d/

USER solr
