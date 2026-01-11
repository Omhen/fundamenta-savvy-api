from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.base_class import BaseModel


class FMPArticle(BaseModel):
    """FMP-published article data."""

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    content = Column(Text, nullable=False)
    tickers = Column(String, nullable=True)
    image = Column(String, nullable=True)
    link = Column(String, nullable=True)
    author = Column(String, nullable=True)
    site = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_fmparticle_link_date', 'link', 'date', unique=True),
        Index('idx_fmparticle_tickers', 'tickers'),
    )


class GeneralNews(BaseModel):
    """General news article from various sources."""

    id = Column(Integer, primary_key=True, index=True)
    published_date = Column(DateTime, index=True, nullable=False)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    publisher = Column(String, nullable=True)
    symbol = Column(String, index=True, nullable=True)
    site = Column(String, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_generalnews_url', 'url', unique=True),
    )


class StockNews(BaseModel):
    """Stock-specific news article."""

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=True)
    published_date = Column(DateTime, index=True, nullable=False)
    publisher = Column(String, nullable=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    site = Column(String, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_stocknews_url', 'symbol', 'url', unique=True),
        Index('idx_stocknews_symbol_date', 'symbol', 'published_date'),
    )
