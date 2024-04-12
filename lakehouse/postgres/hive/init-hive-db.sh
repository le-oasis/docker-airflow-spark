#!/bin/bash
set -e

# Load environment variables from .env file
source .env

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$HIVE_USER') THEN
      CREATE USER $HIVE_USER WITH PASSWORD '$HIVE_PASSWORD';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$RANGER_USER') THEN
      CREATE USER $RANGER_USER WITH PASSWORD '$RANGER_PASSWORD';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$ADMIN_USER') THEN
      CREATE USER $ADMIN_USER WITH PASSWORD '$ADMIN_PASSWORD';
    END IF;
  END
  \$\$;

  SELECT 'CREATE DATABASE metastore' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metastore')\\gexec
  SELECT 'CREATE DATABASE ranger' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ranger')\\gexec

  GRANT ALL PRIVILEGES ON DATABASE metastore TO $HIVE_USER;
  GRANT ALL PRIVILEGES ON DATABASE ranger TO $ADMIN_USER;

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