#importing necessary libaries
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
df = spark.read.option("header",True).csv("s3a://oasis/test/office.csv")

# Printing Result
print(df.show(3))

#### Reading Ratings Dataset
ratings = spark.read\
            .option("header", "true")\
            .option("inferSchema", "true")\
            .csv("s3a://oasis/test/ratings.csv")

# Show top 3             
ratings.show(3)
ratings.registerTempTable("ratings")

#### Reading Movies Dataset
movies = spark.read\
            .option("header", "true")\
            .option("inferSchema", "true")\
            .csv("s3a://oasis/test/movies.csv")
movies.show(3)
movies.registerTempTable("movies")

#### Performing Transformations 
top_100_movies = spark.sql("""
    SELECT title, AVG(rating) as avg_rating
    FROM movies m
    LEFT JOIN ratings r ON m.movieId = r.movieID
    GROUP BY title
    HAVING COUNT(*) > 100
    ORDER BY avg_rating DESC
    LIMIT 100
""")

###
# top_100_movies.write.parquet("s3a://oasis/test/top_100_movies")
####

# Writing Results to S3
top_100_movies.write.option("header","true").csv("s3a://oasis/test/results/resultcsv")
