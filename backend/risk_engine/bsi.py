import numpy as np

def calculate_bsi(prices):

    returns = prices.pct_change().dropna()

    if returns.empty:
        return 0.0

    volatility = returns.std().mean()

    if np.isnan(volatility):
        return 0.0

    return float(abs(volatility * 10))