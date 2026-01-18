from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    company,
    financials,
    prices,
    dividends_earnings,
    economics,
    market,
    sec,
    directory,
    news,
    metrics,
)

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Company domain
api_router.include_router(company.router, prefix="/company", tags=["company"])

# Financial statements domain
api_router.include_router(financials.router, prefix="/financials", tags=["financials"])

# Prices domain
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])

# Dividends and earnings domain
api_router.include_router(dividends_earnings.router, prefix="/dividends-earnings", tags=["dividends-earnings"])

# Economics domain
api_router.include_router(economics.router, prefix="/economics", tags=["economics"])

# Market performance domain
api_router.include_router(market.router, prefix="/market", tags=["market"])

# SEC filings domain
api_router.include_router(sec.router, prefix="/sec", tags=["sec"])

# Directory domain
api_router.include_router(directory.router, prefix="/directory", tags=["directory"])

# News domain
api_router.include_router(news.router, prefix="/news", tags=["news"])

# Metrics domain
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
