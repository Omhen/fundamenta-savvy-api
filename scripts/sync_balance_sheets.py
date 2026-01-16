#!/usr/bin/env python3
"""
Sync Balance Sheets for NYSE and NASDAQ Stocks

This script:
1. Retrieves all StockSymbol records where exchange_short_name is NYSE or NASDAQ
2. Joins with FinancialStatementSymbol to ensure the symbol has financial data
3. For each symbol:
   - Checks the last available balance sheet in the database
   - If no balance sheets exist, fetches all historical balance sheets from FMP
   - If the last quarterly balance sheet is older than 3 months, fetches the latest quarterly balance sheet

Rate limited to comply with API limits.

Usage:
    python -m scripts.sync_balance_sheets

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from fmpclient import FMPClient
from sqlalchemy.orm import Session

from scripts.base import get_db_session, run_async_script
from app.models.financial_statements import BalanceSheet
from app.mappers.financial_mappers import map_balance_sheet
from app.mappers.utils import map_and_save
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials


def get_last_balance_sheet(session: Session, symbol: str) -> Optional[BalanceSheet]:
    """
    Get the most recent balance sheet for a symbol.

    Args:
        session: Database session
        symbol: Stock symbol

    Returns:
        Last balance sheet or None if not found
    """
    return (
        session.query(BalanceSheet)
        .filter(BalanceSheet.symbol == symbol)
        .order_by(BalanceSheet.date.desc())
        .first()
    )


def is_quarterly_statement_stale(statement: BalanceSheet, months: int = 3) -> bool:
    """
    Check if a quarterly balance sheet is older than the specified number of months.

    Args:
        statement: BalanceSheet instance
        months: Number of months to consider stale (default: 3)

    Returns:
        True if the statement is quarterly and older than specified months
    """
    # Check if it's a quarterly statement (Q1, Q2, Q3, Q4)
    if not statement.period or statement.period not in ["Q1", "Q2", "Q3", "Q4"]:
        return False

    try:
        # Parse the statement date
        statement_date = datetime.strptime(statement.date, "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        return statement_date < cutoff_date
    except (ValueError, TypeError):
        # If date parsing fails, consider it stale to trigger an update
        return True


async def fetch_and_store_balance_sheets(
    fmp: FMPClient,
    session: Session,
    symbol: str,
    period: str = "quarter",
    limit: Optional[int] = None
) -> int:
    """
    Fetch balance sheets from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        session: Database session
        symbol: Stock symbol
        period: 'quarter' or 'annual' (default: quarter)
        limit: Maximum number of balance sheets to fetch (None for all)

    Returns:
        Number of balance sheets saved
    """

    try:
        # Fetch balance sheets from FMP
        balance_sheets = await fmp.financials.get_balance_sheet(
            symbol=symbol,
            period=period,
            limit=limit or 100
        )

        if not balance_sheets:
            return 0

        # Map and save to database
        saved_count = map_and_save(
            session=session,
            dtos=balance_sheets,
            mapper_func=map_balance_sheet,
            unique_columns=["symbol", "date"],
            upsert=True
        )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch balance sheets for {symbol}: {e}")
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
        "statements_saved": 0,
        "error": None
    }

    with get_db_session() as session:
        # Get the last balance sheet for this symbol
        last_statement = get_last_balance_sheet(session, symbol)

        if last_statement is None:
            # No balance sheets exist - fetch all historical quarterly balance sheets
            print(f"  {symbol}: No balance sheets found. Fetching all historical data...")
            result["action"] = "fetch_all"

            saved_count = await fetch_and_store_balance_sheets(
                fmp=fmp,
                session=session,
                symbol=symbol,
                period="quarter",
                limit=None  # Fetch all available
            )

            result["statements_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} balance sheets")

        elif is_quarterly_statement_stale(last_statement):
            # Last quarterly balance sheet is older than 3 months - fetch latest
            print(f"  {symbol}: Last quarterly balance sheet from {last_statement.date} is stale. Fetching latest...")
            result["action"] = "fetch_latest"

            saved_count = await fetch_and_store_balance_sheets(
                fmp=fmp,
                session=session,
                symbol=symbol,
                period="quarter",
                limit=1  # Fetch only the latest
            )

            result["statements_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} balance sheet(s)")

        else:
            # Data is up to date
            result["action"] = "skip"
            print(f"  {symbol}: Balance sheets are up to date (last: {last_statement.date})")

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
        "total_statements": 0
    }

    async with FMPClient(api_key=api_key) as fmp:
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")

            try:
                result = await process_symbol(fmp, symbol)

                if result["action"]:
                    results[result["action"]] += 1
                results["total_statements"] += result["statements_saved"]

            except Exception as e:
                print(f"  ERROR: Failed to process {symbol}: {e}")
                results["errors"] += 1

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total symbols processed: {len(symbols)}")
    print(f"  - Fetched all balance sheets: {results['fetch_all']}")
    print(f"  - Fetched latest balance sheet: {results['fetch_latest']}")
    print(f"  - Already up to date: {results['skip']}")
    print(f"  - Errors: {results['errors']}")
    print(f"Total balance sheets saved: {results['total_statements']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_balance_sheets"))
