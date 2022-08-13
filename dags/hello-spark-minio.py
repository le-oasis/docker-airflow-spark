from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
from airflow.utils.dates import days_ago


###############################################
# Parameters
###############################################
minio_conf = {
    "spark.master": "spark://spark-master:7077", 
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": "minio",
    "spark.hadoop.fs.s3a.secret.key": "minio123",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
}


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['youremail@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}




with DAG(dag_id='Talk_Minio_Spark',
        start_date=datetime(2021, 9, 12),  
        schedule_interval=None,
        catchup=False,
        tags=['minio'],
    ) as dag:

    start_task = DummyOperator(
	task_id='start_task'
)



pull_data = SparkSubmitOperator(task_id='Pull_Data',
                                              conn_id='spark_connect',
                                              application='/usr/local/spark/app/minio.py',
                                              conf=minio_conf,
                                              total_executor_cores=2,
                                              packages="org.apache.spark:spark-hadoop-cloud_2.13:3.3.0,com.amazonaws:aws-java-sdk-bundle:1.12.280",
                                              executor_cores=2,
                                              executor_memory='5g',
                                              driver_memory='5g',
                                              name='pull_data',
                                              execution_timeout=timedelta(minutes=10),
                                              dag=dag
                                              )


end_task = DummyOperator(task_id='end_task')                                  


start_task >> pull_data >> end_task