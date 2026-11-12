# Database REST API Service

The persistence gateway for the Cosmos Evaluator orchestration layer. It is the only component that connects to
PostgreSQL, exposing a small HTTP API for recording clients, arbitrator executions, and per-checker executions,
protected by API-key RBAC.

## Overview

The [Arbitrator](../arbitrator/README.md) records everything it does through this service rather than talking to the
database directly. Reads are protected by a read key; all writes require an admin key. The service connects to
PostgreSQL over `asyncpg` (there is no SQLite path). For the storage layer itself, see the
[PostgreSQL container README](../../database/README.md); for the whole orchestration picture, see the
[Orchestration Layer guide](../../docs/services/orchestration.md).

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | read | Health check - returns service status and version |
| GET | `/arbitrator-executions/{request_id}` | read | Fetch a parent execution row |
| GET | `/arbitrator-executions/{request_id}/checker-executions` | read | Fetch all checker-execution rows for a request |
| GET | `/arbitrator-executions/{request_id}/checker-states` | read | Compact per-checker status for one request |
| POST | `/clients` | admin | Upsert a client record |
| POST | `/arbitrator-executions` | admin | Create a parent execution row |
| PUT | `/arbitrator-executions/{request_id}` | admin | Update a parent execution row (status, response, duration) |
| POST | `/arbitrator-executions/heartbeat` | admin | Renew one replica's lease on every request it is orchestrating |
| POST | `/arbitrator-executions/adopt` | admin | Claim requests whose orchestrating replica stopped renewing |
| POST | `/checker-executions` | admin | Create a checker-execution row |
| PUT | `/checker-executions/{execution_id}` | admin | Update a checker-execution row |

The job queue that checker replicas claim their own work from:

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/checker-executions/claim-next` | worker | Long-poll for and claim the oldest queued jobs for one checker |
| POST | `/checker-executions/{execution_id}/heartbeat` | worker | Renew the job lease; reports back whether a cancellation was requested |
| POST | `/checker-executions/{execution_id}/complete` | worker | Record the terminal status and result |
| POST | `/checker-executions/{execution_id}/cancel` | admin | Flag a job so its owner stops at the next checkpoint |
| POST | `/checker-executions/reap` | admin | Return jobs whose owner stopped renewing to the queue |
| POST | `/checker-executions/states` | read | Batch row lookup, backing the arbitrator's poll and its adoption rebuild |

## Authentication and RBAC

Authentication is a three-key model over the `X-API-Key` request header:

| Key | Environment variable | Grants |
|-----|----------------------|--------|
| Read key | `DATABASE_READ_KEY` | Read endpoints and `/health` |
| Admin key | `DATABASE_ADMIN_KEY` | All write endpoints (and, being a superset, reads) |
| Worker keys | `DATABASE_WORKER_KEYS` | The worker rows above, and nothing else — no reads, no other writes |

The read and admin keys are **mandatory in staging and production** (validated at startup). In `local` mode, if no keys
are configured the endpoints are open for convenience. The Arbitrator authenticates with the admin key via its
`ARBITRATOR_DATABASE_API_KEY` setting.

### Provisioning worker keys

A checker replica holds a worker key rather than the admin key, so its entire database surface is the job rows it owns.
Worker keys are optional: with none provisioned, the worker endpoints still accept the admin key, so adding them only
ever narrows access for the pods that hold one.

`DATABASE_WORKER_KEYS` holds a list rather than a single value, so a fleet can be moved onto a new key with both
accepted for the overlap. Supply it comma-separated or as a JSON array; keys must not themselves contain a comma:

```bash
DATABASE_WORKER_KEYS=outgoing-key,incoming-key
DATABASE_WORKER_KEYS=["outgoing-key","incoming-key"]
```

Generate one with `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`. Each checker service reads its own
copy from `<PREFIX>_DATABASE_WORKER_KEY` (e.g. `OBJECTS_DATABASE_WORKER_KEY`), whose value must appear in this list —
otherwise every claim is rejected with 401, which presents as a replica that is healthy and permanently idle rather
than as a startup failure.

## Environment Settings

The service inherits base settings from [`SettingsBase`](../settings_base.py) and adds its own under the `DATABASE_`
prefix. For local development, settings are loaded from `~/.cosmos_evaluator/.env`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_DB_CONFIG` | JSON string | — | Connection blob: `{ "host", "port", "database", "user", "password", "connect_timeout"?, "echo"? }` |
| `DATABASE_READ_KEY` | string | — | API key granting read access |
| `DATABASE_ADMIN_KEY` | string | — | API key granting write access |
| `DATABASE_WORKER_KEYS` | comma-separated string or JSON array | `[]` | API keys granting access to the worker endpoints only |
| `COSMOS_EVALUATOR_ENV` | `local` \| `dev` \| `staging` \| `production` | `local` | Deployment environment |
| `COSMOS_EVALUATOR_LOG_LEVEL` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` | Logging verbosity |

In `local` mode, if `DATABASE_DB_CONFIG` is not set, connection settings are read from
[`database/config.yaml`](../../database/config.yaml), with credentials resolved from
`COSMOS_EVALUATOR_LOCAL_DB_USER` / `COSMOS_EVALUATOR_LOCAL_DB_PASSWORD`, so a standalone dev run auto-connects to the
local Postgres container. An explicitly injected `DATABASE_DB_CONFIG` always wins.

## Run the REST API on `localhost`

```bash
dazel run //services/database:rest_api -- --help
usage: rest_api.py [-h] [--host HOST] [--port [1-65535]] [--log-level {DEBUG,INFO,WARNING,ERROR}]

Run the Database REST API

options:
  -h, --help            show this help message and exit
  --host HOST           Host to bind to
  --port [1-65535]      Port to bind to
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level
```

To bring up the Database REST API together with the Arbitrator and the checker services (all wired up), run the full
local stack with `dazel run //services:rest_apis`.

## Release and Deployment

See the [Deployment Guide](../../docs/deployment.md#orchestration-layer) for building, tagging, pushing, and running
the orchestration containers in production.
