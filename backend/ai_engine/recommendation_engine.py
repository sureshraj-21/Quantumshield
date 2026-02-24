import numpy as np
import yfinance as yf
from risk_engine.hmm_regime import detect_hmm_regime

def generate_ai_signal(symbol):

    data = yf.download(symbol, period="3mo", progress=False)

    if data.empty:
        return None

    returns = data["Close"].pct_change().dropna()

    trend = returns.mean()
    momentum = returns.tail(5).mean()
    volatility = returns.std()

    hmm_regime, _ = detect_hmm_regime(returns)

    regime_factor = 0.1 if hmm_regime == "CALM" else -0.1

    score = (
        0.30 * trend +
        0.20 * momentum -
        0.15 * volatility +
        regime_factor
    )

    if score > 0.02:
        signal = "🟢 STRONG BUY"
    elif score > 0:
        signal = "🟡 HOLD"
    else:
        signal = "🔴 AVOID"

    return {
        "symbol": symbol,
        "score": float(score),
        "signal": signal
    }