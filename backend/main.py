import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from auth.auth_routes import router as auth_router
from database.db import engine, Base
from twilio.rest import Client 

app = FastAPI(
    title="QuantShield AI Optimizer",
    version="2.0"
)

# ===============================
# 🔑 TWILIO CONFIGURATION (Dynamic Fix)
# ===============================
# Hardcoded values-ai vida Render Environment Variables-ku priority kudukanum
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC5a3cdd61a29ed82e3a5f2e54977fb072')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '6ce8a0afe31272c81464ab9a5002c140')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' 
MY_WHATSAPP_NUMBER = 'whatsapp:+919962126306'

# Twilio Client Initialization
client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio Client Initialized")
    except Exception as e:
        print(f"❌ Twilio Init Error: {e}")

# ===============================
# CORS Fix
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 🗄️ Database Table Creation (Login Fix)
# ===============================
@app.on_event("startup")
def startup_event():
    try:
        # Pudhu DB-la tables create panna idhu mukkkiyam
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables synced successfully!")
    except Exception as e:
        print(f"❌ Database Sync Error: {e}")

# ===============================
# 🟢 WHATSAPP NOTIFICATION (Path Fix)
# ===============================
# Inga "/api/send-notification" nu slash mukkkiyam
@app.post("/api/send-notification")
async def send_notification(request: Request):
    if not client:
        return {"status": "error", "message": "Twilio not initialized"}
    
    try:
        data = await request.json()
        msg_content = data.get("msg", "QuantShield Alert Triggered")
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=msg_content,
            to=MY_WHATSAPP_NUMBER
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        print(f"Twilio Send Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"status": "API Running", "accuracy_mode": "Real-time NSE Sync"}

# ===============================
# Register Routers
# ===============================
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api", tags=["Core API"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)