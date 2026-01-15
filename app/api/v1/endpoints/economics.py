"""Economics domain API endpoints."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.economics import (
    TreasuryRate,
    EconomicIndicator,
    EconomicCalendarEvent,
    MarketRiskPremium,
)
from app.schemas.economics import (
    TreasuryRateResponse,
    EconomicIndicatorResponse,
    EconomicCalendarEventResponse,
    MarketRiskPremiumResponse,
)

router = APIRouter()


# Treasury Rate endpoints
@router.get("/treasury-rates", response_model=List[TreasuryRateResponse])
def list_treasury_rates(db: Session = Depends(get_db)):
    """List all treasury rates."""
    rates = db.query(TreasuryRate).order_by(TreasuryRate.date.desc()).all()
    return rates


@router.get("/treasury-rates/{date}", response_model=TreasuryRateResponse)
def get_treasury_rate(date: date, db: Session = Depends(get_db)):
    """Get treasury rate by date."""
    rate = db.query(TreasuryRate).filter(TreasuryRate.date == date).first()
    if not rate:
        raise HTTPException(status_code=404, detail=f"Treasury rate not found for date: {date}")
    return rate


# Economic Indicator endpoints
@router.get("/indicators", response_model=List[EconomicIndicatorResponse])
def list_economic_indicators(
    name: Optional[str] = Query(None, description="Filter by indicator name"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """List economic indicators with optional filters."""
    query = db.query(EconomicIndicator)
    if name:
        query = query.filter(EconomicIndicator.name == name)
    if country:
        query = query.filter(EconomicIndicator.country == country)
    return query.order_by(EconomicIndicator.date.desc()).all()


# Economic Calendar Event endpoints
@router.get("/calendar", response_model=List[EconomicCalendarEventResponse])
def list_economic_calendar(
    country: Optional[str] = Query(None, description="Filter by country"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """List economic calendar events with optional filters."""
    query = db.query(EconomicCalendarEvent)
    if country:
        query = query.filter(EconomicCalendarEvent.country == country)
    if from_date:
        query = query.filter(EconomicCalendarEvent.date >= from_date)
    if to_date:
        query = query.filter(EconomicCalendarEvent.date <= to_date)
    return query.order_by(EconomicCalendarEvent.date).all()


# Market Risk Premium endpoints
@router.get("/risk-premium", response_model=List[MarketRiskPremiumResponse])
def list_market_risk_premiums(db: Session = Depends(get_db)):
    """List all market risk premiums."""
    return db.query(MarketRiskPremium).all()


@router.get("/risk-premium/{country}", response_model=MarketRiskPremiumResponse)
def get_market_risk_premium(country: str, db: Session = Depends(get_db)):
    """Get market risk premium by country."""
    premium = db.query(MarketRiskPremium).filter(MarketRiskPremium.country == country).first()
    if not premium:
        raise HTTPException(status_code=404, detail=f"Market risk premium not found for country: {country}")
    return premium
