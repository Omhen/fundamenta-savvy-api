from sqlalchemy import Integer, Column, String, Float, Index, DateTime, func
from app.db.base_class import BaseModel


class CompanyMetrics(BaseModel):

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_growth_10y = Column(Float, nullable=True)
    years_increasing_dividend = Column(Integer, nullable=True)
    copm = Column(Float, nullable=True)
    roic = Column(Float, nullable=True)
    rota = Column(Float, nullable=True)
    debt_ebitda_ratio = Column(Float, nullable=True)
    ev_ebitda_ratio = Column(Float, nullable=True)
    ev_fcf_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ps_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    dividend_payout = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    sector = Column(String, nullable=True)
    market_cap = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_company_metrics_symbol', 'symbol', unique=True),
    )

