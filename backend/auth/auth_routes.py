from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# 🛑 DB connection settings.py vazhiyaa varum
from database.db import get_db 
from auth.models import User
from auth.auth_utils import create_access_token, hash_password, verify_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Schema for Input Validation
class AuthSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None 

@router.post("/signup")
def register(user_data: AuthSchema, db: Session = Depends(get_db)):
    # 🔍 Check if username or email already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already exists"
        )
    
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
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": new_user.id
        }
    except Exception as e:
        db.rollback()
        # Internal server error detailed message for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database Error: {str(e)}"
        )

@router.post("/login")
def login(user_data: AuthSchema, db: Session = Depends(get_db)):
    # 🔎 Search user in DB
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # 🛡️ Verify User & Password
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    # 🔑 Create JWT Token
    token = create_access_token({"sub": user.username})
    
    # 🟢 RESPONSE: Added email and status for better Frontend sync
    return {
        "access_token": token, 
        "token_type": "bearer",
        "username": user.username,
        "email": user.email,
        "status": "logged_in"
    }