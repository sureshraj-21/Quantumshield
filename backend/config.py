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
# Database (Render Cloud Permission Fix)
# ==============================

# Render-la root folder-la write panna permission prachana varum.
# Adhanaala /tmp/ folder-ai use panrom, anga kandippa write access irukkum.
if os.environ.get('RENDER'):
    db_path = "/tmp/portfolio.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "portfolio.db")

DATABASE_URL = f"sqlite:///{db_path}"
# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "supersecretkey"
)