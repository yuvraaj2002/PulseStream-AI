# api/utils/database.py
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# Ensure .env is loaded from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")
# reate SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

#  Provide session and init_db
def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
