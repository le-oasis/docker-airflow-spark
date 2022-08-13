from pyspark.sql import SparkSession, functions
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark import SQLContext
from itertools import islice
from pyspark.sql.functions import col


#########################################################
s3accessKeyAws = "minio"
s3secretKeyAws = "minio123"
connectionTimeOut = "600000"
s3endPointLoc = "http://localhost:9000"
####################################################

spark = SparkSession \
        .builder \
        .appName("Minio_Test") \
        .config("spark.jars.packages","org.apache.spark:spark-hadoop-cloud_2.13:3.3.0") \
        .config("spark.jars", "/usr/local/spark/app/jars/hadoop-aws-3.2.0.jar,/usr/local/spark/app/jars/hadoop-cloud-storage-3.2.0.jar,/usr/local/spark/app/jars/aws-java-sdk-bundle-1.11.375.jar") \
        .config("spark.hadoop.fs.s3a.endpoint", s3endPointLoc) \
        .config("spark.hadoop.fs.s3a.access.key", s3accessKeyAws) \
        .config("spark.hadoop.fs.s3a.secret.key", s3secretKeyAws) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.driver.maxResultSize", "8g") \
        .config("spark.network.timeout", 600000) \
        .config("spark.executor.heartbeatInterval", 600000) \
        .config("spark.storage.blockManagerSlaveTimeoutMs", 600000) \
        .config("spark.executor.memory", "10g") \
        .master("spark://spark-master:7077") \
        .getOrCreate()



df = spark.read.option("header",True).csv("s3a://bronze/sales/customers/2022/07/02/09/customers.csv")

print(df.show(3))