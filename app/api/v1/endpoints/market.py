"""Market performance domain API endpoints."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.market_performance import (
    SectorPerformance,
    IndustryPerformance,
    SectorPE,
    IndustryPE,
    StockGainer,
    StockLoser,
    ActiveStock,
)
from app.schemas.market import (
    SectorPerformanceResponse,
    IndustryPerformanceResponse,
    SectorPEResponse,
    IndustryPEResponse,
    StockGainerResponse,
    StockLoserResponse,
    ActiveStockResponse,
)

router = APIRouter()


# Sector Performance endpoints
@router.get("/sector-performance/{sector}", response_model=List[SectorPerformanceResponse])
def get_sector_performance_by_sector(sector: str, from_date: Optional[date], to_date: Optional[date], db: Session = Depends(get_db)):
    """Get all performance records for a sector."""
    records = db.query(SectorPerformance).filter(
        SectorPerformance.sector == sector,
        SectorPerformance.date >= from_date,
        SectorPerformance.date <= to_date,
    ).order_by(SectorPerformance.date.desc()).all()
    return records


# Industry Performance endpoints
@router.get("/industry-performance/{industry}", response_model=List[IndustryPerformanceResponse])
def get_industry_performance_by_industry(industry: str, from_date: Optional[date], to_date: Optional[date], db: Session = Depends(get_db)):
    """Get all performance records for an industry."""
    records = db.query(IndustryPerformance).filter(
        IndustryPerformance.industry == industry,
        IndustryPerformance.date >= from_date,
        IndustryPerformance.date <= to_date,
    ).order_by(IndustryPerformance.date.desc()).all()
    return records


# Sector PE endpoints
@router.get("/sector-pe/{sector}", response_model=List[SectorPEResponse])
def get_sector_pe_by_sector(sector: str, from_date: Optional[date], to_date: Optional[date], db: Session = Depends(get_db)):
    """Get all P/E records for a sector."""
    records = db.query(SectorPE).filter(
        SectorPE.sector == sector,
        SectorPE.date >= from_date,
        SectorPE.date <= from_date
    ).order_by(SectorPE.date.desc()).all()
    return records


# Industry PE endpoints
@router.get("/industry-pe/{industry}", response_model=List[IndustryPEResponse])
def get_industry_pe_by_industry(industry: str, db: Session = Depends(get_db)):
    """Get all P/E records for an industry."""
    records = db.query(IndustryPE).filter(
        IndustryPE.industry == industry
    ).order_by(IndustryPE.date.desc()).all()
    return records


# Stock Gainer endpoints
@router.get("/gainers/{date}", response_model=List[StockGainerResponse])
def get_gainers_by_date(date: date, db: Session = Depends(get_db)):
    """Get all stock gainers for a date."""
    gainers = db.query(StockGainer).filter(
        StockGainer.date == date
    ).all()
    return gainers


# Stock Loser endpoints
@router.get("/losers/{date}", response_model=List[StockLoserResponse])
def get_losers_by_date(date: date, db: Session = Depends(get_db)):
    """Get all stock losers for a date."""
    losers = db.query(StockLoser).filter(
        StockLoser.date == date
    ).all()
    return losers


# Active Stock endpoints
@router.get("/actives/{date}", response_model=List[ActiveStockResponse])
def get_actives_by_date(date: date, db: Session = Depends(get_db)):
    """Get all active stocks for a date."""
    actives = db.query(ActiveStock).filter(
        ActiveStock.date == date
    ).all()
    return actives
