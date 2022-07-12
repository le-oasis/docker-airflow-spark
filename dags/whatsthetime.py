from datetime import timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime



from airflow import DAG


from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['youremail@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def print_current_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)

with DAG(
    'current_time_dag',
    default_args=default_args,
    description='current_time_dag',
    schedule_interval='*/5 * * * *',
    start_date=days_ago(2)
) as dag:
    start_task = DummyOperator(
	task_id='start_task',
)
task_time = PythonOperator(
	task_id='current_time',
	   python_callable=print_current_time
)
end_task = DummyOperator(
	task_id='end_task'
)
start_task >> task_time >> end_task