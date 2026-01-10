from sqlalchemy import Column, Date, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class StockSymbol(BaseModel):
    """Stock symbol from the symbol list."""

    symbol = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    exchange_short_name = Column(String, index=True, nullable=True)
    currency = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialStatementSymbol(BaseModel):
    """Symbol with available financial statements."""

    symbol = Column(String, primary_key=True)
    company_name = Column(String, nullable=True)
    trading_currency = Column(String, nullable=True)
    reporting_currency = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Exchange(BaseModel):
    """Exchange information."""

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=True)
    country = Column(String, index=True, nullable=True)
    currency = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Sector(BaseModel):
    """Sector classification."""

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Industry(BaseModel):
    """Industry classification."""

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Country(BaseModel):
    """Country information."""

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SymbolChange(BaseModel):
    """Symbol change record."""

    id = Column(Integer, primary_key=True, index=True)
    old_symbol = Column(String, index=True, nullable=False)
    new_symbol = Column(String, index=True, nullable=False)
    change_date = Column(Date, index=True, nullable=False)
    change_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_symbol_change_old_new', 'old_symbol', 'new_symbol'),
    )
