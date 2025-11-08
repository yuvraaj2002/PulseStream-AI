from fastapi import APIRouter, Depends, HTTPException, status, Query
from api.utils.jwt_handler import create_password_reset_token,verify_token
from api.utils.email_utils import send_reset_email
from api.utils.password_hashing import get_password_hash
from sqlmodel import Session, select
from api.model.auth_model import User, UserCreate, UserRead
from api.utils.database import get_session
from api.utils.password_hashing import hash_password, verify_password
from api.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=user.email, hashed_password=hash_password(user.password))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/request-reset")
def request_password_reset(email: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_password_reset_token(email)
    send_reset_email(email, token)
    return {"status": "success", "message": "Reset link sent"}

@router.post("/reset-password")
def reset_password(token: str = Query(...), new_password: str = Query(...), session: Session = Depends(get_session)):
    payload = verify_token(token)
    if not payload or payload.get("purpose") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    return {"status": "success", "message": "Password reset successfully"}