import numpy as np


def monte_carlo_simulation(
    returns,
    simulations=1000,
    time_horizon=30
):

    mean = returns.mean()
    std = returns.std()

    simulation_results = []

    for _ in range(simulations):

        prices = []
        price = 1

        for _ in range(time_horizon):
            shock = np.random.normal(mean, std)
            price *= (1 + shock)
            prices.append(price)

        simulation_results.append(prices)

    # 🔥 IMPORTANT LINE
    return np.array(simulation_results)