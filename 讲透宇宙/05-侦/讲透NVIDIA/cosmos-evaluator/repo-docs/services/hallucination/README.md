# Hallucination Service 

A microservice for running hallucination detection on paired videos. This service wraps `HallucinationProcessor` and exposes a standardized REST API for deployment as a containerized microservice.

## Overview

The Hallucination Service compares an augmented video against its paired original video and computes a hallucination score based on dynamic pixel disagreement. It provides a synchronous API for validating inputs, processing a clip, and returning score metrics and pass/fail status.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check - returns service status and version |
| POST | `/process` | Process one clip and return hallucination metrics |
| GET | `/config` | Get default hallucination configuration |

## Request Model (`POST /process`)

```json
{
  "clip_id": "clip-123",
  "original_video_url": "s3://bucket/original.mp4",
  "augmented_video_url": "s3://bucket/augmented.mp4",
  "config": {
    "threshold": 0.682
  },
  "verbose": "INFO"
}
```

- `clip_id` (string): identifier for result output
- `original_video_url` (string): local or remote URI to original video
- `augmented_video_url` (string): local or remote URI to augmented video
- `config` (optional object): runtime overrides for `metropolis.hallucination` parameters
- `verbose` (optional): one of `DEBUG`, `INFO`, `WARNING`, `ERROR`

Local paths and `s3://`, `gs://`, `azure://`, `msc://`, or `https://` inputs are supported. Unencrypted `http://` inputs are rejected.

## Response Model (`POST /process`)

The response data contains the clip identifier, pass/fail decision, threshold, score, aligned frame count, dynamic-pixel totals, and elapsed processing time:

```json
{
  "clip_id": "clip-123",
  "passed": true,
  "threshold": 0.682,
  "score": 0.8255804747848313,
  "total_frames": 31,
  "total_hallucinated_dynamic_pixels": 15422,
  "total_augmented_dynamic_pixels": 88419,
  "duration_seconds": 2.418
}
```

If the input videos have different frame counts, the service scores only their aligned frames and logs how many unmatched frames were ignored from each tail.

## Environment Settings

The Hallucination Service inherits base settings from [`SettingsBase`](../settings_base.py). For local development, settings are loaded from `~/.cosmos_evaluator/.env` and `~/.aws/.env`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COSMOS_EVALUATOR_ENV` | `local` \| `dev` \| `staging` \| `production` | `local` | Deployment environment |
| `COSMOS_EVALUATOR_LOG_LEVEL` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` | Logging verbosity |
| `MULTISTORAGECLIENT_CONFIGURATION` | JSON string | - | Multistorage client config used to resolve remote URIs |
| `HALLUCINATION_PROCESS_CONCURRENCY_LIMIT` | integer >= 1 | `4` | Number of job slots on this replica, shared by claimed queue work and `POST /process` |
| `HALLUCINATION_DATABASE_API_URL` | string | `""` | Base URL of the Database REST API whose queue this replica claims from |
| `HALLUCINATION_DATABASE_WORKER_KEY` | string | `""` | Worker-scoped API key sent as `X-API-Key` when claiming and reporting jobs |

The last two turn queue claiming on and are all-or-nothing: set both to claim, or neither to run standalone as a plain
`POST /process` service. Setting exactly one is a startup error rather than a silent fallback. The key must also appear
in the Database REST API's `DATABASE_WORKER_KEYS` list, or every claim is rejected with 401 — which presents as a
replica that is healthy and permanently idle. See
[Provisioning worker keys](../database/README.md#provisioning-worker-keys).

## Run the REST API on `localhost`

```bash
dazel run //services/hallucination:rest_api -- --help
usage: rest_api.py [-h] [--host HOST] [--port [1-65535]] [--log-level {DEBUG,INFO,WARNING,ERROR}]

Run the Hallucination API

options:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to
  --port [1-65535]      Port to bind to
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level
```

## Release and Deployment

See the [Deployment Guide](../../docs/deployment.md) for building, tagging, pushing, and running this service.
