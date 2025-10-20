from kafka import KafkaConsumer, KafkaProducer
from textblob import TextBlob
from langdetect import detect
import json, re

consumer = KafkaConsumer(
    'raw_new_feed',
    bootstrap_servers=['localhost:29092'],
    group_id=None,
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
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

print(" Reading messages from raw_news_feed...")
count = 0
for msg in consumer:
    try:
        data = msg.value
        text = data.get("description") or ""
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

        producer.send("cleaned_news_feed", value=enriched)
        print(f"Cleaned & sent: {enriched['title']}")
        count += 1
    except Exception as e:
        print("Error:", e)

print(f"Finished reading {count} messages.")
