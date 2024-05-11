import sys
from modules.utils import mask_udf, curate_email_udf, curate_country_udf, curate_sales_price_udf, UPDATED
from modules.utils import pysparkFunctions
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType, FloatType, DateType
from pyspark.sql import functions as f
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable


spark = SparkSession.builder \
      .appName("ecomm-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
BRONZE_LAYER_NAMESPACE=sys.argv[2]
SILVER_LAYER_NAMESPACE=sys.argv[3]
ADLS_FOLDER=sys.argv[4]
ECOMM_FOLDER=sys.argv[5]

ECOMM_SCHEMA =[('customer_name', StringType()), ('address', StringType()), ('city', StringType()), ('country', StringType()),
                ('currency', StringType()), ('email', StringType()), ('order_date', DateType()), ('order_mode', StringType()),
                ('order_number', IntegerType()), ('phone', StringType()), ('postalcode', StringType()), ('product_name', StringType()),
                ('sale_price', FloatType()), ('sale_price_usd', FloatType()), ('updated_at', TimestampType())]

ecomm_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+ECOMM_FOLDER.split("/")[0]

fields = [StructField(*field) for field in ECOMM_SCHEMA]
schema_ecomm = StructType(fields)
try:
  deltaTable = DeltaTable.forPath(spark, ecomm_path)
except:
  spark.sql("DROP TABLE IF EXISTS "+ ECOMM_FOLDER.split("/")[0])
  df_logs = pysparkFunctions.gen_blank_df(spark, ECOMM_SCHEMA)
  df_logs.write.format("delta").option("path", ecomm_path).saveAsTable(ECOMM_FOLDER.split("/")[0])
  deltaTable = DeltaTable.forPath(spark, ecomm_path)

bronze_ecomm_path="wasbs://bronze@traininglakehouse.blob.core.windows.net/"+ECOMM_FOLDER

try:
  df_ecomm=spark.read.format("avro").load(bronze_ecomm_path)

  df_ecomm_json = df_ecomm.select(df_ecomm.Body.cast("string")).rdd.map(lambda x: x[0])
  df_ecomm_data = spark.read.json(df_ecomm_json).select('data')
  df_data_values = df_ecomm_data.select('data.customer_name', 'data.address', 'data.city', 'data.country', 'data.currency', 'data.email',
                                        'data.order_date', 'data.order_mode', 'data.order_number', 'data.phone','data.postalcode', 'data.product_name', 'data.sale_price' )

  df_data_values = df_data_values.withColumn('updated_at', f.lit(UPDATED))
  df_data_values = df_data_values.withColumn('phone_masked',mask_udf('phone')).drop('phone').withColumnRenamed('phone_masked', 'phone')
  df_data_values = df_data_values.withColumn('address_masked',mask_udf('address')).drop('address').withColumnRenamed('address_masked', 'address')
  df_data_values = df_data_values.withColumn('order_date', from_unixtime(unix_timestamp('order_date', 'dd/MM/yyy')))
  df_data_values = df_data_values.withColumn('country_curated',curate_country_udf('country')).drop('country').withColumnRenamed('country_curated', 'country')
  
  df_data_values = df_data_values.join(df_currency_final, on=['currency'], how="inner")
  df_data_values = df_data_values.withColumn('sale_price_usd',curate_sales_price_udf('currency', 'currency_value', 'sale_price'))

  df_data_values = df_data_values.withColumn('order_date_new', to_date(df_data_values.order_date, 'yyyy-MM-dd HH:mm:ss')).drop('order_date').withColumnRenamed('order_date_new', 'order_date')
  
  deltaTable.alias("esalesns").merge(
  df_data_values.alias("esalesns_new"),
                    "esalesns.email = esalesns_new.email")                                          \
                    .whenMatchedUpdate(set = {"customer_name":    "esalesns_new.customer_name", 	\
                                              "address":          "esalesns_new.address",           \
                                              "city":             "esalesns_new.city",              \
                                              "country":          "esalesns_new.country",           \
                                              "currency":         "esalesns_new.currency",          \
                                              "email":            "esalesns_new.email",             \
                                              "order_date":       "esalesns_new.order_date",        \
                                              "order_mode":       "esalesns_new.order_mode",        \
                                              "order_number":     "esalesns_new.order_number",      \
                                              "phone":            "esalesns_new.phone",             \
                                              "postalcode":       "esalesns_new.postalcode",        \
                                              "product_name":     "esalesns_new.product_name",      \
                                              "sale_price":       "esalesns_new.sale_price",        \
                                              "sale_price_usd":   "esalesns_new.sale_price_usd",    \
                                              "updated_at":       "esalesns_new.updated_at" } )     \
                    .whenNotMatchedInsert(values =                                                  \
                       {                                         
                                              "customer_name":    "esalesns_new.customer_name", 	\
                                              "address":          "esalesns_new.address",           \
                                              "city":             "esalesns_new.city",              \
                                              "country":          "esalesns_new.country",           \
                                              "currency":         "esalesns_new.currency",          \
                                              "email":            "esalesns_new.email",             \
                                              "order_date":       "esalesns_new.order_date",        \
                                              "order_mode":       "esalesns_new.order_mode",        \
                                              "order_number":     "esalesns_new.order_number",      \
                                              "phone":            "esalesns_new.phone",             \
                                              "postalcode":       "esalesns_new.postalcode",        \
                                              "product_name":     "esalesns_new.product_name",      \
                                              "sale_price":       "esalesns_new.sale_price",        \
                                              "sale_price_usd":   "esalesns_new.sale_price_usd",    \
                                              "updated_at":       "esalesns_new.updated_at"         \
                       }                                                                            \
                     ).execute()
except Exception as e:
  print(e)