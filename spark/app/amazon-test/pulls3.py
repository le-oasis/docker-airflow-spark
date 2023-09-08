import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DateType

# Define schema for orders data
orders_schema = StructType([
    StructField("customer_id", IntegerType(), True),
    StructField("order_date", DateType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("unit_price", IntegerType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("total_price", IntegerType(), True)
])

# Create Spark session
spark = SparkSession.builder.appName("S3ToPostgres").getOrCreate()

# Read orders data from S3
bucket_name = "d2b-internal-assessment-bucket"
prefix = "orders_data"
orders_df = spark.read.schema(orders_schema).csv(f"s3a://{bucket_name}/{prefix}/*.csv")




# # Load DataFrame to Postgres 
# orders.write \
#     .format("jdbc") \
#     .option("url", "jdbc:postgresql://d2b-internal-assessment-dwh.cxeuj0ektqdz.eu-central-1.rds.amazonaws.com:5432/d2b_assessment") \
#     .option("dbtable", "mahmoyin9767_staging.orders_staging") \
#     .option("user", "mahmoyin9767") \
#     .option("password", "yDXXxChDDH") \
#     .option("driver", "org.postgresql.Driver") \
#     .mode("overwrite") \
#     .save()