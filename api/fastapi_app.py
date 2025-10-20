from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaConsumer
from kafka import KafkaProducer, KafkaConsumer
import time
import asyncio, json

app = FastAPI(title="PulseStream AI API",version = "1.0")


#Initialize Kafka Producer
producer =  KafkaProducer(
    bootstrap_servers = ['localhost: 29092'],
    value_serializer = lambda v: json.dumps(v).encode('utf-8')
)

#Publish data on Kafka
@app.post("/publish_news")
def publish_news(article: dict):
    try:
        producer.send("raw_new_feed", value=article)
        producer.flush()
        return{"status":"success","message":"Article published to Kafka"}
    except Exception as e: 
        raise HTTPException(status_code=500,detail=str(e))
                      
                      
@app.get("/health")
def health():
    return {"status":"ok"}

#@app.on_event("startup")
@app.get("/get_cleaned_news")
def get_cleaned_news(limit : int = 5):
    #loop = asyncio.get_event_loop()
    consumer = KafkaConsumer(
        "cleaned_news_feed",
        bootstrap_servers="localhost:29092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        consumer_timeout_ms = 5000
    )
    #await app.consumer.start()
    print("Kafka consumer started...")

    messages = []
    for msg in consumer:
        messages.append(msg.value)
        if len(messages) >= limit:
            break
    consumer.close()

    if not messages:
        raise HTTPException(status_code=404, detail="No Cleaned news found")
    return {"count":len(messages), "data":messages}

@app.on_event("shutdown")
async def stop_consumer():
    await app.consumer.stop()