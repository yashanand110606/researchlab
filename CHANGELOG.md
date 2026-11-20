# Changelog

All notable changes to ResearchLab will be documented in this file.

## [0.1.0] - 2026-11-19

### Added
- Full-stack scientific experiment orchestration platform
- FastAPI backend with RESTful API under `/api/v1/`
- Three scientific experiment types:
  - Numerical Integration Benchmark (Euler, RK4, SciPy RK45)
  - Monte Carlo π Estimation (basic + stratified sampling)
  - Parameter Sweep (grid search over configurable functions)
- PostgreSQL database with 6 models (Experiment, ExperimentRun, Metric, Dataset, ExperimentTag, ExperimentLog)
- SQLAlchemy 2.x async ORM with Alembic migrations
- Celery worker integration for asynchronous execution
- React + TypeScript frontend with Vite
- Dark scientific software aesthetic UI
- TanStack Query for server state management
- Comprehensive test suite (16 tests, all passing)

### Technical Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Celery, Redis
- Frontend: React 18, TypeScript, Tailwind CSS, Vite
- Infrastructure: Docker Compose (configured, Docker not available in dev environment)

### Files Created
- `backend/app/main.py` — FastAPI application entry point
- `backend/app/core/config.py` — Environment-based configuration
- `backend/app/db/models.py` — SQLAlchemy ORM models
- `backend/app/experiments/base.py` — Abstract base experiment class
- `backend/app/experiments/registry.py` — Plugin registry pattern
- `backend/app/experiments/numerical_integration.py` — ODE solver benchmark
- `backend/app/experiments/monte_carlo.py` — π estimation simulation
- `backend/app/experiments/parameter_sweep.py` — Grid parameter sweep
- `backend/app/services/experiment_service.py` — Business logic layer
- `backend/app/api/v1/endpoints/experiments.py` — CRUD endpoints
- `backend/app/api/v1/endpoints/runs.py` — Execution endpoints
- `backend/app/api/v1/endpoints/health.py` — Health checks
- `backend/tests/` — 16 passing tests
- `frontend/src/` — Complete React application
- `frontend/package.json`, `tsconfig.json`, `vite.config.ts`
- `README.md`, `ARCHITECTURE.md`, `API.md`, `DATABASE.md`

## Architecture Highlights
- Modular backend with clean separation between API routes, business logic, repositories, and experiments
- Plugin/registry pattern for extensible experiment types
- Reproducible random number generation via NumPy's Generator API
- Configuration hashing for immutable snapshots
- Proper state transition enforcement (PENDING → QUEUED → RUNNING → COMPLETED/FAILED/CANCELLED)
