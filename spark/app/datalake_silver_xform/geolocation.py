import sys
from modules.utils import UPDATED
from modules.utils import pysparkFunctions
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from pyspark.sql import functions as f
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable


spark = SparkSession.builder \
      .appName("geolocation-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
BRONZE_LAYER_NAMESPACE=sys.argv[2]
SILVER_LAYER_NAMESPACE=sys.argv[3]
ADLS_FOLDER=sys.argv[4]
GEOLOCATION_FOLDER=sys.argv[5]


GEOLOCATION_SCHEMA =[('ip1', IntegerType()), ('ip2', IntegerType()), ('country_code', StringType()), 
                    ('country_name', StringType()),('updated_at', TimestampType())]

geolocation_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+GEOLOCATION_FOLDER
fields = [StructField(*field) for field in GEOLOCATION_SCHEMA]
schema_geolocation = StructType(fields)
try:
  deltaTable = DeltaTable.forPath(spark, geolocation_path)
except:
  spark.sql("DROP TABLE IF EXISTS "+ GEOLOCATION_FOLDER)
  df_geolocation = pysparkFunctions.gen_blank_df(spark, GEOLOCATION_SCHEMA)
  df_geolocation.write.format("delta").option("path", geolocation_path).saveAsTable(GEOLOCATION_FOLDER)
  deltaTable = DeltaTable.forPath(spark, geolocation_path)

bronze_geolocation_path="wasbs://"+BRONZE_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+GEOLOCATION_FOLDER+"/"+ADLS_FOLDER

try:
  df_geolocation_incremental = spark.read.csv(bronze_geolocation_path, schema=schema_geolocation )
  df_geolocation_incremental=df_geolocation_incremental.withColumn('updated_at', f.lit(UPDATED))

  deltaTable.alias("geolocation").merge(
    df_geolocation_incremental.alias("geolocation_new"),
                      "geolocation.ip1 = geolocation_new.ip1") \
                      .whenMatchedUpdate(set = {"ip2":              "geolocation_new.ip2", 	             \
                                                "country_code":     "geolocation_new.country_code",        \
                                                "country_name":     "geolocation_new.country_name",        \
                                                "updated_at":       "geolocation_new.updated_at" } )       \
                      .whenNotMatchedInsert(values =                                                       \
                         {                                                    
                                                "ip1":              "geolocation_new.ip1", 	             \
                                                "ip2":              "geolocation_new.ip2", 	             \
                                                "country_code":     "geolocation_new.country_code",        \
                                                "country_name":     "geolocation_new.country_name",        \
                                                "updated_at":       "geolocation_new.updated_at"           \
                         }                                                                                 \
                       ).execute()                     
except Exception as e:
  print(e)