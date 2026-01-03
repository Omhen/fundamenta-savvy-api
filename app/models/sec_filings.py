from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class SECFiling(BaseModel):
    """General SEC filing data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    cik = Column(String, index=True, nullable=True)
    accepted_date = Column(String, nullable=True)
    filing_date = Column(String, index=True, nullable=False)
    form_type = Column(String, index=True, nullable=True)
    has_financials = Column(Boolean, default=False)
    link = Column(String, nullable=True)
    final_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_sec_filing_symbol_date', 'symbol', 'filing_date'),
        Index('idx_sec_filing_cik_date', 'cik', 'filing_date'),
        Index('idx_sec_filing_form_type', 'form_type'),
    )
