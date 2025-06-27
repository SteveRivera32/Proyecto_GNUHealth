#!/bin/bash
set -e

echo "Descomprimiendo y cargando la base de datos demo..."

gunzip -c /docker-entrypoint-initdb.d/gnuhealth-44-demo.sql.gz | psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Base de datos cargada correctamente."
