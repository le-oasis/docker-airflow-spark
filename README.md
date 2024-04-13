# Building a Modern Data Lake with Minio, Spark, Airflow via Docker.

## Overview
This system utilises the lakehouse data-lake architecture to store and compute data for enterprises.
This readme file will detail how to build an ELT (Extract, Load and Transform) pipeline and connect services that support the Data Lake.

## Setting Up the Data Lake

### Dockerfile: Build the Image.

- A `Dockerfile`  is a text document that contains all the commands a user could call on the command line to assemble an image. 
- `Dockerfile` that contians installations of `JAVA-JDK.v11`, `ApacheSpark.v3.3.0`, `Hadoop.v3`, & other dependencies built on top of `Airflow.v.2.6.0`.
- navigate to the `docker-airflow` directory, this is where the `Dockerfile` is located:
    - `Dockerfile` is a `.dockerfile` file that contains the instructions to build the image.
    - `lakehouse/airflow` --> `airflow-setup` --> `Dockerfile`.
- It will take about ***10minutes*** to build, depending on yor internet speed / platform you use to build the image.
- Run the following command to build the image:

```
docker build --rm --force-rm -t oasiscorp:latest . 
```
### Airflow Init.
- navigate  to: 👉🏼 : `lakehouse/airflow/airflow-setup`

- You must run this `once` before you can get started. This is the initial bootstrap process. 
- You will see a bunch of debug logging during this process. You can scroll through this to see what the initalization process is doing. 
- Ultimately, this process is in charge of running the database setup work and migrations, bootstrapping and all initalization scripts. 
- This is essentially, everything you need to get up and running on Apache Airflow.
- Run the following command to run the init:

~~~
docker-compose up airflow-init
~~~

- output:

![](./doc/air-init.png "Initialize")

- This will create the Airflow database and the Airflow USER. 
- Once we have the Airflow database and the Airflow USER, we can start the Airflow services:

![](./doc/cooked.png "Ready")

<br>

### Starting Services
After running airflow-init & pulling the necessary images, you're ready to rock n roll. 
- Navigate to the `docker` directory:
- Run the following command to start the services:

~~~
docker compose -f docker-compose.yml -f docker-compose.spark.yml up -d
~~~


To ensure the services are running, you can click on the following URLs:


## Table of Docker Images and Services

