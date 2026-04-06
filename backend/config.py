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
# ==============================
# 🗄️ Database Configuration (Hybrid Logic)
# ==============================

EXTERNAL_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT1SJid3SSIECxW@dpg-d79mplffte5s739p8l8g-a.singapore-postgres.render.com/quantshield_db?sslmode=require"

INTERNAL_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT1SJid3SSIECxW@dpg-d79mplffte5s739p8l8g-a/quantshield_db"

# 🔥 Correct detection (no mistake)
if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
    DATABASE_URL = INTERNAL_DB_URL
else:
    DATABASE_URL = EXTERNAL_DB_URL

# Fix for SQLAlchemy prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Debug (optional)
print("Using DB:", DATABASE_URL)

# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")