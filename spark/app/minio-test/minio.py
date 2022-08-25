# Import Necessary Libaries
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from pyspark import SQLContext
from itertools import islice
from pyspark.sql.functions import col

# Spark Session Builder
spark = SparkSession \
    .builder \
    .master("spark://spark-master:7077").getOrCreate()


# Pulling DataFrame from Minio
customers = spark.read.option("header",True).csv("s3a://bronze/sales/customers/2022/07/02/09/customers.csv")


# Printing Result
print(customers.show(3))

# Read SQL
customers.createOrReplaceTempView("customers")


#### Performing Transformations 
uk_customers = spark.sql("""
    SELECT *
    FROM customers
    WHERE country = 'United Kingdom'
    ORDER BY customer_id ASC
    LIMIT 100
""")


# Writing Results to S3
uk_customers.write.option("header","true").csv("s3a://silver/customers/United-Kingdom")
