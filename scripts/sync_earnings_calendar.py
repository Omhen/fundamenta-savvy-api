#!/usr/bin/env python3
"""
Sync Earnings Calendar Events by Date Range

This script fetches earnings calendar events from FMP for a specified date range
and stores them in the database.

Usage:
    python -m scripts.sync_earnings_calendar --from-date 2024-01-01 --to-date 2024-12-31

Arguments:
    --from-date    Start date for the query (format: YYYY-MM-DD)
    --to-date      End date for the query (format: YYYY-MM-DD)

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import argparse
import os
import sys
from datetime import datetime

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.other_mappers import map_earnings_calendar_event
from app.mappers.utils import map_and_save


def validate_date(date_string: str) -> str:
    """
    Validate that a string is a valid date in YYYY-MM-DD format.

    Args:
        date_string: Date string to validate

    Returns:
        The validated date string

    Raises:
        argparse.ArgumentTypeError: If the date is invalid
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_string}'. Expected format: YYYY-MM-DD"
        )


async def fetch_and_store_earnings_calendar(
    fmp: FMPClient,
    from_date: str,
    to_date: str,
) -> int:
    """
    Fetch earnings calendar events from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        Number of events saved
    """
    try:
        # Fetch earnings calendar events from FMP
        print(f"Fetching earnings calendar events from {from_date} to {to_date}...")
        events = await fmp.earnings.get_earnings_calendar(
            from_date=from_date,
            to_date=to_date,
        )

        if not events:
            print("No earnings calendar events found for the specified date range.")
            return 0

        print(f"Retrieved {len(events)} earnings calendar events from FMP")

        # Map and save to database
        print("Upserting events to database...")
        with get_db_session() as session:
            saved_count = map_and_save(
                session=session,
                dtos=events,
                mapper_func=map_earnings_calendar_event,
                unique_columns=["symbol", "date"],
                upsert=True
            )

        return saved_count

    except Exception as e:
        print(f"ERROR: Failed to fetch earnings calendar events: {e}")
        raise


async def main(from_date: str, to_date: str):
    """
    Main script logic.

    Args:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
    """
    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Validate date range
    if from_date > to_date:
        print("ERROR: from_date must be before or equal to to_date", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("SYNC EARNINGS CALENDAR BY DATE RANGE")
    print("=" * 60)
    print(f"Date range: {from_date} to {to_date}")
    print("=" * 60)

    async with FMPClient(api_key=api_key) as fmp:
        saved_count = await fetch_and_store_earnings_calendar(
            fmp=fmp,
            from_date=from_date,
            to_date=to_date,
        )

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Date range: {from_date} to {to_date}")
    print(f"Total earnings calendar events saved: {saved_count}")
    print("=" * 60)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync earnings calendar events from FMP for a date range"
    )
    parser.add_argument(
        "--from-date",
        type=validate_date,
        required=True,
        help="Start date for the query (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to-date",
        type=validate_date,
        required=True,
        help="End date for the query (format: YYYY-MM-DD)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    import asyncio

    args = parse_args()

    async def run():
        await main(from_date=args.from_date, to_date=args.to_date)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(run, "sync_earnings_calendar"))
