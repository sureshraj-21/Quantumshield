import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Core Assets
# ==============================
ASSETS = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
SAFE_HAVEN_ASSETS = ["GOLDBEES.NS", "LIQUIDBEES.NS"]

# ==============================
# Market Indicators
# ==============================
MARKET_INDEX = "^NSEI"
VIX_INDEX = "^INDIAVIX"

# ==============================
# Model Parameters
# ==============================
LOOKBACK_PERIOD = "6mo" 
BSI_THRESHOLD = 2.5
CPS_THRESHOLD = 1.2

# ==============================
# 🗄️ Database Configuration (Hybrid Logic)
# ==============================

# 🌍 1. External URL (Singapore - Use this for Local VS Code Testing)
EXTERNAL_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT1SJid3SSIECxW@dpg-d79mplffte5s739p8l8g-a.singapore-postgres.render.com/quantshield_db?sslmode=require"

# 🔑 2. Internal URL (Fast - Use this ONLY inside Render Cloud)
INTERNAL_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT1SJid3SSIECxW@dpg-d79mplffte5s739p8l8g-a/quantshield_db"

# 🚀 Logic to switch automatically
if os.environ.get('RENDER'):
    # Render-la irukkumbodhu Internal network use pannum (No SSL Error)
    DATABASE_URL = INTERNAL_DB_URL
else:
    # Local VS Code-la run pannumbodhu External URL use pannum
    DATABASE_URL = EXTERNAL_DB_URL

# Fix for SQLAlchemy prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")