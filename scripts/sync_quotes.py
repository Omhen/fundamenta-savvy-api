#!/usr/bin/env python3
"""
Sync Quotes for NYSE and NASDAQ Stocks

This script:
1. Retrieves all StockSymbol records where exchange_short_name is NYSE or NASDAQ
2. Joins with FinancialStatementSymbol to ensure the symbol has financial data
3. Fetches quotes from FMP in configurable batch sizes
4. Upserts quotes to the database

Rate limited to comply with API limits.

Usage:
    python -m scripts.sync_quotes [--batch-size N]

Arguments:
    --batch-size N    Number of symbols to fetch per API call (default: 50)

Environment Variables:
    FMP_API_KEY: Financial Modeling Prep API key (required)
"""

import argparse
import os
import sys
from typing import List

from fmpclient import FMPClient

from scripts.base import get_db_session, run_async_script, setup_logging
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials
from app.mappers.price_mappers import map_quote
from app.mappers.utils import map_and_save


DEFAULT_BATCH_SIZE = 50


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sync stock quotes from FMP")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of symbols to fetch per API call (default: {DEFAULT_BATCH_SIZE})"
    )
    return parser.parse_args()


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def fetch_and_store_quotes(
    fmp: FMPClient,
    symbols: List[str],
    logger
) -> int:
    """
    Fetch quotes from FMP and store them in the database.

    Args:
        fmp: FMP client instance
        symbols: List of stock symbols to fetch
        logger: Logger instance

    Returns:
        Number of quotes saved
    """
    if not symbols:
        return 0

    try:
        saved_count = 0
        for symbol in symbols:
            quotes = None
            try:
                quotes = await fmp.quotes.get_quote(symbol)
            except Exception as ex:
                import pdb;pdb.set_trace()
                raise ex

            if not quotes:
                return 0

            # Handle both single quote and list of quotes
            if not isinstance(quotes, list):
                quotes = [quotes]

            # Map and save to database
            with get_db_session() as session:
                saved_count += map_and_save(
                    session=session,
                    dtos=quotes,
                    mapper_func=map_quote,
                    unique_columns=["symbol", "timestamp"],
                    upsert=True
                )

        return saved_count

    except Exception as e:
        logger.error(f"Failed to fetch quotes: {e}")
        return 0


async def main():
    """Main script logic."""
    args = parse_args()
    logger = setup_logging("sync_quotes")

    # Get API key from environment
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY environment variable not set")
        sys.exit(1)

    # Get NYSE and NASDAQ symbols with financial statements
    logger.info(f"Retrieving symbols with financial statements from {AVAILABLE_EXCHANGES}")
    with get_db_session() as session:
        symbols = get_symbols_with_financials(session, exchanges=AVAILABLE_EXCHANGES)

    logger.info(f"Found {len(symbols)} symbols with financial statement availability")

    if not symbols:
        logger.info("No symbols to process. Exiting.")
        return

    # Split symbols into batches
    batches = chunk_list(symbols, args.batch_size)
    total_saved = 0
    errors = 0

    async with FMPClient(api_key=api_key, rate_limit=120) as fmp:
        for i, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {i}/{len(batches)} ({len(batch)} symbols)")

            try:
                saved_count = await fetch_and_store_quotes(fmp, batch, logger)
                total_saved += saved_count
                logger.info(f"  Saved {saved_count} quotes")

            except Exception as e:
                logger.error(f"Failed to process batch: {e}")
                errors += 1

    # Print summary
    logger.info("=" * 60)
    logger.info("SYNC COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total symbols processed: {len(symbols)}")
    logger.info(f"Total batches: {len(batches)}")
    logger.info(f"Batches with errors: {errors}")
    logger.info(f"Total quotes saved: {total_saved}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_async_script(main, "sync_quotes"))
