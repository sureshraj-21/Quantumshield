from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL 

# 🛡️ Step 1: URL Prefix Fix
# Render URLs often start with 'postgres://', SQLAlchemy needs 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🚀 Step 2: Internal Connection Engine
# Internal network-ku SSL thevai illai, so 'connect_args' remove pannittaen.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,            # 📡 Connection alive-ah irukkanu check pannum.
    pool_recycle=300,              # 🔄 Connection-ai refresh pannum (Prevent timeouts).
    pool_size=10,                  # Number of connections to keep open.
    max_overflow=20                # Extra connections during high traffic.
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()