from pyspark import SparkContext


logFilepath = "/usr/local/spark/resources/data/testfile.txt"  


sc = SparkContext("spark://spark-master:7077", "first app")


logData = sc.textFile(logFilepath).cache()

numAs = logData.filter(lambda s: 'a' in s).count()

numBs = logData.filter(lambda s: 'b' in s).count()

print("Lines with a: %i, lines with b: %i" % (numAs, numBs))