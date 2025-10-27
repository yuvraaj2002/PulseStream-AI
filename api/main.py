# api/main.py
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import pickle
import numpy as np
from utils.feedback_handler import save_feedback

app = FastAPI(
    title="PulseStream Recommender API",
    description="TF-IDF based recommendation and feedback service",
    version="1.0.0"
)




@app.get("/")
def home():
    return {"message": "API running!"}



#  Load artifacts on startup
MODEL_PATH = "model/vectorizer.pkl"
TFIDF_PATH = "model/tfidf_matrix.pkl"
META_PATH = "data/articles_meta.csv"

vectorizer = pickle.load(open(MODEL_PATH, "rb"))
tfidf_matrix = pickle.load(open(TFIDF_PATH, "rb"))
articles_df = pd.read_csv(META_PATH)

#  Helper to build pseudo user vector
def build_user_vector(user_id: str):
    
    # TODO: replace with real personalization logic later
    user_profile_text = "latest articles read by user " + user_id
    return vectorizer.transform([user_profile_text])


@app.get("/recommendations")
def get_recommendations(user_id: str = Query(...), top_n: int = 5):
    try:
        user_vector = build_user_vector(user_id)
        cosine_sim = cosine_similarity(user_vector, tfidf_matrix).flatten()
        top_idx = np.argsort(cosine_sim)[-top_n:][::-1]

        results = articles_df.iloc[top_idx][["article_id", "title"]].copy()
        results["score"] = cosine_sim[top_idx]
        return {"user_id": user_id, "recommendations": results.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Feedback schema
class Feedback(BaseModel):
    user_id: str
    article_id: int
    action: str   # e.g. "clicked", "liked", "ignored"


@app.post("/feedback")
def collect_feedback(data: Feedback):
    try:
        save_feedback(data.user_id, data.article_id, data.action)
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
