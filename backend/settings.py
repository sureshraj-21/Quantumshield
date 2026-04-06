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
# 🗄️ Database Configuration (FINAL FIX)
# ==============================

# 🔥 Render automatically provides DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# ⚠️ Safety check (important)
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found. Please check Render environment variables.")

# Fix prefix (Render sometimes gives postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("✅ Using DB:", DATABASE_URL)

# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")