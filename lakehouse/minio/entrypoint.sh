#!/bin/sh
/usr/bin/mc config host add myminio http://minio:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
/usr/bin/mc alias set myminio http://minio:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
/usr/bin/mc mb myminio/oasis
/usr/bin/mc mb myminio/gold
/usr/bin/mc mb myminio/silver
/usr/bin/mc mb myminio/bronze
/usr/bin/mc policy set public myminio/oasis
/usr/bin/mc policy set public myminio/gold
/usr/bin/mc policy set public myminio/silver
/usr/bin/mc policy set public myminio/bronze
/usr/bin/mc policy download myminio/oasis
/usr/bin/mc policy download myminio/silver
/usr/bin/mc policy download myminio/bronze
/usr/bin/mc policy download myminio/gold