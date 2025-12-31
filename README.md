# Fundamental Savvy API

FastAPI-based REST API interface for the Fundamental Savvy Database, built with SQLAlchemy ORM.

## Features

- FastAPI framework with automatic API documentation
- SQLAlchemy ORM for database operations
- Alembic for database migrations
- Pydantic for data validation
- Example CRUD endpoints for Companies
- Health check endpoint

## Requirements

- Python 3.11 or higher
- PostgreSQL database
- Docker and Docker Compose (optional)

## Installation

### Option 1: Using Docker (Recommended)

The easiest way to run the application is using Docker Compose, which sets up both the API and PostgreSQL database:

```bash
# Start the services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic revision --autogenerate -m "Initial migration"
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f api
```

The API will be available at:
- Main endpoint: http://localhost:8000
- API documentation: http://localhost:8000/api/v1/docs
- Alternative docs: http://localhost:8000/api/v1/redoc

To stop the services:
```bash
docker-compose down
```

### Option 2: Manual Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and configure your database connection:
```
DATABASE_URL=postgresql://user:password@localhost:5432/fundamental_savvy
```

5. Initialize the database with Alembic:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Application

### With Docker
```bash
docker-compose up -d
```

### Without Docker
Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- Main endpoint: http://localhost:8000
- API documentation: http://localhost:8000/api/v1/docs
- Alternative docs: http://localhost:8000/api/v1/redoc

## Docker Commands

Build the image:
```bash
docker build -t fundamental-savvy-api .
```

Run the container:
```bash
docker run -p 8000:8000 --env-file .env fundamental-savvy-api
```

Using Docker Compose (includes PostgreSQL):
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Project Structure

```
fundamental-savvy-api/
├── alembic/              # Database migrations
│   └── versions/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/  # API endpoints
│   ├── core/             # Core configuration
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI application
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check API and database status

### Companies
- `GET /api/v1/companies` - List all companies
- `GET /api/v1/companies/{id}` - Get company by ID
- `GET /api/v1/companies/ticker/{ticker}` - Get company by ticker
- `POST /api/v1/companies` - Create a new company
- `PUT /api/v1/companies/{id}` - Update a company
- `DELETE /api/v1/companies/{id}` - Delete a company

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## Development

The project uses:
- **FastAPI** for the web framework
- **SQLAlchemy 2.0** for ORM
- **Pydantic v2** for data validation
- **Alembic** for database migrations
- **Uvicorn** as the ASGI server

## License

MIT
