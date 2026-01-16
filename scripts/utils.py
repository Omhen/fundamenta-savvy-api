from typing import List

from sqlalchemy.orm import Session

from app.models import StockSymbol, FinancialStatementSymbol


def get_symbols_with_financials(session: Session, exchanges: List[str] = None) -> List[str]:
    """
    Get all symbols that are:
    - Listed on specified exchanges (from StockSymbol)
    - Have financial statements available (from FinancialStatementSymbol)

    Args:
        session: Database session
        exchanges: List of exchange short names (default: ["NYSE", "NASDAQ"])

    Returns:
        List of stock symbols
    """
    exchanges = exchanges or ["NYSE", "NASDAQ"]

    results = (
        session.query(StockSymbol.symbol)
        .join(
            FinancialStatementSymbol,
            StockSymbol.symbol == FinancialStatementSymbol.symbol
        )
        .filter(StockSymbol.exchange_short_name.in_(exchanges))
        .all()
    )

    return [result.symbol for result in results]
