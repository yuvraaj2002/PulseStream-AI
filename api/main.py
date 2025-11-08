from fastapi import FastAPI, Query, HTTPException, Depends 
from pydantic import BaseModel
from api.utils.database import init_db, get_session
from sqlmodel import Session, select
from api.model.auth_model import User
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import pickle
import numpy as np
import os
from api.router.auth_router import router as auth_router
from api.utils.feedback_handler import save_feedback

app = FastAPI(
    title="PulseStream Recommender API",
    description="Dynamic TF-IDF based recommendation and feedback service",
    version="2.0.0"
)

# ---------------------------
# PATH CONFIG
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")
TFIDF_PATH = os.path.join(BASE_DIR, "model", "tfidf_matrix.pkl")
META_PATH = os.path.join(BASE_DIR, "data", "articles_meta.csv")


@app.on_event("startup")
def on_startup():
    init_db()
    
app.include_router(auth_router)
    
@app.get("/")
def home():
    return {"message":"Connected to Neon DB successfully"}

@app.get("/users")
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users
# ---------------------------
# INIT / LOAD DATA
# ---------------------------
def initialize_dummy_data():
    os.makedirs(os.path.join(BASE_DIR, "model"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    articles = [
        {"article_id": 1, "title": "AI in Healthcare"},
        {"article_id": 2, "title": "Data Engineering with Kafka"},
        {"article_id": 3, "title": "Snowflake vs BigQuery"},
        {"article_id": 4, "title": "Machine Learning in Retail"},
        {"article_id": 5, "title": "Python for Data Science"},
    ]
    df = pd.DataFrame(articles)
    df.to_csv(META_PATH, index=False)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df["title"])

    pickle.dump(vectorizer, open(MODEL_PATH, "wb"))
    pickle.dump(tfidf_matrix, open(TFIDF_PATH, "wb"))

    return vectorizer, tfidf_matrix, df

try:
    if not all(os.path.exists(p) for p in [MODEL_PATH, TFIDF_PATH, META_PATH]):
        vectorizer, tfidf_matrix, articles_df = initialize_dummy_data()
    else:
        vectorizer = pickle.load(open(MODEL_PATH, "rb"))
        tfidf_matrix = pickle.load(open(TFIDF_PATH, "rb"))
        articles_df = pd.read_csv(META_PATH)
        if articles_df.empty:
            vectorizer, tfidf_matrix, articles_df = initialize_dummy_data()
except Exception:
    vectorizer, tfidf_matrix, articles_df = initialize_dummy_data()

# ---------------------------
# MODELS
# ---------------------------
class Article(BaseModel):
    title: str

class Feedback(BaseModel):
    user_id: str
    article_id: int
    action: str  # e.g. "liked", "clicked"

# ---------------------------
# ROUTES
# ---------------------------

@app.get("/")
def home():
    return {"message": "PulseStream API is live!"}

@app.post("/add_article")
def add_article(article: Article):
    """Dynamically add a new article and retrain TF-IDF."""
    global articles_df, vectorizer, tfidf_matrix

    try:
        new_id = int(articles_df["article_id"].max()) + 1 if not articles_df.empty else 1
        new_row = pd.DataFrame([{"article_id": new_id, "title": article.title}])
        articles_df = pd.concat([articles_df, new_row], ignore_index=True)

        # Retrain TF-IDF model
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(articles_df["title"])

        # Save updated artifacts
        pickle.dump(vectorizer, open(MODEL_PATH, "wb"))
        pickle.dump(tfidf_matrix, open(TFIDF_PATH, "wb"))
        articles_df.to_csv(META_PATH, index=False)

        return {"status": "success", "new_article_id": new_id, "message": "Article added and TF-IDF retrained."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add article: {str(e)}")


@app.get("/recommendations")
def get_recommendations(user_id: str = Query(...), top_n: int = 5):
    """Return top N recommendations for a user."""
    try:
        user_vector = vectorizer.transform([f"recent reads by {user_id}"])
        cosine_sim = linear_kernel(user_vector, tfidf_matrix).flatten()
        top_idx = np.argsort(cosine_sim)[-top_n:][::-1]
        results = articles_df.iloc[top_idx][["article_id", "title"]].copy()
        results["score"] = cosine_sim[top_idx]
        return {"user_id": user_id, "recommendations": results.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def collect_feedback(data: Feedback):
    """Collect user feedback for retraining."""
    try:
        save_feedback(data.user_id, data.article_id, data.action)
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
