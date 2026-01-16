#!/usr/bin/env python3
"""
Sync Company Profiles for NYSE and NASDAQ Stocks

This script:
1. Retrieves all StockSymbol records where exchange_short_name is NYSE or NASDAQ
2. Joins with FinancialStatementSymbol to ensure the symbol has financial data
3. Fetches company profiles from FMP in configurable batch sizes
4. Upserts company profiles to the database

Rate limited to comply with API limits.

Usage:
    python -m scripts.sync_company_profiles [--batch-size N]

Arguments:
    --batch-size N    Number of symbols to fetch per API call (default: 50)

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys
from typing import List

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.company_mappers import map_company_profile
from app.mappers.utils import map_and_save


# Default batch size for fetching profiles
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials

DEFAULT_BATCH_SIZE = 50


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def fetch_and_store_profiles(
    fmp: FMPClient,
    symbol: str,
) -> int:
    """
    Fetch company profiles from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        symbol: stock symbol to fetch

    Returns:
        Number of profiles saved
    """
    if not symbol:
        return 0

    try:
        # Fetch company profiles from FMP (comma-separated symbols)
        profile = await fmp.company.get_profile(symbol)

        if not profile:
            return 0

        # Map and save to database
        with get_db_session() as session:
            saved_count = map_and_save(
                session=session,
                dtos=[profile],
                mapper_func=map_company_profile,
                unique_columns=["symbol"],
                upsert=True
            )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch profiles: {e}")
        return 0


async def main():
    """
    Main script logic.
    """

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get NYSE and NASDAQ symbols with financial statements
    print(f"Retrieving symbols with financial statements from {AVAILABLE_EXCHANGES}")
    with get_db_session() as session:
        symbols = get_symbols_with_financials(session, exchanges=AVAILABLE_EXCHANGES)

    print(f"Found {len(symbols)} symbols with financial statement availability")

    if not symbols:
        print("No symbols to process. Exiting.")
        return

    total_saved = 0
    errors = 0

    async with FMPClient(api_key=api_key) as fmp:
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[Symbol {i}/{len(symbols)}] Processing {len(symbols)} symbols...")

            try:
                saved_count = await fetch_and_store_profiles(fmp, symbol)
                total_saved += saved_count
                print(f"  Saved {saved_count} company profiles")

            except Exception as e:
                print(f"  ERROR: Failed to process batch: {e}")
                errors += 1

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total symbols processed: {len(symbols)}")
    print(f"Batches with errors: {errors}")
    print(f"Total company profiles saved: {total_saved}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_company_profiles"))
