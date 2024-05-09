#!/bin/bash

# Initialize the Airflow database
airflow db init

# Check if the spark_connect connection exists
if airflow connections get spark_connect; then
    # If it exists, delete it
    airflow connections delete spark_connect
fi

# Create the Spark connection
airflow connections add \
    --conn_id spark_connect \
    --conn_type spark \
    --conn_host spark://oasis-spark \
    --conn_port 7077 \
    --conn_extra '{"queue": "root.default"}'

# Start the Airflow webserver
exec airflow webserver