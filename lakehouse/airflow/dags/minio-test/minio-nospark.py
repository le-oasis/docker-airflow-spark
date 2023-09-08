# Import Python dependencies needed for the workflow
from datetime import datetime
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.S3_hook import S3Hook
import boto3
import pandas as pd


# Python Function
def upload_file(ds, **kwargs):
    with open("/tmp/test.txt", "w") as fp:
        # Creating the content and flushing it. 
        fp.write("Testfile contents.")
        fp.flush()
###############################################
        # Upload generated file to Minio
        s3 = S3Hook('myminio_connection')
        s3.load_file("/tmp/test.txt",
                     key="test/my-test-upload-file.txt",
                     bucket_name="oasis")
###############################################
def read_file_content(ds, **kwargs):
    # Reading the existing file from minio
    s3 = S3Hook('myminio_connection')
    contents = s3.read_key(key="test/testfile.txt"
                           ,bucket_name="oasis")
    print(f"File contents: '{contents}'.")
###############################################    
with DAG(dag_id='Minio-Without-Spark',
        start_date=days_ago(1),  
        schedule_interval=None,
        catchup=False,
        tags=['minio/read/write'],
    ) as dag:
###############################################  
    # Create a task to call your processing function
    t1 = PythonOperator(
        task_id='upload_file_task',
        provide_context=True,
        python_callable=upload_file
    )
###############################################  
    t2 = PythonOperator(
        task_id='read_file_content_task',
        provide_context=True,
        python_callable=read_file_content
    )
 ###############################################     
# first upload the file, then read the other file.
t1 >> t2
###############################################  