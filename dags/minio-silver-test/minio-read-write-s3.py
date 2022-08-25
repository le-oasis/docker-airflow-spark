###############################################
# Import Necessary Libraries
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
    "spark.sql.catalogImplementation": "hive",
    "spark.sql.hive.metastore.version": "2.3.9",
    "spark.sql.hive.metastore.jars": "builtin",
    "spark.sql.hive.metastore.sharedPrefixes": "org.mariadb.jdbc,com.mysql.cj.jdbc,com.mysql.jdbc,org.postgresql,com.microsoft.sqlserver,oracle.jdbc",
    "spark.sql.hive.metastore.schema.verification": "true",
    "spark.sql.hive.metastore.schema.verification.record.version": "true",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
}


###############################################
# Spark App Name; shown on Spark UI
spark_app_name = "Minio-Spark"
###############################################
# Path to Jars
jar_home="/usr/local/spark/resources"
###############################################
# Runtime Arguments
app_jars=f'{jar_home}/jars/hadoop-cloud-storage-3.2.0.jar,{jar_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
driver_class_path=f'{jar_home}/jars/hadoop-cloud-storage-3.2.0.jar:{jar_home}/jars/aws-java-sdk-bundle-1.11.375.jar'
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
###############################################
Silver_Customers = SparkSubmitOperator(task_id='Silver_Customer_Transform',
                                              conn_id='spark_connect',
                                              application='/usr/local/spark/app/minio-test/silver-customers.py',
                                              conf=minio_conf,
                                              total_executor_cores=2,
                                              jars=app_jars,
                                              driver_class_path=driver_class_path,
                                              packages="io.delta:delta-core_2.12:2.0.0,org.apache.hadoop:hadoop-aws:3.2.0,org.apache.spark:spark-hadoop-cloud_2.13:3.2.0",
                                              executor_cores=2,
                                              executor_memory='5g',
                                              driver_memory='5g',
                                              name=spark_app_name,
                                              execution_timeout=timedelta(minutes=10),
                                              dag=dag
                                              )                                             
###############################################
Silver_Orders = SparkSubmitOperator(task_id='Silver_Orders_Transform',
                                              conn_id='spark_connect',
                                              application='/usr/local/spark/app/minio-test/silver-orders.py',
                                              conf=minio_conf,
                                              total_executor_cores=2,
                                              jars=app_jars,
                                              driver_class_path=driver_class_path,
                                              packages="io.delta:delta-core_2.12:2.0.0,org.apache.hadoop:hadoop-aws:3.2.0,org.apache.spark:spark-hadoop-cloud_2.13:3.2.0",
                                              executor_cores=2,
                                              executor_memory='5g',
                                              driver_memory='5g',
                                              name=spark_app_name,
                                              execution_timeout=timedelta(minutes=10),
                                              dag=dag
                                              )                                             
###############################################
Silver_Products = SparkSubmitOperator(task_id='Silver_Product_Transform',
                                              conn_id='spark_connect',
                                              application='/usr/local/spark/app/minio-test/silver-products.py',
                                              conf=minio_conf,
                                              total_executor_cores=2,
                                              jars=app_jars,
                                              driver_class_path=driver_class_path,
                                              packages="io.delta:delta-core_2.12:2.0.0,org.apache.hadoop:hadoop-aws:3.2.0,org.apache.spark:spark-hadoop-cloud_2.13:3.2.0",
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
start_task >> Silver_Customers  >> Silver_Orders >> Silver_Products >> end_task