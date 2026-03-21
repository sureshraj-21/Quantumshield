from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import uvicorn

app = FastAPI(title="QuantShield AI API")

# Streamlit-la idhu thevai illai, aana React-ku idhu romba mukkiyam (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_risk_behavior(returns):
    # Flowchart-la neenga ketta BSI (Buy Strength) logic
    pos_count = (returns > 0).sum()
    score = (pos_count / len(returns)) * 100
    if score > 55: return "STRONG"
    return "MODERATE" if score > 45 else "WEAK"

@app.get("/api/analyze")
async def get_portfolio_analysis(tickers: str = "RELIANCE.NS,TCS.NS"):
    try:
        # Download data with error handling
        raw_data = yf.download(tickers.split(","), period="1y")
        if raw_data is None or raw_data.empty:
            return {"error": "Failed to download data for the specified tickers"}

        data = raw_data['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        returns = data.pct_change().dropna()

        # Advanced Metrics (Future Scope logic)
        volatility = float(returns.std().mean() * np.sqrt(252))
        sharpe = float((returns.mean().mean() / returns.std().mean()) * np.sqrt(252))
        bsi = analyze_risk_behavior(returns.mean(axis=1))
        cps = float(returns.corr().values[np.triu_indices(len(data.columns), k=1)].mean()) if len(data.columns) > 1 else 0.0

        # Monte Carlo Forecast (₹10,000 Scenario)
        investment = 10000
        expected = investment * (1 + (returns.mean().mean() * 252))
        worst_case = investment * (1 - (volatility * 0.5))

        return {
            "decision": "BUY" if sharpe > 1.2 and cps < 0.7 else "HOLD",
            "regime": "STRESS" if volatility > 0.3 or cps > 0.8 else "CALM",
            "bsi_score": bsi,
            "cps_score": round(cps, 2),
            "forecast": {
                "expected": round(expected, 0),
                "worst_case": round(worst_case, 0)
            },
            "allocation": {t: f"{round(100/len(tickers.split(',')), 0)}%" for t in tickers.split(",")}
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)