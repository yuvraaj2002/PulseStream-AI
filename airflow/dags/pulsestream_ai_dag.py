from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'tanish',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='pulsestream_ai_dag',
    default_args=default_args,
    description='Main orchestration DAG for data ingestion',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:
    
    def extract_data():
        print("📥 Extracting data for PulseStream AI...")

    task_extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    trigger_training = TriggerDagRunOperator(
        task_id='trigger_model_training',
        trigger_dag_id='model_training_dag'
    )

    task_extract >> trigger_training
