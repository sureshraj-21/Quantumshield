import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# DATABASE URL CONFIGURATION
# ==========================================

# 1. First, priority for Environment Variable (Render-la set panna idhu work aagum)
# 2. Second, fallback to your hardcoded External URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://quantshield_db_1v8z_user:KarES8T8LjsDEiidGrmP2yagGNFmd5tP@dpg-d7gcpou47okc73fj3ds0-a.oregon-postgres.render.com/quantshield_db_1v8z"
)

# Render specific fix: SQLAlchemy 1.4+ needs 'postgresql://' instead of 'postgres://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==========================================
# ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Connection drop aagama paathukkum
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

# Database helper function (Unga routes-la idhai use pannunga)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()