"""Company domain API endpoints."""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company_profile import (
    CompanyProfile,
    Executive,
    MarketCapitalization,
    EmployeeCount,
    SharesFloat,
    DelistedCompany,
)
from app.schemas.company import (
    CompanyProfileResponse,
    ExecutiveResponse,
    MarketCapitalizationResponse,
    EmployeeCountResponse,
    SharesFloatResponse,
    DelistedCompanyResponse,
)

router = APIRouter()


# Company Profile endpoints
@router.get("/profiles/{symbol}", response_model=CompanyProfileResponse)
def get_company_profile(symbol: str, db: Session = Depends(get_db)):
    """Get company profile by symbol."""
    profile = db.query(CompanyProfile).filter(CompanyProfile.symbol == symbol).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Company profile not found for symbol: {symbol}")
    return profile


@router.get("/profiles", response_model=List[CompanyProfileResponse])
def list_company_profiles(db: Session = Depends(get_db)):
    """List all company profiles."""
    return db.query(CompanyProfile).limit(50).all()


# Executive endpoints
@router.get("/executives/{symbol}", response_model=List[ExecutiveResponse])
def get_executives_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all executives for a company by symbol."""
    executives = db.query(Executive).filter(Executive.symbol == symbol).all()
    return executives


@router.get("/executives/{symbol}/{name}", response_model=ExecutiveResponse)
def get_executive(symbol: str, name: str, db: Session = Depends(get_db)):
    """Get a specific executive by symbol and name."""
    executive = db.query(Executive).filter(
        Executive.symbol == symbol,
        Executive.name == name
    ).first()
    if not executive:
        raise HTTPException(status_code=404, detail=f"Executive not found: {name} at {symbol}")
    return executive


# Market Capitalization endpoints
@router.get("/market-cap/{symbol}", response_model=List[MarketCapitalizationResponse])
def get_market_cap_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all market capitalization records for a symbol."""
    records = db.query(MarketCapitalization).filter(
        MarketCapitalization.symbol == symbol
    ).order_by(MarketCapitalization.date.desc()).all()
    return records


@router.get("/market-cap/{symbol}/{date}", response_model=MarketCapitalizationResponse)
def get_market_cap(symbol: str, date: date, db: Session = Depends(get_db)):
    """Get market capitalization by symbol and date."""
    record = db.query(MarketCapitalization).filter(
        MarketCapitalization.symbol == symbol,
        MarketCapitalization.date == date
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Market cap not found for {symbol} on {date}")
    return record


# Employee Count endpoints
@router.get("/employee-count/{symbol}", response_model=List[EmployeeCountResponse])
def get_employee_count_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all employee count records for a symbol."""
    records = db.query(EmployeeCount).filter(
        EmployeeCount.symbol == symbol
    ).order_by(EmployeeCount.filing_date.desc()).all()
    return records


# Shares Float endpoints
@router.get("/shares-float/{symbol}", response_model=List[SharesFloatResponse])
def get_shares_float_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all shares float records for a symbol."""
    records = db.query(SharesFloat).filter(
        SharesFloat.symbol == symbol
    ).order_by(SharesFloat.date.desc()).all()
    return records


# Delisted Company endpoints
@router.get("/delisted/{symbol}", response_model=DelistedCompanyResponse)
def get_delisted_company(symbol: str, db: Session = Depends(get_db)):
    """Get delisted company by symbol."""
    company = db.query(DelistedCompany).filter(DelistedCompany.symbol == symbol).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Delisted company not found for symbol: {symbol}")
    return company


@router.get("/delisted", response_model=List[DelistedCompanyResponse])
def list_delisted_companies(db: Session = Depends(get_db)):
    """List all delisted companies."""
    return db.query(DelistedCompany).all()
