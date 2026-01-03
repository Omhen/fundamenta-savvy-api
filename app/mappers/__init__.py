"""Mappers for converting FMP client DTOs to database models.

This module provides mapper functions to convert Pydantic DTOs from the
financialmodelingprep-client package into SQLAlchemy database models.

Usage:
    from app.mappers import company_mappers, financial_mappers
    from app.mappers.utils import map_batch, map_and_save

    # Map a single DTO
    db_model = company_mappers.map_company_profile(fmp_dto)

    # Map a batch of DTOs
    db_models = map_batch(fmp_dtos, company_mappers.map_company_profile)

    # Map and save to database
    count = map_and_save(
        session=db_session,
        dtos=fmp_dtos,
        mapper_func=company_mappers.map_company_profile,
        unique_columns=["symbol"]
    )
"""

from app.mappers import (
    company_mappers,
    financial_mappers,
    price_mappers,
    other_mappers,
    utils,
)

__all__ = [
    "company_mappers",
    "financial_mappers",
    "price_mappers",
    "other_mappers",
    "utils",
]
