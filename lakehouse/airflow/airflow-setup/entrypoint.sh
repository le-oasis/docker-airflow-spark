#!/bin/bash

# Check if the spark_connect connection exists
if airflow connections get spark_connect; then
    # If it exists, delete it
    airflow connections delete spark_connect
fi

# Create the Spark connection
airflow connections -a \
    --conn_id spark_connect \
    --conn_type spark \
    --conn_uri 'spark://oasis-spark:7077?extra__spark__queue=root.default'

# Start the Airflow webserver
exec airflow webserver

# Start the Airflow webserver
exec airflow webserver