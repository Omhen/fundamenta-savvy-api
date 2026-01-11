"""Directory domain API endpoints."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.directory import (
    StockSymbol,
    FinancialStatementSymbol,
    Exchange,
    Sector,
    Industry,
    Country,
    SymbolChange,
)
from app.schemas.directory import (
    StockSymbolResponse,
    FinancialStatementSymbolResponse,
    ExchangeResponse,
    SectorResponse,
    IndustryResponse,
    CountryResponse,
    SymbolChangeResponse,
)

router = APIRouter()


# Stock Symbol endpoints
@router.get("/symbols", response_model=List[StockSymbolResponse])
def list_stock_symbols(
    exchange: Optional[str] = Query(None, description="Filter by exchange short name"),
    db: Session = Depends(get_db)
):
    """List all stock symbols."""
    query = db.query(StockSymbol)
    if exchange:
        query = query.filter(StockSymbol.exchange_short_name == exchange)
    return query.all()


@router.get("/symbols/{symbol}", response_model=StockSymbolResponse)
def get_stock_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get stock symbol by symbol."""
    stock = db.query(StockSymbol).filter(StockSymbol.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock symbol not found: {symbol}")
    return stock


# Financial Statement Symbol endpoints
@router.get("/financial-statement-symbols", response_model=List[FinancialStatementSymbolResponse])
def list_financial_statement_symbols(db: Session = Depends(get_db)):
    """List all symbols with financial statements."""
    return db.query(FinancialStatementSymbol).all()


@router.get("/financial-statement-symbols/{symbol}", response_model=FinancialStatementSymbolResponse)
def get_financial_statement_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get financial statement symbol by symbol."""
    fs_symbol = db.query(FinancialStatementSymbol).filter(
        FinancialStatementSymbol.symbol == symbol
    ).first()
    if not fs_symbol:
        raise HTTPException(status_code=404, detail=f"Financial statement symbol not found: {symbol}")
    return fs_symbol


# Exchange endpoints
@router.get("/exchanges", response_model=List[ExchangeResponse])
def list_exchanges(db: Session = Depends(get_db)):
    """List all exchanges."""
    return db.query(Exchange).all()


@router.get("/exchanges/by-name/{name}", response_model=ExchangeResponse)
def get_exchange_by_name(name: str, db: Session = Depends(get_db)):
    """Get exchange by name."""
    exchange = db.query(Exchange).filter(Exchange.name == name).first()
    if not exchange:
        raise HTTPException(status_code=404, detail=f"Exchange not found: {name}")
    return exchange


@router.get("/exchanges/by-code/{code}", response_model=ExchangeResponse)
def get_exchange_by_code(code: str, db: Session = Depends(get_db)):
    """Get exchange by code."""
    exchange = db.query(Exchange).filter(Exchange.code == code).first()
    if not exchange:
        raise HTTPException(status_code=404, detail=f"Exchange not found with code: {code}")
    return exchange


# Sector endpoints
@router.get("/sectors", response_model=List[SectorResponse])
def list_sectors(db: Session = Depends(get_db)):
    """List all sectors."""
    return db.query(Sector).all()


@router.get("/sectors/{sector}", response_model=SectorResponse)
def get_sector(sector: str, db: Session = Depends(get_db)):
    """Get sector by name."""
    sec = db.query(Sector).filter(Sector.sector == sector).first()
    if not sec:
        raise HTTPException(status_code=404, detail=f"Sector not found: {sector}")
    return sec


# Industry endpoints
@router.get("/industries", response_model=List[IndustryResponse])
def list_industries(db: Session = Depends(get_db)):
    """List all industries."""
    return db.query(Industry).all()


@router.get("/industries/{industry}", response_model=IndustryResponse)
def get_industry(industry: str, db: Session = Depends(get_db)):
    """Get industry by name."""
    ind = db.query(Industry).filter(Industry.industry == industry).first()
    if not ind:
        raise HTTPException(status_code=404, detail=f"Industry not found: {industry}")
    return ind


# Country endpoints
@router.get("/countries", response_model=List[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    """List all countries."""
    return db.query(Country).all()


@router.get("/countries/{country}", response_model=CountryResponse)
def get_country(country: str, db: Session = Depends(get_db)):
    """Get country by name."""
    c = db.query(Country).filter(Country.country == country).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Country not found: {country}")
    return c


# Symbol Change endpoints
@router.get("/symbol-changes", response_model=List[SymbolChangeResponse])
def list_symbol_changes(db: Session = Depends(get_db)):
    """List all symbol changes."""
    return db.query(SymbolChange).order_by(SymbolChange.change_date.desc()).all()


@router.get("/symbol-changes/old/{old_symbol}", response_model=List[SymbolChangeResponse])
def get_symbol_changes_by_old(old_symbol: str, db: Session = Depends(get_db)):
    """Get symbol changes by old symbol."""
    changes = db.query(SymbolChange).filter(SymbolChange.old_symbol == old_symbol).all()
    return changes


@router.get("/symbol-changes/new/{new_symbol}", response_model=List[SymbolChangeResponse])
def get_symbol_changes_by_new(new_symbol: str, db: Session = Depends(get_db)):
    """Get symbol changes by new symbol."""
    changes = db.query(SymbolChange).filter(SymbolChange.new_symbol == new_symbol).all()
    return changes
