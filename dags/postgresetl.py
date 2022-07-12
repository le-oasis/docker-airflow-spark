# Step 1: Importing modules
# Import Python dependencies needed for the workflow

import airflow
from datetime import timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago

# Step 2: Default Arguments
# Define default and DAG-specific arguments

args={'owner': 'airflow'}

default_args = {
    'owner': 'airflow',    
    #'start_date': airflow.utils.dates.days_ago(2),
    # 'end_date': datetime(),
    # 'depends_on_past': False,
    #'email': ['airflow@example.com'],
    #'email_on_failure': False,
    # 'email_on_retry': False,
    # If a task fails, retry it once after waiting
    # at least 5 minutes
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Step 3: Instantiate a DAG
# Give the DAG name, configure the schedule, and set the DAG settings.

dag_psql = DAG(
    dag_id = "postgresoperator_demo",
    default_args=default_args,
    # schedule_interval='0 0 * * *',
    schedule_interval='@once',	
    dagrun_timeout=timedelta(minutes=60),
    description='use case of psql operator in airflow',
    start_date = airflow.utils.dates.days_ago(1)
)

# Step 4: Set the Tasks
# The next step is setting up the tasks which want all the tasks in the workflow. 
# Here in the code create_table,insert_data are codes are tasks created by instantiating, 
# and also to execute the SQL query we created create_table_sql_query ,insert_data_sql_query

create_table_sql_query = """ 
CREATE TABLE employee (id INT NOT NULL, name VARCHAR(250) NOT NULL, dept VARCHAR(250) NOT NULL);
"""
insert_data_sql_query = """
insert into employee (id, name, dept) values(1, 'vamshi','bigdata'),(2, 'divya','bigdata'),(3, 'binny','projectmanager'),
(4, 'omair','projectmanager') ;"""

create_table = PostgresOperator(
sql = create_table_sql_query,
task_id = "create_table_task",
postgres_conn_id = "postgres_air",
dag = dag_psql
)

insert_data = PostgresOperator(
sql = insert_data_sql_query,
task_id = "insert_data_task",
postgres_conn_id = "postgres_air",
dag = dag_psql
)

# Step 5: Setting up Dependencies
# Here we are Setting up the dependencies or the order in which the tasks should be executed. 
# Here are a few ways you can define dependencies between them:

create_table >> insert_data

if __name__ == "__main__":
    dag_psql.cli()

