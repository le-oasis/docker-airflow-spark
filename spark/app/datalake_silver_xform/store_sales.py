import sys
from modules.utils import mask_udf, curate_email_udf, curate_country_udf, curate_sales_price_udf, UPDATED
from modules.utils import pysparkFunctions
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, TimestampType, FloatType
from pyspark.sql import functions as f
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable


spark = SparkSession.builder \
      .appName("store_sales-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
BRONZE_LAYER_NAMESPACE=sys.argv[2]
SILVER_LAYER_NAMESPACE=sys.argv[3]
ADLS_FOLDER=sys.argv[4]
STORE_SALES_FOLDER=sys.argv[5]
TABLE_LIST=sys.argv[6]


CUSTOMERS_SCHEMA =[('customer_id', IntegerType()), ('customer_name', StringType()), ('address', StringType()),('city', StringType()),
                    ('postalcode', StringType()), ('country', StringType()), ('phone', StringType()), ('email', StringType()),
                    ('credit_card', StringType()), ('updated_at', TimestampType())]

ORDERS_SCHEMA =[('order_number', IntegerType()), ('customer_id', IntegerType()), ('product_id', IntegerType()), ('order_date', DateType()),
                ('units', IntegerType()), ('sale_price', FloatType()), ('currency', StringType()), ('order_mode', StringType()), 
                ('sale_price_usd', FloatType()), ('updated_at', TimestampType())]

PRODUCTS_SCHEMA =[('product_id', IntegerType()), ('product_name', StringType()), ('product_category', StringType()),
                    ('updated_at', TimestampType())]

for table in TABLE_LIST.split(","): 
  try:
    table_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+STORE_SALES_FOLDER+"/"+table
    bronze_table_path="wasbs://"+BRONZE_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/"+STORE_SALES_FOLDER+"/\[dbo\].\["+table+"\]/"+ADLS_FOLDER
    
    if table=="store_customers":
      TABLE_SCHEMA=CUSTOMERS_SCHEMA
    elif table=="store_orders":
      TABLE_SCHEMA=ORDERS_SCHEMA
    elif table=="products":
      TABLE_SCHEMA=PRODUCTS_SCHEMA

    fields = [StructField(*field) for field in TABLE_SCHEMA]
    schema_stores = StructType(fields)
    try:
      deltaTable = DeltaTable.forPath(spark, table_path)
    except:
      spark.sql("DROP TABLE IF EXISTS "+ table)
      df = pysparkFunctions.gen_blank_df(spark,TABLE_SCHEMA)
      df.write.format("delta").option("path", table_path).saveAsTable(table)
      deltaTable = DeltaTable.forPath(spark, table_path)

    if table=="store_customers":
      df_table_incremental = spark.read.csv(bronze_table_path, schema=schema_stores )

      df_table_curated = df_table_incremental.withColumn('email_curated',curate_email_udf('email')).drop('email').withColumnRenamed('email_curated', 'email')

      df_table_curated = df_table_curated.withColumn('country_curated',curate_country_udf('country')).drop('country').withColumnRenamed('country_curated', 'country')
 
      df_table_curated = df_table_curated.withColumn('phone_masked',mask_udf('phone')).drop('phone').withColumnRenamed('phone_masked', 'phone')
      df_table_curated = df_table_curated.withColumn('credit_card_masked',mask_udf('credit_card')).drop('credit_card').withColumnRenamed('credit_card_masked', 'credit_card')
      df_table_curated = df_table_curated.withColumn('credit_card_masked',mask_udf('credit_card')).drop('credit_card').withColumnRenamed('credit_card_masked', 'credit_card')
      df_table_curated = df_table_curated.withColumn('address_masked',mask_udf('address')).drop('address').withColumnRenamed('address_masked', 'address')
      df_table_curated=df_table_curated.withColumn('updated_at', f.lit(UPDATED))

      deltaTable.alias("store_customers").merge(
      df_table_curated.alias("store_customers_new"),
                      "store_customers.email = store_customers_new.email") \
                      .whenMatchedUpdate(set = {"customer_id": 	    "store_customers_new.customer_id", 	  \
                                                "customer_name":    "store_customers_new.customer_name",  \
                                                "address":          "store_customers_new.address",        \
                                                "city":             "store_customers_new.city",           \
                                                "postalcode":       "store_customers_new.postalcode",     \
                                                "country":          "store_customers_new.country",        \
                                                "phone":            "store_customers_new.phone",          \
                                                "email":            "store_customers_new.email",          \
                                                "credit_card":      "store_customers_new.credit_card",    \
                                                "updated_at":       "store_customers_new.updated_at" } )  \
                      .whenNotMatchedInsert(values =                                                      \
                         {                                                    
                                                "customer_id": 	    "store_customers_new.customer_id", 	  \
                                                "customer_name":    "store_customers_new.customer_name",  \
                                                "address":          "store_customers_new.address",        \
                                                "city":             "store_customers_new.city",           \
                                                "postalcode":       "store_customers_new.postalcode",     \
                                                "country":          "store_customers_new.country",        \
                                                "phone":            "store_customers_new.phone",          \
                                                "email":            "store_customers_new.email",          \
                                                "credit_card":      "store_customers_new.credit_card",    \
                                                "updated_at":       "store_customers_new.updated_at"      \
                         }                                                                                \
                       ).execute()
    elif table=="store_orders":
      ORDERS_SCHEMA_1 =[('order_number', IntegerType()),('customer_id', IntegerType()),('product_id', IntegerType()),('order_date', StringType()),
                        ('units', IntegerType()),('sale_price', FloatType()), ('currency', StringType()), 
                        ('order_mode', StringType()), ('sale_price_usd', FloatType()), ('updated_at', TimestampType())
                       ]
      fields = [StructField(*field) for field in ORDERS_SCHEMA_1]
      schema_stores = StructType(fields)
      df_table_incremental = spark.read.csv(bronze_table_path, schema=schema_stores )

      df_currency=spark.sql('SELECT currency_name AS currency, currency_value from currency')
      columns = ['currency', 'currency_value']
      df_currency_usd = spark.createDataFrame([('USD','1')], columns)
      df_currency_final=df_currency_usd.union(df_currency)
     
      df_table_curated = df_table_incremental.join(df_currency_final, on=['currency'], how="inner")
      df_table_curated = df_table_curated.withColumn('sale_price_usd',curate_sales_price_udf('currency', 'currency_value', 'sale_price'))
      df_table_curated=df_table_curated.withColumn('updated_at', f.lit(UPDATED))
      df_table_curated = df_table_curated.withColumn('order_date_new', to_date(df_table_curated.order_date, 'MM/dd/yyyy')).drop('order_date').withColumnRenamed('order_date_new', 'order_date')
      df_table_curated = df_table_curated.drop('currency_value')


      deltaTable.alias("store_orders").merge(
      df_table_curated.alias("store_orders_new"),
                      "store_orders.order_number = store_orders_new.order_number")                     \
                      .whenMatchedUpdate(set = {"order_number": 	"store_orders_new.order_number",   \
                                                "customer_id":      "store_orders_new.customer_id",    \
                                                "product_id":       "store_orders_new.product_id",     \
                                                "order_date":       "store_orders_new.order_date",     \
                                                "units":            "store_orders_new.units",          \
                                                "sale_price":       "store_orders_new.sale_price",     \
                                                "sale_price_usd":   "store_orders_new.sale_price_usd", \
                                                "currency":         "store_orders_new.currency",       \
                                                "order_mode":       "store_orders_new.order_mode",     \
                                                "updated_at":       "store_orders_new.updated_at" } )  \
                      .whenNotMatchedInsert(values =                                                   \
                         {                                                    
                                                "order_number": 	"store_orders_new.order_number",   \
                                                "customer_id":      "store_orders_new.customer_id",    \
                                                "product_id":       "store_orders_new.product_id",     \
                                                "order_date":       "store_orders_new.order_date",     \
                                                "units":            "store_orders_new.units",          \
                                                "sale_price":       "store_orders_new.sale_price",     \
                                                "sale_price_usd":   "store_orders_new.sale_price_usd", \
                                                "currency":         "store_orders_new.currency",       \
                                                "order_mode":       "store_orders_new.order_mode",     \
                                                "updated_at":       "store_orders_new.updated_at"      \
                         }                                                                             \
                       ).execute()
      deltaTable.delete("order_mode = 'DELETE'")
    elif table=="products":
      df_table_incremental = spark.read.csv(bronze_table_path, schema=schema_stores )
      df_table_curated=df_table_incremental.withColumn('updated_at', f.lit(UPDATED))

      deltaTable.alias("products").merge(
      df_table_curated.alias("products_new"),
                      "products.product_id = products_new.product_id")                                \
                      .whenMatchedUpdate(set = {"product_id": 	    "products_new.product_id", 	      \
                                                "product_name":     "products_new.product_name",      \
                                                "product_category": "products_new.product_category",  \
                                                "updated_at":       "products_new.updated_at" } )     \
                      .whenNotMatchedInsert(values =                                                  \
                         {                                                    
                                                "product_id": 	    "products_new.product_id", 	      \
                                                "product_name":     "products_new.product_name",      \
                                                "product_category": "products_new.product_category",  \
                                                "updated_at":       "products_new.updated_at"         \
                         }                                                                            \
                       ).execute()  

  except Exception as e:
    print(e)