import requests,json, time
from kafka import KafkaProducer

API_KEY = "31514b9d11b242dc9cb7c2eef6d658eb"
producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={API_KEY}"
    response = requests.get(url).json()
    
    #Checking the API
    print("Response:", response)
    if "articles" not in response:
        print("No 'articles' found . check API key or URL.")
        return
    
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