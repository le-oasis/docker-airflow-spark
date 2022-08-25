FROM postgres:9.5.3

COPY hive/hive-schema-2.3.0.postgres.sql /var/lib/postgresql/hive/hive-schema-2.3.0.postgres.sql
COPY hive/hive-txn-schema-2.3.0.postgres.sql /var/lib/postgresql/hive/hive-txn-schema-2.3.0.postgres.sql
COPY hive/upgrade-2.3.0-to-3.0.0.postgres.sql /var/lib/postgresql/hive/upgrade-2.3.0-to-3.0.0.postgres.sql
COPY hive/upgrade-3.0.0-to-3.1.0.postgres.sql /var/lib/postgresql/hive/upgrade-3.0.0-to-3.1.0.postgres.sql

COPY hive/init-hive-db.sh /docker-entrypoint-initdb.d/init-user-db.sh