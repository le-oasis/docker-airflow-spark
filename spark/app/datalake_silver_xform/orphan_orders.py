import sys
from pyspark.sql import *
from pyspark.sql import SparkSession

spark = SparkSession.builder \
      .appName("orphan_orders-silver-xform") \
      .getOrCreate()

STORAGE_ACCOUNT=sys.argv[1]
SILVER_LAYER_NAMESPACE=sys.argv[2]
ADLS_FOLDER=sys.argv[3]

orphan_path="wasbs://"+SILVER_LAYER_NAMESPACE+"@"+STORAGE_ACCOUNT+".blob.core.windows.net/exceptions/orphan_orders/"+ADLS_FOLDER
df_store_orders_orphan=spark.sql("SELECT * FROM store_orders WHERE product_id NOT IN (SELECT product_id FROM products)")
df_store_orders_orphan.write.parquet(orphan_path)