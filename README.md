# Building an ETL(Extract, Transform and Load) pipeline using Python, PostgresSQL, PySpark and Airflow.
This post will detail how to build an ETL (Extract, Transform and Load) pipeline.

## Prerequisites
Definition:
- ETL is the general procedure of copying data from one or more sources into a destination system that represents the data differently from the source(s) or in a different context than the source(s). 
- ***Data Extraction*** involves extracting data from (one or more) homogeneous or heterogeneous sources; 
- ***Data Transformation*** processes data by data cleaning and transforming it into a proper storage format/structure for the purposes of querying and analysis; 
- Finally, ***Data Loading*** describes the insertion of data into the final target database such as an operational `data store` , `data mart` , `data lake` or a `data warehouse`. 

Before we head towards setting up Airflow, let's do a quick overvirew. 
-  [***Apache Airflow***](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html), is an open-source tool for orchestrating complex computational workflows and creating a data processing pipeline. Think of it as a fancy version of a <u>job scheduler or cron job</u>. 
-  A `workflow`  is a series of tasks that are executed in a specific order and we call them `DAGs`. 
-  A  `DAG` <u>(Directed Acyclic Graph)</u> is a graph that contains a set of tasks that are connected by dependencies or a graph with nodes connected via directed edges.

## Setting Up Airflow
- Okay now that we got the basics of what Airflow and DAGs are, let’s set up Airflow. 
- First, we will need to create our custom Airflow Docker image. This image adds and installs a list of Python packages that we will need to run the ETL (Extract, Transform and Load) pipeline.

### Docker Image Build via Dockerfile 
navigate to 

```
docker > airflow-setup > Dockerfile 
```

- The project contains a `Dockerfile` that contians installations of `JAVA-JDK.v11`, `ApacheSpark.v3.2.1`, `Hadoop.v3.2`, & other dependencies built on top of `Airflow.v.2.2.3` .


### Docker Compose File
navigate to 

```
docker > docker-compose.yaml
```
- After creating the foundation of our project in the Dockerfile we can move towards running containers and starting up services. The airflow-docker-compose.yaml below is a modified version of the official Airflow Docker. We have added the following changes:

  - Customized Airflow image that includes the installation of Python dependencies.
  - A custom network (`oasiscorp`) for bridging the containers, this will enable the containers to exist within a shared network.
  - Removes example DAGs.
  - Add our .env file to the Airflow container and,
  - Added hostnames for better IP recogntion. 

The docker-compose.yaml file when deployed will start a list of containers namely:

- `airflow-scheduler` - The scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete.
- `airflow-webserver` - The webserver is available at http://localhost:8080.
- `airflow-worker`  - The worker that executes the tasks given by the scheduler.
- `airflow-init`  - The initialization service.
- `flower ` - The flower app for monitoring the environment. It is available at http:/localhost:5555.
- `postgres`  - The database.
- `redis`  - The redis-broker that forwards messages from scheduler to worker.


## Development

## Clone project

    $ git clone https://github.com/le-oasis/airflow-docker-spark


## Build Image

Build our image from the Dockerfile located in the airflow-docker-spark folder

```
docker build -t docker-prunedge:latest .
```



## Add the Environment File
This will enable the local host runtime and the container runtime to work with the same user. *This is needed for Linux or Linux-style environments - which includes Mac*

~~~
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
~~~


## Airflow Init
You must run this `once` before you can get started. This is the initial bootstrap process. This process will download all of the required Docker container images, and run the initialization sequence required to run Airflow.

~~~
docker-compose up airflow-init
~~~

You will see a bunch of debug logging during this process. You can scroll through this to see what the initalization process is doing. Ultimately, this process is in charge of running the database setup work and migrations, bootstrapping and all initalization scripts. 
Essentially, everything you need to get up and running on Apache Airflow.

- When we run the `docker-compose up airflow-init` command, we will see the following output:

![](./doc/air-init.png "Initialize")
This will create the Airflow database and the Airflow USER. Once we have the Airflow database and the Airflow USER, we can start the Airflow services.

## Personal Rule of Thumb
For ease of use, before starting services, please pull the required docker images first.
~~~
docker pull bitnami/minio:latest
~~~
~~~
docker pull bitnami/spark:latest
~~~
~~~
docker pull jupyter/pyspark-notebook:spark-3.1.2
~~~


