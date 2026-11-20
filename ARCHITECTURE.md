# Architecture Documentation

## System Overview

ResearchLab follows a modular layered architecture with clear separation between presentation, business logic, data access, and scientific computation.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │   React     │  │  TypeScript │  │   Vite      │               │
│  │   Components│  │   Strict    │  │   Bundler   │               │
│  └──────┬──────┘  └─────────────┘  └─────────────┘               │
│         │                                                          │
│  ┌──────┴──────┐                                                  │
│  │ TanStack    │  ┌─────────────┐  ┌─────────────┐               │
│  │  Query      │  │ Tailwind    │  │   Zod       │               │
│  │  (State)    │  │   (CSS)     │  │  (Forms)    │               │
│  └─────────────┘  └─────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │  CORS    │ │Exception │ │ Logging  │ │ Version  │      │  │
│  │  │ Middleware│ │ Handler  │ │ (JSON)   │ │  Control │      │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│  ┌───────────────────────────┼─────────────────────────────────┐ │
│  │                     ROUTER LAYER                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              /api/v1/                                │  │ │
│  │  │  • /experiments (CRUD)                               │  │ │
│  │  │  • /runs (Execution management)                      │  │ │
│  │  │  • /datasets (File storage)                          │  │ │
│  │  │  • /health (System checks)                           │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────┼─────────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────┼─────────────────────────────────┐ │
│  │                   SERVICE LAYER                              │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │            ExperimentService                         │  │ │
│  │  │  • Validation                                        │  │ │
│  │  │  • State transitions                                 │  │ │
│  │  │  • Retry logic                                       │  │ │
│  │  │  • Metric recording                                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────┼─────────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────┼─────────────────────────────────┐ │
│  │                  REPOSITORY LAYER                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │
│  │  │Experient│ │   Run    │ │  Metric  │ │ Dataset  │      │ │
│  │  │ Repository│ │Repository│ │Repository│ │Repository│      │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │ │
│  └───────────────────────────┼─────────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────┼─────────────────────────────────┐ │
│  │                    DATA ACCESS                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              SQLAlchemy 2.x                          │  │ │
│  │  │  • AsyncSession                                      │  │ │
│  │  │  • Declarative Base                                  │  │ │
│  │  │  • Alembic Migrations                                │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────┼─────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌────────────────┐ ┌───────────┐ ┌──────────────┐
    │   PostgreSQL   │ │   Redis   │ │  File Storage│
    │  (Metadata)    │ │  (Broker) │ │  (Uploads)   │
    └────────────────┘ └───────────┘ └──────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     SCIENTIFIC ENGINE                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  ExperimentRegistry                         │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │  │
│  │  │NumericalInt. │ │ MonteCarlo   │ │ParamSweep    │       │  │
│  │  │Benchmark      │ │Simulation    │ │Experiment    │       │  │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘       │  │
│  │         └─────────────────┴─────────────────┘              │  │
│  │                        │                                   │  │
│  │         ┌──────────────┴──────────────┐                   │  │
│  │         │     BaseExperiment          │                   │  │
│  │         │  (abstract base class)      │                   │  │
│  │         │  • validate_config()        │                   │  │
│  │         │  • execute()                │                   │  │
│  │         │  • cleanup()                │                   │  │
│  │         └─────────────────────────────┘                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Experiment Creation Flow
```
User Action
    │
    ▼
Frontend Form (Zod validation)
    │
    ▼
POST /api/v1/experiments
    │
    ▼
Pydantic Schema Validation (ExperimentCreate)
    │
    ▼
ExperimentService.create()
    │
    ├─► Configuration hashing (SHA-256)
    ├─► Increment configuration_version
    │
    ▼
ExperimentRepository.create()
    │
    ▼
INSERT INTO experiments (...)
    │
    ▼
Return ExperimentOut (UUID, timestamps)
```

### Experiment Execution Flow
```
User clicks "Run Experiment"
    │
    ▼
POST /api/v1/runs/experiments/{id}/runs
    │
    ▼
RunRepository.create(PENDING)
    │
    ▼
Try to submit to Celery
    │
    ├── Success ──► Task queued, return RunOut
    │
    └── Failed ──► Log warning, run stays PENDING
                    (Worker picks up when ready)
    
[Celery Worker - Background]
    │
    ▼
run_experiment_task(run_id)
    │
    ▼
Get ExperimentRun from DB
    │
    ▼
Update status → RUNNING, record started_at
    │
    ▼
Load experiment class from registry
    │
    ▼
Execute experiment (blocking computation)
    │
    ├── Success ──► Record metrics & logs
    │               Update status → COMPLETED
    │
    └── Failure ──► Capture error message
                    Update status → FAILED
    
    Return result dict
```

### Metrics Recording Flow
```
Experiment.execute() returns results dict
    │
    ▼
For each metric in ctx.metrics:
    │
    ▼
METRIC(name, value, unit, step, metadata)
    │
    ▼
Batch insert via MetricRepository.add_many()
    │
    ▼
Transaction committed
```

## Key Design Decisions

### 1. Immutable Configuration Snapshots
Each run stores a complete copy of its configuration at execution time. This ensures reproducibility even if the parent experiment is later modified.

```python
snapshot = {
    "type": exp.configuration["experiment"]["type"],
    "parameters": exp.configuration["experiment"]["parameters"],
    "execution": exp.configuration["experiment"]["execution"],
    "_config_hash": hashlib.sha256(...)
}
```

### 2. Plugin Registry Pattern
New experiment types are added by:
1. Subclassing `BaseExperiment`
2. Implementing `validate_config()` and `execute()`
3. Adding import to `registry.py`

No code changes needed to existing components.

### 3. State Machine Enforcement
Valid transitions are explicitly defined and checked:

```python
VALID_TRANSITIONS = {
    "PENDING": {"QUEUED", "CANCELLED"},
    "QUEUED": {"RUNNING", "CANCELLED"},
    "RUNNING": {"COMPLETED", "FAILED", "CANCELLED"},
    "COMPLETED": set(),
    "FAILED": {"QUEUED"},
    "CANCELLED": {"QUEUED"},
}
```

### 4. Separation of Concerns
- **API Layer**: Request validation, response formatting
- **Service Layer**: Business logic, state management
- **Repository Layer**: Database operations
- **Engine Layer**: Scientific computation isolation

### 5. Graceful Degradation
When Celery/Redis unavailable:
- Runs stay in PENDING status
- No silent failures or lost work
- Clear logging indicates issue
- Manual re-execution possible via retry endpoint

## Security Considerations

| Threat | Mitigation |
|--------|------------|
| SQL Injection | SQLAlchemy ORM parameterization |
| XSS | React auto-escaping + no innerHTML |
| File Upload Abuse | Size limits, format whitelisting, checksums |
| Arbitrary Code Execution | Only registered experiment classes allowed |
| Config Injection | Safe YAML loading (no !include, !!python/) |

## Performance Optimizations

1. **Connection Pooling**: SQLAlchemy pool_size/max_overflow configured
2. **Pagination**: All list endpoints support skip/limit
3. **Indexing**: Strategic indexes on foreign keys and status columns
4. **Batch Inserts**: Metrics collected then inserted in bulk
5. **Async I/O**: All database operations use asyncio
