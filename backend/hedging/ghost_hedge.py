from backend.settings import BSI_THRESHOLD, CPS_THRESHOLD
from hedging.safe_haven_allocator import allocate_safe_haven
from database.models import HedgeEvent


def apply_ghost_hedge(allocation, bsi, cps, db=None, user_id=None):

    hedge_status = "INACTIVE"

    if bsi > BSI_THRESHOLD or cps > CPS_THRESHOLD:

        hedge_status = "ACTIVE"

        allocation, hedge_percent = allocate_safe_haven(
            allocation, bsi, cps
        )

        hedge_reason = f"Hedge Activated ({round(hedge_percent*100)}%)"

        # ✅ Save hedge event
        if db and user_id:
            hedge_event = HedgeEvent(
                user_id=user_id,
                bsi=bsi,
                cps=cps,
                status="ACTIVE",
                hedge_reason=hedge_reason
            )

            db.add(hedge_event)
            db.commit()

    return allocation, hedge_status
