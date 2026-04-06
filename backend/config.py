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

RENDER_DB_URL = "postgresql://quantshield_db_user:NLVqB2hddaC58S0g1oT45uXvJ3S4j9uC@dpg-cva791ogph6c73dg0sqg-a.singapore-postgres.render.com/quantshield_db"

# Database URL logic
if os.environ.get('RENDER'):
    # Render cloud-la irukkumbodhu External URL-ai use pannum
    DATABASE_URL = os.environ.get('DATABASE_URL', RENDER_DB_URL)
else:
    # Local-la work pannumbodhu neenga SQLite use pannalaam (illana same URL)
    DATABASE_URL = RENDER_DB_URL 

# 🛡️ SQLAlchemy needs 'postgresql://' not 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==============================
# Security
# ==============================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "supersecretkey"
)