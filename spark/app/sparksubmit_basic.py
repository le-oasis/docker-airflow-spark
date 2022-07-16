import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

# File Paths
logFilepath = "/usr/local/spark/resources/data/testfile.txt"  

# Create spark context
# sc = SparkContext()
sc = SparkContext(master="spark://spark-master:7077")


# Read file
# logData = sc.textFile(logFile).cache()
logData = sc.textFile(logFilepath).cache()

# Get lines with A
numAs = logData.filter(lambda s: 'a' in s).count()

# Get lines with B 
numBs = logData.filter(lambda s: 'b' in s).count()

# Print result
print("Lines with a: %i, lines with b: %i" % (numAs, numBs))

