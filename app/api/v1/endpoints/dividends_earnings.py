"""Dividends and earnings domain API endpoints."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dividends_earnings import (
    Dividend,
    DividendCalendarEvent,
    EarningsReport,
    EarningsCalendarEvent,
)
from app.schemas.dividends_earnings import (
    DividendResponse,
    DividendCalendarEventResponse,
    EarningsReportResponse,
    EarningsCalendarEventResponse,
)

router = APIRouter()


# Dividend endpoints
@router.get("/dividends/{symbol}", response_model=List[DividendResponse])
def get_dividends_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get all dividends for a symbol, optionally filtered by date range."""
    query = db.query(Dividend).filter(Dividend.symbol == symbol)
    if from_date:
        query = query.filter(Dividend.date >= from_date)
    if to_date:
        query = query.filter(Dividend.date <= to_date)
    return query.order_by(Dividend.date.desc()).all()


# Dividend Calendar Event endpoints
@router.get("/dividend-calendar/{symbol}", response_model=List[DividendCalendarEventResponse])
def get_dividend_calendar_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get all dividend calendar events for a symbol."""
    query = db.query(DividendCalendarEvent).filter(DividendCalendarEvent.symbol == symbol)
    if from_date:
        query = query.filter(DividendCalendarEvent.date >= from_date)
    if to_date:
        query = query.filter(DividendCalendarEvent.date <= to_date)
    return query.order_by(DividendCalendarEvent.date.desc()).all()


# Earnings Report endpoints
@router.get("/earnings/{symbol}", response_model=List[EarningsReportResponse])
def get_earnings_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get all earnings reports for a symbol."""
    query = db.query(EarningsReport).filter(EarningsReport.symbol == symbol)
    if from_date:
        query = query.filter(EarningsReport.date >= from_date)
    if to_date:
        query = query.filter(EarningsReport.date <= to_date)
    return query.order_by(EarningsReport.date.desc()).all()


# Earnings Calendar Event endpoints
@router.get("/earnings-calendar/{symbol}", response_model=List[EarningsCalendarEventResponse])
def get_earnings_calendar_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get all earnings calendar events for a symbol."""
    query = db.query(EarningsCalendarEvent).filter(EarningsCalendarEvent.symbol == symbol)
    if from_date:
        query = query.filter(EarningsCalendarEvent.date >= from_date)
    if to_date:
        query = query.filter(EarningsCalendarEvent.date <= to_date)
    return query.order_by(EarningsCalendarEvent.date.desc()).all()
