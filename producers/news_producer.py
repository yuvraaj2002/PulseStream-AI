import requests, json, time
from kafka import KafkaProducer
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={API_KEY}"
    response = requests.get(url).json()
    for article in response.get("articles", []):
        data = {
            "source": article.get("source"),
            "author": article.get("author"),
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "urlToImage": article.get("urlToImage"),
            "publishedAt": article.get("publishedAt"),
            "content": article.get("content")
        }
        producer.send("raw_news_feed", value=data)

while True:
    fetch_news()
    time.sleep(300)  # every 5 minutes
