#!/bin/bash
set -e

# Variables
DB_USER="hive"
DB_NAME="metastore"
SCHEMA_NAME="public"
RANGER_USER="ranger"
RANGER_PASSWORD="security"
ADMIN_USER="admin"
ADMIN_PASSWORD="security"
RANGER_DB="ranger"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  -- Create user if it doesn't exist
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_USER';
    END IF;
  END
  \$\$;

  -- Create database if it doesn't exist
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
      CREATE DATABASE $DB_NAME;
    END IF;
  END
  \$\$;

  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

  \c $DB_NAME

  \i /var/lib/postgresql/hive/hive-schema-2.3.0.postgres.sql
  \i /var/lib/postgresql/hive/hive-txn-schema-2.3.0.postgres.sql
  \i /var/lib/postgresql/hive/upgrade-2.3.0-to-3.0.0.postgres.sql
  \i /var/lib/postgresql/hive/upgrade-3.0.0-to-3.1.0.postgres.sql

  \pset tuples_only
  \o /tmp/grant-privs
  SELECT 'GRANT SELECT,INSERT,UPDATE,DELETE ON "' || schemaname || '"."' || tablename || '" TO $DB_USER ;'
  FROM pg_tables
  WHERE tableowner = CURRENT_USER and schemaname = '$SCHEMA_NAME';
  \o
  \i /tmp/grant-privs

  -- Create ranger users
  CREATE USER $RANGER_USER WITH PASSWORD '$RANGER_PASSWORD';
  CREATE USER $ADMIN_USER WITH PASSWORD '$ADMIN_PASSWORD';
  CREATE DATABASE $RANGER_DB;
  GRANT ALL PRIVILEGES ON DATABASE $RANGER_DB to $ADMIN_USER;
EOSQL