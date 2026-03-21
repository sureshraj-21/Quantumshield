import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Core Assets
# ==============================

ASSETS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS"
]

SAFE_HAVEN_ASSETS = [
    "GOLDBEES.NS",
    "LIQUIDBEES.NS"
]

# ==============================
# Market Indicators
# ==============================

MARKET_INDEX = "^NSEI"
VIX_INDEX = "^INDIAVIX"

# ==============================
# Model Parameters
# ==============================

LOOKBACK_PERIOD = "6mo"   # Better for HMM & MC

BSI_THRESHOLD = 2.5
CPS_THRESHOLD = 1.2

# ==============================
# Database
# ==============================

DATABASE_URL = "sqlite:///./portfolio.db"

# ==============================
# Security
# ==============================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "supersecretkey"
)
