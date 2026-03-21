import numpy as np


def calculate_cps_v2(prices):
    """
    Calculate Correlation Pressure Score (CPS).

    Measures the average correlation between asset price movements.
    Higher correlation indicates crowded/correlated positions, increasing market stress.

    Args:
        prices: DataFrame with asset prices

    Returns:
        float: CPS score (typically 0-2, where higher = more stress)
    """

    returns = prices.pct_change().dropna()

    # If only 1 stock → no correlation possible
    if returns.shape[1] < 2:
        return 0.0

    correlation_matrix = returns.corr()

    correlation_values = correlation_matrix.values[
        np.triu_indices_from(correlation_matrix.values, k=1)
    ]

    if len(correlation_values) == 0:
        return 0.0

    avg_correlation = np.abs(correlation_values).mean()

    if np.isnan(avg_correlation):
        return 0.0

    cps = avg_correlation * 2

    return float(cps)