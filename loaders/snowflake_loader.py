import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaConsumer
import snowflake.connector as sf
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()  # reads .env if present

# ---- Snowflake connection params
SF_PARAMS = dict(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    database=os.getenv("SNOWFLAKE_DATABASE", "PULSESTREAM"),
    schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW_DATA"),
)

TOPIC = "cleaned_news_feed"      # your enriched topic
BROKER = "localhost:29092"       # outside docker; use kafka:9092 if running in a container

def fetch_batch_from_kafka(limit=200, timeout_ms=8000):
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[BROKER],
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=timeout_ms
    )
    rows = []
    for msg in consumer:
        d = msg.value
        rows.append({
            "SOURCE": d.get("source"),
            "TITLE": d.get("title"),
            "TEXT": d.get("text"),
            "LANGUAGE": d.get("language"),
            "SENTIMENT": d.get("sentiment"),
            "POLARITY_SCORE": d.get("polarity_score"),
            "PUBLISHEDAT": d.get("publishedAt"),
            "URL": d.get("url"),
        })
        if len(rows) >= limit:
            break
    consumer.close()
    return pd.DataFrame(rows)

def load_df_to_snowflake(df: pd.DataFrame):
    if df.empty:
        print("No rows to load. Done.")
        return

    # Optional: coerce types / timestamps
    if "PUBLISHEDAT" in df.columns:
        df["PUBLISHEDAT"] = pd.to_datetime(df["PUBLISHEDAT"], errors="coerce", utc=True)

    print(f"Connecting to Snowflake: {SF_PARAMS['account']}")
    conn = sf.connect(**SF_PARAMS)
    try:
        # Ensure we’re in the right DB/Schema/Warehouse
        cs = conn.cursor()
        cs.execute(f"USE WAREHOUSE {SF_PARAMS['warehouse']}")
        cs.execute(f"USE DATABASE {SF_PARAMS['database']}")
        cs.execute(f"USE SCHEMA {SF_PARAMS['schema']}")

        # Write into RAW_DATA.NEWS_RAW
        success, nchunks, nrows, _ = write_pandas(
            conn,
            df,
            table_name="NEWS_RAW",
            auto_create_table=False,  # table already created
            overwrite=False
        )
        print(f"write_pandas -> success={success}, chunks={nchunks}, rows={nrows}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(" Fetching a batch from Kafka…")
    df = fetch_batch_from_kafka(limit=200)
    print(f"Fetched {len(df)} rows.")

    print(" Loading to Snowflake RAW_DATA.NEWS_RAW…")
    load_df_to_snowflake(df)
    print(" Done.")
