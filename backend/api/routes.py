from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.db import SessionLocal
from auth.auth_utils import get_current_user
from auth.models import User
from api.dashboard import get_dashboard_data
from database.models import PortfolioSnapshot, HedgeEvent
from api.stock_agent import router as stock_router
from api.ai_agent import router as ai_agent_router


import yfinance as yf   # ✅ missing import add panninen

router = APIRouter()

# =====================================================
# DB Dependency
# =====================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# ROOT
# =====================================================

@router.get("/")
def root():
    return {
        "message": "AI Financial Complete Portfolio Optimizer Running",
        "version": "2.0",
        "status": "ACTIVE"
    }

# =====================================================
# DASHBOARD
# =====================================================

@router.get("/dashboard")
def dashboard(current_user: User = Depends(get_current_user)):
    try:
        return get_dashboard_data(user_id=current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard error: {str(e)}"
        )

# =====================================================
# PORTFOLIO HISTORY
# =====================================================

@router.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    snapshots = (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.user_id == current_user.id)
        .order_by(PortfolioSnapshot.id.desc())
        .limit(30)
        .all()
    )

    return [
        {
            "date": snap.date,
            "portfolio_value": snap.portfolio_value,
            "bsi": snap.bsi,
            "cps": snap.cps,
            "hedge_status": snap.hedge_status
        }
        for snap in snapshots
    ]

# =====================================================
# HEDGE LOGS
# =====================================================

@router.get("/hedge-logs")
def hedge_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    logs = (
        db.query(HedgeEvent)
        .filter(HedgeEvent.user_id == current_user.id)
        .order_by(HedgeEvent.id.desc())
        .limit(30)
        .all()
    )

    return [
        {
            "time": str(log.triggered_at),
            "bsi": log.bsi,
            "cps": log.cps,
            "status": log.status,
            "reason": log.hedge_reason
        }
        for log in logs
    ]

# =====================================================
# SIMPLE STOCK PREDICTION
# =====================================================

@router.get("/predict/{symbol}")
def predict_stock(symbol: str, current_user: User = Depends(get_current_user)):

    data = yf.download(symbol, period="3mo", progress=False)

    if data.empty:
        raise HTTPException(status_code=404, detail="No data available")

    close = data["Close"]

    returns = close.pct_change().dropna()

    mean_return = returns.mean()
    std = returns.std()

    predicted_price = float(close.iloc[-1] * (1 + mean_return))

    return {
        "symbol": symbol,
        "current_price": float(close.iloc[-1]),
        "predicted_price": predicted_price,
        "volatility": float(std),
        "signal": "BUY" if mean_return > 0 else "SELL"
    }

# =====================================================
# INCLUDE STOCK AGENT ROUTES
# =====================================================

# =====================================================
# AI DATE BASED STOCK PREDICTION
# =====================================================

@router.get("/predict")
def predict_stock(
    stock: str = Query(...),
    date: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    try:
        result = predict_stock_price(stock, date)

        if not result:
            return {"error": "Prediction failed"}

        return result

    except Exception as e:
        return {"error": str(e)}
    
router.include_router(stock_router)
router.include_router(ai_agent_router)