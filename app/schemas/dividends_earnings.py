"""Pydantic schemas for dividends and earnings domain."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class DividendResponse(BaseModel):
    """Dividend response schema."""

    symbol: str
    date: date
    label: Optional[str] = None
    adj_dividend: Optional[float] = None
    dividend: Optional[float] = None
    record_date: Optional[date] = None
    payment_date: Optional[date] = None
    declaration_date: Optional[date] = None

    class Config:
        from_attributes = True


class DividendCalendarEventResponse(BaseModel):
    """Dividend calendar event response schema."""

    symbol: str
    date: date
    label: Optional[str] = None
    adj_dividend: Optional[float] = None
    dividend: Optional[float] = None
    record_date: Optional[date] = None
    payment_date: Optional[date] = None
    declaration_date: Optional[date] = None
    dividend_yield: Optional[float] = None

    class Config:
        from_attributes = True


class EarningsReportResponse(BaseModel):
    """Earnings report response schema."""

    symbol: str
    date: date
    eps: Optional[float] = None
    eps_estimated: Optional[float] = None
    time: Optional[str] = None
    revenue: Optional[float] = None
    revenue_estimated: Optional[float] = None
    fiscal_date_ending: Optional[str] = None
    period: Optional[str] = None

    class Config:
        from_attributes = True


class EarningsCalendarEventResponse(BaseModel):
    """Earnings calendar event response schema."""

    symbol: str
    date: date
    eps: Optional[float] = None
    eps_estimated: Optional[float] = None
    time: Optional[str] = None
    revenue: Optional[float] = None
    revenue_estimated: Optional[float] = None
    fiscal_date_ending: Optional[str] = None
    updated_from_date: Optional[str] = None

    class Config:
        from_attributes = True
