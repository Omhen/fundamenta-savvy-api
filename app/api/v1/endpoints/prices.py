"""Quotes and prices domain API endpoints."""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.quotes_prices import (
    Quote,
    HistoricalPrice,
    IntradayPrice,
)
from app.schemas.prices import (
    QuoteResponse,
    HistoricalPriceResponse,
    IntradayPriceResponse,
)

router = APIRouter()


# Quote endpoints
@router.get("/quotes/{symbol}", response_model=List[QuoteResponse])
def get_quotes_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all quotes for a symbol."""
    quotes = db.query(Quote).filter(
        Quote.symbol == symbol
    ).order_by(Quote.timestamp.desc()).all()
    return quotes


@router.get("/quotes/{symbol}/latest", response_model=QuoteResponse)
def get_latest_quote(symbol: str, db: Session = Depends(get_db)):
    """Get the latest quote for a symbol."""
    quote = db.query(Quote).filter(
        Quote.symbol == symbol
    ).order_by(Quote.timestamp.desc()).first()
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote not found for symbol: {symbol}")
    return quote


# Historical Price endpoints
@router.get("/historical/{symbol}", response_model=List[HistoricalPriceResponse])
def get_historical_prices_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get historical prices for a symbol."""
    query = db.query(HistoricalPrice).filter(
        HistoricalPrice.symbol == symbol
    )
    if from_date:
        query = query.filter(HistoricalPrice.date >= from_date)
    if to_date:
        query = query.filter(HistoricalPrice.date <= to_date)
    return query.order_by(HistoricalPrice.date).all()


# Intraday Price endpoints
@router.get("/intraday/{symbol}", response_model=List[IntradayPriceResponse])
def get_intraday_prices_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all intraday prices for a symbol."""
    prices = db.query(IntradayPrice).filter(
        IntradayPrice.symbol == symbol
    ).order_by(IntradayPrice.date.desc()).all()
    return prices
