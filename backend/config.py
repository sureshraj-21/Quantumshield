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
# 🗄️ External Database (PERMANENT FIX)
# ==============================

# 🛑 PAZHAYA SQLITE CODE-AI REMOVE PANNITTAEN (Adhu thaan delete aagura prachana)
# ✅ INGA UNGA SCREENSHOT-LA IRUNDHA EXTERNAL URL-AI PASTE PANNUNGA

# 🔐 Added '?sslmode=require' at the end to fix SSL errors
# ✅ Internal URL (No SSL parameter needed for Internal)
RENDER_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT1SJid3SSIECxW@dpg-d79mplffte5s739p8l8g-a/quantshield_db"

# Database URL logic
if os.environ.get('RENDER'):
    # Render-la irukkumbodhu internal network-aiye use pannum
    DATABASE_URL = RENDER_DB_URL
else:
    # Local-la irukkumbodhu (Internal URL local-la work aagaathu)
    # Local test-kku SQLite illana External URL use pannalaam
    DATABASE_URL = RENDER_DB_URL

# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "supersecretkey"
)