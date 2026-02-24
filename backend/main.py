from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from auth.auth_routes import router as auth_router
from database.db import engine, Base

app = FastAPI(
    title="AI Financial Complete Portfolio Optimizer",
    version="2.0"
)

# ===============================
# CORS (Allow Frontend Access)
# ===============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Create Database Tables
# ===============================

Base.metadata.create_all(bind=engine)

# ===============================
# Root Health Check
# ===============================

@app.get("/")
def root():
    return {"status": "API Running"}

# ===============================
# Register Routers
# ===============================

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_router, tags=["Core API"])
