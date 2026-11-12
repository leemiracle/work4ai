# Arbitrator Service

The coordinator for the Cosmos Evaluator orchestration layer. It accepts a single evaluation request, discovers the
healthy checker services, builds a dependency-ordered work queue, dispatches to the checkers, aggregates their
results, and records every client, execution, and checker execution through the [Database REST API](../database/README.md).

## Overview

Unlike the individual checker services (which expose a synchronous `POST /process`), the Arbitrator uses a
**submit-and-poll** model: `POST /process/async` returns a `request_id` immediately and runs the work in the
background; clients poll `GET /executions/{request_id}` until the run reaches a terminal status (`success` or `fail`).
The Arbitrator itself never touches PostgreSQL directly — all persistence goes through the Database REST API.

For the end-to-end orchestration story (architecture diagram, dependency graph, per-camera fan-out, and how the three
orchestration components fit together), see the [Orchestration Layer guide](../../docs/services/orchestration.md).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process/async` | Submit an evaluation request; returns `202 Accepted` with a `request_id` |
| GET | `/executions/{request_id}` | Poll the parent execution plus per-checker rows for a submitted request |
| GET | `/checkers` | Probe every configured checker's `/health` in parallel and return the healthy ones |
| GET | `/dependency-graph` | Return the parsed dependency graph as `{ checker: { deps, priority } }` |
| GET | `/config` | Fan out to every checker's `/config` and return the aggregated defaults |
| GET | `/health` | Health check - returns service status and version |
| GET | `/metrics` | Prometheus metrics (requests in progress / queued, per-checker job states) |

## Request Model (`POST /process/async`)

```json
{
  "inputs": {
    "augmented_video_urls": {
      "camera_front_wide_120fov": "s3://bucket/augmented.mp4"
    },
    "rds_hq_url": "s3://bucket/rds_hq.zip",
    "world_model_video_urls": {
      "camera_front_wide_120fov": "s3://bucket/world.mp4"
    },
    "original_video_urls": {
      "camera_front_wide_120fov": "s3://bucket/original.mp4"
    },
    "config": {}
  },
  "checks": ["av.objects_single_view"],
  "output_storage_prefix": "results/run-123"
}
```

- `inputs.augmented_video_urls` (object, required): camera stream id → augmented video URL. At least one entry;
  drives per-camera fan-out.
- `inputs.rds_hq_url` (string): RDS-HQ dataset archive. Required only when a checker that opens the dataset is in the
  resolved queue — `av.objects_single_view` here; subclasses widen the set via `_rds_hq_required_by`.
- `inputs.world_model_video_urls` (optional object): per-camera world-model video for the Objects static (CWIP)
  check. Cameras without an entry are skipped (no shared fallback).
- `inputs.original_video_urls` (optional object): per-camera reference video for the Hallucination check. Cameras
  without an entry are skipped (no shared fallback).
- `inputs.config` (optional object): free-form configuration forwarded to the checkers.
- `checks` (optional list): checker base names to run. If empty, all healthy configured checkers are considered.
- `output_storage_prefix` (optional string): storage prefix forwarded to each checker.

The response is `{ "success": true, "data": { "request_id": <int> }, "timestamp": "..." }`. Poll
`GET /executions/{request_id}` until `data.execution.is_terminal` is `true`.

## Environment Settings

The Arbitrator inherits base settings from [`SettingsBase`](../settings_base.py). For local development, settings are
loaded from `~/.cosmos_evaluator/.env` and `~/.aws/.env`. The `dazel run` local targets pre-populate the checker
endpoints and database URL, so no manual configuration is required for local development.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COSMOS_EVALUATOR_CHECKER_ENDPOINTS` | JSON string | — (required) | JSON object mapping checker base name to base URL |
| `COSMOS_EVALUATOR_DATABASE_API_URL` | string | `""` | Base URL of the Database REST API. Empty disables recording |
| `ARBITRATOR_DATABASE_API_KEY` | string | `""` | API key sent to the Database REST API (must match its `DATABASE_ADMIN_KEY`) |
| `ARBITRATOR_QUEUE_CAPACITY` | integer | unbounded | Max combined queued + in-flight requests per replica |
| `COSMOS_EVALUATOR_ENV` | `local` \| `dev` \| `staging` \| `production` | `local` | Deployment environment |
| `COSMOS_EVALUATOR_LOG_LEVEL` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` | Logging verbosity |

`COSMOS_EVALUATOR_CHECKER_ENDPOINTS` maps each checker's base name to its base URL, for example:

```json
{
  "av.objects_single_view": "http://localhost:8082",
  "metropolis.hallucination": "http://localhost:8085",
  "metropolis.attribute_verification": "http://localhost:8086"
}
```

## Run the REST API on `localhost`

```bash
dazel run //services/arbitrator:rest_api -- --help
usage: rest_api.py [-h] [--host HOST] [--port [1-65535]] [--log-level {DEBUG,INFO,WARNING,ERROR}]

Run the Arbitrator API

options:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to
  --port [1-65535]      Port to bind to
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level
```

To bring up the Arbitrator together with the checker services and the Database REST API (all wired up), run the full
local stack with `dazel run //services:rest_apis`.

## Release and Deployment

See the [Deployment Guide](../../docs/deployment.md#orchestration-layer) for building, tagging, pushing, and running
the orchestration containers in production.
