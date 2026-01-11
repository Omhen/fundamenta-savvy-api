"""Pydantic schemas for news domain."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FMPArticleResponse(BaseModel):
    """FMP article response schema."""

    title: str
    date: datetime
    content: str
    tickers: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None
    author: Optional[str] = None
    site: Optional[str] = None

    class Config:
        from_attributes = True


class GeneralNewsResponse(BaseModel):
    """General news response schema."""

    published_date: datetime
    title: str
    text: str
    url: str
    publisher: Optional[str] = None
    symbol: Optional[str] = None
    site: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True


class StockNewsResponse(BaseModel):
    """Stock news response schema."""

    symbol: Optional[str] = None
    published_date: datetime
    publisher: Optional[str] = None
    title: str
    text: str
    url: str
    site: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True
