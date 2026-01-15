from sqlalchemy import Column, Date, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class TreasuryRate(BaseModel):
    """Treasury rate data for various maturity periods."""

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    month_1 = Column(Float, nullable=True)
    month_2 = Column(Float, nullable=True)
    month_3 = Column(Float, nullable=True)
    month_6 = Column(Float, nullable=True)
    year_1 = Column(Float, nullable=True)
    year_2 = Column(Float, nullable=True)
    year_3 = Column(Float, nullable=True)
    year_5 = Column(Float, nullable=True)
    year_7 = Column(Float, nullable=True)
    year_10 = Column(Float, nullable=True)
    year_20 = Column(Float, nullable=True)
    year_30 = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EconomicIndicator(BaseModel):
    """Economic indicator data point."""

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    value = Column(Float, nullable=True)
    name = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_econ_indicator_name_date', 'name', 'date', unique=True),
    )


class EconomicCalendarEvent(BaseModel):
    """Scheduled economic data release event."""

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True, nullable=False)
    event = Column(String, index=True, nullable=True)
    country = Column(String, index=True, nullable=True)
    currency = Column(String, nullable=True)
    previous = Column(Float, nullable=True)
    estimate = Column(Float, nullable=True)
    actual = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    impact = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_econ_cal_date_event_country', 'date', 'event', 'country', unique=True),
    )


class MarketRiskPremium(BaseModel):
    """Market risk premium data."""

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, unique=True, nullable=False)
    continent = Column(String, index=True, nullable=True)
    total_equity_risk_premium = Column(Float, nullable=True)
    country_risk_premium = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
