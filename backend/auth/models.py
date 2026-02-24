from sqlalchemy import Column, Integer, String
from database.db import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)

    password = Column(String(255))