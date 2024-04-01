# Project Overview

This project sets up a data processing environment using Docker, Apache Airflow, and Apache Spark. The environment includes a Jupyter Notebook with PySpark enabled, a Spark cluster with one master and three workers, and an Airflow setup with a webserver, scheduler, and worker. The project also includes a PostgreSQL database and a Redis database for Airflow to use.

## Docker Compose Files

There are two Docker Compose files used to launch the Docker instances:

1. **docker-compose.yml**: This file sets up the Airflow environment, including the webserver, scheduler, worker, and the PostgreSQL and Redis databases. It also sets up a network bridge for the services to communicate.

2. **docker-compose.spark.yml**: This file sets up the Jupyter Notebook and Spark cluster. The Jupyter Notebook has PySpark enabled and is connected to the PostgreSQL database. The Spark cluster includes one master and three workers.

## How to Use

- To use this project, you need to have Docker installed on your machine. Once Docker is installed, you can use the Docker Compose files to launch the Docker instances.

- To launch the Airflow environment, navigate to the directory containing the docker-compose.yml file and run the following command:

''' 
docker-compose up --biuld -d
'''


To launch the Jupyter Notebook and Spark cluster, navigate to the directory containing the docker-compose.spark.yml file and run the following command:

'''
docker-compose -f docker-compose.spark.yml up
'''


### Accessing the Services

Once the Docker instances are running, you can access the services at the following URLs:

Airflow Web UI: http://localhost:8085
Jupyter Notebook: http://localhost:8888
Spark Master UI: http://localhost:8181
Spark Worker UI: http://localhost:8081

The Airflow webserver, scheduler, and worker are running on ports 8085, 8086, and 8087, respectively. The Jupyter Notebook is running on port 8888, and the Spark master and workers are running on ports 8181, 8081, 8082, and 8083.

### Accessing the PostgreSQL Database

To access the PostgreSQL database, you can use the following connection information:

Host: localhost
Port: 5432
Database: airflow
Username: airflow
Password: airflow



### Stopping the Services

To stop the services, you can use the following command:

down
For the Jupyter Notebook and Spark cluster, use the following command:

down
Further Information
For more detailed information about the services and how to use them, please refer to the official documentation for Apache Airflow and Apache Spark.