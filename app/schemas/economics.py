"""Pydantic schemas for economics domain."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TreasuryRateResponse(BaseModel):
    """Treasury rate response schema."""

    date: date
    month_1: Optional[float] = None
    month_2: Optional[float] = None
    month_3: Optional[float] = None
    month_6: Optional[float] = None
    year_1: Optional[float] = None
    year_2: Optional[float] = None
    year_3: Optional[float] = None
    year_5: Optional[float] = None
    year_7: Optional[float] = None
    year_10: Optional[float] = None
    year_20: Optional[float] = None
    year_30: Optional[float] = None

    class Config:
        from_attributes = True


class EconomicIndicatorResponse(BaseModel):
    """Economic indicator response schema."""

    date: date
    value: Optional[float] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class EconomicCalendarEventResponse(BaseModel):
    """Economic calendar event response schema."""

    date: datetime
    event: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    previous: Optional[float] = None
    estimate: Optional[float] = None
    actual: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    impact: Optional[str] = None

    class Config:
        from_attributes = True


class MarketRiskPremiumResponse(BaseModel):
    """Market risk premium response schema."""

    country: str
    continent: Optional[str] = None
    total_equity_risk_premium: Optional[float] = None
    country_risk_premium: Optional[float] = None

    class Config:
        from_attributes = True
