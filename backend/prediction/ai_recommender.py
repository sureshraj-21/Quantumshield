from prediction.stock_predictor import predict_stock_return
from backend.settings import ASSETS
import yfinance as yf
import numpy as np


def generate_recommendations():

    recommendations = []

    # Download all assets at once (faster)
    data = yf.download(
        ASSETS,
        period="3mo",
        progress=False
    )

    if data.empty:
        return []

    # Handle multi-index safely
    if isinstance(data.columns, tuple) or hasattr(data.columns, "levels"):
        prices = data["Close"]
    else:
        prices = data[["Close"]]

    returns = prices.pct_change().dropna()

    for symbol in prices.columns:

        try:
            predicted_return = predict_stock_return(symbol)
        except:
            continue

        if symbol not in returns.columns:
            continue

        volatility = returns[symbol].std()

        if volatility == 0:
            score = 0
        else:
            # Risk-adjusted predicted return
            score = predicted_return / (volatility + 1e-6)

        recommendations.append({
            "symbol": symbol,
            "predicted_return": round(predicted_return * 100, 2),
            "score": round(score, 4)
        })

    # Rank highest score first
    ranked = sorted(
        recommendations,
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked
