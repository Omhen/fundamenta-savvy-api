"""Pydantic schemas for quotes and prices domain."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """Quote response schema."""

    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    changes_percentage: Optional[float] = None
    change: Optional[float] = None
    day_low: Optional[float] = None
    day_high: Optional[float] = None
    year_high: Optional[float] = None
    year_low: Optional[float] = None
    market_cap: Optional[float] = None
    price_avg_50: Optional[float] = None
    price_avg_200: Optional[float] = None
    exchange: Optional[str] = None
    volume: Optional[int] = None
    avg_volume: Optional[float] = None
    open: Optional[float] = None
    previous_close: Optional[float] = None
    eps: Optional[float] = None
    pe: Optional[float] = None
    earnings_announcement: Optional[str] = None
    shares_outstanding: Optional[float] = None
    timestamp: Optional[int] = None

    class Config:
        from_attributes = True


class HistoricalPriceResponse(BaseModel):
    """Historical price response schema."""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: Optional[float] = None
    volume: int
    unadjusted_volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    vwap: Optional[float] = None
    label: Optional[str] = None
    change_over_time: Optional[float] = None

    class Config:
        from_attributes = True


class IntradayPriceResponse(BaseModel):
    """Intraday price response schema."""

    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    class Config:
        from_attributes = True
