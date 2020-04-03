#!/bin/bash

### Setup script to run before starting Solr

# Create a data-config.xml with the database credentials
export POSTGRES_USER=$POSTGRES_USER
export POSTGRES_PASSWORD=$POSTGRES_PASSWORD
DATA_CONFIG="${CONFIG_DIR}/data-config.xml"

cat > "${DATA_CONFIG}" <<- EOXML
<dataConfig>

  <dataSource
    type="JdbcDataSource"
    name="compendium-db"
    url="jdbc:postgresql://tec-database/$POSTGRES_DB"
    driver="org.postgresql.Driver"
    readOnly="true"
    user="$POSTGRES_USER"
    password="$POSTGRES_PASSWORD" />

  <document name="entries">
    <entity name="compendium" query="select id, title, abstract, url, year, month, day from compendium" />
  </document>

</dataConfig>
EOXML

echo "${DATA_CONFIG} written"
