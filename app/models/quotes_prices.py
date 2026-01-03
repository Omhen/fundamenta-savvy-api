from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class Quote(BaseModel):
    """Real-time stock quote data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    changes_percentage = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    day_low = Column(Float, nullable=True)
    day_high = Column(Float, nullable=True)
    year_high = Column(Float, nullable=True)
    year_low = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    price_avg_50 = Column(Float, nullable=True)
    price_avg_200 = Column(Float, nullable=True)
    exchange = Column(String, nullable=True)
    volume = Column(BigInteger, nullable=True)
    avg_volume = Column(Float, nullable=True)
    open = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    pe = Column(Float, nullable=True)
    earnings_announcement = Column(String, nullable=True)
    shares_outstanding = Column(Float, nullable=True)
    timestamp = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_quote_symbol_timestamp', 'symbol', 'timestamp'),
    )


class HistoricalPrice(BaseModel):
    """Historical end-of-day price data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=False)
    unadjusted_volume = Column(BigInteger, nullable=True)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    label = Column(String, nullable=True)
    change_over_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_historical_price_symbol_date', 'symbol', 'date', unique=True),
    )


class IntradayPrice(BaseModel):
    """Intraday price data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_intraday_price_symbol_date', 'symbol', 'date', unique=True),
    )
