#!/usr/bin/env python3
"""
Sync Income Statements for NYSE and NASDAQ Stocks

This script:
1. Retrieves all StockSymbol records where exchange_short_name is NYSE or NASDAQ
2. Joins with FinancialStatementSymbol to ensure the symbol has financial data
3. For each symbol:
   - Checks the last available income statement in the database
   - If no statements exist, fetches all historical income statements from FMP
   - If the last quarterly statement is older than 3 months, fetches the latest quarterly statement

Rate limited to comply with API limits.

Usage:
    python -m scripts.sync_income_statements

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from fmpclient import FMPClient
from sqlalchemy.orm import Session

from scripts.base import get_db_session, run_async_script, RateLimiter
from app.models.directory import StockSymbol, FinancialStatementSymbol
from app.models.financial_statements import IncomeStatement
from app.mappers.financial_mappers import map_income_statement
from app.mappers.utils import map_and_save
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials


def get_last_income_statement(session: Session, symbol: str) -> Optional[IncomeStatement]:
    """
    Get the most recent income statement for a symbol.

    Args:
        session: Database session
        symbol: Stock symbol

    Returns:
        Last income statement or None if not found
    """
    return (
        session.query(IncomeStatement)
        .filter(IncomeStatement.symbol == symbol)
        .order_by(IncomeStatement.date.desc())
        .first()
    )


def is_quarterly_statement_stale(statement: IncomeStatement, months: int = 3) -> bool:
    """
    Check if a quarterly income statement is older than the specified number of months.

    Args:
        statement: IncomeStatement instance
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


async def fetch_and_store_income_statements(
    fmp: FMPClient,
    session: Session,
    symbol: str,
    period: str = "quarter",
    limit: Optional[int] = None
) -> int:
    """
    Fetch income statements from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        session: Database session
        symbol: Stock symbol
        period: 'quarter' or 'annual' (default: quarter)
        limit: Maximum number of statements to fetch (None for all)

    Returns:
        Number of statements saved
    """

    try:
        # Fetch income statements from FMP
        income_statements = await fmp.financials.get_income_statement(
            symbol=symbol,
            period=period,
            limit=limit or 100
        )

        if not income_statements:
            return 0

        # Map and save to database
        saved_count = map_and_save(
            session=session,
            dtos=income_statements,
            mapper_func=map_income_statement,
            unique_columns=["symbol", "date"],
            upsert=True
        )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch income statements for {symbol}: {e}")
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
        # Get the last income statement for this symbol
        last_statement = get_last_income_statement(session, symbol)

        if last_statement is None:
            # No statements exist - fetch all historical quarterly statements
            print(f"  {symbol}: No income statements found. Fetching all historical data...")
            result["action"] = "fetch_all"

            saved_count = await fetch_and_store_income_statements(
                fmp=fmp,
                session=session,
                symbol=symbol,
                period="quarter",
                limit=None  # Fetch all available
            )

            result["statements_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} income statements")

        elif is_quarterly_statement_stale(last_statement):
            # Last quarterly statement is older than 3 months - fetch latest
            print(f"  {symbol}: Last quarterly statement from {last_statement.date} is stale. Fetching latest...")
            result["action"] = "fetch_latest"

            saved_count = await fetch_and_store_income_statements(
                fmp=fmp,
                session=session,
                symbol=symbol,
                period="quarter",
                limit=1  # Fetch only the latest
            )

            result["statements_saved"] = saved_count
            print(f"  {symbol}: Saved {saved_count} income statement(s)")

        else:
            # Data is up to date
            result["action"] = "skip"
            print(f"  {symbol}: Income statements are up to date (last: {last_statement.date})")

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
    print(f"  - Fetched all statements: {results['fetch_all']}")
    print(f"  - Fetched latest statement: {results['fetch_latest']}")
    print(f"  - Already up to date: {results['skip']}")
    print(f"  - Errors: {results['errors']}")
    print(f"Total income statements saved: {results['total_statements']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_income_statements"))
