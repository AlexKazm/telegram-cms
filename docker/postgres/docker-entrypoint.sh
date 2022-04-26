#!/bin/bash
set -e

if [ "$1" = 'postgres' ]; then
    chown -R postgres "$PGDATA"

    if [ -z "$(ls -A "$PGDATA")" ]; then
        gosu postgres initdb
    fi

    exec gosu postgres "$@"

elif [ "$1" = 'init' ]; then
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER god;
  CREATE DATABASE mashinki;
  GRANT ALL PRIVILEGES ON DATABASE mashinki TO god;
EOSQL
fi

exec "$@"
