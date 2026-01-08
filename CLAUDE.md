# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI-based REST API for the Fundamental Savvy Database. The API provides financial data from the Financial Modeling Prep (FMP) API, using SQLAlchemy ORM with PostgreSQL and Alembic for migrations.

## Development Commands

### Running the Application

**With Docker (recommended):**
```bash
docker-compose up -d
docker-compose logs -f api
```

**Without Docker:**
```bash
# Ensure virtual environment is activated
uvicorn app.main:app --reload
```

API available at:
- Main: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# With Docker
docker-compose exec api alembic revision --autogenerate -m "Description"
docker-compose exec api alembic upgrade head
```

### Scripts

Scripts for ETL and periodic tasks are located in `scripts/`. Run them with:

```bash
python -m scripts.script_name
```

Scripts use the base utilities from `scripts/base.py` which provides:
- `get_db_session()` - Context manager for database sessions
- `run_script()` - Wrapper with logging and error handling
- `RateLimiter` - Rate limiter for API calls

See `scripts/example.py` for template.

## Architecture

### Project Structure

```
app/
├── api/v1/endpoints/    # API endpoint definitions
├── core/                # Configuration (settings from .env)
├── db/                  # Database session and base classes
├── models/              # SQLAlchemy ORM models (organized by domain)
├── schemas/             # Pydantic schemas for validation
├── mappers/             # DTO-to-ORM mappers for FMP client
└── main.py              # FastAPI application entry point

alembic/                 # Database migrations
scripts/                 # ETL and periodic task scripts
```

### Key Components

**Configuration**: Settings loaded via `pydantic-settings` from `.env` file (see `app/core/config.py`)

**Database Session**:
- `SessionLocal` from `app/db/session.py` creates sessions
- `get_db()` is FastAPI dependency for endpoints
- For scripts, use `get_db_session()` from `scripts/base.py`

**Models**: All SQLAlchemy models inherit from `BaseModel` (in `app/db/base_class.py`), which:
- Auto-generates table names from class names
- Provides a `.dict()` method for serialization
- Inherits from declarative `Base`

**Model Organization** (`app/models/`):
- `company_profile.py` - Company data, executives, market cap, employees
- `financial_statements.py` - Income statement, balance sheet, cash flow
- `quotes_prices.py` - Real-time quotes, historical prices, intraday data
- `dividends_earnings.py` - Dividend data and earnings reports
- `economics.py` - Treasury rates, economic indicators
- `market_performance.py` - Sector/industry performance, gainers/losers
- `sec_filings.py` - SEC filing records
- `directory.py` - Reference tables (symbols, exchanges, sectors, industries)

**Mappers** (`app/mappers/`): Convert FMP client DTOs to SQLAlchemy models
- Organized by domain: `company_mappers.py`, `financial_mappers.py`, `price_mappers.py`, `other_mappers.py`
- Use `map_and_save()` from `utils.py` for batch operations with upsert support

### FMP Client Integration

The project uses a custom FMP client package (`fmpclient`) from a private GitHub repository. Key usage patterns:

```python
from fmpclient import FMPClient
from app.mappers.company_mappers import map_company_profile
from app.mappers.utils import map_and_save

fmp = FMPClient(api_key="YOUR_KEY")
profiles = fmp.company.get_profile("AAPL,GOOGL,MSFT")

with get_db_session() as session:
    count = map_and_save(
        session=session,
        dtos=profiles,
        mapper_func=map_company_profile,
        unique_columns=["symbol"],
        upsert=True
    )
```

### Database Operations

**Bulk Operations** (from `app/mappers/utils.py`):
- `bulk_insert_or_update()` - PostgreSQL upsert (INSERT ... ON CONFLICT DO UPDATE)
- `bulk_insert_ignore()` - Insert with conflict ignore (INSERT ... ON CONFLICT DO NOTHING)
- `map_and_save()` - Convenience function combining mapping and bulk operations

**Migration Best Practices**:
- Import all models in `alembic/env.py` (already done with `from app.models import *`)
- Alembic automatically reads `DATABASE_URL` from settings
- Use `--autogenerate` to detect model changes

### API Structure

**Routing**: Routes are registered in `app/api/v1/__init__.py` using FastAPI's `APIRouter`
- All routes prefixed with `/api/v1` (configured in `app/core/config.py`)
- Endpoints organized in `app/api/v1/endpoints/`

**Current Endpoints**:
- `/api/v1/health` - Health check

## Development Patterns

### Creating a New Script

1. Create file in `scripts/` directory
2. Import base utilities: `from scripts.base import get_db_session, run_script`
3. Define `main()` function with your logic
4. Use `get_db_session()` context manager for database access
5. Call `run_script(main, "script_name")` in `if __name__ == "__main__"`

### Creating a New Endpoint

1. Create file in `app/api/v1/endpoints/`
2. Define `APIRouter()` instance
3. Create endpoint functions with appropriate decorators
4. Register router in `app/api/v1/__init__.py`

### Adding a New Model

1. Create model class in appropriate file in `app/models/`
2. Inherit from `BaseModel`
3. Add imports to `app/models/__init__.py`
4. Create mapper function in appropriate file in `app/mappers/`
5. Generate migration: `alembic revision --autogenerate -m "Add YourModel"`
6. Review and apply: `alembic upgrade head`

## Environment Variables

Required in `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/fundamental_savvy
ENVIRONMENT=development
```

See `.env.example` for template.

## Docker Notes

Docker Compose includes:
- `api` service - FastAPI application with hot reload
- `db` service - PostgreSQL 15 with health checks
- Volume mounts for `app/` and `alembic/` directories for development
- SSH key forwarding for private FMP client repository access

The Docker setup requires SSH key at `../../.ssh/id_ed25519_github` for installing the private FMP client package.
