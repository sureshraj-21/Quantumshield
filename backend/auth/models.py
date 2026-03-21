from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)

    password_hash = Column(String(255))
    is_premium = Column(Boolean, default=False)