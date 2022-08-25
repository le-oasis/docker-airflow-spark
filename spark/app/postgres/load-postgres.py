################################################################################
# Import Libraries
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col, to_timestamp
from pyspark.sql.types import DoubleType
import pandas as pd 
################################################################################
# Create spark session
spark = (SparkSession
    .builder
    .getOrCreate()
)
################################################################################
# Parameters
################################################################################




################################################################################
# Extract data from Postgres
################################################################################



# Read CSV Data
print("######################################")
print("READING CSV FILES")
print("######################################")
################################################################################
df_movies_csv = (
    spark.read
    .format("csv")
    .option("header", True)
    .load("/usr/local/spark/resources/data/movies.csv")
)
################################################################################
df_ratings_csv = (
    spark.read
    .format("csv")
    .option("header", True)
    .load("/usr/local/spark/resources/data/ratings.csv")
    .withColumnRenamed("timestamp","timestamp_epoch")
)
################################################################################

################################################################################
# Transform data
################################################################################

################################################################################
# Convert epoch to timestamp and rating to DoubleType
df_ratings_csv_fmt = (
    df_ratings_csv
    .withColumn('rating', col("rating").cast(DoubleType()))
    .withColumn('timestamp', to_timestamp(from_unixtime(col("timestamp_epoch"))))
)
################################################################################


################################################################################
# Load data
################################################################################


################################################################################
# Load data to Postgres
print("######################################")
print("LOADING POSTGRES TABLES")
print("######################################")
################################################################################
(
    df_movies_csv.write
    .format("jdbc")
    .option("url", 'jdbc:postgresql://oasispostgres:5432/metastore')
    .option("dbtable", "public.movies")
    .option("user", 'hive')
    .option("password", 'hive')
    .mode("overwrite")
    .save()
)
################################################################################
(
     df_ratings_csv_fmt
     .select([c for c in df_ratings_csv_fmt.columns if c != "timestamp_epoch"])
     .write
     .format("jdbc")
     .option("url", 'jdbc:postgresql://oasispostgres:5432/metastore')
     .option("dbtable", "public.ratings")
     .option("user", 'hive')
     .option("password", 'hive')
     .mode("overwrite")
     .save()
)
################################################################################