| Docker Image | Docker Hub Link | Port | Service | Description |
|--------------|-----------------|------|---------|-------------|
| apache/airflow:2.6.0 | [Link](https://hub.docker.com/r/apache/airflow) | [8085](http://localhost:8085) | Airflow | Airflow is a platform created by the community to programmatically author, schedule and monitor workflows.|
| bde2020/spark-master:3.2.0-hadoop3.2 | [Link](https://hub.docker.com/r/bde2020/spark-master) | [8080](http://localhost:8080) | Spark Master | Spark Master is the heart of the Spark application. It is the central coordinator that schedules tasks on worker nodes.|
| bde2020/spark-worker:3.2.0-hadoop3.2 | [Link](https://hub.docker.com/r/bde2020/spark-worker) | [8081](http://localhost:8081) | Spark Worker | Spark Worker is the node that runs the tasks assigned by the Spark Master.|
| jupyter/pyspark-notebook:spark-3.2.0 | [Link](https://hub.docker.com/r/jupyter/pyspark-notebook) | [8888](http://localhost:8888) | Jupyter Notebook | Jupyter Notebook is an open-source web application that allows you to create and share documents that contain live code, equations, visualizations and narrative text.|
| postgres:9.5.3 | [Link](https://hub.docker.com/_/postgres) | [5432](http://localhost:5432) | Postgres | PostgreSQL is a powerful, open source object-relational database system.|
| bitnami/zookeeper:3.7.0 | [Link](https://hub.docker.com/r/bitnami/zookeeper) | [2181](http://localhost:2181) | Zookeeper | ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.|
| apache/nifi-registry:latest | [Link](https://hub.docker.com/r/apache/nifi-registry) | [18080](http://localhost:18080) | Nifi Registry | NiFi Registry is a complementary application that provides a central location for storage and management of shared resources across one or more instances of NiFi and/or MiNiFi.|
| apache/nifi:1.15.0 | [Link](https://hub.docker.com/r/apache/nifi) | [8091](http://localhost:8091) | Nifi | Apache NiFi supports powerful and scalable directed graphs of data routing, transformation, and system mediation logic.|
| minio/minio | [Link](https://hub.docker.com/r/minio/minio) | [9000](http://localhost:9000) | Minio | MinIO is a high performance, distributed object storage system.|
| minio/mc | [Link](https://hub.docker.com/r/minio/mc) | [9000](http://localhost:9000) | Minio Client | MinIO Client (mc) provides a modern alternative to UNIX commands like ls, cat, cp, mirror, diff, find etc. It supports filesystems and Amazon S3 compatible cloud storage service (AWS Signature v2 and v4).|
| redis:latest | [Link](https://hub.docker.com/_/redis) | [6379](http://localhost:6379) | Redis | Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker.|


## Status of Containers

To check the status of the containers, run the following command:

```
docker ps
```

## Spark Architecture 
* Apache Spark is an open source - data processing engine for large datasets. 
* It is highly scalable and enables users to perform large-scale data transformation and analysis. Also enables stream data analysis in real-time.
* The Spark architecture is a distributed processing framework, as shown below:

![](./doc/architecture.png "Blueprint")



### Connecting Spark with Airflow via Airflow DAG

1. Go to the Spark webUI on http://localhost:8085

2. Click on `Admin` ->  `Connections` in the top bar. 

3. Click on `Add a new record` and input the following details:

- Conn Id:  `spark_connect`  - This is the name of the connection.
- Conn Type: `Spark` - This is the type of connection.
- Host: `spark://spark-master` - This is the hostname of the Spark Master.
- Port: `7077`  - This is the port of the Spark Master.
- Extra: `{"queue": "root.default"}` - This is the name of the queue that the Spark job will be submitted to.

4. Save the connection settings. 

![](./doc/sparkcon.png "Spark DAG")

5. Run the `SparkOperatorDemo` DAG.

6. After a couple minutes you should see the DAG run as successful. 

![](./doc/sparkdag.png "Spark DAG")

7. Check the DAG log for the result.

![](./doc/sparklog.png "Spark DAG")

8. Check the Spark UI http://localhost:8181 for the result of our DAG & Spark submit via terminal:

![](./doc/sparkui.png "Spark DAG")

## Dockerfile for Jupyter Notebook with Spark

This Dockerfile sets up a Jupyter Notebook environment with Apache Spark installed, enabling you to run Spark jobs within Jupyter notebooks.

### Instructions

To use this Dockerfile, follow these steps:

1. Build the Docker image: `docker build -t jupyter-spark .`

2. Run the Docker container: `docker run -p 8888:8888 jupyter-spark`

3. For Jupyter notebook, you must copy the URL with the token generated when the container is started and paste in your browser. 

4. The URL with the token can be taken from container logs using:
 
```
docker logs $(docker ps -q --filter "ancestor=jupyter/pyspark-notebook:spark-3.2.0") 2>&1 | grep 'http://127.0.0.1' | tail -1

```


### Spark Installation

The Dockerfile downloads and installs Apache Spark based on the specified versions. The Spark binaries are fetched from the Apache archive.

- If `scala_version` is not provided, Spark is downloaded without Scala support.
- If `scala_version` is provided, Spark is downloaded with Scala support.

The downloaded Spark archive is extracted to `/usr/local`.

### Spark Configuration

The Dockerfile sets the necessary environment variables for Spark:

- `SPARK_HOME` is set to `/usr/local/spark`, the installation directory.
- `SPARK_OPTS` defines additional options for the Spark driver, such as memory allocation and log level.
- The `PATH` variable is updated to include the Spark binaries (`${SPARK_HOME}/bin`).

A symbolic link is created to the Spark installation directory based on the specified versions, ensuring `SPARK_HOME` is correctly set.

Additionally, a link is created in the `before_notebook` hook to automatically source the `PYTHONPATH` environment variable.

### Additional Notes

The Dockerfile also creates the directory `/usr/local/bin/before-notebook.d` and creates a symbolic link to the `spark-config.sh` script in the Spark sbin directory. This allows you to configure Spark before starting the Jupyter Notebook.

Refer to the official Apache Spark documentation for further information on configuring and using Spark with Jupyter Notebook.


## Spark Master & Worker

- Spark Master is the heart of the Spark application. It is the central coordinator that schedules tasks on worker nodes.
- Spark Worker is the node that runs the tasks assigned by the Spark Master.

The Spark Master and Worker are configured using the following environment variables:

- `SPARK_MASTER_HOST` is set to `spark-master` to ensure the Spark Master is accessible from the Spark Worker.
- `SPARK_MASTER_PORT` is set to `7077` to ensure the Spark Master is accessible from the Spark Worker.
- `SPARK_MASTER_WEBUI_PORT` is set to `8080` to ensure the Spark Master UI is accessible from the host.
- `SPARK_WORKER_WEBUI_PORT` is set to `8081` to ensure the Spark Worker UI is accessible from the host.



## Airflow: http://localhost:8085

Airflow UI Login: 
* username: airflow 
* password: airflow

## Spark: http://localhost:8181

* Spark Master & Workers.


## Minio: http://localhost:9001

* Minio is the best server which is suited for storing unstructured data such as photos, videos, log files, backups, and container.
* This would serve as our Object Storage Service. 

## Postgres
- Access to the Postgres database is available using the following command:

```
docker exec -it postgres_container psql -U hive

```

## Nifi: http://localhost:8091/nifi/

* NiFi is the best server which is suited for processing data.
* This would serve as our Data Processing Service.


## Nifi Registry: http://localhost:18080/nifi-registry

* NiFi Registry is the best server which is suited for storing and retrieving data.
* This would serve as our Data Storage Service.





## Connecting Postgres with Airflow via Airflow DAG

- In this scenario, we are going to schedule a dag file to create a table and insert data into it in PostgreSQL using the Postgres Operator.
- The DAG file we're executing is named `hello-postgres` in our DAGs folder. 
- Our DAG file will have two simple tasks of using SQL query to create_table & insert_data into our 'test' database. 
- After setting up our DAG, we need to configure the connection details in Airflow. 
- Open the service in your browser at http://localhost:8085 and create a connection.
- Click on `Admin` ->  `Connections` in the top bar. 
- Let's create a new one for our purpose.

Click on Create and fill in the necessary details:

- Conn Id : `postgres_connect` - the ID with which we can retrieve the connection details later on.
- Conn Type : `Postgres` - Select it from the dropdown menu.
- Host : `postgres` - {defined in the .env file}
- Schema : `metastore` - the database name.
- Login : `airflow` - or whichever username you set in your docker-compose.yml file.
- Password : `airflow`  - or whichever password you set in your docker-compose.yml file.
- Posrt : `5432`  - the standard port for the database within the docker network.

Click on save: Creating the connection airflow to connect the Postgres DB.

- Head back to the Airflow UI, activate the DAG on the left and click on "Trigger DAG" on the right-hand side. DAG Succesful 

### Validate DAG

- A little sanity check to make sure the DAG is worked and our SQL tables have been populated.
- We're going to head into the postgres container 
- Navigate to the `docker` directory:
- Run the following command:

```
docker exec -it  postgres_container psql -U airflow metastore
```

- After gaining acces, we can run a SQL query to validate the data has been inserted.

![](./doc/postgres2.png "SQL")


## Connecting Minio with Airflow via Airflow DAG

1. Go to the Minio webUI on http://localhost:9000
2. Click on bucket icon on the left-menu Bar marked red below the create a S3 Bucket with name `miniobucket`.
3. locally create a new file named minio_testfile.txt with the content "This is the content of a testfile from MinIO".
4. Select your bucket and click on Browse. Create a new directory called test by click on the icon marked in red.
5. Upload a .txt file (`testfile.txt`) from your local directory to the test folder in the S3 bucket below. 
6. After setting up our `Conn Id` DAG, we need to configure the connection details in Airflow. 
7. Open the service in your browser at http://localhost:8085 and click on `Admin` ->  `Connections` in the top bar. 

Click on Create and fill in the necessary details:

- Conn Id :`myminio_connection`  - the ID with which we can retrieve the connection details later on.
- Conn Type : `S3`  - Select it from the dropdown menu.
- Extras:  
```
{"aws_access_key_id": "xxxx", "aws_secret_access_key": "xxxxxx", "host": "http://minio:9000"}
```

### Validate DAG

- A little sanity check to make sure the DAG is worked and our Minio bucket has been modified.
- We're going to head into the Minio UI http://localhost:9000

![](./doc/miniodag.png "minio")


# Extras and Useful Commands

## Adding New Users: Airflow

* airflow-init:
    * The initialization service. This sets up a database in the Airflow UI and creates users to login into the UI. 
    * You can add a user via the airflow command line interface (cli) by typing the following command 

```
airflow users create -u <USERNAME> -f <FIRST> -l <LAST> -r <ROLE> -e <EMAIL>
```

## Memory and CPU utilization

When all the containers are running, you can experience system lag if your system is not able to handle the load. Monitoring the CPU and Memory utilization of the containers is crucial to maintaining good performance and a reliable system. To monitor the CPU and Memory utilization of the containers, we use the Docker command-line tool stats command, which gives us a live look at our containers resource utilization. We can use this tool to gauge the CPU, Memory, Network, and disk utilization of every running container.

```
docker stats
```
## Docker Commands

    List Images:
    $ docker images <repository_name>

    List Containers:
    $ docker container ls

    Check container logs:
    $ docker logs -f <container_name>

    To build a Dockerfile after changing sth (run inside directoty containing Dockerfile):
    $ docker build --rm -t <tag_name> .

    Access container bash:
    $ docker exec -it <container_name> bash

    Remove Images & Containers:
    $ docker system prune -a

    Remove Volumes:
    $ docker volume prune

## Useful docker-compose commands

    Start Containers:
    $ docker-compose -f <compose-file.yml> up -d

    Stop Containers:
    $ docker-compose -f <compose-file.yml> down --remove-orphans

    Stop Containers & Remove Volumes:
    $ docker-compose -f <compose-file.yml> down --remove-orphans -v

## Postgres 

enter the Postgres Conatiner via CLI command :

```
docker exec -it  postgres_container psql 
```


## .env

Before starting Airflow for the first time, we need to prepare our environment. We need to add the Airflow USER to our .env file because some of the container’s directories that we mount, will not be owned by the root user. The directories are:

- ./dags - you can put your DAG files here.
- ./logs - contains logs from task execution and scheduler.
- ./plugins - you can put your custom plugins here.

```
mkdir -p ./dags ./logs ./plugins
chmod -R 777 ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" >> .env
echo -e "AIRFLOW_GID=0" >> .env

```

## Why do we need an ETL pipeline?

Assume we had a set of data that we wanted to use. However, this data is unclean, missing information, and inconsistent as with most data. One solution would be to have a program clean and transform this data so that:

- There is no missing information
- Data is consistent
- Data is fast to load into another program
- With smart devices, online communities, and E-Commerce, there is an abundance of raw, unfiltered data in today’s industry.
- However, most of it is squandered because it is difficult to interpret due to it being tangled. ETL pipelines are available to combat this by automating data collection and transformation so that analysts can use them for business insights.


## Modern Data Lake with Minio

- I will walk-through a step-by-step process to demonstrate how we can leverage 
- an S3-Compatible Object Storage [Minio](https://blog.min.io/modern-data-lake-with-minio-part-1/) and a Distributed SQL query engine [Trino](https://hub.docker.com/r/trinodb/trino) to achieve this.      
- Minimal example to run Trino with Minio and the Hive standalone metastore on Docker.

### Installation and Setup

Install [s3cmd](https://s3tools.org/s3cmd) with:

```bash
sudo apt update
sudo apt install -y \
    s3cmd \
    openjdk-11-jre-headless  # Needed for trino-cli
```

Pull and run all services with:

```bash
docker-compose up
```

Configure `s3cmd` with (or use the `minio.s3cfg` configuration):

```bash
s3cmd --config minio.s3cfg --configure
```

Use the following configuration for the `s3cmd` configuration when prompted:

```
Access Key: minio_access_key
Secret Key: minio_secret_key
Default Region [US]:
S3 Endpoint [s3.amazonaws.com]: localhost:9000
DNS-style bucket+hostname:port template for accessing a bucket [%(bucket)s.s3.amazonaws.com]: localhost:9000
Encryption password:
Path to GPG program [/usr/bin/gpg]:
Use HTTPS protocol [Yes]: no
```

To create a bucket and upload data to minio, type:

```bash
s3cmd --config minio.s3cfg mb s3://iris
s3cmd --config minio.s3cfg put data/iris.parq s3://iris
```
To list all object in all buckets, type:

```bash
s3cmd --config minio.s3cfg la
```


## User defined network 
User-defined bridges provide automatic DNS resolution between containers, meaning one container will be able to “talk” to the other containers in the same network of docker containers. On a user-defined bridge network (like oasiscorp in our case), containers can resolve each other by name or alias. This is very practical as we won't have to manually look up and configure specific IP addresses.

## Official Docker Image Docs
https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html