navigate to 

```
pwd > docker 
```

## Starting Services
After running airflow-init & pulling the necessary images, you're ready to rock n roll. Copy and paste the following to your terminal. 
~~~
docker compose  -f docker-compose.yaml  -f docker-compose.spark.yaml up -d
~~~


# Access & Login

Airflow: http://localhost:8080

Airflow UI Login: 
* username: airflow 
* password: airflow

Minio: http://localhost:9000

* username: minio 
* password: miniosecret

Spark Master: http://localhost:8181
Jupyter: http://localhost:8888


Postgres - Database airflow:

* Server: localhost:5432
* Database: airflow
* User: airflow
* Password: airflow

Jupyter Notebook: http://127.0.0.1:8888
  * For Jupyter notebook, you must copy the URL with the token generated when the container is started and paste in your browser. The URL with the token can be taken from container logs using:
 
```
docker logs $(docker ps -q --filter "ancestor=jupyter/pyspark-notebook:latest") 2>&1 | grep 'http://127.0.0.1' | tail -1

```


  
        $ docker logs -f jupyter_container



# FYI

## Why do we need an ETL pipeline?

Assume we had a set of data that we wanted to use. However, this data is unclean, missing information, and inconsistent as with most data. One solution would be to have a program clean and transform this data so that:

- There is no missing information
- Data is consistent
- Data is fast to load into another program
- With smart devices, online communities, and E-Commerce, there is an abundance of raw, unfiltered data in today’s industry.
- However, most of it is squandered because it is difficult to interpret due to it being tangled. ETL pipelines are available to combat this by automating data collection and transformation so that analysts can use them for business insights.


## User defined network 
User-defined bridges provide automatic DNS resolution between containers, meaning one container will be able to “talk” to the other containers in the same network of docker containers. On a user-defined bridge network (like oasiscorp in our case), containers can resolve each other by name or alias. This is very practical as we won't have to manually look up and configure specific IP addresses.

## Adding New Users

* airflow-init:
    * The initialization service. This sets up a database in the Airflow UI and creates users to login into the UI. 
    * For our UI:
    * Username: airflow
    * Password: airflow 
    * You can add a user via the airflow command line interface (cli) by typing the following command 

```
airflow users create -u <USERNAME> -f <FIRST> -l <LAST> -r <ROLE> -e <EMAIL>
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


## Docker-compose.spark.yaml 
docker > docker-compose.spark.yaml

- Here's the settings for our second .yaml file:

* minio: Object Storage.
    * Minio is the best server which is suited for storing unstructured data such as photos, videos, log files, backups, and container.
    * This would serve as our Object Storage Service. 
    * Port: 9000
    * References: 
      * https://quay.io/repository/minio/minio?tab=tags&tag=RELEASE.2022-06-11T19-55-32Z

Apache Spark implementation (docker-compose.spark.yml)

* spark: Spark Master.
    * The process that requests resources in the cluster and makes them available to the Spark Driver.
    * Image: bitnami/spark:latest
    * Port: 8181
    * References: 
      * https://github.com/bitnami/bitnami-docker-spark
      * https://hub.docker.com/r/bitnami/spark/tags/?page=1&ordering=last_updated

* spark-worker-N: 
    * Workers (slaves) are running Spark instances where executors live to execute tasks. They are the compute nodes in Spark.
    * Image: bitnami/spark:latest
    * References: 
      * https://github.com/bitnami/bitnami-docker-spark
      * https://hub.docker.com/r/bitnami/spark/tags/?page=1&ordering=last_updated

* jupyter-spark: 
  * Jupyter notebook with pyspark for interactive development.
  * Image: jupyter/pyspark-notebook:spark-3.1.2
  * Port: 8888
  * References: 
    * https://hub.docker.com/layers/jupyter/pyspark-notebook/spark-3.1.2/images/sha256-37398efc9e51f868e0e1fde8e93df67bae0f9c77d3d3ce7fe3830faeb47afe4d?context=explore
    * https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-pyspark-notebook
    * https://hub.docker.com/r/jupyter/pyspark-notebook/tags/



### Official Docker Image Docs
https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html