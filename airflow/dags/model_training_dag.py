from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import snowflake.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
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
    dag_id='model_training_dag',
    default_args=default_args,
    description='Model training DAG for PulseStream AI',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:
    
    def train_model():
        print("✅ Starting model training job...")
        # Your Snowflake connection and TF-IDF logic here

    task_train_model = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )


# --- Connection info (update credentials) ---
SNOWFLAKE_USER = "Tanish"
SNOWFLAKE_PASSWORD = "Tanish12345678"
SNOWFLAKE_ACCOUNT = "XAPUZMR-GY39323"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "PULSESTREAM"
SNOWFLAKE_SCHEMA = "ANALYTICS"

# --- Extract task ---
def extract_from_snowflake():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    query = """
        SELECT TITLE, TEXT, SOURCE, SENTIMENT, POLARITY_SCORE
        FROM FACT_ARTICLE_FEATURES
        WHERE TITLE IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()

    os.makedirs("/opt/airflow/data", exist_ok=True)
    df.to_csv("/opt/airflow/data/news_features.csv", index=False)
    print(f"Extracted {len(df)} records from Snowflake.")

# --- Transform + Model task ---
def train_model():
    df = pd.read_csv("/opt/airflow/data/news_features.csv")
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(df["TEXT"].fillna(""))

    similarity_matrix = cosine_similarity(tfidf)
    sim_df = pd.DataFrame(similarity_matrix)
    sim_df.to_csv("/opt/airflow/data/similarity_matrix.csv", index=False)
    print("Model trained — similarity matrix saved!")

# --- DAG definition ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 10, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="model_training_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["pulse_dbt", "snowflake", "ml"]
) as dag:

    extract_task = PythonOperator(
        task_id="extract_from_snowflake",
        python_callable=extract_from_snowflake,
    )

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    extract_task >> train_task
