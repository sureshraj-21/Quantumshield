import yfinance as yf
import numpy as np
from fastapi import APIRouter, Depends
from auth.auth_utils import get_current_user
from auth.models import User
from risk_engine.hmm_regime import detect_hmm_regime
from risk_engine.bsi import calculate_bsi
from risk_engine.cps import calculate_cps
from risk_engine.monte_carlo import monte_carlo_simulation

router = APIRouter()


@router.get("/analyze-stock/{symbol}")
def analyze_stock(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    try:

        data = yf.download(symbol, period="3mo", progress=False)

        if data.empty:
            return {"error": "No data found"}

        close = data["Close"]
        returns = close.pct_change().dropna()

        current_price = float(close.iloc[-1])

        # Basic Prediction
        predicted_return = float(returns.mean())
        volatility = float(returns.std())

        sharpe = (
            predicted_return / volatility
            if volatility > 0 else 0
        )

        # Regime Detection
        regime, _ = detect_hmm_regime(returns)

        # BSI & CPS
        bsi = calculate_bsi(data[["Close"]])
        cps = calculate_cps(data[["Close"]])

        # Monte Carlo
        mc_paths = monte_carlo_simulation(returns)

        mc_final = mc_paths[:, -1]

        mc_expected = float(np.mean(mc_final))
        mc_worst = float(np.percentile(mc_final, 5))

        # Investment Simulation
        invest_expected = 10000 * mc_expected
        invest_worst = 10000 * mc_worst

        # AI Decision Logic
        decision = "HOLD"

        if sharpe > 0.8 and regime == "CALM":
            decision = "BUY"
        elif sharpe < 0 or regime == "STRESS":
            decision = "AVOID"

        return {
            "current_price": current_price,
            "predicted_return": predicted_return,
            "volatility": volatility,
            "sharpe": sharpe,
            "regime": regime,
            "bsi": bsi,
            "cps": cps,
            "monte_carlo_expected": mc_expected,
            "investment_10000_expected": invest_expected,
            "investment_10000_worst": invest_worst,
            "decision": decision
        }

    except Exception as e:
        return {"error": str(e)}