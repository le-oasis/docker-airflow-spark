# Datalakehouse Preparation with Apache Airflow, Docker & Apache Spark.
Hello World, welcome to the Oasis. 
Fasten your seatbelts as we present to you a Data Engineering Architecture that facilitates distributed data processing (Apache Spark) & schedluing processing tasks (Apache Airflow).

Prerequisites
* Apache Airflow is a tool to express and execute workflows as directed acyclic graphs (DAGs).
* Apache Spark utilizes in-memory caching and optimized query execution to provide a fast and efficient big data processing solution. 
* Environment Variables: are a set of configurable values that allow you to dynamically fine tune your Airflow deployment. They’re defined in the airflow.cfg.

This project contains the following containers and thier environment variables:

* Airflow: For Airflow to work, we downloaded the raw [yaml](https://airflow.apache.org/docs/apache-airflow/2.3.2/docker-compose.yaml) file and made some environment varibale changes to the default settings. 
    * Image: [apache/airflow:2.3.2](https://hub.docker.com/r/apache/airflow)
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

* airflow-trigger:
    * This triggers the DAG automatically based on the specified scheduling parameters.
    * command: triggerer
    * References: 
      * https://hub.docker.com/r/apache/airflow/tags

* airflow-init:
    * The initialization service. This sets up a database in the Airflow UI and creates users to login into the UI. 
    * For our UI:
    * Username: admin
    * Password: poolp 
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
    * Image: bitnami/spark:3.1.2
    * Port: 8181
    * References: 
      * https://github.com/bitnami/bitnami-docker-spark
      * https://hub.docker.com/r/bitnami/spark/tags/?page=1&ordering=last_updated

* spark-worker-N: 
    * Workers (slaves) are running Spark instances where executors live to execute tasks. They are the compute nodes in Spark.
    * Image: bitnami/spark:3.1.2
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

## Architecture components
## Setup

### Clone project

    $ git clone https://github.com/le-oasis/airflow-docker-spark

### Build Image

Build our image from the Dockerfile located in the airflow-docker-spark folder

    $ docker build --rm --force-rm -t prunedge  .

### Start Services

    $ docker-compose -f docker-compose.spark.yml up

Note: when running the docker-compose for the first time, the images `postgres:13`, `apache/airflow:2.3.2`, `bitnami/minio` ,`bitnami/spark:3.1.2` and `jupyter/pyspark-notebook:spark-3.1.2` will be downloaded before the containers started.

### Check if you can access

Airflow: http://localhost:8080

Spark Master: http://localhost:8181


Postgres - Database airflow:

* Server: localhost:5432
* Database: airflow
* User: airflow
* Password: airflow

Jupyter Notebook: http://127.0.0.1:8888
  * For Jupyter notebook, you must copy the URL with the token generated when the container is started and paste in your browser. The URL with the token can be taken from container logs using:
  
        $ docker logs -f docker_jupyter-spark_1

