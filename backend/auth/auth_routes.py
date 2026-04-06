from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# 🛑 IMPORT-AI database/db.py-LA IRUNDHU EDUKKANUM (Athu dhaan settings-ai use pannum)
from database.db import get_db 
from auth.models import User
from auth.auth_utils import create_access_token, hash_password, verify_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AuthSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None 

# 🛑 Indha LOCAL get_db THEVAI ILLA, database/db.py-la irundhu varanum
# Neenga inga SessionLocal() direct-ah use panna, athu settings.py-ai detect pannaadhu.

@router.post("/signup")
def register(user_data: AuthSchema, db: Session = Depends(get_db)):
    # 🔍 Check if user exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    try:
        hashed_pw = hash_password(user_data.password)
        new_user = User(
            username=user_data.username, 
            email=user_data.email, 
            password=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully"}
    except Exception as e:
        db.rollback()
        # ⚠️ SQL Error details-ai inga thaan pakkalam
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(user_data: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "username": user.username 
    }