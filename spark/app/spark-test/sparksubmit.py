# Import Libraries
from pyspark import SparkContext

# Test basic functionality of Spark
logFilepath = "/usr/local/spark/resources/data/testfile.txt" 

# Create a SparkContext
sc = SparkContext("spark://spark-master:7077", "first app")

# Load the text file into a Spark RDD
logData = sc.textFile(logFilepath).cache()

# Count the number of "a" in the text file
numAs = logData.filter(lambda s: 'a' in s).count()

# Count the number of "b" in the text file
numBs = logData.filter(lambda s: 'b' in s).count()

# Print the results
print("Lines with a: %i, lines with b: %i" % (numAs, numBs))