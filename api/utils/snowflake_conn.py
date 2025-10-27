# api/utils/snowflake_conn.py
import snowflake.connector
import os

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "PULSESTREAM"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "ANALYTICS")
    )
