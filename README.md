# Datalakehouse via Apache Airflow, Docker & Apache Spark.
## Setting Up Airflow for a Data Warehouse
- Airflow Version: 2.2.3
- The original yaml file [yaml](https://airflow.apache.org/docs/apache-airflow/2.2.3/docker-compose.yaml) was edited for ease of use on any system.
- These directions are provided from the [Official Airflow Docker Documentation](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)

## Clone project

    $ git clone https://github.com/le-oasis/airflow-docker-spark


## Docker File 

- The Docker File contains `JAVA-JDK.v11`, `ApacheSpark.v3.0.1`, & `Hadoop.v3.2` built on top of `Airflow.v2.2.3` 
-  To use `Apache Spark` along with the `Apache Airflow` containers, you need to install the `apache-airflow-providers-apache-spark` plugin, the provider was installed along with numpy and pandas 😊.
-  This was defined in the Docker Image, you can extend your packages by adding them in the `requirements.txt`.


## Build Image

Build our image from the Dockerfile located in the airflow-docker-spark folder

    $ docker build --rm --force-rm -t prunedge .


## Pull Image from Docker Hub

- Another option is the pull the image hosted on my [Dockerhub](https://hub.docker.com/r/mahmud1400/prunedge/tags)

    $ docker pull mahmud1400/prunedge:latest


## Add the Environment File
This will enable the local host runtime and the container runtime to work with the same user. *This is needed for Linux or Linux-style environments - which includes Mac*

~~~
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
~~~


## Initial Setup Work
You must run this `once` before you can get started. This is the initial bootstrap process. This process will download all of the required Docker container images, and run the initialization sequence required to run Airflow.

~~~
docker-compose up airflow-init
~~~

You will see a bunch of debug logging during this process. You can scroll through this to see what the initalization process is doing. Ultimately, this process is in charge of running the database setup work and migrations, bootstrapping and all initalization scripts. Essentially, everything you need to get up and running on Apache Airflow.


## Personal Rule of Thumb
For ease of use, before starting services, pull the required docker images first.
~~~
docker pull bitnami/minio:latest
~~~
~~~
docker pull bitnami/spark:latest
~~~
~~~
docker pull jupyter/pyspark-notebook:spark-3.1.2
~~~


## Starting Services
After running airflow-init & pulling the necessary images, you're ready to rock n roll 
~~~
docker compose  -f docker-compose.yaml  -f docker-compose.spark.yaml up -d
~~~


# Access & Login

Airflow: http://localhost:8080

Airflow UI Login: 
* username: airflow 
* password: airflow

Minio: http://localhost:9000
Airflow UI Login: 
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
  
        $ docker logs -f jupyter_container


# Theory & Implementation

## User defined network 
User-defined bridges provide automatic DNS resolution between containers, meaning one container will be able to “talk” to the other containers in the same network of docker containers. On a user-defined bridge network (like oasiscorp in our case), containers can resolve each other by name or alias. This is very practical as we won't have to manually look up and configure specific IP addresses.

## Theory

This project contains the following containers and thier environment variables:

* Airflow: For Airflow to work, we downloaded the raw [yaml](https://airflow.apache.org/docs/apache-airflow/2.3.2/docker-compose.yaml) file and made some environment varibale changes to the default settings. 
    * Image: [apache/airflow:2.2.3](https://hub.docker.com/r/apache/airflow)
    * AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    * _PIP_ADDITIONAL_REQUIREMENTS:- apache-airflow-providers-apache-spark
    * Refrences:
      * https://hub.docker.com/r/apache/airflow/tags

* airflow-webserver:
    * This is the UI of Airflow, that can be used to get an overview of the overall health of different Directed Acyclic Graphs (DAG) and also help in visualizing different components and states of each DAG.
    * command: webserver
    * References: 
      * https://hub.docker.com/r/apache/airflow/tags

* airflow-scheduler:
    * The Airflow scheduler monitors all tasks and all DAGs, and triggers the task instances whose dependencies have been met.
    * command: scheduler
    * References: 
      * https://hub.docker.com/r/apache/airflow/tags

* airflow-worker:
    * Airflow workers listen to, and process, queues containing workflow tasks.
    * command: celery worker
    * References: 
      * https://hub.docker.com/r/apache/airflow/tags


* airflow-init:
    * The initialization service. This sets up a database in the Airflow UI and creates users to login into the UI. 
    * For our UI:
    * Username: airflow
    * Password: airflow 
    * You can add a user via the airflow command line interface (cli) by typing the following command 

```
airflow users create -u <USERNAME> -f <FIRST> -l <LAST> -r <ROLE> -e <EMAIL>
```


* redis:
    * A broker that forwards messages from scheduler to worker.
    * Image: redis:latest
    * Port: 6379
    * References: 
      * https://hub.docker.com/_/redis?tab=tags

* postgres:
    * The database for Airflow UI. 
    * Image: [postgres:13](https://hub.docker.com/_/postgres)
    * Database Port: 5432
    * POSTGRES_USER: airflow 
    * POSTGRES_PASSOWRD: airflow
    * References: https://hub.docker.com/_/postgres

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