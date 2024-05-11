import airflow
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

###############################################
# Parameters & Arguments
###############################################
STORAGE_ACCOUNT="STORAGE_ACCOUNT"
ADLS_KEY="ADLS_KEY"
BRONZE_LAYER_NAMESPACE="BRONZE_LAYER_NAMESPACE"
SILVER_LAYER_NAMESPACE="SILVER_LAYER_NAMESPACE"
STORE_SALES_FOLDER="STORE_SALES_FOLDER"
ADLS_FOLDER="ADLS_FOLDER"
TABLE_LIST="TABLE_LIST"
CURRENCY_LIST="CURRENCY_LIST"
CURRENCY_FOLDER="CURRENCY_FOLDER"
GEOLOCATION_FOLDER="GEOLOCATION_FOLDER"
LOGS_FOLDER="LOGS_FOLDER"
ECOMM_FOLDER="ECOMM_FOLDER"
###############################################
minio_conf = {
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.hadoop.fs.s3a.endpoint": "http://mcstoredatalake:9000",
    "spark.hadoop.fs.s3a.access.key": "minio",
    "spark.hadoop.fs.s3a.secret.key": "minio123",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
}
###############################################
# Spark App Name; shown on Spark UI
spark_app_name = "Minio_Spark"
###############################################
# Path to Spark App
spark_app = "/usr/local/spark/app"
###############################################
# Path to Jars
jar_home="/usr/local/spark/resources"
###############################################
# Runtime Arguments
driver_class_path=f'{jar_home}/jars/hadoop-aws-3.2.0.jar,{jar_home}/jars/hadoop-cloud-storage-3.2.0.jar,{jar_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
driver_class_path=f'{jar_home}/jars/hadoop-aws-3.2.0.jar:{jar_home}/jars/hadoop-cloud-storage-3.2.0.jar:{jar_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
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
###############################################
now = datetime.now()
###############################################
default_args = {
    "owner": "mcstore",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["mcstore@mcstore.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}
###############################################
dag = DAG(
        dag_id="spark-silver", 
        description="This DAG an integration between Spark and the data lake (Minio). It controls all data transformations within the silver layer of the data lake.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )
###############################################
start = DummyOperator(task_id="start", dag=dag)
###############################################
spark_job_currency = SparkSubmitOperator(
    task_id="currency-silver-xform",
    application="{spark_app}/currency.py",
    name="currency-silver-xform",
    conn_id="mcstore_con_spark",
    conf=minio_conf,
    application_args=[STORAGE_ACCOUNT,BRONZE_LAYER_NAMESPACE,SILVER_LAYER_NAMESPACE,ADLS_FOLDER,CURRENCY_FOLDER,CURRENCY_LIST],
    jars=driver_class_path,
    driver_class_path=driver_class_path,
    dag=dag)
###############################################
spark_job_store_sales = SparkSubmitOperator(
    task_id="store_sales-silver-xform",
    application="{spark_app}/store_sales.py",
    name="store_sales-silver-xform",
    conn_id="mcstore_con_spark",
    conf=minio_conf,
    application_args=[STORAGE_ACCOUNT,BRONZE_LAYER_NAMESPACE,SILVER_LAYER_NAMESPACE,ADLS_FOLDER,STORE_SALES_FOLDER,TABLE_LIST],
    jars=driver_class_path,
    driver_class_path=driver_class_path,
    dag=dag)
###############################################
spark_job_logs = SparkSubmitOperator(
    task_id="logs-silver-xform",
    application="{spark_app}/logs.py",
    name="logs-silver-xform",
    conn_id="mcstore_con_spark",
    conf=minio_conf,
    application_args=[STORAGE_ACCOUNT,BRONZE_LAYER_NAMESPACE,SILVER_LAYER_NAMESPACE,ADLS_FOLDER,LOGS_FOLDER],
    jars=driver_class_path,
    driver_class_path=driver_class_path,
    dag=dag)
###############################################
spark_job_orphan_orders = SparkSubmitOperator(
    task_id="orphan_orders-silver-xform",
    application="{spark_app}/orphan_orders.py",
    name="orphan_orders-silver-xform",
    conn_id="mcstore_con_spark",
    conf=minio_conf,
    application_args=[STORAGE_ACCOUNT,SILVER_LAYER_NAMESPACE,ADLS_FOLDER],
    dag=dag)
###############################################
spark_job_geolocation = SparkSubmitOperator(
    task_id="geolocation-silver-xform",
    application="{spark_app}/geolocation.py",
    name="geolocation-silver-xform",
    conn_id="mcstore_con_spark",
    conf=minio_conf,
    application_args=[STORAGE_ACCOUNT,BRONZE_LAYER_NAMESPACE,SILVER_LAYER_NAMESPACE,ADLS_FOLDER,GEOLOCATION_FOLDER],
    jars=driver_class_path,
    driver_class_path=driver_class_path,
    dag=dag)
###############################################
end = DummyOperator(task_id="end", dag=dag)
###############################################
start >> [spark_job_currency, spark_job_store_sales, spark_job_logs, spark_job_orphan_orders, spark_job_geolocation] >> end
###############################################

