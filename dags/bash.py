import airflow
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'jozimar',
    'start_date': datetime(2022, 8, 12),
    'retries': 10,
	  'retry_delay': timedelta(hours=1)
}
with airflow.DAG('Spark_Minio_Bash',
                  default_args=default_args,
                  schedule_interval=None) as dag:
    task_elt_documento_pagar = BashOperator(
        task_id='Run',
        bash_command="python /usr/local/spark/app/final.py",
    )