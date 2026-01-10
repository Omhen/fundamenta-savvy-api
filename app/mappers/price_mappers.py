"""Mappers for converting FMP client DTOs to database models - Prices and Quotes."""

from typing import Optional
from datetime import datetime, date

from fmpclient.models import quote as fmp_quote
from fmpclient.models import price as fmp_price


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse a date string to a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
    """Parse a datetime string to a datetime object."""
    if not datetime_str:
        return None
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d")
        except ValueError:
            return None
from app.models.quotes_prices import (
    Quote,
    HistoricalPrice,
    IntradayPrice,
)


def map_quote(dto: fmp_quote.Quote) -> Quote:
    """Convert FMP Quote DTO to database model."""
    return Quote(
        symbol=dto.symbol,
        name=dto.name,
        price=dto.price,
        changes_percentage=dto.changes_percentage,
        change=dto.change,
        day_low=dto.day_low,
        day_high=dto.day_high,
        year_high=dto.year_high,
        year_low=dto.year_low,
        market_cap=dto.market_cap,
        price_avg_50=dto.price_avg_50,
        price_avg_200=dto.price_avg_200,
        exchange=dto.exchange,
        volume=dto.volume,
        avg_volume=dto.avg_volume,
        open=dto.open,
        previous_close=dto.previous_close,
        eps=dto.eps,
        pe=dto.pe,
        earnings_announcement=dto.earnings_announcement,
        shares_outstanding=dto.shares_outstanding,
        timestamp=dto.timestamp,
    )


def map_historical_price(dto: fmp_price.HistoricalPrice, symbol: Optional[str] = None) -> HistoricalPrice:
    """Convert FMP HistoricalPrice DTO to database model.

    Args:
        dto: FMP HistoricalPrice DTO
        symbol: Stock symbol (required as it's not always in the HistoricalPrice DTO)
    """
    if not symbol:
        raise ValueError("Symbol is required for HistoricalPrice mapping")

    return HistoricalPrice(
        symbol=symbol,
        date=parse_date(dto.date),
        open=dto.open,
        high=dto.high,
        low=dto.low,
        close=dto.close,
        adj_close=dto.adj_close,
        volume=dto.volume,
        unadjusted_volume=dto.unadjusted_volume,
        change=dto.change,
        change_percent=dto.change_percent,
        vwap=dto.vwap,
        label=dto.label,
        change_over_time=dto.change_over_time,
    )


def map_intraday_price(dto: fmp_price.IntradayPrice, symbol: Optional[str] = None) -> IntradayPrice:
    """Convert FMP IntradayPrice DTO to database model.

    Args:
        dto: FMP IntradayPrice DTO
        symbol: Stock symbol (required as it's not in the IntradayPrice DTO)
    """
    if not symbol:
        raise ValueError("Symbol is required for IntradayPrice mapping")

    return IntradayPrice(
        symbol=symbol,
        date=parse_datetime(dto.date),
        open=dto.open,
        high=dto.high,
        low=dto.low,
        close=dto.close,
        volume=dto.volume,
    )
