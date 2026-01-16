#!/usr/bin/env python3
"""
Sync Historical Prices for specified symbols and date range.

This script:
1. Receives from_date, to_date, and a list of symbols as parameters
2. Fetches historical end-of-day price data from FMP for each symbol
3. Saves the data to the database

Usage:
    python -m scripts.sync_historical_prices --from-date 2024-01-01 --to-date 2024-12-31 --symbols AAPL GOOGL MSFT
    python -m scripts.sync_historical_prices --from-date 2024-01-01 --to-date 2024-12-31 --symbols AAPL,GOOGL,MSFT

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.price_mappers import map_historical_price
from app.mappers.utils import map_and_save, parse_date
from scripts.config import AVAILABLE_EXCHANGES, AVAILABLE_INDICES
from scripts.utils import get_symbols_with_financials


def parse_symbols(symbols_arg: List[str]) -> List[str]:
    """
    Parse symbols from command line arguments.

    Handles both space-separated and comma-separated symbols:
    - --symbols AAPL GOOGL MSFT
    - --symbols AAPL,GOOGL,MSFT
    """
    result = []
    for item in symbols_arg:
        # Split by comma in case user provides comma-separated list
        parts = item.split(",")
        for part in parts:
            symbol = part.strip().upper()
            if symbol:
                result.append(symbol)
    return result


async def fetch_and_store_historical_prices(
    fmp: FMPClient,
    symbol: str,
    from_date: datetime,
    to_date: datetime,
) -> int:
    """
    Fetch historical prices from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        symbol: Stock symbol
        from_date: Start date for historical data
        to_date: End date for historical data

    Returns:
        Number of records saved
    """
    try:
        # Fetch historical prices from FMP
        historical_prices = await fmp.prices.get_historical_eod(
            symbol=symbol,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
        )

        if not historical_prices:
            return 0

        # Map and save to database
        with get_db_session() as session:
            saved_count = map_and_save(
                session=session,
                dtos=historical_prices,
                mapper_func=map_historical_price,
                unique_columns=["symbol", "date"],
                upsert=True,
                symbol=symbol,  # Required by map_historical_price
            )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch historical prices for {symbol}: {e}")
        return 0


async def main():
    """Main script logic."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Sync historical prices for specified symbols and date range."
    )
    parser.add_argument(
        "--from-date",
        type=parse_date,
        required=True,
        help="Start date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--to-date",
        type=parse_date,
        required=True,
        help="End date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    from_date = args.from_date
    to_date = args.to_date

    # Get symbols with financial statements
    print(f"Retrieving symbols with financial statements from {AVAILABLE_EXCHANGES}")
    with get_db_session() as session:
        symbols = get_symbols_with_financials(session, exchanges=AVAILABLE_EXCHANGES)
    symbols += AVAILABLE_INDICES

    print(f"Found {len(symbols)} symbols with financial statement availability")

    # Validate date range
    if from_date > to_date:
        print("ERROR: from-date must be before or equal to to-date", file=sys.stderr)
        sys.exit(1)

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    print(f"Syncing historical prices:")
    print(f"  Date range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print(f"  Symbols: {', '.join(symbols)}")
    print()

    # Process each symbol
    results = {
        "success": 0,
        "errors": 0,
        "total_prices": 0,
    }

    async with FMPClient(api_key=api_key) as fmp:
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")

            try:
                saved_count = await fetch_and_store_historical_prices(
                    fmp=fmp,
                    symbol=symbol,
                    from_date=from_date,
                    to_date=to_date,
                )

                if saved_count > 0:
                    results["success"] += 1
                    results["total_prices"] += saved_count
                    print(f"  Saved {saved_count} price records")
                else:
                    print(f"  No data found")

            except Exception as e:
                print(f"  ERROR: Failed to process {symbol}: {e}")
                results["errors"] += 1

    # Print summary
    print()
    print("=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total symbols processed: {len(symbols)}")
    print(f"  - Successful: {results['success']}")
    print(f"  - Errors: {results['errors']}")
    print(f"Total price records saved: {results['total_prices']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_historical_prices"))
