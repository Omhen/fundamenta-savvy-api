#!/usr/bin/env python3
"""
Sync Dividends for NYSE and NASDAQ Stocks

This script:
1. Retrieves all StockSymbol records where exchange_short_name is NYSE or NASDAQ
2. Joins with FinancialStatementSymbol to ensure the symbol has financial data
3. For each symbol:
   - Checks the last available dividend in the database
   - If no dividends exist, fetches all historical dividends from FMP
   - If the last dividend is older than 3 months, fetches the latest dividends

Rate limited to comply with API limits.

Usage:
    python -m scripts.sync_dividends

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from fmpclient import FMPClient
from sqlalchemy.orm import Session

from scripts.base import get_db_session, run_async_script
from app.models.directory import StockSymbol, FinancialStatementSymbol
from app.models.dividends_earnings import Dividend
from app.mappers.other_mappers import map_dividend
from app.mappers.utils import map_and_save
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials


def get_last_dividend(session: Session, symbol: str) -> Optional[Dividend]:
    """
    Get the most recent dividend for a symbol.

    Args:
        session: Database session
        symbol: Stock symbol

    Returns:
        Last dividend or None if not found
    """
    return (
        session.query(Dividend)
        .filter(Dividend.symbol == symbol)
        .order_by(Dividend.date.desc())
        .first()
    )


def is_dividend_stale(dividend: Dividend, months: int = 3) -> bool:
    """
    Check if a dividend is older than the specified number of months.

    Args:
        dividend: Dividend instance
        months: Number of months to consider stale (default: 3)

    Returns:
        True if the dividend is older than specified months
    """
    try:
        # Parse the dividend date
        dividend_date = datetime.strptime(dividend.date, "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        return dividend_date < cutoff_date
    except (ValueError, TypeError):
        # If date parsing fails, consider it stale to trigger an update
        return True


async def fetch_and_store_dividends(
    fmp: FMPClient,
    session: Session,
    symbol: str,
) -> int:
    """
    Fetch dividends from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        session: Database session
        symbol: Stock symbol

    Returns:
        Number of dividends saved
    """

    try:
        # Fetch dividends from FMP
        dividends = await fmp.dividends.get_dividends(symbol=symbol)

        if not dividends:
            return 0

        # Map and save to database
        saved_count = map_and_save(
            session=session,
            dtos=dividends,
            mapper_func=map_dividend,
            unique_columns=["symbol", "date"],
            upsert=True
        )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch dividends for {symbol}: {e}")
        return 0


async def process_symbol(fmp: FMPClient, symbol: str) -> dict:
    """
    Process a single symbol: check existing data and fetch/update as needed.

    Args:
        fmp: FMP client instance
        symbol: Stock symbol

    Returns:
        Dict with processing statistics
    """
    result = {
        "symbol": symbol,
        "action": None,
        "dividends_saved": 0,
        "error": None
    }

    with get_db_session() as session:
        # Get the last dividend for this symbol
        last_dividend = get_last_dividend(session, symbol)

        if last_dividend is None:
            # No dividends exist - fetch all historical dividends
            print(f"  {symbol}: No dividends found. Fetching all historical data...")
            result["action"] = "fetch_all"

            saved_count = await fetch_and_store_dividends(
                fmp=fmp,
                session=session,
                symbol=symbol,
            )

            result["dividends_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} dividends")

        elif is_dividend_stale(last_dividend):
            # Last dividend is older than 3 months - fetch latest
            print(f"  {symbol}: Last dividend from {last_dividend.date} is stale. Fetching latest...")
            result["action"] = "fetch_latest"

            saved_count = await fetch_and_store_dividends(
                fmp=fmp,
                session=session,
                symbol=symbol,
            )

            result["dividends_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} dividend(s)")

        else:
            # Data is up to date
            result["action"] = "skip"
            print(f"  {symbol}: Dividends are up to date (last: {last_dividend.date})")

    return result


async def main():
    """Main script logic."""

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get NYSE and NASDAQ symbols with financial statements
    print("Retrieving NYSE and NASDAQ symbols with financial statements...")
    with get_db_session() as session:
        symbols = get_symbols_with_financials(session, exchanges=AVAILABLE_EXCHANGES)

    print(f"Found {len(symbols)} NYSE/NASDAQ symbols with financial statement availability")

    if not symbols:
        print("No symbols to process. Exiting.")
        return

    # Process each symbol
    print("\nProcessing symbols...")
    results = {
        "fetch_all": 0,
        "fetch_latest": 0,
        "skip": 0,
        "errors": 0,
        "total_dividends": 0
    }

    async with FMPClient(api_key=api_key) as fmp:
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")

            try:
                result = await process_symbol(fmp, symbol)

                if result["action"]:
                    results[result["action"]] += 1
                results["total_dividends"] += result["dividends_saved"]

            except Exception as e:
                print(f"  ERROR: Failed to process {symbol}: {e}")
                results["errors"] += 1

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total symbols processed: {len(symbols)}")
    print(f"  - Fetched all dividends: {results['fetch_all']}")
    print(f"  - Fetched latest dividends: {results['fetch_latest']}")
    print(f"  - Already up to date: {results['skip']}")
    print(f"  - Errors: {results['errors']}")
    print(f"Total dividends saved: {results['total_dividends']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_dividends"))
