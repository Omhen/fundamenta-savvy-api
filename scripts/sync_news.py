#!/usr/bin/env python3
"""
Sync News from FMP

This script fetches news articles from FMP (FMP articles, general news, and stock news)
and stores them in the database.

Usage:
    python -m scripts.sync_news
    python -m scripts.sync_news --from-date 2024-01-01 --to-date 2024-12-31
    python -m scripts.sync_news --page 0 --limit 100

Arguments:
    --from-date    Start date for general/stock news (format: YYYY-MM-DD, optional)
    --to-date      End date for general/stock news (format: YYYY-MM-DD, optional)
    --page         Page number for pagination (default: 0)
    --limit        Results per page (default: 50, max: 250 for general/stock news)

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import argparse
import os
import sys
from datetime import datetime

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script
from app.mappers.other_mappers import (
    map_fmp_article,
    map_general_news,
    map_stock_news,
)
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


async def fetch_and_store_fmp_articles(
    fmp: FMPClient,
    page: int,
    limit: int,
) -> int:
    """
    Fetch FMP articles and store them in the database.

    Args:
        fmp: FMP client instance
        page: Page number for pagination
        limit: Results per page

    Returns:
        Number of articles saved
    """
    print(f"Fetching FMP articles (page={page}, limit={limit})...")
    articles = await fmp.news.get_fmp_articles(page=page, limit=limit)

    if not articles:
        print("No FMP articles found.")
        return 0

    print(f"Retrieved {len(articles)} FMP articles")

    with get_db_session() as session:
        saved_count = map_and_save(
            session=session,
            dtos=articles,
            mapper_func=map_fmp_article,
            unique_columns=["link", "date"],
            upsert=True
        )

    return saved_count


async def fetch_and_store_general_news(
    fmp: FMPClient,
    from_date: str | None,
    to_date: str | None,
    page: int,
    limit: int,
) -> int:
    """
    Fetch general news and store them in the database.

    Args:
        fmp: FMP client instance
        from_date: Start date (YYYY-MM-DD) or None
        to_date: End date (YYYY-MM-DD) or None
        page: Page number for pagination
        limit: Results per page

    Returns:
        Number of articles saved
    """

    print(f"Fetching general news (page={page}, limit={limit})...")
    articles = await fmp.news.get_general_news(
        from_date=None,  # Premium Feature
        to_date=None,  # Preimium Feature
        page=page,
        limit=limit,
    )

    if not articles:
        print("No general news found.")
        return 0

    print(f"Retrieved {len(articles)} general news articles")

    with get_db_session() as session:
        saved_count = map_and_save(
            session=session,
            dtos=articles,
            mapper_func=map_general_news,
            unique_columns=["url"],
            upsert=True
        )

    return saved_count


async def fetch_and_store_stock_news(
    fmp: FMPClient,
    from_date: str | None,
    to_date: str | None,
    page: int,
    limit: int,
) -> int:
    """
    Fetch stock news and store them in the database.

    Args:
        fmp: FMP client instance
        from_date: Start date (YYYY-MM-DD) or None
        to_date: End date (YYYY-MM-DD) or None
        page: Page number for pagination
        limit: Results per page

    Returns:
        Number of articles saved
    """

    print(f"Fetching stock news (page={page}, limit={limit})...")
    articles = await fmp.news.get_stock_news(
        from_date=None,  # Premium Feature
        to_date=None,  # Preimium Feature
        page=page,
        limit=limit,
    )

    if not articles:
        print("No stock news found.")
        return 0

    print(f"Retrieved {len(articles)} stock news articles")

    with get_db_session() as session:
        saved_count = map_and_save(
            session=session,
            dtos=articles,
            mapper_func=map_stock_news,
            unique_columns=["symbol", "url"],
            upsert=True
        )

    return saved_count


async def main(
    from_date: str | None,
    to_date: str | None,
    page: int,
    limit: int,
):
    """
    Main script logic.

    Args:
        from_date: Start date (YYYY-MM-DD) or None
        to_date: End date (YYYY-MM-DD) or None
        page: Page number for pagination
        limit: Results per page
    """
    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("ERROR: FMP_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Validate date range if both provided
    if from_date and to_date and from_date > to_date:
        print("ERROR: from_date must be before or equal to to_date", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("SYNC NEWS")
    print("=" * 60)
    if from_date or to_date:
        print(f"Date range: {from_date or 'N/A'} to {to_date or 'N/A'}")
    print(f"Page: {page}, Limit: {limit}")
    print("=" * 60)

    fmp_articles_count = 0
    general_news_count = 0
    stock_news_count = 0

    async with FMPClient(api_key=api_key) as fmp:
        # Fetch FMP articles (no date filtering available)
        try:
            fmp_articles_count = await fetch_and_store_fmp_articles(
                fmp=fmp,
                page=page,
                limit=limit,
            )
        except Exception as e:
            print(f"ERROR: Failed to fetch FMP articles: {e}")

        print("-" * 60)

        # Fetch general news
        try:
            general_news_count = await fetch_and_store_general_news(
                fmp=fmp,
                from_date=from_date,
                to_date=to_date,
                page=page,
                limit=limit,
            )
        except Exception as e:
            print(f"ERROR: Failed to fetch general news: {e}")

        print("-" * 60)

        # Fetch stock news
        try:
            stock_news_count = await fetch_and_store_stock_news(
                fmp=fmp,
                from_date=from_date,
                to_date=to_date,
                page=page,
                limit=limit,
            )
        except Exception as e:
            print(f"ERROR: Failed to fetch stock news: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"FMP articles saved:    {fmp_articles_count}")
    print(f"General news saved:    {general_news_count}")
    print(f"Stock news saved:      {stock_news_count}")
    print(f"Total articles saved:  {fmp_articles_count + general_news_count + stock_news_count}")
    print("=" * 60)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync news from FMP (FMP articles, general news, stock news)"
    )
    parser.add_argument(
        "--from-date",
        type=validate_date,
        required=False,
        default=None,
        help="Start date for general/stock news (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to-date",
        type=validate_date,
        required=False,
        default=None,
        help="End date for general/stock news (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--page",
        type=int,
        required=False,
        default=0,
        help="Page number for pagination (default: 0)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        required=False,
        default=250,
        help="Results per page (default: 50, max: 250 for general/stock news)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    import asyncio

    args = parse_args()

    async def run():
        await main(
            from_date=args.from_date,
            to_date=args.to_date,
            page=args.page,
            limit=args.limit,
        )

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(run, "sync_news"))
