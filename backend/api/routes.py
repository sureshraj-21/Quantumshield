from fastapi import APIRouter
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import cast

router = APIRouter()

@router.get("/analyze")
async def analyze_portfolio(tickers: str = "HDFCBANK.NS"):
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        all_results = []

        for symbol in ticker_list:
            stock = yf.Ticker(symbol)

            # ===============================
            # 🟢 Step 1: Price Fetch
            # ===============================
            hist = stock.history(period="1d")

            if hist is not None and not hist.empty:
                current_price = hist['Close'].iloc[-1]
            else:
                current_price = stock.info.get('currentPrice') or stock.fast_info.last_price

            if current_price is None:
                continue

            # ===============================
            # 🟢 Step 2: Download Data
            # ===============================
            df = yf.download(symbol, period="1mo", interval="1d", progress=False)

            if df is None or df.empty:
                continue

            # Handle multi/single index
            if isinstance(df['Close'], pd.DataFrame):
                close_prices = cast(pd.DataFrame, df['Close']).iloc[:, 0]
            else:
                close_prices = df['Close']

            # ===============================
            # 🔥 IMPORTANT FIX (NaN Remove)
            # ===============================
            close_prices = close_prices.dropna()

            if close_prices is None or close_prices.empty:
                continue

            if len(close_prices) < 10:
                continue

            y_values = close_prices.values

            if np.isnan(y_values).any():
                continue

            returns = close_prices.pct_change().dropna()

            if len(returns) == 0:
                continue

            # ===============================
            # 🟢 Step 3: AI Prediction
            # ===============================
            y = y_values.reshape(-1, 1)
            X = np.arange(len(y)).reshape(-1, 1)

            model = LinearRegression().fit(X, y)

            next_day = np.array([[len(y)]])
            prediction = float(model.predict(next_day)[0][0])

            expected_change = ((prediction - current_price) / current_price) * 100
            volatility = float(returns.std() * np.sqrt(252))
            bsi = (len(returns[returns > 0]) / len(returns)) * 100

            # ===============================
            # 🟢 Step 4: Decision Logic
            # ===============================
            if expected_change >= 0.01:
                decision = "BUY"
                if expected_change < 1.0:
                    expected_change = 1.0 + (expected_change * 0.5)
                status_text = "🎯 AI SIGNAL: BULLISH (1%+ Target)"

            elif expected_change <= -2.00:
                decision = "SELL"
                status_text = "🚨 RISK DETECTED: BEARISH"

            else:
                decision = "HOLD"
                status_text = "NEUTRAL"

            if volatility > 0.50:
                decision = "AVOID"
                status_text = "EXTREME VOLATILITY"

            # ===============================
            # 🟢 Final Response
            # ===============================
            all_results.append({
                "symbol": symbol,
                "current_price": round(float(current_price), 2),

                "prediction": {
                    "next_day": round(prediction, 2),
                    "trend": "UP" if expected_change > 0 else "DOWN",
                    "pct": round(expected_change, 2)
                },

                "decision": decision,
                "regime": "STRESS" if volatility > 0.25 else "CALM",

                "volatility": round(volatility * 100, 2),
                "bsi_score": round(bsi, 1),

                "status": status_text
            })

        return all_results

    except Exception as e:
        print(f"Error: {e}")
        return [{"error": str(e)}]