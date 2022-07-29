# Building on Top of Airflow version 2.2.3
# AUTHOR: Mahmud Oyinloye 
# Contributors: Demilade Somide, John Oloniyo
# Supervising Line Manager: Oladimeji Oladepo
# DESRIPTION: AIRFLOW Container with Java 11 and SPARK BINARIES 
# BUILD: docker build --rm --force-rm -t docker-prunedge:latest . 
# BASED ON: https://github.com/puckel/docker-airflow
# INSPIRED BY: https://github.com/cordon-thiago/airflow-spark


# Airflow Image Definition 
ARG AIRFLOW_BASE_IMAGE=apache/airflow:2.2.3
ARG AIRFLOW_HOME=/opt/airflow
FROM docker.io/${AIRFLOW_BASE_IMAGE}


# Spark & Hadoop Versions 
ENV SPARK_VERSION=3.3.0
ENV HADOOP_VERSION=3
ENV SPARK_INSTALL_ROOT=/spark

# Spark Environment 
# Spark Home
ENV SPARK_HOME=${SPARK_INSTALL_ROOT}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

# Let's Rock n Roll
USER root

# Install Airflow Extras, please edit depending on your project requirements
ARG AIRFLOW_EXTRAS="apache.atlas,apache.spark,apache.hive,amazon,jdbc,sqlite,celery,postgres,redis,mysql,ssh"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        vim-tiny \
        nano-tiny \
        wget \
        unzip \
        bzip2 \
        build-essential \
        ca-certificates \
        curl \
        libsasl2-dev \
        sudo \
        jq \
        locales \
        fonts-liberation \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/nano nano /bin/nano-tiny 10 \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

# Copy a script that we will use to correct permissions after running certain commands
COPY fix-permissions /usr/local/bin/fix-permissions
RUN chmod a+rx /usr/local/bin/fix-permissions


# Configure Locale
# Configure some required variables
ENV SHELL=/bin/bash \
    NB_USER=$NB_USER \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

# Directory for Spark Binaries (SPARK_INSTALL_ROOT)
RUN mkdir "${SPARK_INSTALL_ROOT}"
USER $USER


# Install Spark Binaries (Spark 3.2.1)
RUN cd "${SPARK_INSTALL_ROOT}" && \
    wget --show-progress https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz


# Install Java
ARG JAVA_LIBRARY=openjdk-11-jdk-headless
ENV JAVA_LIBRARY=${JAVA_LIBRARY}
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ${JAVA_LIBRARY} \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \ 
    && apt-get install libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Airflow Packages & Providers
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow/airflow.cfg
# RUN chown -R airflow: ${AIRFLOW_HOME}

#https://airflow.apache.org/docs/apache-airflow/stable/extra-packages-ref.html
USER airflow
RUN pip install apache-airflow[${AIRFLOW_EXTRAS}]
COPY requirements.txt .
# RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir --user apache-airflow-providers-apache-spark
RUN pip install --no-cache-dir --user boto3
RUN pip install --no-cache-dir --user airflow-clickhouse-plugin[pandas]
RUN pip install --no-cache-dir --user apache-airflow-providers-cncf-kubernetes
RUN pip install --no-cache-dir -r requirements.txt


# COPY requirements.txt .
# RUN pip install -r requirements.txt
# USER airflow
# # Now we initialize the PostgreSQL backend
# # https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html#database-uri
# RUN airflow db init