from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class PortfolioSnapshot(Base):

    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    date = Column(String(50))
    portfolio_value = Column(Float)
    bsi = Column(Float)
    cps = Column(Float)
    hedge_status = Column(String(50))
    nifty_value = Column(Float)
    india_vix = Column(Float)

    user = relationship("User")


class HedgeEvent(Base):

    __tablename__ = "hedge_events"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    triggered_at = Column(DateTime, default=datetime.utcnow)

    bsi = Column(Float)
    cps = Column(Float)

    status = Column(String(50))
    hedge_reason = Column(String(255))

    user = relationship("User")