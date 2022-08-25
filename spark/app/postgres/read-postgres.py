################################################################################
# Import Libraries
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
################################################################################
# Create spark session
spark = (SparkSession
    .builder
    .getOrCreate()
)
################################################################################
# Read Postgres
################################################################################
print("######################################")
print("READING POSTGRES TABLES")
print("######################################")
################################################################################
df_movies = (
    spark.read
    .format("jdbc")
    .option("url", 'jdbc:postgresql://oasispostgres:5432/metastore')
    .option("dbtable", "public.movies")
    .option("user", 'hive')
    .option("password", 'hive')
    .load()
)
################################################################################
df_ratings = (
    spark.read
    .format("jdbc")
    .option("url", 'jdbc:postgresql://oasispostgres:5432/metastore')
    .option("dbtable", "public.ratings")
    .option("user", 'hive')
    .option("password", 'hive')
    .load()
)
################################################################################
# Tpo 10 movies with more ratings
df_movies = df_movies.alias("m")
df_ratings = df_ratings.alias("r")
################################################################################
df_join = df_ratings.join(df_movies, df_ratings.movieId == df_movies.movieId).select("r.*","m.title")
################################################################################
df_result = (
    df_join
    .groupBy("title")
    .agg(
        F.count("timestamp").alias("qty_ratings")
        ,F.mean("rating").alias("avg_rating")
    )
    .sort(F.desc("qty_ratings"))
    .limit(10)
)
################################################################################
print("######################################")
print("EXECUTING QUERY AND SAVING RESULTS")
print("######################################")
# Writing Results to S3
df_result.coalesce(1).write.option("header","true").csv("s3a://silver/CSV/Postgres")
################################################################################