"""Utility functions for batch mapping and database operations."""

from typing import List, TypeVar, Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

T = TypeVar('T')
U = TypeVar('U')


def map_batch(dtos: List[T], mapper_func: Callable[[T], U], **kwargs) -> List[U]:
    """Map a list of DTOs to database models using the provided mapper function.

    Args:
        dtos: List of DTO objects
        mapper_func: Function to map a single DTO to a database model
        **kwargs: Additional keyword arguments to pass to the mapper function

    Returns:
        List of database model instances

    Example:
        >>> from fmpclient.models import company
        >>> from app.mappers.company_mappers import map_company_profile
        >>> dtos = [company.CompanyProfile(...), ...]
        >>> models = map_batch(dtos, map_company_profile)
    """
    return [mapper_func(dto, **kwargs) for dto in dtos]


def bulk_insert_or_update(
    session: Session,
    models: List[T],
    unique_columns: List[str],
) -> None:
    """Bulk insert or update database models.

    Uses PostgreSQL's INSERT ... ON CONFLICT DO UPDATE for efficient upserts.

    Args:
        session: SQLAlchemy session
        models: List of database model instances
        unique_columns: List of column names that form the unique constraint

    Example:
        >>> from app.models import CompanyProfile
        >>> from app.db.session import get_db
        >>> session = next(get_db())
        >>> models = [CompanyProfile(...), ...]
        >>> bulk_insert_or_update(session, models, ["symbol"])
    """
    if not models:
        return

    model_class = type(models[0])
    table = model_class.__table__

    # Convert models to dictionaries, excluding id if None (for auto-increment)
    values = []
    for model in models:
        if hasattr(model, 'dict'):
            model_dict = model.dict()
        else:
            model_dict = {
                c.name: getattr(model, c.name)
                for c in table.columns
                if hasattr(model, c.name)
            }

        # Remove id if it's None to allow auto-increment
        if model_dict.get('id') is None:
            model_dict.pop('id', None)

        values.append(model_dict)

    # Create insert statement
    stmt = insert(table).values(values)

    # Create update dict (all columns except the unique ones and created_at)
    update_dict = {
        c.name: stmt.excluded[c.name]
        for c in table.columns
        if c.name not in unique_columns and c.name != 'created_at' and c.name != 'id'
    }

    # Add ON CONFLICT DO UPDATE clause
    stmt = stmt.on_conflict_do_update(
        index_elements=unique_columns,
        set_=update_dict
    )

    session.execute(stmt)


def bulk_insert_ignore(
    session: Session,
    models: List[T],
    unique_columns: List[str],
) -> None:
    """Bulk insert database models, ignoring conflicts.

    Uses PostgreSQL's INSERT ... ON CONFLICT DO NOTHING for efficient inserts.

    Args:
        session: SQLAlchemy session
        models: List of database model instances
        unique_columns: List of column names that form the unique constraint

    Example:
        >>> from app.models import HistoricalPrice
        >>> from app.db.session import get_db
        >>> session = next(get_db())
        >>> models = [HistoricalPrice(...), ...]
        >>> bulk_insert_ignore(session, models, ["symbol", "date"])
    """
    if not models:
        return

    model_class = type(models[0])
    table = model_class.__table__

    # Convert models to dictionaries, excluding id if None (for auto-increment)
    values = []
    for model in models:
        if hasattr(model, 'dict'):
            model_dict = model.dict()
        else:
            model_dict = {
                c.name: getattr(model, c.name)
                for c in table.columns
                if hasattr(model, c.name)
            }

        # Remove id if it's None to allow auto-increment
        if model_dict.get('id') is None:
            model_dict.pop('id', None)

        values.append(model_dict)

    # Create insert statement with ON CONFLICT DO NOTHING
    stmt = insert(table).values(values).on_conflict_do_nothing(
        index_elements=unique_columns
    )

    session.execute(stmt)


def map_and_save(
    session: Session,
    dtos: List[T],
    mapper_func: Callable[[T], U],
    unique_columns: List[str],
    upsert: bool = True,
    **mapper_kwargs
) -> int:
    """Map DTOs to models and save them to the database.

    Convenience function that combines mapping and database operations.

    Args:
        session: SQLAlchemy session
        dtos: List of DTO objects
        mapper_func: Function to map a single DTO to a database model
        unique_columns: List of column names that form the unique constraint
        upsert: If True, update on conflict; if False, ignore conflicts
        **mapper_kwargs: Additional keyword arguments to pass to the mapper function

    Returns:
        Number of records processed

    Example:
        >>> from fmpclient.models import company
        >>> from app.mappers.company_mappers import map_company_profile
        >>> from app.db.session import get_db
        >>> session = next(get_db())
        >>> dtos = [company.CompanyProfile(...), ...]
        >>> count = map_and_save(session, dtos, map_company_profile, ["symbol"])
        >>> session.commit()
    """
    if not dtos:
        return 0

    models = map_batch(dtos, mapper_func, **mapper_kwargs)

    if upsert:
        bulk_insert_or_update(session, models, unique_columns)
    else:
        bulk_insert_ignore(session, models, unique_columns)

    return len(models)
