FROM apache/zeppelin:0.9.0
ENV SPARK_VERSION=3.0.1
ENV HADOOP_VERSION=3.2
ENV SPARK_INSTALL_ROOT=/spark

ENV SPARK_HOME=${SPARK_INSTALL_ROOT}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

USER root
RUN mkdir "${SPARK_INSTALL_ROOT}"
USER $USER

RUN cd "${SPARK_INSTALL_ROOT}" && \
    wget --show-progress https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz