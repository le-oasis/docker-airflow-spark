#!/bin/bash
set -e

# Use environment variables for user and password
: "${HIVE_USER:=hive}"
: "${HIVE_PASSWORD:=hive}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$HIVE_USER') THEN
      CREATE USER $HIVE_USER WITH PASSWORD '$HIVE_PASSWORD';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metastore') THEN
      CREATE DATABASE metastore;
    END IF;
  END
  \$\$;

  GRANT ALL PRIVILEGES ON DATABASE metastore TO $HIVE_USER;

  \c metastore

  \i /var/lib/postgresql/hive/hive-schema-2.3.0.postgres.sql
  \i /var/lib/postgresql/hive/hive-txn-schema-2.3.0.postgres.sql
  \i /var/lib/postgresql/hive/upgrade-2.3.0-to-3.0.0.postgres.sql
  \i /var/lib/postgresql/hive/upgrade-3.0.0-to-3.1.0.postgres.sql

  \pset tuples_only
  \o /tmp/grant-privs
SELECT 'GRANT SELECT,INSERT,UPDATE,DELETE ON "' || schemaname || '"."' || tablename || '" TO $HIVE_USER ;'
FROM pg_tables
WHERE tableowner = CURRENT_USER and schemaname = 'public';
  \o
  \i /tmp/grant-privs
EOSQL