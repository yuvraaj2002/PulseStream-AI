from pydantic import BaseModel, Field, Emailstr
from typing import Optional

class ArticleBase(BaseModel):
    title: str = Field(...,min_length=3,max_length=100)
    content : str = Field(...,min_length=10)
    author_email: Emailstr

class ArticleCreate(ArticleBase):
    """Used for incoming POST reqs"""
    pass

class ArticleResponse(ArticleBase):
    """Used for sending resp back to user"""
    id : int