{{ config(MATERIALIZED='table') }}

SELECT
    SOURCE,
    LANGUAGE,
    SENTIMENT,
    COUNT(*) AS article_count,
    AVG(POLARITY_SCORE) as avg_polarity
FROM {{ref('stg_news_raw')}}
GROUP BY SOURCE, LANGUAGE, SENTIMENT