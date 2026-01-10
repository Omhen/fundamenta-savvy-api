#!/usr/bin/env python3
"""
Sync Economic Indicators by Date Range

This script fetches economic indicators from FMP for a specified date range
and stores them in the database. It processes one indicator at a time.

Usage:
    python -m scripts.sync_economic_indicators --indicators GDP,unemploymentRate --from-date 2020-01-01 --to-date 2024-12-31

Arguments:
    --indicators   Comma-separated list of indicator names to retrieve
    --from-date    Start date for the query (format: YYYY-MM-DD)
    --to-date      End date for the query (format: YYYY-MM-DD)

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
from app.mappers.other_mappers import map_economic_indicator
from app.mappers.utils import map_and_save

DEFAULT_INDICATORS = ['GDP', 'realGDP', 'nominalPotentialGDP', 'realGDPPerCapita', 'federalFunds', 'CPI', 'inflationRate', 'inflation', 'retailSales', 'consumerSentiment', 'durableGoods', 'unemploymentRate', 'totalNonfarmPayroll', 'initialClaims', 'industrialProductionTotalIndex', 'newPrivatelyOwnedHousingUnitsStartedTotalUnits', 'totalVehicleSales', 'retailMoneyFunds', 'smoothedUSRecessionProbabilities', '3MonthOr90DayRatesAndYieldsCertificatesOfDeposit', 'commercialBankInterestRateOnCreditCardPlansAllAccounts', '30YearFixedRateMortgageAverage', '15YearFixedRateMortgageAverage', 'tradeBalanceGoodsAndServices']


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


def parse_indicators(indicators_string: str) -> List[str]:
    """
    Parse comma-separated indicator names.

    Args:
        indicators_string: Comma-separated indicator names

    Returns:
        List of indicator names

    Raises:
        argparse.ArgumentTypeError: If no valid indicators provided
    """
    indicators = [ind.strip() for ind in indicators_string.split(",") if ind.strip()]
    if not indicators:
        raise argparse.ArgumentTypeError("At least one indicator name is required")
    return indicators


def filter_by_date_range(dtos: list, from_date: str, to_date: str) -> list:
    """
    Filter DTOs by date range.

    Args:
        dtos: List of DTOs with a 'date' attribute
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        Filtered list of DTOs
    """
    return [
        dto for dto in dtos
        if dto.date and from_date <= dto.date <= to_date
    ]


async def fetch_and_store_indicator(
    fmp: FMPClient,
    indicator_name: str,
    from_date: str,
    to_date: str,
) -> int:
    """
    Fetch economic indicator data from FMP and store in the database.

    Args:
        fmp: FMP client instance
        indicator_name: Name of the economic indicator
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)

    Returns:
        Number of records saved
    """
    try:
        # Fetch indicator data from FMP
        print(f"  Fetching data from FMP...")
        indicators = await fmp.economics.get_economic_indicator(name=indicator_name)

        if not indicators:
            print(f"  No data found for indicator '{indicator_name}'")
            return 0

        print(f"  Retrieved {len(indicators)} total records from FMP")

        # Filter by date range
        filtered = filter_by_date_range(indicators, from_date, to_date)
        print(f"  Filtered to {len(filtered)} records within date range")

        if not filtered:
            print(f"  No records within the specified date range")
            return 0

        # Map and save to database
        print(f"  Upserting to database...")
        with get_db_session() as session:
            saved_count = map_and_save(
                session=session,
                dtos=filtered,
                mapper_func=map_economic_indicator,
                unique_columns=["name", "date", "country"],
                upsert=True
            )

        return saved_count

    except Exception as e:
        print(f"  ERROR: Failed to fetch indicator '{indicator_name}': {e}")
        raise


async def main(indicators: List[str], from_date: str, to_date: str):
    """
    Main script logic.

    Args:
        indicators: List of indicator names to fetch
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
    """
    indicators = indicators or DEFAULT_INDICATORS
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
    print("SYNC ECONOMIC INDICATORS")
    print("=" * 60)
    print(f"Indicators: {', '.join(indicators)}")
    print(f"Date range: {from_date} to {to_date}")
    print("=" * 60)

    results = {
        "successful": 0,
        "failed": 0,
        "total_records": 0,
    }

    async with FMPClient(api_key=api_key) as fmp:
        for i, indicator_name in enumerate(indicators, 1):
            print(f"\n[{i}/{len(indicators)}] Processing '{indicator_name}'...")

            try:
                saved_count = await fetch_and_store_indicator(
                    fmp=fmp,
                    indicator_name=indicator_name,
                    from_date=from_date,
                    to_date=to_date,
                )
                results["successful"] += 1
                results["total_records"] += saved_count
                print(f"  Saved {saved_count} records")

            except Exception as e:
                results["failed"] += 1
                print(f"  Failed: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Indicators requested: {len(indicators)}")
    print(f"  - Successful: {results['successful']}")
    print(f"  - Failed: {results['failed']}")
    print(f"Total records saved: {results['total_records']}")
    print("=" * 60)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync economic indicators from FMP for a date range"
    )
    parser.add_argument(
        "--indicators",
        type=parse_indicators,
        required=False,
        help="Comma-separated list of indicator names (e.g., GDP,unemploymentRate)"
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
        await main(
            indicators=args.indicators,
            from_date=args.from_date,
            to_date=args.to_date,
        )

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(run, "sync_economic_indicators"))
