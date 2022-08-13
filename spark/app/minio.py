#importing necessary libaries
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
    .master("spark://spark-master:7077") \
    .config("spark.jars", "/usr/local/spark/app/jars/hadoop-aws-3.2.0.jar,/usr/local/spark/app/jars/hadoop-cloud-storage-3.2.0.jar") \
    .getOrCreate()


spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", s3endPointLoc)
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", s3accessKeyAws)
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", s3secretKeyAws)
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.timeout", connectionTimeOut)

spark.sparkContext._jsc.hadoopConfiguration().set("spark.sql.debug.maxToStringFields", "100")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
spark.sparkContext._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")



df = spark.read.option("header",True).csv("s3a://bronze/sales/customers/2022/07/02/09/customers.csv")

print(df.show(3))