import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago


###############################################
# Parameters & Arguments
###############################################
minio_conf = {
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": "minio",
    "spark.hadoop.fs.s3a.secret.key": "minio123",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
}
###############################################
# Spark App Name; shown on Spark UI
spark_app_name = "Minio_Spark"
###############################################
# Path to Jars
spark_home = "/usr/local/spark/app"
###############################################
# Runtime Arguments
app_jars=f'{spark_home}/jars/hadoop-aws-3.2.0.jar,{spark_home}/jars/hadoop-cloud-storage-3.2.0.jar,{spark_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
driver_class_path=f'{spark_home}/jars/hadoop-aws-3.2.0.jar:{spark_home}/jars/hadoop-cloud-storage-3.2.0.jar:{spark_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
###############################################
# DAG Definition
###############################################
# Arguments
args = {
    'owner': 'airflow',    
    'retry_delay': timedelta(minutes=5),
}
###############################################
# DAG Definition
with DAG(
    dag_id='Spark_Minio_Connect',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['read/write', 'minio'],
) as dag:
        start_task = DummyOperator(
	task_id='start_task'
)
###############################################
# Sequence of Tasks
Pull_Data_From_S3 = SparkSubmitOperator(task_id='Pull_Data',
                                              conn_id='spark_connect',
                                              application='/usr/local/spark/app/minio.py',
                                              conf=minio_conf,
                                              total_executor_cores=2,
                                              jars=app_jars,
                                              driver_class_path=driver_class_path,
                                              packages="org.apache.spark:spark-hadoop-cloud_2.13:3.3.0",
                                              executor_cores=2,
                                              executor_memory='5g',
                                              driver_memory='5g',
                                              name=spark_app_name,
                                              execution_timeout=timedelta(minutes=10),
                                              dag=dag
                                              )                                             

###############################################
end_task = DummyOperator(task_id='end_task')                                  
###############################################
start_task >> Pull_Data_From_S3 >> end_task