import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
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

# Spark App Name; shown on Spark UI
spark_app_name = "Spark Minio"

# Path to Jars
spark_home = "/usr/local/spark/app"

# Runtime Arguments
app_jars=f'{spark_home}/jars/hadoop-aws-3.2.0.jar,{spark_home}/jars/hadoop-cloud-storage-3.2.0.jar,{spark_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
driver_class_path=f'{spark_home}/jars/hadoop-aws-3.2.0.jar:{spark_home}/jars/hadoop-cloud-storage-3.2.0.jar:{spark_home}/jars/aws-java-sdk-bundle-1.11.375.jar'



###############################################
# DAG Definition
###############################################
default_args = {
    'owner': 'airflow',    
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
dag_spark = DAG(
        dag_id = "Minio_Reads3_Spark",
        default_args=default_args,
        schedule_interval=None,	
        dagrun_timeout=timedelta(minutes=10),
        description='use case of sparkoperator in airflow',
        tags=['minio-read/write', 'S3'],
        start_date = airflow.utils.dates.days_ago(1)
)


# Spark Submit Operator
spark_submit_local = SparkSubmitOperator(
    task_id="Spark_Min",
    application="/usr/local/spark/app/minio.py", 
    jars=app_jars,
    driver_class_path=driver_class_path,
    packages="org.apache.spark:spark-hadoop-cloud_2.13:3.3.0",
    name=spark_app_name,
    conn_id="spark_connect",
    conf=minio_conf,
    dag=dag_spark)


spark_submit_local

if __name__ == "__main__":
    dag_spark.cli()