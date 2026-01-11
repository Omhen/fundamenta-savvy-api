"""Pydantic schemas for SEC filings domain."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class SECFilingResponse(BaseModel):
    """SEC filing response schema."""

    symbol: str
    cik: Optional[str] = None
    accepted_date: Optional[datetime] = None
    filing_date: date
    form_type: Optional[str] = None
    has_financials: Optional[bool] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    class Config:
        from_attributes = True
