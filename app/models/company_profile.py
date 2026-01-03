from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class CompanyProfile(BaseModel):
    """Company profile information."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    vol_avg = Column(Integer, nullable=True)
    mkt_cap = Column(Integer, nullable=True)
    last_div = Column(Float, nullable=True)
    range = Column(String, nullable=True)
    changes = Column(Float, nullable=True)
    company_name = Column(String, nullable=False)
    currency = Column(String, nullable=True)
    cik = Column(String, index=True, nullable=True)
    isin = Column(String, nullable=True)
    cusip = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    exchange_short_name = Column(String, nullable=True)
    industry = Column(String, index=True, nullable=True)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)
    ceo = Column(String, nullable=True)
    sector = Column(String, index=True, nullable=True)
    country = Column(String, index=True, nullable=True)
    full_time_employees = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    dcf_diff = Column(Float, nullable=True)
    dcf = Column(Float, nullable=True)
    image = Column(String, nullable=True)
    ipo_date = Column(String, nullable=True)
    default_image = Column(Boolean, nullable=True)
    is_etf = Column(Boolean, default=False)
    is_actively_trading = Column(Boolean, default=True)
    is_adr = Column(Boolean, default=False)
    is_fund = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_company_sector_industry', 'sector', 'industry'),
        Index('idx_company_country_exchange', 'country', 'exchange'),
    )


class Executive(BaseModel):
    """Company executive information."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    title = Column(String, nullable=True)
    name = Column(String, nullable=False)
    pay = Column(Float, nullable=True)
    currency_pay = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    year_born = Column(Integer, nullable=True)
    title_since = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_executive_symbol_name', 'symbol', 'name'),
    )


class MarketCapitalization(BaseModel):
    """Historical market capitalization data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    market_cap = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_market_cap_symbol_date', 'symbol', 'date', unique=True),
    )


class EmployeeCount(BaseModel):
    """Company employee count data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    cik = Column(String, nullable=True)
    acceptance_time = Column(String, nullable=True)
    period_of_report = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    form_type = Column(String, nullable=True)
    filing_date = Column(String, index=True, nullable=True)
    employee_count = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_employee_symbol_date', 'symbol', 'filing_date'),
    )


class SharesFloat(BaseModel):
    """Company shares float and liquidity data."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=True)
    free_float = Column(Float, nullable=True)
    float_shares = Column(Float, nullable=True)
    outstanding_shares = Column(Float, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_shares_float_symbol_date', 'symbol', 'date'),
    )


class DelistedCompany(BaseModel):
    """Delisted company information."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    ipo_date = Column(String, nullable=True)
    delisted_date = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
