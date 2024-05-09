#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin') THEN
            CREATE USER admin WITH PASSWORD 'admin';
        END IF;
    END
    \$\$;
    SELECT 'CREATE DATABASE metastore_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metastore_db')\\gexec
    GRANT ALL PRIVILEGES ON DATABASE metastore_db TO admin;

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
            CREATE USER airflow WITH PASSWORD 'airflow';
        END IF;
    END
    \$\$;
    SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\\gexec
    GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
EOSQL