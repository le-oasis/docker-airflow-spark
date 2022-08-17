#!/bin/bash -c

/usr/bin/mc config host add ${MINIO_ALIAS} ${MINIO_URL} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD};

/usr/bin/mc mb ${MINIO_ALIAS}/bronze;
/usr/bin/mc policy download ${MINIO_ALIAS}/bronze;

/usr/bin/mc mb ${MINIO_ALIAS}/silver;
/usr/bin/mc policy download ${MINIO_ALIAS}/silver;

/usr/bin/mc mb ${MINIO_ALIAS}/gold;
/usr/bin/mc policy download ${MINIO_ALIAS}/gold;

exit 0;