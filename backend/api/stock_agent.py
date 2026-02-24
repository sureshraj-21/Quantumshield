import yfinance as yf
import numpy as np
import math
from fastapi import APIRouter, Depends
from auth.auth_utils import get_current_user
from auth.models import User
from risk_engine.hmm_regime import detect_hmm_regime
from risk_engine.bsi import calculate_bsi
from risk_engine.cps import calculate_cps
from risk_engine.monte_carlo import monte_carlo_simulation

router = APIRouter()

STOCK_LIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]


def safe_float(x):
    try:
        if x is None or math.isnan(x) or math.isinf(x):
            return 0.0
        return float(x)
    except:
        return 0.0


def analyze_single_stock(symbol):

    data = yf.download(symbol, period="6mo", progress=False)

    if data.empty:
        return None

    close = data["Close"]
    returns = close.pct_change().dropna()

    if len(returns) < 30:
        return None

    current_price = safe_float(close.iloc[-1])

    momentum = returns.tail(20).mean()
    long_term = returns.mean()

    predicted_return = safe_float((momentum * 0.6) + (long_term * 0.4))
    volatility = safe_float(returns.std())

    sharpe = 0
    if volatility > 0:
        sharpe = safe_float(
            (predicted_return * 252) /
            (volatility * np.sqrt(252))
        )

    regime, stress_prob = detect_hmm_regime(returns)

    price_df = data[["Close"]]
    bsi = safe_float(calculate_bsi(price_df))
    cps = safe_float(calculate_cps(price_df))
    # -------------------------
    # FORCE DEMO HEDGE LOGIC
    # -------------------------
    hedge_status = "INACTIVE"

    # Strong stock → no hedge
    if sharpe > 0.8:
        hedge_status = "INACTIVE"

    # Weak stock → hedge active
    elif sharpe < 0:
        hedge_status = "ACTIVE"

    # Medium → regime based
    else:
        if regime == "STRESS" or bsi > 1:
            hedge_status = "ACTIVE"

    mc_paths = monte_carlo_simulation(returns)

    if mc_paths.size == 0:
        mc_expected = 1.0
        mc_worst = 0.9
    else:
        mc_final = mc_paths[:, -1]
        mc_expected = safe_float(np.mean(mc_final))
        mc_worst = safe_float(np.percentile(mc_final, 5))

    # SCORE
    score = (
        sharpe * 0.6
        - volatility * 5
        - bsi * 0.05
        - cps * 0.05
    )

    if regime == "STRESS":
        score -= 0.5

    return {
        "symbol": symbol,
        "current_price": current_price,
        "predicted_return": predicted_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "regime": regime,
        "bsi": bsi,
        "cps": cps,
        "hedge_status": hedge_status,
        "monte_carlo_expected": mc_expected,
        "investment_10000_expected": 10000 * mc_expected,
        "investment_10000_worst": 10000 * mc_worst,
        "score": score
    }


@router.get("/analyze-stock/{symbol}")
def analyze_stock(symbol: str, current_user: User = Depends(get_current_user)):

    results = []

    for s in STOCK_LIST:
        data = analyze_single_stock(s)
        if data:
            results.append(data)

    if len(results) < 3:
        return {"error": "Not enough valid stocks"}

    # SORT BY SCORE
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # ASSIGN DECISIONS
    results[0]["decision"] = "BUY"
    results[1]["decision"] = "HOLD"
    results[2]["decision"] = "AVOID"

    # Return only selected stock
    for stock_data in results:
        if stock_data["symbol"] == symbol:
            return stock_data

    return {"error": "Stock not found"}