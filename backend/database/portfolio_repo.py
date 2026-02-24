from database.models import PortfolioSnapshot


def save_portfolio_snapshot(
    db,
    user_id,   # ✅ ADD THIS
    date,
    portfolio_value,
    bsi,
    cps,
    hedge_status,
    nifty_value,
    india_vix,
    allocation
):

    snapshot = PortfolioSnapshot(
        user_id=user_id,   # ✅ VERY IMPORTANT
        date=date,
        portfolio_value=portfolio_value,
        bsi=bsi,
        cps=cps,
        hedge_status=hedge_status,
        nifty_value=nifty_value,
        india_vix=india_vix
    )

    db.add(snapshot)
    db.commit()
