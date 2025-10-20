from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
import asyncio, json

app = FastAPI(title="PulseStream AI API")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.on_event("startup")
async def start_consumer():
    loop = asyncio.get_event_loop()
    app.consumer = AIOKafkaConsumer(
        "cleaned_news_feed",
        bootstrap_servers="localhost:29092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset='earliest'
    )
    await app.consumer.start()
    print("Kafka consumer started...")
    
@app.on_event("shutdown")
async def stop_consumer():
    await app.consumer.stop()
    
@app.get("/news/latest")
async def get_latest(limit: int = 10):
    messages = []
    async for msg in app.consumer:
        if len(messages) >= limit:
            break
    return messages