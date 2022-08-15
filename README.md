# Building a Modern Data Lake with Minio, Spark, Airflow via Docker.

## Overview
This system utilises the lakehouse data-lake architecture to store and compute data for enterprises.
This readme file will detail how to build an ELT (Extract, Load and Transform) pipeline and connect services that support the Data Lake.

## Setting Up the Data Lake

## Docker Images 
- For ease of use, before starting services, please pull the required docker images first.
- Run the following commands in order to pull the required docker images.

~~~
docker pull apache/airflow:2.2.3
~~~
~~~
docker pull bde2020/spark-master:3.3.0-hadoop3.3
~~~
~~~
docker pull bde2020/spark-worker:3.3.0-hadoop3.3
~~~
~~~
docker pull jupyter/pyspark-notebook:spark-3.2.1
~~~
~~~
docker pull postgres:latest
~~~
~~~
docker pull bitnami/zookeeper:3.7.0
~~~
~~~
docker pull apache/nifi-registry:latest
~~~
~~~
docker pull apache/nifi:1.15.0
~~~
~~~
docker pull docker.io/bitnami/minio:2022
~~~
~~~
docker pull minio/mc
~~~
~~~
docker pull redis:latest
~~~
## Dockerfile: Build the Image.
- A `Dockerfile`  is a text document that contains all the commands a user could call on the command line to assemble an image. 
- `Dockerfile` that contians installations of `JAVA-JDK.v11`, `ApacheSpark.v3.3.0`, `Hadoop.v3`, & other dependencies built on top of `Airflow.v.2.2.3`.
- navigate to the `docker-airflow` directory, this is where the `Dockerfile` is located:
    - `Dockerfile` is a `.dockerfile` file that contains the instructions to build the image.
    - `docker` --> `airflow-setup` --> `Dockerfile`.
- It will take about ***10minutes*** to build, depending on yor internet speed / platform you use to build the image.
- Run the following command to build the image:

```
docker build --rm --force-rm -t docker-prunedge:latest . 
```
## Airflow Init.
- navigate back to: 👉🏼 : `docker`

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

## Starting Services
After running airflow-init & pulling the necessary images, you're ready to rock n roll. 
- Navigate to the `docker` directory:
- Run the following command to start the services:

~~~
docker compose -f docker-compose.yml -f docker-compose.spark.yml up -d
~~~


To ensure the services are running, you can click on the following URLs:

### Jupyter: http://localhost:8888

* For Jupyter notebook, you must copy the URL with the token generated when the container is started and paste in your browser. 
* The URL with the token can be taken from container logs using:
 
```
docker logs $(docker ps -q --filter "ancestor=jupyter/pyspark-notebook:spark-3.2.1") 2>&1 | grep 'http://127.0.0.1' | tail -1
```

### Airflow: http://localhost:8085

Airflow UI Login: 
* username: airflow 
* password: airflow

### Spark: http://localhost:8181

* Spark Master & Workers.


### Minio: http://localhost:9001

* Minio is the best server which is suited for storing unstructured data such as photos, videos, log files, backups, and container.
* This would serve as our Object Storage Service. 

### Postgres
- Access to the Postgres database is available using the following command:

```
docker exec -it  mcstore-postgresdb psql -U airflow

```

### Nifi: http://localhost:8091/nifi/

* NiFi is the best server which is suited for processing data.
* This would serve as our Data Processing Service.


### Nifi Registry: http://localhost:18080/nifi-registry

* NiFi Registry is the best server which is suited for storing and retrieving data.
* This would serve as our Data Storage Service.


## Spark Architecture 
* Apache Spark is an open source - data processing engine for large datasets. 
* It is highly scalable and enables users to perform large-scale data transformation and analysis. Also enables stream data analysis in real-time.
* The Spark architecture is a distributed processing framework, as shown below:

![](./doc/architecture.png "Blueprint")


## Connecting Spark with Airflow via Airflow DAG
1. Configure a Spark Connection by Accessing the AirflowUI http://localhost:8085 and creating a connection.
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


## Connecting Postgres with Airflow via Airflow DAG

- In this scenario, we are going to schedule a dag file to create a table and insert data into it in PostgreSQL using the Postgres Operator.
- The DAG file we're executing is named `hello-postgres` in our DAGs folder. 
- Our DAG file will have two simple tasks of using SQL query to create_table & insert_data into our 'test' database. 
- After setting up our DAG, we need to configure the connection details in Airflow. 
- Open the service in your browser at http://localhost:8085 and create a connection.
- Click on `Admin` ->  `Connections` in the top bar. 
- Let's create a new one for our purpose.

Click on Create and fill in the necessary details:

- Conn Id : `postgres_air` - the ID with which we can retrieve the connection details later on.
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
docker exec -it  mcstore-postgresdb psql -U airflow metastore
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
docker exec -it  mcstore-postgresdb bash 
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
