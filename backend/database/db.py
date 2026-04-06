from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import DATABASE_URL

# 🛡️ Fix prefix (Render sometimes gives postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🚀 Create Engine (Production Ready)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Connection alive check
    pool_recycle=300,     # Prevent timeout
    pool_size=10,
    max_overflow=20
)

# 📦 Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🧱 Base Class
Base = declarative_base()

# 🔌 Dependency (FastAPI use)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()