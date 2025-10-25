{{config(MATERIALIZED='table')}}

SELECT
    TITLE,
    SOURCE,
    LANGUAGE,
    SENTIMENT,
    POLARITY_SCORE,
    LENGTH(TEXT) AS text_length,
    CASE 
        WHEN POLARITY_SCORE > 0 THEN 'Positive'
        WHEN POLARITY_SCORE < 0 THEN 'Negative'  
        ELSE  'Neutral'
    END AS Ssentiment_label
FROM {{ref('stg_news_raw')}}
WHERE TITLE IS NOT NULL