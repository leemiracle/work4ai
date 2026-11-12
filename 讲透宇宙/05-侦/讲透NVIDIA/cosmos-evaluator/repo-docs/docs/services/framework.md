# Service Framework

The Cosmos Evaluator service framework provides building blocks for wrapping evaluation checks as REST API microservices. Each service follows a consistent pattern: receive a request, validate it, run the check, and return formatted results.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
│                                                     │
│   GET /health     POST /process     GET /config     │
└────────┬──────────────┬──────────────────┬──────────┘
         │              │                  │
         │    ┌─────────▼──────────┐       │
         │    │  RequestHandler    │       │
         │    │  (parse & validate)│       │
         │    └─────────┬──────────┘       │
         │              │                  │
         │    ┌─────────▼──────────┐       │
         │    │    ServiceBase     │       │
         │    │(validate & process)│       │
         │    └─────────┬──────────┘       │
         │              │                  │
         │    ┌─────────▼──────────┐       │
         │    │ ResponseFormatter  │       │
         │    │  (format response) │       │
         │    └────────────────────┘       │
         │                                 │
    ┌────▼─────────────────────────────────▼──┐
    │           StorageProvider                │
    │    (upload results, download inputs)     │
    └─────────────────────────────────────────┘
```

## Core Components

### ServiceBase

The abstract base class that all checker services inherit from. Defines the contract every service must implement.

```python
from services.framework.service_base import ServiceBase

class MyService(ServiceBase[MyRequest, MyResult]):

    async def validate_input(self, request: MyRequest) -> bool:
        """Validate that the request data is processable.
        Return True if valid. Raise an exception with details if not."""
        ...

    async def process(self, request: MyRequest) -> MyResult:
        """Run the evaluation logic. Returns the result."""
        ...
```

`ServiceBase` is generic over `RequestType` and `ResponseType` — both should be Pydantic `BaseModel` subclasses.

It also provides:
- A pre-configured `self.logger` for structured logging
- `cleanup(output_dir)` to remove temporary directories after processing

### Protocols

The framework defines three protocol interfaces. These are runtime-checkable Python protocols, so you can implement them however you like as long as the method signatures match.

#### RequestHandler

Parses and validates incoming HTTP requests into your domain model.

```python
class RequestHandler(Protocol[RequestType]):
    async def parse(self, raw_request: Any) -> RequestType: ...
    async def validate(self, request_data: RequestType) -> bool: ...
    def get_content_type(self) -> str: ...
```

**Built-in implementation:** `JsonRequestHandler` — Parses JSON request bodies into Pydantic models.

#### ResponseFormatter

Formats service responses into a consistent envelope.

```python
class ResponseFormatter(Protocol[ResponseType]):
    async def format_success(self, data: Any, metadata: dict | None = None) -> ResponseType: ...
    async def format_error(self, error: Exception, status_code: int = 500) -> ResponseType: ...
    async def format_progress(self, progress: float, message: str = "") -> ResponseType: ...
    def get_content_type(self) -> str: ...
