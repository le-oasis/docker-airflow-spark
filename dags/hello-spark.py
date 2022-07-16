from email.policy import default
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {

    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2022, 7, 14),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("spark-dag", default_args=default_args, schedule_interval=None)

# t1 and t2  are examples of tasks created by instantiating operators

t1 = BashOperator(task_id="spark-test", bash_command="/home/airflow/.local/bin/spark-submit --master spark://spark-master:7077 /usr/local/spark/app/sparksubmit_basic.py /usr/local/spark/resources/data/testfile.txt", dag=dag)


# --conf spark.driver.host=$(hostname -i)

t2 = BashOperator(task_id="print_date", bash_command="date", dag=dag)


t2.set_upstream(t1)