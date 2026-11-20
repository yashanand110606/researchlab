# Database Schema

## ER Diagram

```mermaid
erDiagram
    EXPERIMENTS ||--o{ EXPERIMENT_RUNS : "1:N"
    EXPERIMENTS ||--o{ EXPERIMENT_TAGS : "1:N"
    EXPERIMENT_RUNS ||--o{ METRICS : "1:N"
    EXPERIMENT_RUNS ||--o{ EXPERIMENT_LOGS : "1:N"
    
    EXPERIMENTS {
        UUID id PK
        VARCHAR(255) name
        TEXT description
        VARCHAR(100) category
        JSONB configuration
        INT configuration_version
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }
    
    EXPERIMENT_RUNS {
        UUID id PK
        UUID experiment_id FK
        VARCHAR(20) status
        JSONB configuration_snapshot
        INT random_seed
        TIMESTAMPTZ started_at
        TIMESTAMPTZ completed_at
        FLOAT duration_seconds
        TEXT error_message
        VARCHAR(255) worker_id
        TIMESTAMPTZ created_at
    }
    
    METRICS {
        UUID id PK
        UUID run_id FK
        VARCHAR(255) name
        FLOAT value
        VARCHAR(50) unit
        TIMESTAMPTZ recorded_at
        INT step
        JSONB metadata
    }
    
    DATASETS {
        UUID id PK
        VARCHAR(255) name
        TEXT description
        VARCHAR(512) filename
        VARCHAR(50) file_format
        VARCHAR(64) checksum
        BIGINT size_bytes
        TIMESTAMPTZ created_at
    }
    
    EXPERIMENT_TAGS {
        UUID id PK
        UUID experiment_id FK
        VARCHAR(50) tag
        TIMESTAMPTZ created_at
        UNIQUE(experiment_id, tag)
    }
    
    EXPERIMENT_LOGS {
        UUID id PK
        UUID run_id FK
        TIMESTAMPTZ timestamp
        VARCHAR(10) level
        TEXT message
        JSONB metadata
    }
```

## Tables

### experiments
Stores experiment definitions with versioned configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Experiment display name |
| description | TEXT | NULLABLE | Optional description |
| category | VARCHAR(100) | NOT NULL, default 'general' | Categorization |
| configuration | JSONB | NOT NULL | Full experiment config |
| configuration_version | INT | NOT NULL, default 1 | Incremented on update |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last modification |

**Indexes:** category, created_at

### experiment_runs
Stores individual execution attempts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| experiment_id | UUID | FK → experiments.id ON DELETE CASCADE | Parent experiment |
| status | VARCHAR(20) | NOT NULL, default 'PENDING' | Execution state |
| configuration_snapshot | JSONB | NOT NULL | Immutable config at runtime |
| random_seed | INT | NULLABLE | Seed for reproducibility |
| started_at | TIMESTAMPTZ | NULLABLE | Execution start time |
| completed_at | TIMESTAMPTZ | NULLABLE | Execution end time |
| duration_seconds | FLOAT | NULLABLE | Total runtime |
| error_message | TEXT | NULLABLE | Error details if failed |
| worker_id | VARCHAR(255) | NULLABLE | Worker that processed |
| created_at | TIMESTAMPTZ | NOT NULL | Queue creation time |

**Status values:** PENDING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED

**Indexes:** experiment_id, status, created_at

### metrics
Time-series measurements from runs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| run_id | UUID | FK → experiment_runs.id ON DELETE CASCADE | Source run |
| name | VARCHAR(255) | NOT NULL | Metric identifier |
| value | FLOAT | NOT NULL | Numeric value |
| unit | VARCHAR(50) | NULLABLE | Physical unit |
| recorded_at | TIMESTAMPTZ | NOT NULL | Timestamp |
| step | INT | NULLABLE | Step index (optional) |
| metadata | JSONB | NULLABLE | Extra context |

**Indexes:** run_id, name, recorded_at

### datasets
Uploaded data files with integrity verification.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Display name |
| description | TEXT | NULLABLE | Optional description |
| filename | VARCHAR(512) | NOT NULL | Stored filename |
| file_format | VARCHAR(50) | NOT NULL | Format type |
| checksum | VARCHAR(64) | NOT NULL | SHA-256 hash |
| size_bytes | BIGINT | NOT NULL, default 0 | File size |
| created_at | TIMESTAMPTZ | NOT NULL | Upload time |

**Indexes:** filename, created_at

### experiment_tags
Many-to-many tags for experiments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| experiment_id | UUID | FK → experiments.id ON DELETE CASCADE | Parent experiment |
| tag | VARCHAR(50) | NOT NULL | Tag name |
| created_at | TIMESTAMPTZ | NOT NULL | Assignment time |

**Constraints:** UNIQUE(experiment_id, tag) prevents duplicates

### experiment_logs
Execution logs per run.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| run_id | UUID | FK → experiment_runs.id ON DELETE CASCADE | Source run |
| timestamp | TIMESTAMPTZ | NOT NULL | Log time |
| level | VARCHAR(10) | NOT NULL | DEBUG/INFO/WARNING/ERROR |
| message | TEXT | NOT NULL | Log content |
| metadata | JSONB | NULLABLE | Extra context |

**Indexes:** run_id, timestamp

## Migration History

### Version: initial_models
- Created all six tables
- Added indexes for query performance
- Set up foreign keys with cascading deletes where appropriate

## Connection Settings

```python
engine = create_async_engine(
    "postgresql+psycopg://user:pass@host:port/dbname",
    pool_size=10,
    max_overflow=20,
    echo=False
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```
