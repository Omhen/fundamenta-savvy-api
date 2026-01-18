"""Pydantic schemas for company metrics domain."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class CompanyMetricsResponse(BaseModel):
    """Company metrics response schema."""

    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None

    # Valuation ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None

    # Enterprise value ratios
    ev_ebitda_ratio: Optional[float] = None
    ev_fcf_ratio: Optional[float] = None

    # Profitability
    copm: Optional[float] = None
    roic: Optional[float] = None
    rota: Optional[float] = None

    # Leverage
    debt_ebitda_ratio: Optional[float] = None

    # Dividends
    dividend_yield: Optional[float] = None
    dividend_payout: Optional[float] = None
    dividend_growth_10y: Optional[float] = None
    years_increasing_dividend: Optional[int] = None

    # Score
    score: Optional[float] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyMetricsListResponse(BaseModel):
    """Paginated list response for company metrics."""

    items: List[CompanyMetricsResponse]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        from_attributes = True
