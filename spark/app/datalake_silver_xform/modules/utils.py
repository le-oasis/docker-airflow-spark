from pyspark.sql.types import StructType, StructField, StringType, FloatType
from pyspark.sql.functions import udf
import hashlib
import datetime


class pysparkFunctions:
    def gen_blank_df(spark, schema_struct):
        fields = [StructField(*field) for field in schema_struct]
        schema = StructType(fields)
        df = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)
        return df

class pythonFunctions:
    def mask_value(column):
        mask_value = hashlib.sha256(column.encode()).hexdigest()
        return mask_value

    def curate_email(email):
        curated_value = email.lower()
        return curated_value

    def curate_country(country):
        if (country == 'USA' or country == 'United States'):
            curated_value = 'USA'
        elif (country == 'UK' or country == 'United Kingdom'):
            curated_value = 'UK'
        elif (country == 'CAN' or country == 'Canada'):
            curated_value = 'CAN'
        elif (country == 'IND' or country == 'India'):
            curated_value = 'IND'
        else:
            curated_value = country
        return curated_value

    def curate_sales_price(currency, currency_value, sales_price):
        if (currency != 'USD'):
            curated_value = float(sales_price)/float(currency_value)
            return float(curated_value)
        else:
            return float(sales_price)

    def ip_to_country(ip):
        ipsplit = ip.split(".")
        ip_number=16777216*int(ipsplit[0]) + 65536*int(ipsplit[1]) + 256*int(ipsplit[2]) + int(ipsplit[3])  
        return ip_number

mask_udf = udf(pythonFunctions.mask_value, StringType())
curate_email_udf = udf(pythonFunctions.curate_email, StringType())
curate_country_udf = udf(pythonFunctions.curate_country, StringType())
curate_sales_price_udf = udf(pythonFunctions.curate_sales_price, FloatType())
ip_to_country_udf = udf(pythonFunctions.ip_to_country, StringType())


UPDATED=datetime.datetime.today().replace(second=0, microsecond=0)