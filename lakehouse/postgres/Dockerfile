FROM postgres:14

COPY hive/*.sql /var/lib/postgresql/hive/
COPY hive/init-hive-db.sh /docker-entrypoint-initdb.d/init-user-db.sh