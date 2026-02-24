import numpy as np

def optimize_portfolio(prices):

    returns = prices.pct_change().dropna()

    if returns.empty:
        # fallback equal weight
        n = len(prices.columns)
        return {asset: 1/n for asset in prices.columns}

    cov = returns.cov()
    mean_returns = returns.mean()

    try:
        inv_cov = np.linalg.pinv(cov)

        raw_weights = inv_cov.dot(mean_returns)

        # Remove negative weights (long-only)
        raw_weights = np.maximum(raw_weights, 0)

        # If all weights become zero
        if raw_weights.sum() == 0:
            n = len(prices.columns)
            return {asset: 1/n for asset in prices.columns}

        # Normalize to sum = 1
        weights = raw_weights / raw_weights.sum()

        return {
            asset: float(weights[i])
            for i, asset in enumerate(prices.columns)
        }

    except Exception:
        # fallback equal weight if math fails
        n = len(prices.columns)
        return {asset: 1/n for asset in prices.columns}
