# Scripts Module

This directory contains scripts for periodic tasks and cronjobs.

## Structure

- Each script should be a standalone Python file that can be executed directly
- Scripts should use the database session from `app.db.session`
- Scripts should use the models from `app.models`
- Scripts should use the mappers from `app.mappers`

## Running Scripts

Scripts can be run directly from the command line:

```bash
# From the project root
python -m scripts.script_name

# Or directly
python scripts/script_name.py
```

## Scheduling with Cron

Example crontab entries:

```cron
# Run daily at 2 AM
0 2 * * * cd /path/to/fundamental-savvy-api && python -m scripts.script_name

# Run every hour
0 * * * * cd /path/to/fundamental-savvy-api && python -m scripts.script_name
```

## Docker Execution

To run scripts in Docker:

```bash
docker-compose exec api python -m scripts.script_name
```

## Environment Variables

Scripts will use the same environment variables as the API (from .env or docker-compose.yml).
