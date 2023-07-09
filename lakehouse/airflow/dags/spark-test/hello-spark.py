# Import Python dependencies needed for the workflow
import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

###############################################
# Parameters & Arguments
spark_app_name="Spark_Test"
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
    dag_id='Spark-Test',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['read', 'spark'],
) as dag:
        start_task = DummyOperator(
	task_id='start_task'
)
###############################################

###############################################
# Sequence of Tasks
Spark_Test = SparkSubmitOperator(task_id='Spark_Test',
                                              application='/usr/local/spark/app/spark-test/sparksubmit.py',
                                              conn_id= 'spark_connect', 
                                              total_executor_cores=2,
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
start_task >> Spark_Test >> end_task