import datetime
from .snowflake_conn import get_snowflake_connection

def save_feedback(user_id:str,article_id:int,action:str):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    query = f"""
        INSERT INTO ANALYTICS.USER_FEEDBACK(USER_ID,ARTICLE_ID,ACTION,TIMESTAMP)
        VALUES('{user_id}',{article_id},'{action}','{timestamp}')
    """
    cursor.execute(query)
    cursor.close()
    conn.close()
    