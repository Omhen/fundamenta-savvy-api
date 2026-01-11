"""Mappers for converting FMP client DTOs to database models - Other data types."""

from datetime import datetime
from typing import Optional
from fmpclient.models import directory as fmp_directory
from fmpclient.models import company as fmp_company
from fmpclient.models import dividends_earnings as fmp_div_earn
from fmpclient.models import economics as fmp_economics
from fmpclient.models import market_performance as fmp_market
from fmpclient.models import sec_filings as fmp_sec
from fmpclient.models import news as fmp_news

from app.mappers.utils import parse_date, parse_datetime
from app.models.directory import (
    StockSymbol,
    FinancialStatementSymbol,
    Exchange,
    Sector,
    Industry,
    Country,
    SymbolChange,
)
from app.models.dividends_earnings import (
    Dividend,
    DividendCalendarEvent,
    EarningsReport,
    EarningsCalendarEvent,
)
from app.models.economics import (
    TreasuryRate,
    EconomicIndicator,
    EconomicCalendarEvent,
    MarketRiskPremium,
)
from app.models.market_performance import (
    SectorPerformance,
    IndustryPerformance,
    SectorPE,
    IndustryPE,
    StockGainer,
    StockLoser,
    ActiveStock,
)
from app.models.sec_filings import SECFiling
from app.models.news import (
    FMPArticle,
    GeneralNews,
    StockNews,
)


# Company mappers
def map_stock_symbol(dto: fmp_company.SearchResult) -> StockSymbol:
    """Convert FMP StockSymbol DTO to database model."""
    return StockSymbol(
        symbol=dto.symbol,
        name=dto.name,
        exchange=dto.exchange_full_name,
        exchange_short_name=dto.exchange,
        currency=dto.currency,
    )


def map_financial_statement_symbol(dto: fmp_directory.FinancialStatementSymbol) -> FinancialStatementSymbol:
    """Convert FMP FinancialStatementSymbol DTO to database model."""
    return FinancialStatementSymbol(
        symbol=dto.symbol,
        company_name=dto.company_name,
        trading_currency=dto.trading_currency,
        reporting_currency=dto.reporting_currency,
    )


# Directory mappers
def map_exchange(dto: fmp_directory.Exchange) -> Exchange:
    """Convert FMP Exchange DTO to database model."""
    return Exchange(
        name=dto.name,
        code=dto.code,
        country=dto.country,
        currency=dto.currency,
    )


def map_sector(dto: fmp_directory.Sector) -> Sector:
    """Convert FMP Sector DTO to database model."""
    return Sector(sector=dto.sector)


def map_industry(dto: fmp_directory.Industry) -> Industry:
    """Convert FMP Industry DTO to database model."""
    return Industry(industry=dto.industry)


def map_country(dto: fmp_directory.Country) -> Country:
    """Convert FMP Country DTO to database model."""
    return Country(country=dto.country)


def map_symbol_change(dto: fmp_directory.SymbolChange) -> SymbolChange:
    """Convert FMP SymbolChange DTO to database model."""
    return SymbolChange(
        old_symbol=dto.old_symbol,
        new_symbol=dto.new_symbol,
        change_date=parse_date(dto.change_date),
        change_type=dto.change_type,
    )


# Dividend and earnings mappers
def map_dividend(dto: fmp_div_earn.Dividend) -> Dividend:
    """Convert FMP Dividend DTO to database model."""
    return Dividend(
        symbol=dto.symbol,
        date=parse_date(dto.date),
        label=dto.label,
        adj_dividend=dto.adj_dividend,
        dividend=dto.dividend,
        record_date=parse_date(dto.record_date),
        payment_date=parse_date(dto.payment_date),
        declaration_date=parse_date(dto.declaration_date),
    )


