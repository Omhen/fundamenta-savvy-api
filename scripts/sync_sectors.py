#!/usr/bin/env python3
"""
Sync Sector List from FMP

Fetches the complete list of available sectors from Financial Modeling Prep
and upserts them to the database.

Usage:
    python -m scripts.sync_sectors

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import os
import sys

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.other_mappers import map_sector
from app.mappers.utils import map_and_save


async def main():
    """Sync sector list from FMP to database."""

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Fetch sector list from FMP
    print("Fetching sector list from Financial Modeling Prep...")
    try:
        async with FMPClient(api_key=api_key) as fmp:
            sectors = await fmp.directory.get_available_sectors()
            print(f"Retrieved {len(sectors)} sectors from FMP")

            if not sectors:
                print("No sectors found. Exiting.")
                return

            # Map and save to database
            print("Upserting sectors to database...")
            with get_db_session() as session:
                saved_count = map_and_save(
                    session=session,
                    dtos=sectors,
                    mapper_func=map_sector,
                    unique_columns=["sector"],
                    upsert=False,
                )

            print(f"Successfully upserted {saved_count} sectors to database")

    except Exception as e:
        print(f"ERROR: Failed to fetch sector list from FMP: {e}", file=sys.stderr)
        raise

    # Print summary
    print()
    print("=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total sectors saved: {saved_count}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_sectors"))
