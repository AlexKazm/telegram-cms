#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER telegramcms WITH PASSWORD 'telegramcms';
    CREATE DATABASE telegramcms_db WITH OWNER telegramcms;
    GRANT ALL PRIVILEGES ON DATABASE telegramcms_db TO telegramcms;
EOSQL
