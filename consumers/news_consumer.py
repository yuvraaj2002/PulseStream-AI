from kafka import KafkaConsumer, KafkaProducer
from textblob import TextBlob
from langdetect import detect
import json, re

consumer = KafkaConsumer(
    'raw_news_feed',
    bootstrap_servers=['localhost:9092'],
    group_id='pulse_cleaner_group_v3',       # NEW GROUP ID (forces fresh read)
    auto_offset_reset='earliest',            # start from beginning
    enable_auto_commit=False,                # avoid skipping committed offsets
    consumer_timeout_ms=10000,               # stop after 10s if no new data
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return polarity, "positive"
    elif polarity < -0.1:
        return polarity, "negative"
    else:
        return polarity, "neutral"

count = 0
for msg in consumer:
    try:
        data = msg.value
        text = data.get("description") or data.get("text") or ""
        cleaned_text = clean_text(text)
        lang = detect(cleaned_text) if cleaned_text else "unknown"
        polarity, sentiment = analyze_sentiment(cleaned_text)

        enriched = {
            "source": data.get("source", "unknown"),
            "title": data.get("title", ""),
            "text": cleaned_text,
            "language": lang,
            "sentiment": sentiment,
            "polarity_score": round(polarity, 3),
            "publishedAt": data.get("publishedAt", ""),
            "url": data.get("url", "")
        }

        producer.send("clean_news_feed", value=enriched)
        print(f"✅ Cleaned & sent: {enriched['title'][:60]}...")
        count += 1
    except Exception as e:
        print(f"❌ Error processing message: {e}")

print(f"🔹 Finished reading {count} messages.")
