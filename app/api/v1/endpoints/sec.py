"""SEC filings domain API endpoints."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sec_filings import SECFiling
from app.schemas.sec import SECFilingResponse

router = APIRouter()


@router.get("/filings/{symbol}", response_model=List[SECFilingResponse])
def get_filings_by_symbol(
    symbol: str,
    form_type: Optional[str] = Query(None, description="Filter by form type (e.g., 10-K, 10-Q, 8-K)"),
    db: Session = Depends(get_db)
):
    """Get all SEC filings for a symbol."""
    query = db.query(SECFiling).filter(SECFiling.symbol == symbol)
    if form_type:
        query = query.filter(SECFiling.form_type == form_type)
    return query.order_by(SECFiling.filing_date.desc()).all()


@router.get("/filings/cik/{cik}", response_model=List[SECFilingResponse])
def get_filings_by_cik(
    cik: str,
    form_type: Optional[str] = Query(None, description="Filter by form type"),
    db: Session = Depends(get_db)
):
    """Get all SEC filings for a CIK."""
    query = db.query(SECFiling).filter(SECFiling.cik == cik)
    if form_type:
        query = query.filter(SECFiling.form_type == form_type)
    return query.order_by(SECFiling.filing_date.desc()).all()


@router.get("/filings/by-date/{filing_date}", response_model=List[SECFilingResponse])
def get_filings_by_date(
    filing_date: date,
    form_type: Optional[str] = Query(None, description="Filter by form type"),
    db: Session = Depends(get_db)
):
    """Get all SEC filings for a specific date."""
    query = db.query(SECFiling).filter(SECFiling.filing_date == filing_date)
    if form_type:
        query = query.filter(SECFiling.form_type == form_type)
    return query.all()
