"""Pydantic schemas for company domain."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class CompanyProfileResponse(BaseModel):
    """Company profile response schema."""

    symbol: str
    price: Optional[float] = None
    beta: Optional[float] = None
    vol_avg: Optional[int] = None
    mkt_cap: Optional[int] = None
    last_div: Optional[float] = None
    range: Optional[str] = None
    changes: Optional[float] = None
    company_name: str
    currency: Optional[str] = None
    cik: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    exchange: Optional[str] = None
    exchange_short_name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    ceo: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    full_time_employees: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    dcf_diff: Optional[float] = None
    dcf: Optional[float] = None
    image: Optional[str] = None
    ipo_date: Optional[date] = None
    default_image: Optional[bool] = None
    is_etf: Optional[bool] = None
    is_actively_trading: Optional[bool] = None
    is_adr: Optional[bool] = None
    is_fund: Optional[bool] = None

    class Config:
        from_attributes = True


class ExecutiveResponse(BaseModel):
    """Executive response schema."""

    symbol: str
    title: Optional[str] = None
    name: str
    pay: Optional[float] = None
    currency_pay: Optional[str] = None
    gender: Optional[str] = None
    year_born: Optional[int] = None
    title_since: Optional[str] = None

    class Config:
        from_attributes = True


class MarketCapitalizationResponse(BaseModel):
    """Market capitalization response schema."""

    symbol: str
    date: date
    market_cap: float

    class Config:
        from_attributes = True


class EmployeeCountResponse(BaseModel):
    """Employee count response schema."""

    symbol: str
    cik: Optional[str] = None
    acceptance_time: Optional[str] = None
    period_of_report: Optional[str] = None
    company_name: Optional[str] = None
    form_type: Optional[str] = None
    filing_date: Optional[date] = None
    employee_count: Optional[int] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class SharesFloatResponse(BaseModel):
    """Shares float response schema."""

    symbol: str
    date: Optional[date] = None
    free_float: Optional[float] = None
    float_shares: Optional[float] = None
    outstanding_shares: Optional[float] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class DelistedCompanyResponse(BaseModel):
    """Delisted company response schema."""

    symbol: str
    company_name: Optional[str] = None
    exchange: Optional[str] = None
    ipo_date: Optional[date] = None
    delisted_date: Optional[date] = None

    class Config:
        from_attributes = True