```

**Built-in implementation:** `JsonResponseFormatter` — Wraps responses in a standard JSON envelope:

**Success response:**

```json
{
  "success": true,
  "data": { ... },
  "metadata": { ... },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Error response:**

```json
{
  "success": false,
  "error": {
    "type": "ValueError",
    "message": "Invalid input",
    "code": null,
    "details": null
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

Additional methods on `JsonResponseFormatter`:
- `format_validation_error(validation_errors, status_code=422)` — For Pydantic validation failures
- `format_paginated_response(items, total, page, page_size)` — For paginated list endpoints

#### StorageProvider

Cloud-agnostic interface for storing and retrieving files and data.

```python
class StorageProvider(Protocol):
    async def store(self, data: Any, key: str, metadata: dict | None = None) -> str: ...
    async def retrieve(self, key: str) -> Any: ...
    async def delete(self, key: str) -> bool: ...
    async def exists(self, key: str) -> bool: ...
    def list_keys(self, prefix: str = "") -> AsyncIterator[str]: ...
    async def store_file(self, file_path: Path, key: str, ...) -> StorageUrls: ...
    async def generate_presigned_url(self, key: str, ...) -> str: ...
    async def download_from_url(self, url: str, destination: Path) -> Path: ...
```

**Built-in implementations:**
- `LocalStorageProvider` — File system storage (good for development)
- `S3StorageProvider` — AWS S3 with presigned URL support
- `AzureBlobStorageProvider` — Azure Blob Storage with account-key or SAS-token auth and SAS presigned URLs
- `StorageProviderFactory` — Creates the right provider based on settings

Each direction is selected independently via `COSMOS_EVALUATOR_{INPUT,OUTPUT}_STORAGE_TYPE` (`local`, `s3`, or `azure`),
falling back to `COSMOS_EVALUATOR_STORAGE_TYPE`. See
[storage_providers/README.md](../../services/framework/storage_providers/README.md) for the per-backend settings
mapping and the `download_from_url` scope notes.

`StorageUrls` is a dataclass with `raw` (permanent) and `presigned` (temporary access) URL fields.

### SettingsBase

Base class for service configuration using Pydantic Settings:

```python
from services.settings_base import SettingsBase

class Settings(SettingsBase):
    my_custom_setting: str = Field(default="value")

    model_config = SettingsConfigDict(
        env_prefix="MYCHECKER_",
        ...
    )
```

Common settings inherited from `SettingsBase`:

| Setting | Env Variable | Default | Description |
|---------|-------------|---------|-------------|
| `env` | `COSMOS_EVALUATOR_ENV` | `local` | Environment: `local` for development |
| `log_level` | `COSMOS_EVALUATOR_LOG_LEVEL` | `INFO` | Logging level |
| `storage_type` | `COSMOS_EVALUATOR_STORAGE_TYPE` | `s3` | Storage backend: `s3`, `azure` or `local` |
| `storage_url` | `COSMOS_EVALUATOR_STORAGE_URL` | — | Target address: bucket or container, plus the account, endpoint and region the URL carries |
| `storage_access_key` | `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY` | — | S3 access key ID |
| `storage_secret_key` | `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` | — | S3 secret access key, or the Azure account key |
| `storage_session_token` | `COSMOS_EVALUATOR_STORAGE_SESSION_TOKEN` | — | S3 session token, or an Azure SAS token |

In `local` environment, credentials are automatically loaded from `~/.cosmos_evaluator/.env`.

### API key gate

`install_api_key_auth` (`services/framework/auth.py`) puts a single service-wide key in front of an app; the checkers
built by `build_checker_app` and the arbitrator all install it. The key comes from
`COSMOS_EVALUATOR_STAGING_API_KEY` / `COSMOS_EVALUATOR_PROD_API_KEY` (or a service-prefixed override), selected by
`COSMOS_EVALUATOR_ENV`. With no key set — the local and dev default — the gate is a no-op and every endpoint is open.

With a key set, requests need an `X-API-Key` header matching it or they get a 401. `/health` stays open so probes and
arbitrator service discovery keep working, `/metrics` so scrapers that have nowhere to put a key can still read it, as
does the docs surface (`/docs`, `/openapi.json`, `/redoc`). The key is
declared as a security scheme in the OpenAPI document, so `/docs` shows an **Authorize** button: paste the key there
once and Swagger UI attaches the header to every "Try it out" on the page.

This coarse gate is unrelated to the Database REST API's role-based keys (`DATABASE_READ_KEY` / `DATABASE_ADMIN_KEY` /
`DATABASE_WORKER_KEYS`), which stay per-endpoint.

## Standard Endpoints

Every Cosmos Evaluator service exposes at least the first three endpoints below, and services built by `build_checker_app` also expose `GET /metrics`. Individual services may add more.

### `GET /health`

Returns service status for monitoring and service discovery.

```json
{
  "success": true,
  "data": {
    "service": "objects",
    "status": "healthy",
    "version": "1.1.0",
    "environment": "local"
  }
}
```

### `POST /process`

The main processing endpoint. Accepts a request, runs the check, and returns results.

The request and response models are service-specific (see individual check documentation). The response is always wrapped in the standard envelope.

### `GET /config`

Returns the default configuration for the checker, useful for clients to discover available options.

```json
{
  "success": true,
  "data": {
    "default_config": {
      "av.objects_single_view": { ... }
    }
  }
}
```

### `GET /metrics`

Prometheus text exposition (`text/plain; version=0.0.4`) of **this replica's** occupancy — not the deployment's. Scrapers address pods directly rather than through the gateway, so the fleet-wide view comes from summing across targets. Every series carries a `checker` label holding the qualified checker name, matching the label the arbitrator exports for the same checker so demand and capacity can be correlated without relabeling.

```text
# HELP checker_slots_active Processing slots currently in use on this replica.
# TYPE checker_slots_active gauge
checker_slots_active{checker="av.objects_single_view"} 1
# HELP checker_slots_limit Configured processing slot ceiling for this replica.
# TYPE checker_slots_limit gauge
checker_slots_limit{checker="av.objects_single_view"} 2
# HELP checker_jobs_in_flight Claimed jobs this replica is running detached and holding a lease on. ...
# TYPE checker_jobs_in_flight gauge
checker_jobs_in_flight{checker="av.objects_single_view"} 1
```

Unlike the other three, this response is not wrapped in the JSON envelope: the exposition format is fixed by the scraper.

## Running Services

```bash
# All services together
dazel run //services:rest_apis

# Individual services
dazel run //services/objects/single_view:rest_api

# With custom port
dazel run //services/objects/single_view:rest_api -- --port 9000
```

Default ports (local development):

| Service | Port |
|---------|------|
| Arbitrator | 8080 |
| Objects Single View | 8082 |
| Database REST API | 8087 |

For how the Arbitrator and Database REST API coordinate checkers and record results, see the
[Orchestration Layer Guide](orchestration.md).

## Example: Calling the Objects Service

```bash
# Check health
curl http://localhost:8082/health

# Get default config
curl http://localhost:8082/config

# Process a request. The clip_id is auto-derived from the RDS-HQ archive (not a request field), so
# rds_hq_url must be a single-clip zip with its layer folders (pose/, ftheta_intrinsic/, ...) at the top
# level. world_model_video_url is optional: provide it to run the static (CWIP) check two-stream, or omit it
# to run camera-only (the static check on the camera stream alone, presence derived from the type head). The
# repo ships a ready-made fixture, checks/sample_data/rds_hq_single_clip.zip, paired with the 0d21d408
# world/augmented sample videos. Paths must be readable by the Objects service; see checks/objects.md for the
# mounted-path (/data) Docker variant.
curl -X POST http://localhost:8082/process \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "camera_front_wide_120fov",
    "rds_hq_url": "checks/sample_data/rds_hq_single_clip.zip",
    "augmented_video_url": "checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4",
    "world_model_video_url": "checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4"
  }'

# Camera-only: omit world_model_video_url to run the static check on the camera stream alone. The
# static check then runs on the camera stream alone, with no world-model reference downloaded.
curl -X POST http://localhost:8082/process \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "camera_front_wide_120fov",
    "rds_hq_url": "checks/sample_data/rds_hq_single_clip.zip",
    "augmented_video_url": "checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4"
  }'
```

## Building a Custom Service

See the [Custom Checker Tutorial](../tutorials/custom_checker.md) for a complete walkthrough of building a new checker service from scratch.

The general steps are:

1. **Define models** — Pydantic request/response models
2. **Implement service** — Subclass `ServiceBase` with your check logic
3. **Configure settings** — Subclass `SettingsBase` for service-specific config
4. **Build REST API** — FastAPI app with `/health`, `/process`, `/config` endpoints
5. **Create BUILD file** — Bazel targets for library, binary, and tests

The Objects service in `services/objects/single_view/` serves as a reference implementation.
