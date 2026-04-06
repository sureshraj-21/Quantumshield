from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import uvicorn

app = FastAPI(title="QuantShield AI API")

# ===============================
# 🌐 CORS (React / Vercel support)
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 🧠 BSI CALCULATION (FIXED)
# ===============================
def analyze_risk_behavior(returns):
    pos_count = (returns > 0).sum()
    score = (pos_count / len(returns)) * 100
    return round(score, 2)  # 🔥 numeric value (IMPORTANT)

# ===============================
# 📊 MAIN ANALYZE API
# ===============================
@app.get("/api/analyze")
async def get_portfolio_analysis(tickers: str = "RELIANCE.NS,TCS.NS"):
    try:
        symbols = tickers.split(",")

        # 🔽 Download data
        raw_data = yf.download(symbols, period="1y")

        if raw_data is None or raw_data.empty:
            return {"error": "❌ Failed to download data"}

        data = raw_data["Close"]

        # Single stock handle
        if isinstance(data, pd.Series):
            data = data.to_frame()

        returns = data.pct_change().dropna()

        # ===============================
        # 📈 METRICS
        # ===============================
        volatility = float(returns.std().mean() * np.sqrt(252))
        sharpe = float(
            (returns.mean().mean() / returns.std().mean()) * np.sqrt(252)
        )

        bsi = analyze_risk_behavior(returns.mean(axis=1))

        cps = (
            float(
                returns.corr().values[
                    np.triu_indices(len(data.columns), k=1)
                ].mean()
            )
            if len(data.columns) > 1
            else 0.0
        )

        # ===============================
        # 💰 PRICE (FIXED)
        # ===============================
        current_price = float(data.iloc[-1].mean())

        # ===============================
        # 🎯 FORECAST
        # ===============================
        investment = 10000
        expected = investment * (1 + (returns.mean().mean() * 252))
        worst_case = investment * (1 - (volatility * 0.5))

        # ===============================
        # 🧠 FINAL RESPONSE
        # ===============================
        return {
            "symbol": symbols[0],
            "decision": "BUY" if sharpe > 1.2 and cps < 0.7 else "HOLD",
            "regime": "STRESS" if volatility > 0.3 or cps > 0.8 else "CALM",
            "bsi_score": bsi,  # ✅ numeric
            "cps_score": round(cps, 2),
            "volatility": round(volatility, 2),
            "sharpe": round(sharpe, 2),
            "current_price": round(current_price, 2),  # ✅ added
            "forecast": {
                "expected": round(expected, 0),
                "worst_case": round(worst_case, 0),
            },
            "allocation": {
                t: f"{round(100/len(symbols), 0)}%" for t in symbols
            },
        }

    except Exception as e:
        return {"error": str(e)}

# ===============================
# 🟢 ROOT CHECK
# ===============================
@app.get("/")
def root():
    return {"status": "QuantShield API Running 🚀"}

# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)