# User table (SQLModel)
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid
from typing import Optional


#ORM Table ->tha actual table
class User(SQLModel, table=True):
    id : uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True,index=True)
    username : str = Field(index=True,nullable=False)
    email : EmailStr = Field(index=True,nullable=False,unique=True)
    hashed_password:str 
    created_at : datetime = Field(default_factory=datetime.utcnow)
    
#input schema for registration -> request body validation
class UserCreate(BaseModel):
    email:EmailStr
    password: str
    
#output schema response seialization to hide passwords
class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True
        
class EmailEvent(SQLModel,table=True):
    id: Optional[int] = Field(default=None,primary_key=True)
    user_email : str
    event_type: str
    status : str
    timestamp: datetime = Field(default_factory=datetime.utcnow)