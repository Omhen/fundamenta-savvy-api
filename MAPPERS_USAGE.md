# Mappers Usage Guide

This document explains how to use the mapper functions to convert FMP client DTOs into database models.

## Overview

The `app/mappers` module provides functions to convert Pydantic DTOs from the `financialmodelingprep-client` package into SQLAlchemy database models for storage in the Fundamental Savvy Database.

## Basic Usage

### Single DTO Mapping

```python
from fmpclient.models import company
from app.mappers.company_mappers import map_company_profile

# Get DTO from FMP client
fmp_dto = company.CompanyProfile(
    symbol="AAPL",
    company_name="Apple Inc.",
    # ... other fields
)

# Convert to database model
db_model = map_company_profile(fmp_dto)

# Save to database
from app.db.session import get_db
session = next(get_db())
session.add(db_model)
session.commit()
```

### Batch Mapping

```python
from fmpclient.models import financial
from app.mappers.financial_mappers import map_income_statement
from app.mappers.utils import map_batch

# Get list of DTOs from FMP client
fmp_dtos = [
    financial.IncomeStatement(...),
    financial.IncomeStatement(...),
    # ...
]

# Convert all to database models
db_models = map_batch(fmp_dtos, map_income_statement)

# Save to database
session.add_all(db_models)
session.commit()
```

### Map and Save in One Step

```python
from fmpclient.models import quote
from app.mappers.price_mappers import map_quote
from app.mappers.utils import map_and_save
from app.db.session import get_db

# Get DTOs
quotes = [quote.Quote(...), quote.Quote(...)]

# Map and save with upsert
session = next(get_db())
count = map_and_save(
    session=session,
    dtos=quotes,
    mapper_func=map_quote,
    unique_columns=["symbol", "timestamp"],
    upsert=True  # Update on conflict
)
session.commit()

print(f"Processed {count} quotes")
```

## Available Mappers

### Company Mappers (`company_mappers`)

- `map_company_profile(dto)` - Company profile information
- `map_executive(dto, symbol)` - Executive data (requires symbol)
- `map_market_capitalization(dto)` - Market cap history
- `map_employee_count(dto)` - Employee count data
- `map_shares_float(dto)` - Shares float data
- `map_delisted_company(dto)` - Delisted company info

### Financial Mappers (`financial_mappers`)

- `map_income_statement(dto)` - Income statement
- `map_balance_sheet(dto)` - Balance sheet
- `map_cash_flow_statement(dto)` - Cash flow statement

### Price Mappers (`price_mappers`)

- `map_quote(dto)` - Real-time quote
- `map_historical_price(dto, symbol)` - Historical price (requires symbol)
- `map_intraday_price(dto, symbol)` - Intraday price (requires symbol)

### Other Mappers (`other_mappers`)

**Directory:**
- `map_stock_symbol(dto)` - Stock symbol
- `map_exchange(dto)` - Exchange info
- `map_sector(dto)` - Sector
- `map_industry(dto)` - Industry
- `map_country(dto)` - Country
- `map_symbol_change(dto)` - Symbol change

**Dividends & Earnings:**
- `map_dividend(dto)` - Dividend
- `map_dividend_calendar_event(dto)` - Dividend calendar
- `map_earnings_report(dto)` - Earnings report
- `map_earnings_calendar_event(dto)` - Earnings calendar

**Economics:**
- `map_treasury_rate(dto)` - Treasury rates
- `map_economic_indicator(dto)` - Economic indicator
- `map_economic_calendar_event(dto)` - Economic calendar
- `map_market_risk_premium(dto)` - Market risk premium

**Market Performance:**
- `map_sector_performance(dto)` - Sector performance
- `map_industry_performance(dto)` - Industry performance
- `map_sector_pe(dto)` - Sector P/E
- `map_industry_pe(dto)` - Industry P/E
- `map_stock_gainer(dto, date)` - Stock gainer (requires date)
- `map_stock_loser(dto, date)` - Stock loser (requires date)
- `map_active_stock(dto, date)` - Active stock (requires date)

**SEC Filings:**
- `map_sec_filing(dto)` - SEC filing

## Utility Functions

### `map_batch(dtos, mapper_func, **kwargs)`

Maps a list of DTOs to database models.

**Parameters:**
- `dtos`: List of DTO objects
- `mapper_func`: Mapper function to use
- `**kwargs`: Additional arguments for the mapper

**Returns:** List of database models

### `bulk_insert_or_update(session, models, unique_columns)`

Bulk insert or update with PostgreSQL upsert.

**Parameters:**
- `session`: SQLAlchemy session
- `models`: List of database models
- `unique_columns`: Columns forming unique constraint

### `bulk_insert_ignore(session, models, unique_columns)`

Bulk insert, ignoring conflicts.

**Parameters:**
- `session`: SQLAlchemy session
- `models`: List of database models
- `unique_columns`: Columns forming unique constraint

### `map_and_save(session, dtos, mapper_func, unique_columns, upsert=True, **mapper_kwargs)`

Map DTOs and save to database in one operation.

**Parameters:**
- `session`: SQLAlchemy session
- `dtos`: List of DTOs
- `mapper_func`: Mapper function
- `unique_columns`: Unique constraint columns
- `upsert`: If True, update on conflict; if False, ignore
- `**mapper_kwargs`: Additional mapper arguments

**Returns:** Number of records processed

## Complete Example: ETL Pipeline

```python
from fmpclient import FMPClient
from app.db.session import get_db
from app.mappers.company_mappers import map_company_profile
from app.mappers.financial_mappers import map_income_statement
from app.mappers.utils import map_and_save

# Initialize FMP client
fmp = FMPClient(api_key="your_api_key")

# Get database session
session = next(get_db())

# Fetch company profiles
symbols = ["AAPL", "GOOGL", "MSFT"]
profiles = []
for symbol in symbols:
    profile = fmp.company.get_profile(symbol)
    if profile:
        profiles.append(profile)

# Save company profiles
profile_count = map_and_save(
    session=session,
    dtos=profiles,
    mapper_func=map_company_profile,
    unique_columns=["symbol"],
    upsert=True
)

# Fetch and save income statements
for symbol in symbols:
    statements = fmp.financial.get_income_statement(symbol, period="annual")
    if statements:
        stmt_count = map_and_save(
            session=session,
            dtos=statements,
            mapper_func=map_income_statement,
            unique_columns=["symbol", "date"],
            upsert=True
        )
        print(f"Saved {stmt_count} income statements for {symbol}")

# Commit all changes
session.commit()
print(f"Total profiles saved: {profile_count}")
```

## Best Practices

1. **Always use transactions**: Wrap database operations in transactions
2. **Use bulk operations**: For large datasets, use `map_and_save` or bulk utilities
3. **Handle errors**: Wrap in try/except and rollback on error
4. **Use upsert for updates**: Set `upsert=True` to update existing records
5. **Verify unique constraints**: Ensure unique_columns match your indexes

## Error Handling

```python
from sqlalchemy.exc import SQLAlchemyError

session = next(get_db())
try:
    count = map_and_save(
        session=session,
        dtos=dtos,
        mapper_func=map_company_profile,
        unique_columns=["symbol"]
    )
    session.commit()
    print(f"Successfully saved {count} records")
except SQLAlchemyError as e:
    session.rollback()
    print(f"Error saving data: {e}")
    raise
finally:
    session.close()
```
