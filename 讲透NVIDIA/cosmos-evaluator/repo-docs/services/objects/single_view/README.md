# Objects Single-View Service

A microservice for processing single-view objects analysis using computer vision and world model data. This service provides a standardized REST API interface for deployment as a containerized microservice.

## Overview

The Objects Single-View Service analyzes correspondence between segmented objects in camera images and tracked objects in the world model, returning correspondence scores and statistics. It claims its own work off the `checker_executions` queue, and also accepts a clip directly on `POST /process`.

**Camera-only mode.** The static (CWIP) check runs camera-only whenever no world-model video is supplied — the world-model video (`world_model_video_url` on a cloud request, `world_video_path` on a local one) is optional, and omitting it selects camera-only rather than failing. In camera-only mode the world video is neither required nor downloaded, and the static presence mask is derived from the type head instead of the similarity head. See the [checker README](../../../checks/objects/single_view/README.md#camera-only-mode) for the semantics and the `presence` config block.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check - returns service status and version |
| GET | `/metrics` | Prometheus metrics - claimed-job slot occupancy for this replica |
| POST | `/process` | Process single-view objects analysis |
| GET | `/config` | Get default configuration |

## Environment Settings

The Objects Single-View Service inherits base settings from [`SettingsBase`](../../settings_base.py). For local development, settings are loaded from `~/.cosmos_evaluator/.env` and `~/.aws/.env`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COSMOS_EVALUATOR_ENV` | `local` \| `dev` \| `staging` \| `production` | `local` | Deployment environment |
| `COSMOS_EVALUATOR_LOG_LEVEL` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` | Logging verbosity |
| `COSMOS_EVALUATOR_STORAGE_TYPE` | `s3` \| `local` | `s3` | Storage backend for downloading inputs and uploading results |
| `COSMOS_EVALUATOR_STORAGE_URL` | string | - | Target address, e.g. `https://my-bucket.s3.us-west-2.amazonaws.com` (required when `COSMOS_EVALUATOR_STORAGE_TYPE=s3`) |
| `OBJECTS_PROCESS_CONCURRENCY_LIMIT` | integer >= 1 | `3` | Number of job slots on this replica, shared by claimed queue work and `POST /process`. The claim loop stops taking work when no slot is free; a `/process` caller waits for one rather than being turned away |
| `OBJECTS_MODEL_DEVICE` | `cuda` \| `cpu` | `cuda` | Device for CWIP and SegFormer inference. Startup fails fast when set to `cuda` on a host with no usable GPU stack |
| `OBJECTS_DATABASE_API_URL` | string | `""` | Base URL of the Database REST API whose queue this replica claims from, e.g. `https://<host>` |
| `OBJECTS_DATABASE_WORKER_KEY` | string | `""` | Worker-scoped API key sent as `X-API-Key` when claiming and reporting jobs |

The last two turn queue claiming on, and are all-or-nothing: set both to claim, or neither to run standalone as a
plain `POST /process` service. Setting exactly one is a startup error rather than a silent fallback, because a replica
that comes up healthy and never claims anything is invisible until somebody notices the queue is not draining.

The key must also appear in the Database REST API's own `DATABASE_WORKER_KEYS` list, or every claim is rejected with
401 — which likewise presents as a healthy, permanently idle replica. See
[Provisioning worker keys](../../database/README.md#provisioning-worker-keys).

## Run the REST API on `localhost`

```bash
dazel run //services/objects/single_view:rest_api -- --help
usage: rest_api.py [-h] [--host HOST] [--port [1-65535]] [--log-level {DEBUG,INFO,WARNING,ERROR}]

Run the Objects Single-View API

options:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to (default: 0.0.0.0)
  --port [1-65535]      Port to bind to (default: 8080)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level (default: INFO)
```

## Release and Deployment

See the [Deployment Guide](../../../docs/deployment.md) for building, tagging, pushing, and running this service.
