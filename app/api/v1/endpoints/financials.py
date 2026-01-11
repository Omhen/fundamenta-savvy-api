"""Financial statements domain API endpoints."""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.financial_statements import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
)
from app.schemas.financials import (
    IncomeStatementResponse,
    BalanceSheetResponse,
    CashFlowStatementResponse,
)

router = APIRouter()


# Income Statement endpoints
@router.get("/income-statements/{symbol}", response_model=List[IncomeStatementResponse])
def get_income_statements_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all income statements for a symbol."""
    statements = db.query(IncomeStatement).filter(
        IncomeStatement.symbol == symbol
    ).order_by(IncomeStatement.date.desc()).all()
    return statements


# Balance Sheet endpoints
@router.get("/balance-sheets/{symbol}", response_model=List[BalanceSheetResponse])
def get_balance_sheets_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all balance sheets for a symbol."""
    statements = db.query(BalanceSheet).filter(
        BalanceSheet.symbol == symbol
    ).order_by(BalanceSheet.date.desc()).all()
    return statements


# Cash Flow Statement endpoints
@router.get("/cash-flow-statements/{symbol}", response_model=List[CashFlowStatementResponse])
def get_cash_flow_statements_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get all cash flow statements for a symbol."""
    statements = db.query(CashFlowStatement).filter(
        CashFlowStatement.symbol == symbol
    ).order_by(CashFlowStatement.date.desc()).all()
    return statements
