"""News domain API endpoints."""

from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.news import (
    FMPArticle,
    GeneralNews,
    StockNews,
)
from app.schemas.news import (
    FMPArticleResponse,
    GeneralNewsResponse,
    StockNewsResponse,
)

router = APIRouter()


# FMP Article endpoints
@router.get("/fmp-articles", response_model=List[FMPArticleResponse])
def list_fmp_articles(
    tickers: Optional[str] = Query(None, description="Filter by tickers"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """List FMP articles."""
    query = db.query(FMPArticle)
    if tickers:
        query = query.filter(FMPArticle.tickers.contains(tickers))
    if from_date:
        query = query.filter(FMPArticle.date >= from_date)
    if to_date:
        query = query.filter(FMPArticle.date <= to_date)
    return query.order_by(FMPArticle.date.desc()).all()


# General News endpoints
@router.get("/general", response_model=List[GeneralNewsResponse])
def list_general_news(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """List general news articles."""
    query = db.query(GeneralNews)
    if symbol:
        query = query.filter(GeneralNews.symbol == symbol)
    if from_date:
        query = query.filter(GeneralNews.date >= from_date)
    if to_date:
        query = query.filter(GeneralNews.date <= to_date)
    return query.order_by(GeneralNews.published_date.desc()).all()


# Stock News endpoints
@router.get("/stock/{symbol}", response_model=List[StockNewsResponse])
def get_stock_news_by_symbol(
    symbol: str,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """Get all stock news for a symbol."""
    query = db.query(StockNews).filter(StockNews.symbol == symbol)
    if from_date:
        query = query.filter(StockNews.published_date >= from_date)
    if to_date:
        query = query.filter(StockNews.published_date <= to_date)
    return query.order_by(StockNews.published_date.desc()).all()


@router.get("/stock", response_model=List[StockNewsResponse])
def list_stock_news(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db)
):
    """List all stock news."""
    query = db.query(StockNews)
    if from_date:
        query = query.filter(StockNews.published_date >= from_date)
    if to_date:
        query = query.filter(StockNews.published_date <= to_date)
    return query.order_by(StockNews.published_date.desc()).all()
