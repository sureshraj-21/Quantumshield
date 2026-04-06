import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from auth.auth_routes import router as auth_router
# 🗄️ Database engine and Base
from database.db import engine, Base 
from twilio.rest import Client 

app = FastAPI(
    title="QuantShield AI Optimizer",
    version="2.0"
)

# ===============================
# 🔑 TWILIO CONFIGURATION
# ===============================
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC5a3cdd61a29ed82e3a5f2e54977fb072')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'd4150507de5b905fe8c39541294495de')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' 
MY_WHATSAPP_NUMBER = 'whatsapp:+919962126306'

try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    print(f"Twilio Client Init Error: {e}")
    client = None

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 🗄️ DATABASE REFRESH LOGIC (FIX FOR STATUS 500)
# ===============================
@app.on_event("startup")
def startup_event():
    try:
        # 🛡️ Step 1: Drop old tables if they are corrupted (Optional, but safe for first time)
        # Base.metadata.drop_all(bind=engine) 
        
        # 🛡️ Step 2: Create all tables in External Render SQL
        Base.metadata.create_all(bind=engine)
        print("✅ External Database tables synced successfully!")
    except Exception as e:
        print(f"❌ Database Creation Error: {e}")

# ===============================
# 🟢 WHATSAPP NOTIFICATION
# ===============================
@app.post("/api/send-notification")
async def send_notification(request: Request):
    if not client:
        return {"status": "error", "message": "Twilio not configured"}
    
    data = await request.json()
    msg_content = data.get("msg", "QuantShield Alert Triggered")
    
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=msg_content,
            to=MY_WHATSAPP_NUMBER
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"status": "API Running", "accuracy_mode": "Real-time NSE Sync"}

# Register Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api", tags=["Core API"])

if __name__ == "__main__":
    # Render uses 'PORT' environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)