from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import SessionLocal
from auth.models import User
from auth.auth_utils import create_access_token
from pydantic import BaseModel

router = APIRouter()

# Schema for JSON Request
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

# ===============================
# REGISTER Fix (With Error Handling)
# ===============================
@router.post("/signup")
def register(user_data: AuthSchema, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    try:
        # 2. Create new user object
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password # Professional project-na inga hash pannanum (bcrypt)
        )
        
        # 3. Save to Database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully"}
        
    except Exception as e:
        db.rollback() # Error vandha process-ai cancel pannum
        print(f"Database Error: {e}") # Render Logs-la error kaatum
        raise HTTPException(
            status_code=500, 
            detail=f"Database Write Error: Check if disk is read-only. Error: {str(e)}"
        )

# ===============================
# LOGIN Fix
# ===============================
@router.post("/login")
def login(user_data: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or user.password != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}