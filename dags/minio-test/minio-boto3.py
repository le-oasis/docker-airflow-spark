# Import Python dependencies needed for the workflow
from datetime import datetime
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.S3_hook import S3Hook
import boto3
import pandas as pd


###############################################
# Parameters & Arguments
Bucket = 'bronze'
Key = "/sales/customers/2022/07/02/09/customers.csv"
###############################################
# Python Function
# Read CSV from S3
def read_data():
    # # Read CSV
    s3 = boto3.client('s3',aws_access_key_id='minio',aws_secret_access_key='minio123',endpoint_url='http://minio:9000')
    read_file = s3.get_object(Bucket=Bucket, Key=Key)
    df = pd.read_csv(read_file['Body'],sep=',')
    top5 = df.head()
    print(top5)
###############################################
# DAG Definition
with DAG(dag_id='Minio-Boto3',
        start_date=days_ago(1),  
        schedule_interval=None,
        catchup=False,
        tags=['minio/boto3'],
    ) as dag:
###############################################
    # Create a task to call your processing function
###############################################
    t1 = DummyOperator(task_id='start_task')
###############################################
    t2 = PythonOperator(
        task_id='read_data',
        provide_context=True,
        python_callable=read_data
    )
###############################################
    t3 = DummyOperator(task_id='end_task')
 ###############################################
t1 >> t2 >> t3
###############################################