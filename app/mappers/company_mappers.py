"""Mappers for converting FMP client DTOs to database models - Company data."""

from typing import Optional
from fmpclient.models import company as fmp_company
from app.models.company_profile import (
    CompanyProfile,
    Executive,
    MarketCapitalization,
    EmployeeCount,
    SharesFloat,
    DelistedCompany,
)


def map_company_profile(dto: fmp_company.CompanyProfile) -> CompanyProfile:
    """Convert FMP CompanyProfile DTO to database model."""
    return CompanyProfile(
        symbol=dto.symbol,
        price=dto.price,
        beta=dto.beta,
        vol_avg=dto.vol_avg,
        mkt_cap=dto.mkt_cap,
        last_div=dto.last_div,
        range=dto.range,
        changes=dto.changes,
        company_name=dto.company_name,
        currency=dto.currency,
        cik=dto.cik,
        isin=dto.isin,
        cusip=dto.cusip,
        exchange=dto.exchange,
        exchange_short_name=dto.exchange_short_name,
        industry=dto.industry,
        website=dto.website,
        description=dto.description,
        ceo=dto.ceo,
        sector=dto.sector,
        country=dto.country,
        full_time_employees=dto.full_time_employees,
        phone=dto.phone,
        address=dto.address,
        city=dto.city,
        state=dto.state,
        zip=dto.zip,
        dcf_diff=dto.dcf_diff,
        dcf=dto.dcf,
        image=dto.image,
        ipo_date=dto.ipo_date,
        default_image=dto.default_image,
        is_etf=dto.is_etf,
        is_actively_trading=dto.is_actively_trading,
        is_adr=dto.is_adr,
        is_fund=dto.is_fund,
    )


def map_executive(dto: fmp_company.Executive, symbol: Optional[str] = None) -> Executive:
    """Convert FMP Executive DTO to database model.

    Args:
        dto: FMP Executive DTO
        symbol: Stock symbol (required as it's not in the Executive DTO)
    """
    if not symbol:
        raise ValueError("Symbol is required for Executive mapping")

    return Executive(
        symbol=symbol,
        title=dto.title,
        name=dto.name,
        pay=dto.pay,
        currency_pay=dto.currency_pay,
        gender=dto.gender,
        year_born=dto.year_born,
        title_since=dto.title_since,
    )


def map_market_capitalization(dto: fmp_company.MarketCapitalization) -> MarketCapitalization:
    """Convert FMP MarketCapitalization DTO to database model."""
    return MarketCapitalization(
        symbol=dto.symbol,
        date=dto.date,
        market_cap=dto.market_cap,
    )


def map_employee_count(dto: fmp_company.EmployeeCount) -> EmployeeCount:
    """Convert FMP EmployeeCount DTO to database model."""
    return EmployeeCount(
        symbol=dto.symbol,
        cik=dto.cik,
        acceptance_time=dto.acceptance_time,
        period_of_report=dto.period_of_report,
        company_name=dto.company_name,
        form_type=dto.form_type,
        filing_date=dto.filing_date,
        employee_count=dto.employee_count,
        source=dto.source,
    )


def map_shares_float(dto: fmp_company.SharesFloat) -> SharesFloat:
    """Convert FMP SharesFloat DTO to database model."""
    return SharesFloat(
        symbol=dto.symbol,
        date=dto.date,
        free_float=dto.free_float,
        float_shares=dto.float_shares,
        outstanding_shares=dto.outstanding_shares,
        source=dto.source,
    )


def map_delisted_company(dto: fmp_company.DelistedCompany) -> DelistedCompany:
    """Convert FMP DelistedCompany DTO to database model."""
    return DelistedCompany(
        symbol=dto.symbol,
        company_name=dto.company_name,
        exchange=dto.exchange,
        ipo_date=dto.ipo_date,
        delisted_date=dto.delisted_date,
    )
