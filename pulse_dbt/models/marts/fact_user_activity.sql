{{config(MATERIALIZED='table')}}

SELECT 
    NULL AS user_id,
    NULL AS article_title,
    NULL AS interaction_type,
    NULL AS timestamp
WHERE FALSE