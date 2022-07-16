import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.utils.dates import days_ago


default_args = {
    'owner': 'airflow',    
    #'start_date': airflow.utils.dates.days_ago(2),
    # 'end_date': datetime(),
    # 'depends_on_past': False,
    # 'email': ['airflow@example.com'],
    # 'email_on_failure': False,
    #'email_on_retry': False,
    # If a task fails, retry it once after waiting
    # at least 5 minutes
    #'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag_spark = DAG(
        dag_id = "sparkoperator_demo",
        default_args=default_args,
        # schedule_interval='0 0 * * *',
        schedule_interval='@once',	
        dagrun_timeout=timedelta(minutes=60),
        description='use case of sparkoperator in airflow',
        start_date = airflow.utils.dates.days_ago(1)
)


spark_submit_local = SparkSubmitOperator(
		application ='/usr/local/spark/app/basic.py' ,
		conn_id= 'spark_connect', 
		task_id='spark_submit_task', 
		dag=dag_spark
		)

spark_submit_local

if __name__ == "__main__":
    dag_spark.cli()