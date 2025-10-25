{{ config(materialized='view') }}

SELECT
    TITLE,
    TEXT,
    SOURCE,
    LANGUAGE,
    SENTIMENT,
    POLARITY_SCORE,
    URL
FROM {{ source('raw_data', 'news_raw') }}
WHERE TITLE IS NOT NULL
