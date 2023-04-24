# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
#This Dockerfile is based on the work of Mahmud Oyinloye (https://github.com/le-oasis)

# Set up variables for customizing the build
ARG OWNER=jupyter
ARG BASE_CONTAINER=$OWNER/scipy-notebook

# Use the specified base container image for this image
FROM $BASE_CONTAINER

# sets a label for the Docker image being built. Labels provide metadata about the image, 
# such as the maintainer or version information, that can be useful for organizing and managing images.
LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

# Fix: https://github.com/hadolint/hadolint/wiki/DL4006
# Fix: https://github.com/koalaman/shellcheck/wiki/SC3014

# This line in the Dockerfile sets the default shell used 
#for subsequent commands to /bin/bash, with the following options:
# -o pipefail: this sets the shell option to exit with a non-zero status if any command in a pipeline fails, 
# rather than just the last command.
# -c: this tells the shell to read the following command from its arguments.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Spark dependencies
# Default values can be overridden at build time
# (ARGS are in lower case to distinguish them from ENV)

# Set default values for Spark, Hadoop, and Java versions as build arguments.
ARG spark_version="3.2.0"
ARG hadoop_version="3.2"
ARG scala_version
ARG openjdk_version="11"

# Set environment variables for Spark and Hadoop versions.
ENV APACHE_SPARK_VERSION="${spark_version}" \
    HADOOP_VERSION="${hadoop_version}"

# Update package list, install OpenJDK, and remove package list files to reduce image size.
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    "openjdk-${openjdk_version}-jre-headless" \
    ca-certificates-java && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Spark installation
WORKDIR /tmp

RUN if [ -z "${scala_version}" ]; then \
    wget -qO "spark.tgz" "https://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"; \
  else \
    wget -qO "spark.tgz" "https://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}-scala${scala_version}.tgz"; \
  fi && \
  tar xzf "spark.tgz" -C /usr/local --owner root --group root --no-same-owner && \
  rm "spark.tgz"

# Configure Spark
ENV SPARK_HOME=/usr/local/spark
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info" \
    PATH="${PATH}:${SPARK_HOME}/bin"

RUN if [ -z "${scala_version}" ]; then \
    ln -s "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" "${SPARK_HOME}"; \
  else \
    ln -s "spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}-scala${scala_version}" "${SPARK_HOME}"; \
  fi && \
  # Add a link in the before_notebook hook in order to source automatically PYTHONPATH && \
  mkdir -p /usr/local/bin/before-notebook.d && \
  ln -s "${SPARK_HOME}/sbin/spark-config.sh" /usr/local/bin/before-notebook.d/spark-config.sh

# # Configure IPython system-wide
# COPY ipython_kernel_config.py "/etc/ipython/ipython_kernel_config.py"
# RUN fix-permissions "/etc/ipython/"

USER ${NB_UID}

# Install Packages
RUN pip install --upgrade pip
COPY requirements.txt .

# Install Packages
RUN pip install --no-cache-dir -r requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Set the working directory to the user's home directory.
WORKDIR "${HOME}"

# Expose ports 4040, 8088, and 8089 for the container to use.
EXPOSE 4040 8088 8089