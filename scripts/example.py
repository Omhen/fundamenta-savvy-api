#!/usr/bin/env python3
"""
Example script demonstrating how to create periodic tasks.

This script shows best practices for:
- Database session management
- Logging
- Error handling
- Using the FMP client
- Using mappers to save data
"""

from scripts.base import get_db_session, run_script


def main():
    """Main script logic."""

    # Example 1: Simple database query
    with get_db_session() as session:
        from app.models.company_profile import CompanyProfile

        # Query example
        count = session.query(CompanyProfile).count()
        print(f"Total companies in database: {count}")

    # Example 2: Fetch data from FMP and save to database
    # Uncomment and modify as needed:
    """
    from fmpclient import FMPClient
    from app.mappers.company_mappers import map_company_profile
    from app.mappers.utils import map_and_save

    fmp = FMPClient(api_key="YOUR_API_KEY")

    with get_db_session() as session:
        # Fetch company profiles
        profiles = fmp.company.get_profile("AAPL,GOOGL,MSFT")

        # Map and save to database
        saved_count = map_and_save(
            session=session,
            dtos=profiles,
            mapper_func=map_company_profile,
            unique_columns=["symbol"],
            upsert=True
        )

        print(f"Saved {saved_count} company profiles")
    """


if __name__ == "__main__":
    run_script(main, "example_script")
