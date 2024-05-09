#!/bin/sh
/usr/bin/mc alias set myminio http://minio:9000 accesskey secretkey
/usr/bin/mc mb myminio/oasis
/usr/bin/mc mb myminio/gold
/usr/bin/mc mb myminio/silver
/usr/bin/mc mb myminio/bronze
/usr/bin/mc anonymous set public myminio/oasis
/usr/bin/mc anonymous set public myminio/gold
/usr/bin/mc anonymous set public myminio/silver
/usr/bin/mc anonymous set public myminio/bronze
/usr/bin/mc policy download myminio/oasis
/usr/bin/mc policy dxownload myminio/silver
/usr/bin/mc policy download myminio/bronze
/usr/bin/mc policy download myminio/gold
/usr/bin/mc cp testfile.txt myminio/oasis

