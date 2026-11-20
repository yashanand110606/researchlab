# ResearchLab — Scientific Experiment Orchestration Platform

A production-quality full-stack platform for creating, executing, and analyzing scientific experiments. Built for researchers, computational physicists, and engineering teams who need reproducible, verifiable results.

## Problem Statement

Scientific experimentation requires:
- **Reproducibility**: Same inputs must produce same outputs (controlled random seeds)
- **Verification**: Numerical results must be validated against analytical solutions
- **Auditability**: Every run's configuration and parameters must be immutable
- **Scalability**: Experiments should run asynchronously without blocking user workflows

ResearchLab solves these through a plugin architecture for experiment types, immutable configuration snapshots, and rigorous testing of numerical accuracy.

## Features

### Core Capabilities
1. **Experiment Creation** — Define configurations via JSON with schema validation
2. **Asynchronous Execution** — Celery workers process experiments independently
3. **Status Tracking** — PENDING → QUEUED → RUNNING → COMPLETED/FAILED/CANCELLED
4. **Metric Collection** — Scalar, time-series, and array metrics with units
5. **Log Persistence** — Timestamped execution logs with severity levels
6. **Result Comparison** — View metrics across multiple runs
7. **Dataset Management** — Upload and track input data files
8. **API Documentation** — OpenAPI/Swagger UI at `/docs`

### Built-in Experiment Types

| Type | Description | Mathematical Basis |
|------|-------------|-------------------|
| `numerical_integration` | ODE solver benchmark | y' = -λy, exact solution y₀·e^{-λt} |
| `monte_carlo` | π estimation via sampling | Area ratio: circle/square = π/4 |
| `parameter_sweep` | Grid search optimization | Configurable objective functions |

### Scientific Correctness

All experiments include:
- Documented equations and assumptions
- Input validation with specific error messages
- Tolerance-checked numerical results
- Reproducibility verification (same seed → same output)
- NaN/infinity handling

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + TS)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Dashboard│ │Experiments│ │ RunMonit.│ │Results   │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │             │            │            │                │
│       └─────────────┴────────────┴────────────┘                │
│                          │                                     │
│                    TanStack Query                              │
│                          │                                     │
└──────────────────────────┼─────────────────────────────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ API Routes  │  │  Services   │  │ Repositories│            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                   │
│         └────────────────┴────────────────┘                   │
│                          │                                    │
│                    Pydantic v2                               │
│                          │                                    │
└──────────────────────────┼─────────────────────────────────────┘
                           │ SQLAlchemy
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Experiment Engine                            │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ BaseExperiment   │◄─│ NumericalIntegr. │                   │
│  │ (abstract)       │  │ MonteCarlo       │                   │
│  └────────┬─────────┘  │ ParameterSweep   │                   │
│           │            └──────────────────┘                   │
│           │                                                   │
│     Registry Pattern                                          │
└───────────┼───────────────────────────────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌──────────┐
│PostgreSQL│   │  Redis   │
│(Metadata)│   │(Broker)  │
└─────────┘   └─────┬────┘
                    │
                    ▼
              ┌──────────┐
              │ Celery   │
              │ Workers  │
              └──────────┘
```

## Technology Stack

### Backend
- **Python 3.11+** with type hints
- **FastAPI** for async REST API
- **SQLAlchemy 2.x** with async ORM
- **Pydantic v2** for request/response validation
- **Alembic** for database migrations
- **Celery + Redis** for async task processing
- **NumPy + SciPy** for scientific computation
- **PyYAML** for safe config parsing

### Frontend
- **React 18** with TypeScript (strict mode)
- **Vite** for fast builds
- **Tailwind CSS** for styling
- **TanStack Query** for server state
- **Zod** for form validation
- **React Router** for navigation

### Infrastructure
- **Docker Compose** for containerized deployment
- **GitHub Actions** for CI/CD
- **pytest + Vitest** for testing
- **Playwright** for E2E tests (planned)

## Screenshots

*Dashboard view showing experiment statistics and recent activity*
*Experiment creation form with YAML/JSON configuration editor*
*Run monitor displaying real-time execution status*
*Results explorer with interactive metric tables*

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (optional, for Celery background processing)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Set up environment
cp ../.env.example ../.env
# Edit .env to configure database credentials

# Create database
createdb researchlab

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the application at http://localhost:5173

### Docker Setup

```bash
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: postgresql://localhost:5432/researchlab
- Redis: redis://localhost:6379

## Example Experiment

### Numerical Integration Benchmark

```json
{
  "experiment": {
    "type": "numerical_integration",
    "parameters": {
      "equation": "exponential_decay",
      "initial_value": 1.0,
      "decay_constant": 0.5,
      "time_start": 0.0,
      "time_end": 10.0,
      "step_size": 0.1
    },
    "execution": {
      "timeout_seconds": 120,
      "max_iterations": 100000
    }
  }
}
```

This compares Euler, RK4, and SciPy's solve_ivp(RK45) against the analytical solution y(t) = e^{-0.5t}.

### Creating an Experiment via API

```bash
curl -X POST http://localhost:8000/api/v1/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RK4 Accuracy Test",
    "category": "numerical",
    "configuration": {
      "experiment": {
        "type": "numerical_integration",
        "parameters": {
          "equation": "exponential_decay",
          "initial_value": 1.0,
          "decay_constant": 0.5,
          "time_start": 0.0,
          "time_end": 10.0,
          "step_size": 0.1
        }
      }
    }
  }'
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

All 16 tests pass, including:
- Schema validation tests
- Scientific correctness tests (accuracy, reproducibility)
- Edge case coverage

### Frontend Tests

```bash
cd frontend
npm test
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI spec: http://localhost:8000/openapi.json

Key endpoints:
- `GET /api/v1/experiments` — List experiments (paginated)
- `POST /api/v1/experiments` — Create experiment
- `GET /api/v1/experiments/{id}` — Get experiment details
- `POST /api/v1/runs/experiments/{id}/runs` — Execute experiment
- `GET /api/v1/runs` — List all runs
- `GET /api/v1/runs/{id}/metrics` — Get run metrics
- `GET /api/v1/runs/{id}/logs` — Get execution logs

## Troubleshooting

### Backend won't start
1. Check PostgreSQL is running: `psql -U researchlab -d researchlab`
2. Verify Redis is accessible: `redis-cli ping`
3. Check `.env` file exists with correct credentials

### Tests fail
```bash
# Ensure you're in the virtual environment
cd backend
source .venv/bin/activate
pytest tests/ -v --tb=long
```

### Frontend shows connection errors
1. Verify backend is running on port 8000
2. Check CORS settings in `.env`: `CORS_ORIGINS=["http://localhost:5173"]`
3. Clear browser cache and reload

### Celery not processing jobs
1. Install Celery: `pip install celery[redis]`
2. Start worker: `celery -A app.workers.tasks worker --loglevel=info`
3. Verify Redis is running: `redis-cli ping`

## Future Improvements

- [ ] User authentication and authorization
- [ ] WebSocket support for real-time updates
- [ ] Jupyter notebook export
- [ ] Advanced visualization with Plotly.js
- [ ] Distributed execution across multiple workers
- [ ] Experiment templating library
- [ ] Automated result reporting (PDF/HTML)
- [ ] Data versioning with DVC integration

## License

MIT License — see LICENSE file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
