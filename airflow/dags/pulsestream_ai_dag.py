from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "pulsestream",
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id="pulsestream_ai_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/15 * * * *",   # every 15 minutes
    catchup=False,
    default_args=default_args,
    description="Orchestrate producer -> consumer for PulseStream-AI"
) as dag:

    # 1) Produce a fresh batch of raw news
    produce_raw = BashOperator(
        task_id="produce_raw_feed",
        bash_command="python /opt/pulsestream/producers/news_producer.py"
    )

    # 2) Consume-clean-enrich that batch into cleaned_news_feed
    consume_clean = BashOperator(
        task_id="consume_and_clean",
        bash_command="python /opt/pulsestream/consumers/news_consumer.py"
    )

    produce_raw >> consume_clean
