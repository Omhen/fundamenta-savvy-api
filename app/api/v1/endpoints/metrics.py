"""Company metrics domain API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import CompanyMetrics
from app.schemas.metrics import CompanyMetricsResponse, CompanyMetricsListResponse

router = APIRouter()


@router.get("/{symbol}", response_model=CompanyMetricsResponse)
def get_company_metrics(symbol: str, db: Session = Depends(get_db)):
    """Get metrics for a specific symbol."""
    metrics = db.query(CompanyMetrics).filter(CompanyMetrics.symbol == symbol.upper()).first()
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Metrics not found for symbol: {symbol}")
    return metrics


@router.get("/", response_model=CompanyMetricsListResponse)
def list_company_metrics(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    min_pe_ratio: Optional[float] = Query(None, description="Minimum P/E ratio"),
    max_pe_ratio: Optional[float] = Query(None, description="Maximum P/E ratio"),
    min_dividend_yield: Optional[float] = Query(None, description="Minimum dividend yield"),
    max_dividend_yield: Optional[float] = Query(None, description="Maximum dividend yield"),
    min_roic: Optional[float] = Query(None, description="Minimum ROIC"),
    max_roic: Optional[float] = Query(None, description="Maximum ROIC"),
    min_market_cap: Optional[float] = Query(None, description="Minimum market cap"),
    max_market_cap: Optional[float] = Query(None, description="Maximum market cap"),
    min_years_increasing_dividend: Optional[int] = Query(None, description="Minimum years of increasing dividends"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List company metrics with filtering and pagination.

    Use this endpoint for screener functionality to filter companies by various metrics.
    """
    query = db.query(CompanyMetrics)

    # Apply filters
    if sector:
        query = query.filter(CompanyMetrics.sector == sector)

    if min_pe_ratio is not None:
        query = query.filter(CompanyMetrics.pe_ratio >= min_pe_ratio)
    if max_pe_ratio is not None:
        query = query.filter(CompanyMetrics.pe_ratio <= max_pe_ratio)

    if min_dividend_yield is not None:
        query = query.filter(CompanyMetrics.dividend_yield >= min_dividend_yield)
    if max_dividend_yield is not None:
        query = query.filter(CompanyMetrics.dividend_yield <= max_dividend_yield)

    if min_roic is not None:
        query = query.filter(CompanyMetrics.roic >= min_roic)
    if max_roic is not None:
        query = query.filter(CompanyMetrics.roic <= max_roic)

    if min_market_cap is not None:
        query = query.filter(CompanyMetrics.market_cap >= min_market_cap)
    if max_market_cap is not None:
        query = query.filter(CompanyMetrics.market_cap <= max_market_cap)

    if min_years_increasing_dividend is not None:
        query = query.filter(CompanyMetrics.years_increasing_dividend >= min_years_increasing_dividend)

    # Get total count before pagination
    total = query.count()

    # Calculate pagination
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    offset = (page - 1) * page_size

    # Apply pagination and ordering
    items = (
        query
        .order_by(CompanyMetrics.symbol)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return CompanyMetricsListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/sectors/list", response_model=list[str])
def list_sectors(db: Session = Depends(get_db)):
    """Get list of unique sectors in metrics data."""
    sectors = (
        db.query(CompanyMetrics.sector)
        .filter(CompanyMetrics.sector.isnot(None))
        .distinct()
        .order_by(CompanyMetrics.sector)
        .all()
    )
    return [s[0] for s in sectors]
