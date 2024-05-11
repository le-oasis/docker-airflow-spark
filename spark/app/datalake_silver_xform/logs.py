import sys
from modules.utils import ip_to_country_udf, UPDATED
from modules.utils import pysparkFunctions
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from pyspark.sql import functions as f
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable


spark = SparkSession.builder \
      .appName("logs-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
BRONZE_LAYER_NAMESPACE=sys.argv[2]
SILVER_LAYER_NAMESPACE=sys.argv[3]
ADLS_FOLDER=sys.argv[4]
LOGS_FOLDER=sys.argv[5]


LOGS_SCHEMA =[('time', StringType()), ('remote_ip', StringType()), ('country_name', StringType()), ('ip_number', IntegerType()),
                ('request', StringType()), ('response', StringType()), ('agent', StringType()), ('updated_at', TimestampType())]


logs_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+LOGS_FOLDER
fields = [StructField(*field) for field in LOGS_SCHEMA]
schema_logs = StructType(fields)
try:
  deltaTable = DeltaTable.forPath(spark, logs_path)
except:
  spark.sql("DROP TABLE IF EXISTS "+ LOGS_FOLDER)
  df_logs = pysparkFunctions.gen_blank_df(spark, LOGS_SCHEMA)
  df_logs.write.format("delta").option("path", logs_path).saveAsTable(LOGS_FOLDER)
  deltaTable = DeltaTable.forPath(spark, logs_path)
  
bronze_logs_path="wasbs://"+BRONZE_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+LOGS_FOLDER+"/"+ADLS_FOLDER

try:
  df_logs_incremental = spark.read.json(bronze_logs_path, schema=schema_logs )
  df_logs_incremental = df_logs_incremental.withColumn('updated_at', f.lit(UPDATED))
  df_logs_incremental = df_logs_incremental.withColumn('time', from_unixtime(unix_timestamp('time', 'dd/MM/yyy:HH:m:ss')))
  df_logs_incremental = df_logs_incremental.withColumn('ip_number',ip_to_country_udf('remote_ip'))
  df_logs_incremental = df_logs_incremental.withColumn("ip_number_int", df_logs_incremental['ip_number'].cast('int')).drop('ip_number').withColumnRenamed('ip_number_int', 'ip_number')
  df_logs_incremental.registerTempTable('logs_incr')
  
  df_logs_incremental=spark.sql(" SELECT logs_incr.time, logs_incr.remote_ip, geolocation.country_name, logs_incr.ip_number, logs_incr.request, logs_incr.response, " \
                                " logs_incr.agent, logs_incr.updated_at " \
                                " FROM logs_incr JOIN geolocation WHERE ip1 <= ip_number AND ip2 >= ip_number")
  
  deltaTable.alias("logs").merge(
      df_logs_incremental.alias("logs_incr"),
      "logs.remote_ip = logs_incr.remote_ip") \
    .whenNotMatchedInsertAll() \
    .execute()
  
except Exception as e:
    print(e)