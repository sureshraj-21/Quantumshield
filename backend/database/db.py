from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# 🔗 Step 1: Inga thaan unga Screenshot URL irukkum
from config import DATABASE_URL 

# ==========================================
# ENGINE (FIXED FOR EXTERNAL RENDER SQL)
# ==========================================

# 🛡️ Render SQL URLs usually start with 'postgres://' 
# But SQLAlchemy needs 'postgresql://' to work correctly.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Helps avoid disconnect issues with External DB
    pool_recycle=3600    # Keeps the connection fresh
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

# 🟢 Dependency to get DB session (Unga routes-la use panna)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()