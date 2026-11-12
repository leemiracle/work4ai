# Attribute Verification Service

A microservice for running attribute verification on augmented images or videos. This service wraps
`AttributeVerificationProcessor` and exposes a standardized REST API for deployment as a containerized microservice.

## Overview

The Attribute Verification Service validates whether expected scene attributes (for example, weather or time of day)
are present in augmented image or video media. It provides an API for validating inputs, processing a clip, and
returning per-check details with pass/fail summary metrics.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check - returns service status and version |
| POST | `/process` | Process one clip and return attribute verification results |
| GET | `/config` | Get default attribute verification configuration |

## Request Model (`POST /process`)

```json
{
  "clip_id": "clip-123",
  "augmented_video_url": "s3://bucket/augmented.mp4",
  "config": {
    "selected_variables": {
      "weather": "sunny"
    }
  },
  "verbose": "INFO"
}
```

- `clip_id` (string): identifier for result output
- `augmented_video_url` (string): local or remote URI to an augmented image or video; the legacy field name is retained
  for API compatibility
- `config` (optional object): runtime overrides for `metropolis.attribute_verification` parameters
- `verbose` (optional): one of `DEBUG`, `INFO`, `WARNING`, `ERROR`

The `config` override supports `exclude_variables`, `extra_questions`, `question_generation.generate_options`, and
`vlm_verification.frames`. Fixed questions may set `request_reasoning: true`; their explanation is returned as
`vlm_reasoning`. Summary errors represent model or media failures separately from incorrect VLM answers.

## Environment Settings

The Attribute Verification Service inherits base settings from [`SettingsBase`](../settings_base.py). For local development, settings are loaded from `~/.cosmos_evaluator/.env` and `~/.aws/.env`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COSMOS_EVALUATOR_ENV` | `local` \| `dev` \| `staging` \| `production` | `local` | Deployment environment |
| `COSMOS_EVALUATOR_LOG_LEVEL` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` | Logging verbosity |
| `LLM_API_KEY` | secret string | - | Recommended API key for the question-generation LLM endpoint |
| `VLM_API_KEY` | secret string | - | Recommended API key for the visual-verification VLM endpoint |
| `BUILD_NVIDIA_API_KEY` | secret string | - | Legacy shared fallback for either model role |
| `MULTISTORAGECLIENT_CONFIGURATION` | JSON string | - | Multistorage client config used to resolve remote URIs |
| `ATTRIBUTE_VERIFICATION_PROCESS_CONCURRENCY_LIMIT` | integer >= 1 | `4` | Number of job slots on this replica, shared by claimed queue work and `POST /process` |
| `ATTRIBUTE_VERIFICATION_DATABASE_API_URL` | string | `""` | Base URL of the Database REST API whose queue this replica claims from |
| `ATTRIBUTE_VERIFICATION_DATABASE_WORKER_KEY` | string | `""` | Worker-scoped API key sent as `X-API-Key` when claiming and reporting jobs |

For authenticated model endpoints, prefer `LLM_API_KEY` and `VLM_API_KEY`; they may contain the same credential if both
endpoints accept it. Each model config may instead use `api_key_env` to name a custom environment variable. Credential
precedence is custom `api_key_env`, then the corresponding role-specific key, then legacy `BUILD_NVIDIA_API_KEY`.
Unauthenticated local endpoints need no model key.

The last two turn queue claiming on and are all-or-nothing: set both to claim, or neither to run standalone as a plain
`POST /process` service. Setting exactly one is a startup error rather than a silent fallback. The key must also appear
in the Database REST API's `DATABASE_WORKER_KEYS` list, or every claim is rejected with 401 — which presents as a
replica that is healthy and permanently idle. See
[Provisioning worker keys](../database/README.md#provisioning-worker-keys).

## Run the REST API on `localhost`

```bash
dazel run //services/attribute_verification:rest_api -- --help
usage: rest_api.py [-h] [--host HOST] [--port [1-65535]] [--log-level {DEBUG,INFO,WARNING,ERROR}]

Run the Attribute Verification API

options:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to
  --port [1-65535]      Port to bind to
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level
```

## Release and Deployment

See the [Deployment Guide](../../docs/deployment.md) for building, tagging, pushing, and running this service.
