#!/usr/bin/env python3
"""
Sync Stock List from FMP

Fetches the complete list of available stocks from Financial Modeling Prep
and upserts them to the database.

Rate limited to max 2 requests per second to comply with API limits.

This script should be run periodically (e.g., daily) to keep the stock
directory up to date.

Usage:
    python -m scripts.sync_stock_list

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.other_mappers import map_stock_symbol
from app.mappers.utils import map_and_save


async def main():
    """Sync stock list from FMP to database."""

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Fetch stock list from FMP
    print("Fetching stock list from Financial Modeling Prep...")
    try:
        async with FMPClient(api_key=api_key) as fmp:
            for query in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                print(f"Querying for {query=}")
                stock_list = await fmp.search.search_symbol(query=query, limit=30_000)
                print(f"Retrieved {len(stock_list)} stocks from FMP")
                await upsert_stock_details(stock_list)
        print("Database sync complete!")
    except Exception as e:
        print(f"ERROR: Failed to fetch stock list from FMP: {e}", file=sys.stderr)
        raise


async def upsert_stock_details(stock_list):
    # Map and save to database
    print("Upserting stocks to database...")
    with get_db_session() as session:
        saved_count = map_and_save(
            session=session,
            dtos=stock_list,
            mapper_func=map_stock_symbol,
            unique_columns=["symbol"],
            upsert=True
        )

        print(f"Successfully upserted {saved_count} stocks to database")


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_stock_list"))
