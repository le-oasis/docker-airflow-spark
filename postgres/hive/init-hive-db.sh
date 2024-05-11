#!/bin/bash
set -e

# Variables
DB_USER="hive"
DB_NAME="metastore"
AIRFLOW_USER="airflow"
AIRFLOW_DB="airflow"
SCHEMA_NAME="public"
RANGER_USER="ranger"
RANGER_PASSWORD="${RANGER_PASSWORD:-security}"
ADMIN_USER="admin"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-security}"
RANGER_DB="ranger"
HIVE_PASSWORD="${HIVE_PASSWORD:-hive}"

# Create hive user if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$HIVE_PASSWORD';
    END IF;
  END
  \$\$;
EOSQL

# Check if the metastore database exists
DB_EXISTS=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

# If the database does not exist, create it
if [ "$DB_EXISTS" = "1" ]
then
    echo "Database $DB_NAME already exists, skipping creation."
else
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $DB_NAME;"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    echo "Database $DB_NAME created."
fi

# Check if the airflow database exists
AIRFLOW_DB_EXISTS=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$AIRFLOW_DB'")

# If the database does not exist, create it
if [ "$AIRFLOW_DB_EXISTS" = "1" ]
then
    echo "Database $AIRFLOW_DB already exists, skipping creation."
else
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $AIRFLOW_DB;"
    psql -U "$POSTGRES_USER" -c "CREATE USER $AIRFLOW_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $AIRFLOW_DB TO $AIRFLOW_USER;"
    echo "Database $AIRFLOW_DB created and user $AIRFLOW_USER created with all privileges on $AIRFLOW_DB."
fi

# Create the hive schema
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
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

# Restore the dvdrental database
DB_RENTAL="dvdrental"
DB_RENTAL_EXISTS=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_RENTAL'")

if [ "$DB_RENTAL_EXISTS" = "1" ]
then
    echo "Database $DB_RENTAL already exists, skipping restore."
else
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $DB_RENTAL;"
    pg_restore --dbname=$DB_RENTAL --username=$POSTGRES_USER --section=data --section=post-data --section=pre-data  /var/lib/postgresql/dvdrental.tar
    echo "Database $DB_RENTAL restored."
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_RENTAL TO $POSTGRES_USER;"
fi