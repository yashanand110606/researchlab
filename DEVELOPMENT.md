# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (for Celery background processing)
- Docker Compose (optional, for containerized development)

## Project Structure

```
ResearchLab/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── core/               # Config, logging, exceptions
│   │   ├── db/                 # Models, session, repositories
│   │   ├── experiments/        # Registry, base class, runners
│   │   ├── metrics/            # Metrics service
│   │   ├── datasets/           # Dataset storage
│   │   ├── schemas/            # Pydantic models
│   │   ├── services/           # Business logic
│   │   └── workers/            # Celery tasks
│   ├── alembic/              # Migrations
│   ├── tests/                # Test suite
│   ├── pyproject.toml        # Dependencies
│   └── Dockerfile
├── frontend/                # React + TypeScript
│   ├── src/
│   │   ├── components/       # Reusable UI
│   │   ├── pages/            # Route components
│   │   ├── lib/              # API client, utils
│   │   └── schemas/          # TypeScript types
│   ├── public/               # Static assets
│   └── package.json
├── scripts/                 # Dev helpers
├── .env.example             # Environment template
└── docker-compose.yml       # Container orchestration
```

## Local Development Setup

### Option A: Direct Installation

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Frontend
cd ../frontend
npm install

# Database
createdb researchlab
alembic upgrade head

# Start services
uvicorn app.main:app --reload  # Terminal 1
npm run dev                    # Terminal 2
```

### Option B: Docker Compose

```bash
docker-compose up -d
docker-compose ps  # Verify all services running
```

Access at http://localhost:5173 (frontend) and http://localhost:8000/docs (API).

## Adding a New Experiment Type

1. Create `backend/app/experiments/my_experiment.py`:

```python
from app.experiments.base import BaseExperiment, ExperimentContext

class MyExperiment(BaseExperiment):
    type_name = "my_experiment"
    
    def validate_config(self, config: dict) -> list[str]:
        errors = []
        # Add validation logic here
        return errors
    
    def execute(self, ctx: ExperimentContext) -> dict:
        # Implement scientific computation
        ctx.log("INFO", "Starting my experiment")
        results = {...}
        return results
```

2. Register in `registry.py`:

```python
from app.experiments.my_experiment import MyExperiment
register_experimentaliment_class(MyExperiment)
```

3. Add tests in `tests/test_scientific.py`.

## Running Tests

```bash
# Backend (all tests)
cd backend
pytest tests/ -v

# Backend (specific test file)
pytest tests/test_scientific.py -v

# Frontend
cd frontend
npm test

# Frontend (watch mode)
npm run test:watch
```

## Code Style

### Python
- Follow PEP 8
- Use type hints everywhere
- Run ruff before committing: `ruff check .`
- Run mypy for type checking: `mypy app/`

### TypeScript
- Strict mode enabled
- No `any` without justification
- Run linting: `npm run lint`

## Common Tasks

### Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Seeding Data

Create `scripts/seeds.py` with sample experiments:

```python
import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import Experiment

async def seed():
    async with AsyncSessionLocal() as session:
        exp = Experiment(
            name="Sample RK4 Benchmark",
            category="numerical",
            configuration={...}
        )
        session.add(exp)
        await session.commit()
```

### Building for Production

```bash
# Frontend
npm run build
# Output: frontend/dist/

# Backend
pip install uvicorn[gunicorn]
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
