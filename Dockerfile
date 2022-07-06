ARG AIRFLOW_BASE_IMAGE=apache/airflow:2.2.3

FROM docker.io/${AIRFLOW_BASE_IMAGE}


ENV SPARK_VERSION=3.0.1
ENV HADOOP_VERSION=3.2
ENV SPARK_INSTALL_ROOT=/spark

ENV SPARK_HOME=${SPARK_INSTALL_ROOT}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

USER root
RUN mkdir "${SPARK_INSTALL_ROOT}"
USER $USER

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN cd "${SPARK_INSTALL_ROOT}" && \
    wget --show-progress https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz



ARG JAVA_LIBRARY=openjdk-11-jdk-headless
ENV JAVA_LIBRARY=${JAVA_LIBRARY}


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ${JAVA_LIBRARY} \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install -U pip
RUN pip install --no-cache-dir --user apache-airflow-providers-apache-spark
RUN pip install --no-cache-dir --user boto3
RUN pip install --no-cache-dir --user airflow-clickhouse-plugin[pandas]
COPY requirements.txt .
RUN pip install -r requirements.txt



