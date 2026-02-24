def allocate_safe_haven(allocation, bsi, cps):

    # Make copy (avoid modifying original dict)
    new_allocation = allocation.copy()

    stress_score = (bsi + cps) / 2

    # Dynamic hedge scaling (10% to 40%)
    hedge_percent = min(0.10 + stress_score * 0.05, 0.40)

    reduction_factor = 1 - hedge_percent

    # Reduce existing assets
    for asset in new_allocation:
        new_allocation[asset] *= reduction_factor

    # Add hedge assets safely
    gold_weight = hedge_percent * 0.6
    liquid_weight = hedge_percent * 0.4

    new_allocation["GOLDBEES.NS"] = \
        new_allocation.get("GOLDBEES.NS", 0) + gold_weight

    new_allocation["LIQUIDBEES.NS"] = \
        new_allocation.get("LIQUIDBEES.NS", 0) + liquid_weight

    # Normalize to exactly 1
    total = sum(new_allocation.values())

    if total > 0:
        for asset in new_allocation:
            new_allocation[asset] /= total

    return new_allocation, hedge_percent
