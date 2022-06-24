"""This dag only runs some simple tasks to make a new directory& check the directory."""


from email.policy import default
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {

    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2022, 6, 14),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),

    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),

}

dag = DAG("example_dag", default_args=default_args, schedule_interval=timedelta(1))

# t1 and t2  are examples of tasks created by instantiating operators

t1 = BashOperator(task_id="make_dir", bash_command="mkdir test_dir", dag=dag)
t2 = BashOperator(task_id="check_dir", bash_command="ls", dag=dag)
t2.set_upstream(t1)