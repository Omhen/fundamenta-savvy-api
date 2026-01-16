#!/usr/bin/env python3
"""
Sync Historical Sector Performance from FMP

This script:
1. Reads the complete list of sectors from the database
2. For each sector, fetches historical sector performance from FMP
3. Stores the data in the SectorPerformance table

Usage:
    python -m scripts.sync_sector_performance --from-date 2024-01-01 --to-date 2024-12-31

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List

from fmpclient import FMPClient
from sqlalchemy.orm import Session

from scripts.base import get_db_session, run_async_script
from app.models.directory import Sector
from app.mappers.other_mappers import map_historical_sector_performance
from app.mappers.utils import map_and_save


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def get_all_sectors(session: Session) -> List[str]:
    """
    Get all sectors from the database.

    Args:
        session: Database session

    Returns:
        List of sector names
    """
    results = session.query(Sector.sector).all()
    return [result.sector for result in results]


async def fetch_and_store_sector_performance(
    fmp: FMPClient,
    sector: str,
    from_date: datetime,
    to_date: datetime,
) -> int:
    """
    Fetch historical sector performance from FMP and store in the database.

    Args:
        fmp: FMP client instance
        sector: Sector name
        from_date: Start date for historical data
        to_date: End date for historical data

    Returns:
        Number of records saved
    """
    try:
        # Fetch historical sector performance from FMP
        performances = await fmp.market_performance.get_historical_sector_performance(
            sector=sector,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
        )

        if not performances:
            return 0

        # Map and save to database
        with get_db_session() as session:
            saved_count = map_and_save(
                session=session,
                dtos=performances,
                mapper_func=map_historical_sector_performance,
                unique_columns=["sector", "date"],
                upsert=True,
            )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch sector performance for {sector}: {e}")
        return 0


async def main():
    """Main script logic."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Sync historical sector performance for all sectors in the database."
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

    # Validate date range
    if from_date > to_date:
        print("ERROR: from-date must be before or equal to to-date", file=sys.stderr)
        sys.exit(1)

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Get all sectors from database
    print("Retrieving sectors from database...")
    with get_db_session() as session:
        sectors = get_all_sectors(session)

    if not sectors:
        print("No sectors found in database. Run sync_sectors first.")
        sys.exit(1)

    print(f"Found {len(sectors)} sectors")
    print(f"Date range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print()

    # Process each sector
    results = {
        "success": 0,
        "no_data": 0,
        "errors": 0,
        "total_records": 0,
    }

    async with FMPClient(api_key=api_key) as fmp:
        for i, sector in enumerate(sectors, 1):
            print(f"[{i}/{len(sectors)}] Processing {sector}...")

            try:
                saved_count = await fetch_and_store_sector_performance(
                    fmp=fmp,
                    sector=sector,
                    from_date=from_date,
                    to_date=to_date,
                )

                if saved_count > 0:
                    results["success"] += 1
                    results["total_records"] += saved_count
                    print(f"  Saved {saved_count} performance records")
                else:
                    results["no_data"] += 1
                    print(f"  No data found")

            except Exception as e:
                print(f"  ERROR: Failed to process {sector}: {e}")
                results["errors"] += 1

    # Print summary
    print()
    print("=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total sectors processed: {len(sectors)}")
    print(f"  - Successful: {results['success']}")
    print(f"  - No data: {results['no_data']}")
    print(f"  - Errors: {results['errors']}")
    print(f"Total performance records saved: {results['total_records']}")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_sector_performance"))
