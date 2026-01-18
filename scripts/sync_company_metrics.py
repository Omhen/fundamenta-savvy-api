#!/usr/bin/env python3
"""
Sync Company Metrics

This script calculates and stores pre-computed metrics for all companies with
financial statements in the database.

Metrics calculated include:
- Valuation: P/E, P/B, P/S
- Enterprise value: EV/EBITDA, EV/FCF
- Profitability: COPM, ROIC, ROTA
- Leverage: Debt/EBITDA
- Dividends: Yield, Payout, 10Y Growth, Years Increasing

The script:
1. Gets all symbols with financial statements from NYSE/NASDAQ
2. For each symbol, calculates metrics from existing database data
3. Upserts results into the company_metrics table

Usage:
    python -m scripts.sync_company_metrics [--batch-size N]

Arguments:
    --batch-size N    Number of symbols to process before committing (default: 100)
"""

import argparse
import sys
from typing import List

from scripts.base import get_db_session, run_script, setup_logging
from scripts.config import AVAILABLE_EXCHANGES
from scripts.utils import get_symbols_with_financials
from app.mappers.metrics_mappers import calculate_company_metrics
from app.mappers.utils import bulk_insert_or_update


DEFAULT_BATCH_SIZE = 100


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sync company metrics from financial data")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of symbols to process before committing (default: {DEFAULT_BATCH_SIZE})"
    )
    return parser.parse_args()


def process_batch(session, symbols: List[str], logger) -> tuple:
    """
    Process a batch of symbols and return metrics models.

    Returns:
        Tuple of (metrics_list, errors_count)
    """
    metrics_list = []
    errors = 0

    for symbol in symbols:
        try:
            metrics = calculate_company_metrics(symbol, session)
            if metrics:
                metrics_list.append(metrics)
        except Exception as e:
            logger.warning(f"Error calculating metrics for {symbol}: {e}")
            errors += 1

    return metrics_list, errors


def main():
    """Main script logic."""
    args = parse_args()
    logger = setup_logging("sync_company_metrics")

    # Get all symbols with financial statements
    logger.info(f"Retrieving symbols with financial statements from {AVAILABLE_EXCHANGES}")
    with get_db_session() as session:
        symbols = get_symbols_with_financials(session, exchanges=AVAILABLE_EXCHANGES)

    logger.info(f"Found {len(symbols)} symbols to process")

    if not symbols:
        logger.info("No symbols to process. Exiting.")
        return

    total_saved = 0
    total_errors = 0
    batch_size = args.batch_size

    # Process in batches
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} symbols)")

        with get_db_session() as session:
            # Calculate metrics for all symbols in batch
            metrics_list, errors = process_batch(session, batch, logger)
            total_errors += errors

            if metrics_list:
                # Bulk upsert all metrics
                bulk_insert_or_update(
                    session=session,
                    models=metrics_list,
                    unique_columns=["symbol"]
                )
                total_saved += len(metrics_list)
                logger.info(f"  Saved {len(metrics_list)} metrics")

    # Print summary
    logger.info("=" * 60)
    logger.info("SYNC COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total symbols processed: {len(symbols)}")
    logger.info(f"Total metrics saved: {total_saved}")
    logger.info(f"Total errors: {total_errors}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_script(main, "sync_company_metrics")
