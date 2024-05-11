import sys
from modules.utils import UPDATED
from modules.utils import pysparkFunctions
from pyspark.sql.types import StructType, StructField, TimestampType, StringType, FloatType
from pyspark.sql import functions as f
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from delta.tables import DeltaTable


spark = SparkSession.builder \
      .appName("currency-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
BRONZE_LAYER_NAMESPACE=sys.argv[2]
SILVER_LAYER_NAMESPACE=sys.argv[3]
ADLS_FOLDER=sys.argv[4]
CURRENCY_FOLDER=sys.argv[5]
CURRENCY_LIST=sys.argv[6]


CURRENCY_SCHEMA =[('currency_value', FloatType()), ('currency_name', StringType()),('updated_at', TimestampType())]


currency_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+CURRENCY_FOLDER
fields = [StructField(*field) for field in CURRENCY_SCHEMA]
schema_currency = StructType(fields)
try:
  deltaTable = DeltaTable.forPath(spark, currency_path)
except:
  spark.sql("DROP TABLE IF EXISTS "+ CURRENCY_FOLDER)
  df_currency = pysparkFunctions.gen_blank_df(spark, CURRENCY_SCHEMA)
  df_currency.write.format("delta").option("path", currency_path).saveAsTable(CURRENCY_FOLDER)
  deltaTable = DeltaTable.forPath(spark, currency_path)
    
for currency in CURRENCY_LIST.split(","):
  bronze_currency_path="wasbs://"+BRONZE_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+CURRENCY_FOLDER+"/"+currency+"/"+ADLS_FOLDER

  try:
    df_currency_incremental = spark.read.csv(bronze_currency_path, schema=schema_currency )
    df_currency_incremental=df_currency_incremental.withColumn('currency_name', f.lit(currency))
    df_currency_incremental=df_currency_incremental.withColumn('updated_at', f.lit(UPDATED))

    deltaTable.alias("currency").merge(
    df_currency_incremental.alias("currency_new"),
                    "currency.currency_name = currency_new.currency_name") \
                    .whenMatchedUpdate(set = {"currency_value":   "currency_new.currency_value", 	\
                                              "updated_at":       "currency_new.updated_at" } )     \
                    .whenNotMatchedInsert(values =                                                  \
                       {                                                    
                                              "currency_value":   "currency_new.currency_value", 	\
                                              "currency_name":    "currency_new.currency_name",     \
                                              "updated_at":       "currency_new.updated_at"         \
                       }                                                                            \
                     ).execute()
  except Exception as e:
    print(e)