def map_dividend_calendar_event(dto: fmp_div_earn.DividendCalendarEvent) -> DividendCalendarEvent:
    """Convert FMP DividendCalendarEvent DTO to database model."""
    return DividendCalendarEvent(
        symbol=dto.symbol,
        date=parse_date(dto.date),
        label=dto.label,
        adj_dividend=dto.adj_dividend,
        dividend=dto.dividend,
        record_date=parse_date(dto.record_date),
        payment_date=parse_date(dto.payment_date),
        declaration_date=parse_date(dto.declaration_date),
        dividend_yield=dto.dividend_yield,
    )


def map_earnings_report(dto: fmp_div_earn.EarningsReport) -> EarningsReport:
    """Convert FMP EarningsReport DTO to database model."""
    return EarningsReport(
        symbol=dto.symbol,
        date=parse_date(dto.date),
        eps=dto.eps,
        eps_estimated=dto.eps_estimated,
        time=dto.time,
        revenue=dto.revenue,
        revenue_estimated=dto.revenue_estimated,
        fiscal_date_ending=dto.fiscal_date_ending,
        period=dto.period,
    )


def map_earnings_calendar_event(dto: fmp_div_earn.EarningsCalendarEvent) -> EarningsCalendarEvent:
    """Convert FMP EarningsCalendarEvent DTO to database model."""
    return EarningsCalendarEvent(
        symbol=dto.symbol,
        date=parse_date(dto.date),
        eps=dto.eps,
        eps_estimated=dto.eps_estimated,
        time=dto.time,
        revenue=dto.revenue,
        revenue_estimated=dto.revenue_estimated,
        fiscal_date_ending=dto.fiscal_date_ending,
        updated_from_date=dto.updated_from_date,
    )


# Economics mappers
def map_treasury_rate(dto: fmp_economics.TreasuryRate) -> TreasuryRate:
    """Convert FMP TreasuryRate DTO to database model."""
    return TreasuryRate(
        date=parse_date(dto.date),
        month_1=dto.month_1,
        month_2=dto.month_2,
        month_3=dto.month_3,
        month_6=dto.month_6,
        year_1=dto.year_1,
        year_2=dto.year_2,
        year_3=dto.year_3,
        year_5=dto.year_5,
        year_7=dto.year_7,
        year_10=dto.year_10,
        year_20=dto.year_20,
        year_30=dto.year_30,
    )


def map_economic_indicator(dto: fmp_economics.EconomicIndicator) -> EconomicIndicator:
    """Convert FMP EconomicIndicator DTO to database model."""
    return EconomicIndicator(
        date=parse_date(dto.date),
        value=dto.value,
        name=dto.name,
        country=dto.country,
        period=dto.period,
    )


def map_economic_calendar_event(dto: fmp_economics.EconomicCalendarEvent) -> EconomicCalendarEvent:
    """Convert FMP EconomicCalendarEvent DTO to database model."""
    return EconomicCalendarEvent(
        date=parse_date(dto.date),
        event=dto.event,
        country=dto.country,
        currency=dto.currency,
        previous=dto.previous,
        estimate=dto.estimate,
        actual=dto.actual,
        change=dto.change,
        change_percentage=dto.change_percentage,
        impact=dto.impact,
    )


def map_market_risk_premium(dto: fmp_economics.MarketRiskPremium) -> MarketRiskPremium:
    """Convert FMP MarketRiskPremium DTO to database model."""
    return MarketRiskPremium(
        country=dto.country,
        continent=dto.continent,
        total_equity_risk_premium=dto.total_equity_risk_premium,
        country_risk_premium=dto.country_risk_premium,
    )


# Market performance mappers
def map_sector_performance(dto: fmp_market.SectorPerformance) -> SectorPerformance:
    """Convert FMP SectorPerformance DTO to database model."""
    return SectorPerformance(
        sector=dto.sector,
        date=parse_date(dto.date),
        exchange=dto.exchange,
        average_change=dto.average_change,
    )


def map_industry_performance(dto: fmp_market.IndustryPerformance) -> IndustryPerformance:
    """Convert FMP IndustryPerformance DTO to database model."""
    return IndustryPerformance(
        industry=dto.industry,
        date=parse_date(dto.date),
        exchange=dto.exchange,
        average_change=dto.average_change,
    )


