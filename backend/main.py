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
# 🔑 TWILIO CONFIGURATION (Final Fix)
# ===============================
# Note: Render Environment Variables-la indha names-aiye use pannunga
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC5a3cdd61a29ed82e3a5f2e54977fb072')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'a4bde39f35a4757c3c9602e258766bec')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

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
@app.post("/api/send-notification")
async def send_notification(request: Request):
    if not client:
        # Twilio initialise aagalana logic inga break aagum
        return {"status": "error", "message": "Twilio not initialized"}
    
    try:
        data = await request.json()
        msg_content = data.get("msg", "QuantShield Alert Triggered")
        
        # ✅ FIX: Explicit 'whatsapp:' prefix with your number
        target_number = 'whatsapp:+919962126306' 

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER, 
            body=msg_content,
            to=target_number
        )
        
        print(f"✅ Message Sent Successfully! SID: {message.sid}")
        return {"status": "success", "sid": message.sid}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Twilio Send Error: {error_msg}")
        if "authenticate" in error_msg.lower() or "auth" in error_msg.lower():
            print("⚠️  Auth Token may be expired or revoked. Regenerate at console.twilio.com")
        if "not opted in" in error_msg.lower() or "21608" in error_msg:
            print("⚠️  Recipient has not joined the WhatsApp sandbox.")
        return {"status": "error", "message": error_msg}
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