"""Pydantic schemas for market performance domain."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class SectorPerformanceResponse(BaseModel):
    """Sector performance response schema."""

    sector: str
    date: date
    exchange: Optional[str] = None
    average_change: Optional[float] = None

    class Config:
        from_attributes = True


class IndustryPerformanceResponse(BaseModel):
    """Industry performance response schema."""

    industry: str
    date: date
    exchange: Optional[str] = None
    average_change: Optional[float] = None

    class Config:
        from_attributes = True


class SectorPEResponse(BaseModel):
    """Sector P/E response schema."""

    date: date
    sector: str
    exchange: Optional[str] = None
    pe: Optional[str] = None

    class Config:
        from_attributes = True


class IndustryPEResponse(BaseModel):
    """Industry P/E response schema."""

    date: date
    industry: str
    exchange: Optional[str] = None
    pe: Optional[str] = None

    class Config:
        from_attributes = True


class StockGainerResponse(BaseModel):
    """Stock gainer response schema."""

    symbol: str
    name: Optional[str] = None
    change: Optional[float] = None
    price: Optional[float] = None
    exchange: Optional[str] = None
    changes_percentage: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


class StockLoserResponse(BaseModel):
    """Stock loser response schema."""

    symbol: str
    name: Optional[str] = None
    change: Optional[float] = None
    price: Optional[float] = None
    exchange: Optional[str] = None
    changes_percentage: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


class ActiveStockResponse(BaseModel):
    """Active stock response schema."""

    symbol: str
    name: Optional[str] = None
    change: Optional[float] = None
    price: Optional[float] = None
    changes_percentage: Optional[str] = None
    exchange: Optional[str] = None
    date: date

    class Config:
        from_attributes = True
