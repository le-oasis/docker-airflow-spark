from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.S3_hook import S3Hook
import boto3
import pandas as pd

Bucket = 'oasis'
Key = "/test/office.csv"

# Read CSV from S3
def read_data():
    # # Read CSV
    s3 = boto3.client('s3',aws_access_key_id='minio',aws_secret_access_key='minio123',endpoint_url='http://minio:9000')
    read_file = s3.get_object(Bucket=Bucket, Key=Key)
    df = pd.read_csv(read_file['Body'],sep=',')
    top5 = df.head()
    print(top5)


# def read_file_content(ds, **kwargs):
#     # Reading the existing file from minio
#     s3 = S3Hook('myminio_connection')
#     contents = s3.read_key(key="test/testfile.txt"
#                            ,bucket_name="miniobucket")
#     print(f"File contents: '{contents}'.")
    

with DAG(dag_id='Read_S3_Data',
        start_date=datetime(2022, 8, 12),  
        schedule_interval=None,
        catchup=False,
        tags=['minio'],
    ) as dag:

    # Create a task to call your processing function


    t1 = DummyOperator(task_id='start_task')

    t2 = PythonOperator(
        task_id='read_data',
        provide_context=True,
        python_callable=read_data
    )

    t3 = DummyOperator(task_id='end_task')
    
# first upload the file, then read the other file.
t1 >> t2 >> t3