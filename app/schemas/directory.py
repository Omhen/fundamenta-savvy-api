"""Pydantic schemas for directory domain."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class StockSymbolResponse(BaseModel):
    """Stock symbol response schema."""

    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    exchange_short_name: Optional[str] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True


class FinancialStatementSymbolResponse(BaseModel):
    """Financial statement symbol response schema."""

    symbol: str
    company_name: Optional[str] = None
    trading_currency: Optional[str] = None
    reporting_currency: Optional[str] = None

    class Config:
        from_attributes = True


class ExchangeResponse(BaseModel):
    """Exchange response schema."""

    name: str
    code: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True


class SectorResponse(BaseModel):
    """Sector response schema."""

    sector: str

    class Config:
        from_attributes = True


class IndustryResponse(BaseModel):
    """Industry response schema."""

    industry: str

    class Config:
        from_attributes = True


class CountryResponse(BaseModel):
    """Country response schema."""

    country: str

    class Config:
        from_attributes = True


class SymbolChangeResponse(BaseModel):
    """Symbol change response schema."""

    old_symbol: str
    new_symbol: str
    change_date: date
    change_type: Optional[str] = None

    class Config:
        from_attributes = True
