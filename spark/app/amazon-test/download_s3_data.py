################################################################################
import os
import sys
import pyspark
from pyspark.sql import SparkSession
from delta.tables import *
from delta.tables import DeltaTable
from pyspark.sql.functions import *
from pyspark.sql import *
from pyspark.sql.types import *
from pyspark.sql import functions as f
from pyspark.sql.functions import from_unixtime, col, to_timestamp
from pyspark.sql.functions import udf
import hashlib
import urllib.request
import json
from datetime import timedelta, date
from pyspark import SparkContext
from pyspark import SQLContext
from itertools import islice
from pyspark.sql.functions import col
################################################################################


import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os


def download_path(filename):
    """
    Args:
        filename: name of the file located in s3 bucket that will be downloaded
    
    output:
        downloads a specific filename from s3 and saves it to a local directory called data
        for staging
    """
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    bucket_name = 'd2b-internal-assessment-bucket'
    response = s3.list_objects(Bucket=bucket_name, Prefix="orders_data")
    # specify directory to save downloaded files
    local = '/home/jovyan/work/data'
    if not os.path.exists(local):
       os.makedirs(local)

    s3.download_file(bucket_name, "orders_data/{}".format(filename), local + "/" "{}".format(filename))


if __name__ == "__main__":
    download_path("orders.csv")
    download_path("reviews.csv")
    download_path("shipment_deliveries.csv")
