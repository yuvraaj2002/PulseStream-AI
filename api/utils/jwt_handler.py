#JWT creating + decoding
from datetime import datetime, timedelta 
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    from jose import JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def create_password_reset_token(email: str):
    """Short-lived token for password reset"""
    return create_access_token({"sub": email, "purpose": "reset"}, timedelta(minutes=15))
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    """dependency to extract and validate the user from th JWQT token"""
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate":"Bearer"}
    )
    
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_email: str=payload.get("sub")
        if user_email is None:
            raise credentials_exception
        return {"email":user_email}
    except JWTError:
        raise credentials_exception
    