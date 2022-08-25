######################################################################################
# Import Necessary Libraries
import os
from delta.tables import *
from delta.tables import DeltaTable
from pyspark.sql.functions import *
from pyspark.sql import *
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType,array,ArrayType,DateType,TimestampType, FloatType
from pyspark.sql import functions as f
from pyspark.sql.functions import udf
import hashlib
import datetime
import urllib.request
import json
from datetime import timedelta, date
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark import SQLContext
from itertools import islice
from pyspark.sql.functions import col
import sys
# from modules.utils import mask_udf, curate_email_udf, curate_country_udf, curate_sale_price_udf, UPDATED
# from modules.utils import pysparkFunctions
######################################################################################
# PySpark Functions
def gen_blank_df(spark, schema_struct):
    fields = [StructField(*field) for field in schema_struct]
    schema = StructType(fields)
    df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)
    return df
######################################################################################
def mask_value(column):
  mask_value = hashlib.sha256(column.encode()).hexdigest()
  return mask_value
######################################################################################
def curate_email(email):
  curated_value = email.lower()
  return curated_value
######################################################################################
def curate_country(country):
  if (country == 'USA' or country == 'United States'):
    curated_value = 'USA'
  elif (country == 'UK' or country == 'United Kingdom'):
    curated_value = 'UK'
  elif (country == 'CAN' or country == 'Canada'):
    curated_value = 'CAN'
  elif (country == 'IND' or country == 'India'):
    curated_value = 'IND'
  else:
    curated_value = country
  return curated_value
######################################################################################
def curate_sale_price(currency, currency_value, sale_price):
  if (currency != 'USD'):
    curated_value = float(sale_price)/float(currency_value)
    return float(curated_value)
  else:
    return float(sale_price)
######################################################################################
def ip_to_country(ip):
  ipsplit = ip.split(".")
  ip_number=16777216*int(ipsplit[0]) + 65536*int(ipsplit[1]) + 256*int(ipsplit[2]) + int(ipsplit[3])  
  return ip_number
######################################################################################
mask_udf = udf(mask_value, StringType())
curate_email_udf = udf(curate_email, StringType())
curate_country_udf = udf(curate_country, StringType())
curate_sale_price_udf = udf(curate_sale_price, FloatType())
ip_to_country_udf = udf(ip_to_country, StringType())
######################################################################################
UPDATED=datetime.datetime.today().replace(second=0, microsecond=0)
######################################################################################
# Spark Session Builder
spark = SparkSession \
    .builder \
    .master("spark://spark-master:7077").getOrCreate()
######################################################################################
# Orders Schema 
ORDERS_SCHEMA =[('order_number', IntegerType()), ('customer_id', IntegerType()), ('product_id', IntegerType()), ('order_date', DateType()),
                ('units', IntegerType()), ('sale_price', FloatType()), ('currency', StringType()), ('order_mode', StringType()), ('updated_at', TimestampType())]
######################################################################################
# Set the Schema
fields = [StructField(*field) for field in ORDERS_SCHEMA]
schema_stores = StructType(fields)
######################################################################################
# Pulling DataFrame from Minio
df_table_incremental = spark.read.option("header",True).schema(schema_stores).csv("s3a://bronze/sales/orders/2022/07/02/09/orders.csv")
######################################################################################
# Printing Result
print(df_table_incremental.show(3))
print(df_table_incremental.printSchema())
######################################################################################
df_table_curated=df_table_incremental.withColumn('updated_at', f.lit(UPDATED))
df_table_curated = df_table_curated.withColumn('order_date_new', to_date(df_table_curated.order_date, 'MM/dd/yyyy')).drop('order_date').withColumnRenamed('order_date_new', 'order_date')
######################################################################################
# Printing Result
print(df_table_curated.show(3))
######################################################################################
# Send Result to Silver Layer 
# Writing Results to S3

# Transform Customers Table to Curated Table in CSV Format
df_table_curated.write.option("header","true").csv("s3a://silver/CSV/orders")

# Transform Customers Table to Curated Table in Parquet Format
df_table_curated.write.option("compression","snappy").parquet("s3a://silver/Curated/orders")

# Transform Customers Table to Curated Table in Delta Format
df_table_curated.write.format("delta").mode("overwrite").option('overwriteSchema','true').save("s3a://silver/Delta/orders")
######################################################################################






