#!/usr/bin/env python3
"""
Sync Financial Statement Symbol List from FMP

Fetches the list of symbols with available financial statements from
Financial Modeling Prep and upserts them to the database.

This endpoint returns symbols that have at least one type of financial
statement available (income statement, balance sheet, or cash flow statement).

Rate limited to max 2 requests per second to comply with API limits.

This script should be run periodically (e.g., weekly) to keep the
financial statement symbol list up to date.

Usage:
    python -m scripts.sync_financial_statement_symbols

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.other_mappers import map_financial_statement_symbol
from app.mappers.utils import map_and_save


async def main():
    """Sync financial statement symbol list from FMP to database."""

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Fetch financial statement symbol list from FMP
    print("Fetching financial statement symbol list from Financial Modeling Prep...")
    try:
        async with FMPClient(api_key=api_key) as fmp:
            # Get list of symbols with available financial statements
            symbol_list = await fmp.directory.get_financial_statement_symbols()
            print(f"Retrieved {len(symbol_list)} symbols with financial statements from FMP")

            # Map and save to database
            print("Upserting symbols to database...")
            with get_db_session() as session:
                saved_count = map_and_save(
                    session=session,
                    dtos=symbol_list,
                    mapper_func=map_financial_statement_symbol,
                    unique_columns=["symbol"],
                    upsert=True
                )

                print(f"Successfully upserted {saved_count} symbols to database")

        print("Database sync complete!")
    except Exception as e:
        print(f"ERROR: Failed to fetch financial statement symbols from FMP: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_financial_statement_symbols"))
