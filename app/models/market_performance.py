from sqlalchemy import Column, Date, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class SectorPerformance(BaseModel):
    """Sector performance snapshot data."""

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    exchange = Column(String, nullable=True)
    average_change = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_sector_perf_sector_date', 'sector', 'date', unique=True),
    )


class IndustryPerformance(BaseModel):
    """Industry performance snapshot data."""

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    exchange = Column(String, nullable=True)
    average_change = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_industry_perf_industry_date', 'industry', 'date', unique=True),
    )


class SectorPE(BaseModel):
    """Sector P/E ratio snapshot data."""

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    sector = Column(String, index=True, nullable=False)
    exchange = Column(String, nullable=True)
    pe = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_sector_pe_sector_date', 'sector', 'date', unique=True),
    )


class IndustryPE(BaseModel):
    """Industry P/E ratio snapshot data."""

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    industry = Column(String, index=True, nullable=False)
    exchange = Column(String, nullable=True)
    pe = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_industry_pe_industry_date', 'industry', 'date', unique=True),
    )


class StockGainer(BaseModel):
    """Biggest stock gainer data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    change = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    exchange = Column(String, nullable=True)
    changes_percentage = Column(String, nullable=True)
    date = Column(Date, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_gainer_date_symbol', 'date', 'symbol'),
    )


class StockLoser(BaseModel):
    """Biggest stock loser data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    change = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    exchange = Column(String, nullable=True)
    changes_percentage = Column(String, nullable=True)
    date = Column(Date, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_loser_date_symbol', 'date', 'symbol'),
    )


class ActiveStock(BaseModel):
    """Most actively traded stock data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    change = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    changes_percentage = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    date = Column(Date, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_active_date_symbol', 'date', 'symbol'),
    )
