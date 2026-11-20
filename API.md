# API Reference

Base URL: `http://localhost:8000/api/v1`

All responses are JSON. Errors follow consistent format:
```json
{"detail": "Error message"}
```

## Health Endpoints

### GET /health
Check basic system health.

**Response:**
```json
{
  "status": "ok",
  "database": "connected"
}
```

### GET /ready
Detailed readiness check with component status.

**Response:**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

## Experiments

### GET /experiments
List experiments with pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Number of records to skip |
| limit | int | 20 | Max records to return (max 100) |
| category | string | null | Filter by category |
| search | string | null | Search name/description |
| sort_by | string | created_at | Sort field |
| sort_order | string | desc | asc or desc |

**Response:**
```json
{
  "items": [
    {
      "id": "uuid-string",
      "name": "RK4 Benchmark",
      "description": "...",
      "category": "numerical",
      "configuration": {...},
      "configuration_version": 1,
      "created_at": "2026-11-19T...",
      "updated_at": "2026-11-19T..."
    }
  ],
  "pagination": {
    "total": 42,
    "skip": 0,
    "limit": 20
  }
}
```

### POST /experiments
Create a new experiment.

**Request Body:**
```json
{
  "name": "My Experiment",
  "description": "Optional description",
  "category": "physics",
  "configuration": {
    "experiment": {
      "type": "numerical_integration",
      "parameters": {...},
      "execution": {...}
    }
  }
}
```

**Response:** 201 Created with Experiment object.

### GET /experiments/{id}
Get experiment details.

**Response:** Experiment object.

### PATCH /experiments/{id}
Update experiment fields. Only provided fields are updated; configuration update increments version.

### DELETE /experiments/{id}
Delete experiment and all associated runs (cascade).

**Response:** 204 No Content.

### POST /experiments/{id}/duplicate
Duplicate an experiment with new UUID.

**Response:** 201 Created with duplicate experiment.

### POST /experiments/{id}/tags
Add a tag to an experiment.

**Request Body:**
```json
{"tag": "benchmark"}
```

### DELETE /experiments/{id}/tags/{tag}
Remove a tag from an experiment.

**Response:** `{"deleted": true, "tag": "benchmark"}`

### GET /experiments/types
List all available experiment types.

**Response:**
```json
{
  "types": ["numerical_integration", "monte_carlo", "parameter_sweep"],
  "details": [
    {
      "type": "numerical_integration",
      "description": "Compare numerical ODE solvers..."
    }
  ]
}
```

## Runs

### POST /runs/experiments/{experiment_id}/runs
Create and queue a new run.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| random_seed | int | Optional seed for reproducibility |

**Response:** 201 Created with Run object.

### GET /runs
List runs with optional filters.

**Query Parameters:**
| Parameter | Type | Default |
|-----------|------|---------|
| experiment_id | uuid | null |
| status | string | null |
| skip | int | 0 |
| limit | int | 50 |

**Response:**
```json
{
  "items": [...],
  "count": 10
}
```

### GET /runs/{id}
Get run details including status, duration, error message.

**Response:** Run object with all fields.

### POST /runs/{id}/cancel
Cancel a pending or queued run.

**Response:** Updated Run object.

### POST /runs/{id}/retry
Retry a failed or cancelled run as new execution.

**Response:** 201 Created with new Run object.

### GET /runs/{id}/logs
Get execution logs for a run.

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "timestamp": "2026-11-19T...",
      "level": "INFO",
      "message": "Starting integration benchmark...",
      "metadata": {}
    }
  ],
  "count": 5
}
```

### GET /runs/{id}/metrics
Get metrics recorded during execution.

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "euler_max_abs_error",
      "value": 0.0234,
      "unit": "",
      "recorded_at": "2026-11-19T...",
      "step": null,
      "metadata": {}
    }
  ],
  "count": 12
}
```

### GET /runs/{id}/results
Get compiled results summary.

**Response:** Aggregated metrics and computed values.

## Datasets

### GET /datasets
List uploaded datasets.

**Query Parameters:** skip, limit

### POST /datasets
Upload a dataset file.

**Content-Type:** multipart/form-data

**Form Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Dataset name |
| file_format | Yes | Format identifier (csv, json, npz, etc.) |
| description | No | Optional description |
| file | Yes | The file to upload |

**Response:** Dataset metadata including checksum.

### DELETE /datasets/{id}
Delete a dataset and its stored file.

**Response:** 204 No Content.

## Response Schemas

### Experiment
```typescript
interface Experiment {
  id: string;              // UUID
  name: string;
  description: string | null;
  category: string;
  configuration: Record<string, unknown>;
  configuration_version: number;
  created_at: string;      // ISO 8601
  updated_at: string;      // ISO 8601
}
```

### ExperimentRun
```typescript
interface ExperimentRun {
  id: string;              // UUID
  experiment_id: string;   // UUID
  status: 'PENDING' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  configuration_snapshot: Record<string, unknown>;
  random_seed: number | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  worker_id: string | null;
  created_at: string;
}
```

### Metric
```typescript
interface Metric {
  id: string;
  run_id: string;
  name: string;
  value: number;
  unit: string | null;
  recorded_at: string;
  step: number | null;
  metadata: Record<string, unknown> | null;
}
```

## Error Responses

| Status Code | Meaning | Example Detail |
|-------------|---------|----------------|
| 400 | Bad Request | Missing required field |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Invalid state transition |
| 422 | Validation Error | Configuration schema violation |
| 500 | Internal Error | Unexpected exception |
