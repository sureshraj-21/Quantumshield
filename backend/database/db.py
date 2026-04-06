from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import DATABASE_URL

# ==========================================
# ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # helps avoid MySQL disconnect issues
)

# ==========================================
# SESSION
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==========================================
# BASE MODEL
# ==========================================

Base = declarative_base()