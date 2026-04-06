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

# 🚀 Step 2: Add SSL and Pooling parameters
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}, # 🛡️ Intha line thaan SSL error-ai fix pannum
    pool_pre_ping=True,                  # Verifies connection before using it
    pool_recycle=300,                    # Refreshes connection every 5 minutes
    pool_size=5,                         # Limit number of connections
    max_overflow=10                      # Extra connections if needed
)

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