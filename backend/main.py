import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from auth.auth_routes import router as auth_router
from database.db import engine, Base
from twilio.rest import Client 

app = FastAPI(
    title="AI Financial Complete Portfolio Optimizer",
    version="2.0"
)

# ===============================
# 🔑 YOUR LIVE TWILIO CONFIGURATION
# ===============================
TWILIO_ACCOUNT_SID = 'AC5a3cdd61a29ed82e3a5f2e54977fb072' 
TWILIO_AUTH_TOKEN = '2d6ff54c561af6b0a868df61c9bffc43'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' # Twilio Sandbox Number
MY_WHATSAPP_NUMBER = 'whatsapp:+919962126306'    # Unga Mobile Number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ===============================
# CORS (Allow Frontend Access)
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Create Database Tables
# ===============================
Base.metadata.create_all(bind=engine)

# ===============================
# 🟢 WHATSAPP NOTIFICATION ENDPOINT
# ===============================
@app.post("/api/send-notification")
async def send_notification(request: Request):
    data = await request.json()
    msg_content = data.get("msg", "QuantShield Alert Triggered")
    
    try:
        # 🚀 Sending WhatsApp message to +919962126306
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=msg_content,
            to=MY_WHATSAPP_NUMBER
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        print(f"Twilio Error: {e}")
        return {"status": "error", "message": str(e)}

# ===============================
# Root Health Check
# ===============================
@app.get("/")
def root():
    return {"status": "API Running", "accuracy_mode": "Real-time NSE Sync"}

# ===============================
# Register Routers
# ===============================
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, prefix="/api", tags=["Core API"])

# ===============================
# Windows Execution Fix
# ===============================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)