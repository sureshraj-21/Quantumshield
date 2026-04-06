import yfinance as yf
import numpy as np
import pandas as pd
from backend.settings import ASSETS, LOOKBACK_PERIOD
from risk_engine.bsi import calculate_bsi
from risk_engine.cps import calculate_cps
from risk_engine.monte_carlo import monte_carlo_simulation
from risk_engine.hmm_regime import detect_hmm_regime
from optimizer.markowitz import optimize_portfolio
from hedging.ghost_hedge import apply_ghost_hedge
from database.db import SessionLocal
from database.portfolio_repo import save_portfolio_snapshot


# =====================================================
# DASHBOARD DATA ENGINE (ADVANCED VERSION)
# =====================================================

def get_dashboard_data(user_id: int):

    db = SessionLocal()

    try:

        # =================================================
        # DOWNLOAD MARKET DATA
        # =================================================
        prices = yf.download(
            ASSETS,
            period=LOOKBACK_PERIOD,
            progress=False
        )

        if prices.empty:
            return {"error": "Market data unavailable"}

        # Handle MultiIndex safely
        if isinstance(prices.columns, pd.MultiIndex):
            prices = prices["Close"]
        else:
            prices = prices[["Close"]]

        prices = prices.dropna()

        if prices.empty:
            return {"error": "No closing price data"}

        # =================================================
        # PORTFOLIO SERIES
        # =================================================
        portfolio_series = prices.sum(axis=1)
        portfolio_value = float(portfolio_series.iloc[-1])
        returns = portfolio_series.pct_change().dropna()

        # =================================================
        # RISK METRICS
        # =================================================
        if not returns.empty:

            sharpe_ratio = (
                returns.mean() * 252 /
                (returns.std() * np.sqrt(252) + 1e-6)
            )

            downside = returns[returns < 0]

            sortino_ratio = (
                returns.mean() * 252 /
                (downside.std() * np.sqrt(252) + 1e-6)
                if len(downside) > 0 else 0
            )

        else:
            sharpe_ratio = 0
            sortino_ratio = 0

        cumulative = portfolio_series.cummax()
        drawdown = (portfolio_series - cumulative) / cumulative
        max_drawdown = float(drawdown.min())

        # =================================================
        # MARKET REGIME
        # =================================================
        hmm_regime, stress_probability = detect_hmm_regime(returns)

        # =================================================
        # BEHAVIORAL RISK
        # =================================================
        bsi = calculate_bsi(prices)
        cps = calculate_cps(prices)

        # =================================================
        # PORTFOLIO OPTIMIZATION
        # =================================================
        allocation = optimize_portfolio(prices)
        allocation, hedge_status = apply_ghost_hedge(
            allocation, bsi, cps
        )

        # =================================================
        # RISK CONTRIBUTION (REAL CALCULATION)
        # =================================================
        risk_contribution = {}

        if not prices.empty and allocation:

            asset_returns = prices.pct_change().dropna()
            cov_matrix = asset_returns.cov()

            weights = np.array([
                allocation.get(asset, 0)
                for asset in prices.columns
            ])

            portfolio_var = np.dot(
                weights.T,
                np.dot(cov_matrix, weights)
            )

            if portfolio_var > 0:
                marginal = np.dot(cov_matrix, weights)
                contrib = weights * marginal / portfolio_var

                for i, asset in enumerate(prices.columns):
                    risk_contribution[asset] = float(contrib[i])

        # =================================================
        # PERFORMANCE HISTORY
        # =================================================
        performance = [
            {"date": str(d.date()), "value": float(v)}
            for d, v in portfolio_series.items()
        ]

        # =================================================
        # MONTE CARLO SIMULATION
        # =================================================
        if not returns.empty:
            mc_paths = monte_carlo_simulation(returns)
            mc_final = mc_paths[:, -1]
            mc_var_5 = float(np.percentile(mc_final, 5))
            mc_expected = float(np.mean(mc_final))
        else:
            mc_var_5 = 0.0
            mc_expected = 0.0

        # =================================================
        # ADVANCED AI STOCK RANKING
        # =================================================
        recommendations = []

        asset_returns = prices.pct_change().dropna()

        for asset in prices.columns:

            returns_asset = asset_returns[asset]

            if len(returns_asset) < 5:
                continue

            momentum = returns_asset.mean() * 252
            volatility = returns_asset.std() * np.sqrt(252)

            sharpe = momentum / (volatility + 1e-6)

            # Weighted AI Score
            score = float(
                (momentum * 0.5) +
                (sharpe * 0.3) -
                (volatility * 0.2)
            )

            # Signal classification
            if score > 0.05:
                signal = "BUY"
            elif score > 0:
                signal = "HOLD"
            else:
                signal = "SELL"

            confidence = min(abs(score) * 100, 95)

            recommendations.append({
                "stock": asset,
                "score": round(score, 4),
                "signal": signal,
                "confidence": round(confidence, 2),
                "momentum": round(momentum, 4),
                "volatility": round(volatility, 4),
                "sharpe": round(sharpe, 4)
            })

        recommendations = sorted(
            recommendations,
            key=lambda x: x["score"],
            reverse=True
        )

        # =================================================
        # SAVE SNAPSHOT
        # =================================================
        if performance:
            save_portfolio_snapshot(
                db=db,
                user_id=user_id,
                date=performance[-1]["date"],
                portfolio_value=portfolio_value,
                bsi=bsi,
                cps=cps,
                hedge_status=hedge_status,
                nifty_value=0,
                india_vix=0,
                allocation=allocation
            )

        # =================================================
        # RETURN FULL DASHBOARD DATA
        # =================================================
        return {
            "portfolio_value": portfolio_value,
            "bsi": bsi,
            "cps": cps,
            "hedge_status": hedge_status,
            "allocation": allocation,
            "performance": performance,
            "sharpe_ratio": float(sharpe_ratio),
            "sortino_ratio": float(sortino_ratio),
            "max_drawdown": max_drawdown,
            "risk_contribution": risk_contribution,
            "mc_var_5": mc_var_5,
            "mc_expected": mc_expected,
            "hmm_regime": hmm_regime,
            "stress_probability": stress_probability,
            "recommendations": recommendations
        }

    finally:
        db.close()