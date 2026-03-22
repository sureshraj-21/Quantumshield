from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import SessionLocal
from auth.models import User
from auth.auth_utils import create_access_token, hash_password, verify_password
from pydantic import BaseModel

router = APIRouter()

class AuthSchema(BaseModel):
    username: str
    password: str
    email: str = None 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def register(user_data: AuthSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    try:
        hashed_pw = hash_password(user_data.password)
        new_user = User(username=user_data.username, email=user_data.email, password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(user_data: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # Password verify pannum bodhu manual input empty-ah irundha fail aagum
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    
    # 🟢 IMPORTANT: Returning username to display in Frontend
    return {
        "access_token": token, 
        "token_type": "bearer",
        "username": user.username 
    }