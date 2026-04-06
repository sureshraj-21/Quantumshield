from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL 

# 🛡️ Step 1: URL Prefix Fix
# Render SQL URLs 'postgres://' nu start aagum, aana SQLAlchemy 'postgresql://' thaan ethirpaarkkum.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🚀 Step 2: SSL & Pooling Parameters
# Intha settings thaan unga connection-ai "Live"-ah vachirukkum.
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",      # 🔒 CRITICAL: Render SQL-ku ithu kandippa venum.
        "connect_timeout": 10      # Connection try panna 10 seconds time limit.
    },
    pool_pre_ping=True,            # 📡 Connection "Live"-ah irukkanu check pannum.
    pool_recycle=300,              # 🔄 Ovvoru 5 mins-kum connection-ai refresh pannum.
    pool_size=10,                  # Database kooda 10 connections ready-ah vachirukkum.
    max_overflow=20                # Extra connections thevaippatta allow pannum.
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency to get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()