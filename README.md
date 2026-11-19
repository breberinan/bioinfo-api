# Bioinformatics Variant API

FastAPI + PostgreSQL backend for managing bioinformatics projects. Later weeks will add VCF uploads, parsed variants and annotations.

## Stack

- Python 3.13, FastAPI, Pydantic v2
- PostgreSQL 16, SQLAlchemy 2.0 (async, asyncpg), Alembic
- Poetry, Docker / Docker Compose
- Ruff, pre-commit, pytest, GitHub Actions

## Project structure

```
app/
  api/routes/     # route handlers
  core/           # settings
  db/             # declarative base, async session
  models/         # SQLAlchemy models
  schemas/        # Pydantic schemas
  services/       # business logic
  main.py         # FastAPI app
alembic/          # migrations
tests/
```

## Quick start (Docker)

```bash
docker compose up --build
```

The API is at http://localhost:8000 and the interactive docs at http://localhost:8000/docs. Migrations run automatically on startup.

## Local development (without Docker for the API)

```bash
# 1. Install dependencies
poetry install

# 2. Start only the database
docker compose up -d db

# 3. Configure environment
cp .env.example .env

# 4. Apply migrations
poetry run alembic upgrade head

# 5. Run the API
poetry run uvicorn app.main:app --reload
```

## Tests

Tests use an in-memory SQLite database, so no Postgres is needed:

```bash
poetry run pytest
```

Coverage is measured automatically and the run fails if line coverage drops below 80%. Each test gets its own fresh database, so tests are fast, independent and repeatable (FIRST principles).

## Linting and formatting

```bash
poetry run ruff check .
poetry run ruff format .
```

Install the git hooks once (ruff, trailing whitespace, end-of-file fixer):

```bash
poetry run pre-commit install
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/projects/` | Create a project (201) |
| GET | `/projects/` | List projects (`skip`, `limit` query params) |
| DELETE | `/projects/{project_id}/` | Delete a project (204, or 404 if missing) |
| GET | `/health` | Health check |

## Migrations

```bash
poetry run alembic revision --autogenerate -m "describe change"
poetry run alembic upgrade head
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs ruff lint, ruff format check and pytest on every push and pull request.

## Logging

Logs go to stdout in one format: `time | level | module | message`. Set `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR) in `.env` or `docker-compose.yml`.

- DEBUG: query details (pagination values, number of rows found)
- INFO: each HTTP request (method, path, status, duration), project created or deleted
- WARNING: deleting a project that does not exist
- ERROR: database failures (with stack trace, after a rollback)

Only IDs are logged. Project names and descriptions are never written to logs.

## Design notes

- **Layers, one job each (SRP):** routes handle HTTP, services hold the logic, models describe tables, schemas validate data.
- **Dependency injection:** the database session is injected into routes with FastAPI `Depends`, so tests can swap in a test database without touching the code.
- **DRY / KISS:** one `_commit` helper handles commit, rollback and error logging; settings come from one `Settings` class.
