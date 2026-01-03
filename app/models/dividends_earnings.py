from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class Dividend(BaseModel):
    """Individual stock dividend data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    label = Column(String, nullable=True)
    adj_dividend = Column(Float, nullable=True)
    dividend = Column(Float, nullable=True)
    record_date = Column(String, nullable=True)
    payment_date = Column(String, nullable=True)
    declaration_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_dividend_symbol_date', 'symbol', 'date', unique=True),
    )


class DividendCalendarEvent(BaseModel):
    """Calendar dividend event."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    label = Column(String, nullable=True)
    adj_dividend = Column(Float, nullable=True)
    dividend = Column(Float, nullable=True)
    record_date = Column(String, nullable=True)
    payment_date = Column(String, nullable=True)
    declaration_date = Column(String, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_div_calendar_symbol_date', 'symbol', 'date'),
    )


class EarningsReport(BaseModel):
    """Company earnings report."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    eps = Column(Float, nullable=True)
    eps_estimated = Column(Float, nullable=True)
    time = Column(String, nullable=True)
    revenue = Column(Float, nullable=True)
    revenue_estimated = Column(Float, nullable=True)
    fiscal_date_ending = Column(String, nullable=True)
    period = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_earnings_symbol_date', 'symbol', 'date', unique=True),
        Index('idx_earnings_symbol_period', 'symbol', 'period'),
    )


class EarningsCalendarEvent(BaseModel):
    """Calendar earnings announcement."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    eps = Column(Float, nullable=True)
    eps_estimated = Column(Float, nullable=True)
    time = Column(String, nullable=True)
    revenue = Column(Float, nullable=True)
    revenue_estimated = Column(Float, nullable=True)
    fiscal_date_ending = Column(String, nullable=True)
    updated_from_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_earnings_cal_symbol_date', 'symbol', 'date'),
    )