def map_sector_pe(dto: fmp_market.SectorPE) -> SectorPE:
    """Convert FMP SectorPE DTO to database model."""
    return SectorPE(
        date=parse_date(dto.date),
        sector=dto.sector,
        exchange=dto.exchange,
        pe=dto.pe,
    )


def map_industry_pe(dto: fmp_market.IndustryPE) -> IndustryPE:
    """Convert FMP IndustryPE DTO to database model."""
    return IndustryPE(
        date=parse_date(dto.date),
        industry=dto.industry,
        exchange=dto.exchange,
        pe=dto.pe,
    )


def map_stock_gainer(dto: fmp_market.StockGainer, date_val: Optional[date] = None) -> StockGainer:
    """Convert FMP StockGainer DTO to database model.

    Args:
        dto: FMP StockGainer DTO
        date_val: Date object (required as it's not in the DTO)
    """
    if not date_val:
        date_val = datetime.now().date()

    return StockGainer(
        symbol=dto.symbol,
        name=dto.name,
        change=dto.change,
        price=dto.price,
        exchange=dto.exchange,
        changes_percentage=dto.changes_percentage,
        date=date_val,
    )


def map_stock_loser(dto: fmp_market.StockLoser, date_val: Optional[date] = None) -> StockLoser:
    """Convert FMP StockLoser DTO to database model.

    Args:
        dto: FMP StockLoser DTO
        date_val: Date object (required as it's not in the DTO)
    """
    if not date_val:
        date_val = datetime.now().date()

    return StockLoser(
        symbol=dto.symbol,
        name=dto.name,
        change=dto.change,
        price=dto.price,
        exchange=dto.exchange,
        changes_percentage=dto.changes_percentage,
        date=date_val,
    )


def map_active_stock(dto: fmp_market.ActiveStock, date_val: Optional[date] = None) -> ActiveStock:
    """Convert FMP ActiveStock DTO to database model.

    Args:
        dto: FMP ActiveStock DTO
        date_val: Date object (required as it's not in the DTO)
    """
    if not date_val:
        date_val = datetime.now().date()

    return ActiveStock(
        symbol=dto.symbol,
        name=dto.name,
        change=dto.change,
        price=dto.price,
        changes_percentage=dto.changes_percentage,
        exchange=dto.exchange,
        date=date_val,
    )


# SEC filings mapper
def map_sec_filing(dto: fmp_sec.SECFiling) -> SECFiling:
    """Convert FMP SECFiling DTO to database model."""
    return SECFiling(
        symbol=dto.symbol,
        cik=dto.cik,
        accepted_date=parse_datetime(dto.accepted_date),
        filing_date=parse_date(dto.filing_date),
        form_type=dto.form_type,
        has_financials=dto.has_financials or False,
        link=dto.link,
        final_link=dto.final_link,
    )


# News mappers
def map_fmp_article(dto: fmp_news.FMPArticle) -> FMPArticle:
    """Convert FMP FMPArticle DTO to database model."""
    return FMPArticle(
        title=dto.title,
        date=parse_datetime(dto.date),
        content=dto.content,
        tickers=dto.tickers,
        image=dto.image,
        link=dto.link,
        author=dto.author,
        site=dto.site,
    )


def map_general_news(dto: fmp_news.GeneralNews) -> GeneralNews:
    """Convert FMP GeneralNews DTO to database model."""
    return GeneralNews(
        published_date=parse_datetime(dto.published_date),
        title=dto.title,
        text=dto.text,
        url=dto.url,
        publisher=dto.publisher,
        symbol=dto.symbol,
        site=dto.site,
        image=dto.image,
    )


def map_stock_news(dto: fmp_news.StockNews) -> StockNews:
    """Convert FMP StockNews DTO to database model."""
    return StockNews(
        symbol=dto.symbol,
        published_date=parse_datetime(dto.published_date),
        publisher=dto.publisher,
        title=dto.title,
        text=dto.text,
        url=dto.url,
        site=dto.site,
        image=dto.image,
    )
