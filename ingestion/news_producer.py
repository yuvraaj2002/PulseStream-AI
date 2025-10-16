import requests,json, time
from kafka import KafkaProducer

API_KEY = "eb76b05c-5e2c-4727-a3b0-d48df7c6ff6b"
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={API_KEY}"
    response = requests.get(url).json()
    for article in response["articles"]:
        data = {
            "source":article["source"]["name"],
            "title":article["title"],
            "description":article["description"],
            "url":article["url"],
            "publishedAt":article["publishedAt"]
        }
        producer.send("raw_news_feed",value=data)
        
while True:
    fetch_news()
    time.sleep(5)