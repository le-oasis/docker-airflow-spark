from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.types import *

import boto3

# Set AWS credentials
spark = SparkSession.builder \
    .appName("S3Read") \
    .getOrCreate()

sc = spark.sparkContext

# Parameters & Arguments
bucket_name = 'd2b-internal-assessment-bucket'
key = "orders_data/orders.csv"

# Define schema for orders data
orders_schema = StructType([
    StructField("customer_id", IntegerType(), True),
    StructField("order_date", DateType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("unit_price", IntegerType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("total_price", IntegerType(), True)
])

# Read Orders Data from S3
def read_data():
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, key)
    body = obj.get()['Body'].read().decode('utf-8')
    df = spark.read.csv(sc.parallelize(body.splitlines()), header=True, schema=orders_schema)
    top5 = df.limit(5)
    top5.show()


# # Call the function
read_data()





# from pyspark.sql import SparkSession
# from pyspark.conf import SparkConf
# from pyspark import SparkContext
# import boto3

# # Set AWS credentials
# spark = SparkSession.builder \
#     .appName("S3Read") \
#     .getOrCreate()

# sc = spark.sparkContext

# # Parameters & Arguments
# bucket_name = 'd2b-internal-assessment-bucket'
# key = "orders_data/orders.csv"
# # Define schema for orders data
# orders_schema = StructType([
#     StructField("customer_id", IntegerType(), True),
#     StructField("order_date", DateType(), True),
#     StructField("product_id", IntegerType(), True),
#     StructField("unit_price", IntegerType(), True),
#     StructField("quantity", IntegerType(), True),
#     StructField("total_price", IntegerType(), True)
# ])

# # Read Orders Data from S3
# def read_data():
#     s3 = boto3.resource('s3')
#     obj = s3.Object(bucket_name, key)
#     body = obj.get()['Body'].read().decode('utf-8')
#     df = spark.read.csv(sc.parallelize(body.splitlines()), header=True, schema)
#     top5 = df.limit(5)
#     top5.show()

# # Call the function
# read_data()
