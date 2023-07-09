# Step 1: Importing modules
# Import Python dependencies needed for the workflow
import airflow
from datetime import timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
###############################################
# Step 2: Default Arguments
# Define default and DAG-specific arguments
###############################################
args = {
    'owner': 'airflow',    
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
###############################################
# Step 3: Instantiate a DAG
# Give the DAG name, configure the schedule, and set the DAG settings.
with DAG(
    dag_id='Postgres-Demo',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['read/write', 'postgres'],
) as dag:
        start_task = DummyOperator(
	task_id='start_task'
)
############################################################
# Step 4: Set the Tasks
# The next step is setting up the tasks which want all the tasks in the workflow. 
# Here in the code create_table,insert_data are codes are tasks created by instantiating, 
# and also to execute the SQL query we created create_table_sql_query ,insert_data_sql_query
##################################################################
create_table_sql_query = """ 
CREATE TABLE IF NOT EXISTS customers (id INT NOT NULL, created timestamp DEFAULT CURRENT_TIMESTAMP,
  updated timestamp DEFAULT CURRENT_TIMESTAMP,
  first_name varchar(100) NOT NULL,
  last_name varchar(100) NOT NULL,
  email varchar(255) NOT NULL UNIQUE, PRIMARY KEY(id)
);
"""
##################################################################
insert_data_sql_query = """
INSERT INTO customers (id, created, first_name, last_name, email) 
VALUES (1, '2021-02-16 00:16:06', 'Scott', 'Haines', 'scott@coffeeco.com'), 
(2,'2021-02-16 00:16:06', 'John', 'Hamm', 'john.hamm@acme.com'), 
(3,'2021-02-16 00:16:06', 'Milo', 'Haines', 'mhaines@coffeeco.com'),
(4,'2021-02-21 21:00:00', 'Penny', 'Haines', 'penny@coffeeco.com'),
(5,'2021-02-21 22:00:00', 'Cloud', 'Fast', 'cloud.fast@acme.com'),
(6,'2021-02-21 23:00:00', 'Marshal', 'Haines', 'paws@coffeeco.com'),
(7,'2021-02-24 09:00:00', 'Willow', 'Haines', 'willow@coffeeco.com'),
(8,'2021-02-24 09:00:00', 'Clover', 'Haines', 'pup@coffeeco.com');"""
##################################################################
# Step 5: Create the Tasks
create_table = PostgresOperator(
sql = create_table_sql_query,
task_id = "create_table_task",
postgres_conn_id = "postgres_air",
dag = dag
)
##################################################################
insert_data = PostgresOperator(
sql = insert_data_sql_query,
task_id = "insert_data_task",
postgres_conn_id = "postgres_air",
dag = dag
)
##################################################################
# Step 5: Setting up Dependencies
# Here we are Setting up the dependencies or the order in which the tasks should be executed. 
# Here are a few ways you can define dependencies between them:
###############################################
end_task = DummyOperator(task_id='end_task')                                  
###############################################
start_task >> create_table >> insert_data >> end_task
###############################################

