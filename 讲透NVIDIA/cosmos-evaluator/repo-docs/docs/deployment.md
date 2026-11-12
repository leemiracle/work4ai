# Deployment

This guide covers how to build, tag, push, and run Cosmos Evaluator service containers for production environments. Each checker runs as an independent container exposing a REST API. The default port is configurable via the `UVICORN_PORT` environment variable.

## AWS Quick Start

The rest of this guide starts at `git clone` and assumes a provisioned GPU host, an S3 bucket, and credentials. If you are standing up a fresh AWS environment, the following is the minimal setup that runs the GPU-backed checkers. Cosmos Evaluator ships no Terraform/Helm/CloudFormation — these are one-time manual steps.

- **Instance + AMI:** a GPU instance is required for the Objects and Physical Plausibility checks with their default configurations. A `g5.xlarge` (NVIDIA A10G, 24 GB) in `us-west-2` on the **Deep Learning Base GPU AMI (Ubuntu 22.04)** is a known-good Objects baseline — it ships the NVIDIA driver, Docker, and the NVIDIA Container Toolkit. Size Physical Plausibility deployments for the configured batch size. Hallucination and Attribute Verification are CPU-only and can run on a smaller instance.
- **Storage:** create an S3 bucket for inputs and outputs (e.g. `s3://<your-bucket>`), in the same region as the instance.
- **Credentials via instance role (recommended):** attach an EC2 instance-role (instance profile) to the box rather than baking static keys into the containers. A minimal policy grants read/write on the bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::<your-bucket>",
        "arn:aws:s3:::<your-bucket>/*"
      ]
    }
  ]
}
```

  With the role attached and the static `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY`/`_SECRET_KEY` left unset, the checkers resolve credentials through boto3's default chain, which ends at the instance role (see [Storage Provider](#storage-provider)).
- **IMDS hop limit (required for containers):** a container on the default Docker bridge network is one network hop away from the EC2 instance metadata service, so the instance role is unreachable unless the metadata hop limit is raised to `2`:

```bash
aws ec2 modify-instance-metadata-options \
  --instance-id <instance-id> \
  --http-put-response-hop-limit 2 \
  --http-endpoint enabled
```

  Without this, boto3 (and `multistorageclient`) silently fall through to "no credentials" even though the role is attached.

Once the host, bucket, role, and hop limit are in place, continue with the build and run steps below.

## Services Overview

| Service | Image Tag | GPU Required | Default Port |
|---------|-----------|:------------:|:------------:|
| Objects | `objects-checker:1.1.0` | Yes | 8000 |
| Hallucination | `hallucination-checker:1.1.0` | No | 8080 |
| Attribute Verification | `attribute-verification-checker:1.1.0` | No | 8080 |
| Physical Plausibility | `physical-plausibility-checker:1.1.0` | Yes | 8000 |

The table lists locally built image tags. Physical Plausibility also has a published image at
`nvcr.io/nvidia/cosmos/physical-plausibility-checker:1.1.1`; see
[Physical Plausibility](#physical-plausibility) for its checkpoint mount and remote-video setup.

To run the checkers behind a coordinator that fans out a single request to multiple checkers and records results, see
the [Orchestration Layer](#orchestration-layer) section below.

## Building Container Images

Set up the build environment, then use `dazel run` to build and load each image into the local Docker daemon:

```bash
source tools/env_setup.sh

dazel run //services/objects/single_view:image_load
dazel run //services/hallucination:image_load
dazel run //services/attribute_verification:image_load
dazel run //services/physical_plausibility:image_load
```

For detailed build and run instructions per service, see the individual checker documentation:

| Service | Documentation |
|---------|---------------|
| Objects | [Objects Check — Docker Container](checks/objects.md#docker-container) |
| Hallucination | [Hallucination Check](checks/hallucination.md) |
| Attribute Verification | [Attribute Verification Check](checks/attribute_verification.md) |
| Physical Plausibility | [Physical Plausibility Check](checks/physical_plausibility.md) |

## Tagging and Pushing to a Registry

After building and loading the images locally, tag and push them to any OCI-compatible container registry:

```bash
# Tag the images for your registry
docker tag objects-checker:1.1.0 your-registry.example.com/cosmos-evaluator/objects:1.1.0
docker tag hallucination-checker:1.1.0 your-registry.example.com/cosmos-evaluator/hallucination-checker:1.1.0
docker tag attribute-verification-checker:1.1.0 your-registry.example.com/cosmos-evaluator/attribute-verification-checker:1.1.0
docker tag physical-plausibility-checker:1.1.0 your-registry.example.com/cosmos-evaluator/physical-plausibility-checker:1.1.0

# Push to the registry
docker push your-registry.example.com/cosmos-evaluator/objects:1.1.0
docker push your-registry.example.com/cosmos-evaluator/hallucination-checker:1.1.0
docker push your-registry.example.com/cosmos-evaluator/attribute-verification-checker:1.1.0
docker push your-registry.example.com/cosmos-evaluator/physical-plausibility-checker:1.1.0
```

Replace `your-registry.example.com/cosmos-evaluator` with your actual registry path (e.g., an ECR, GCR, ACR, or NVCR endpoint).

## Environment Configuration for Production

Please add the following environment variables to a `~/.cosmos_evaluator/.env` file for your deployment environment configuration:

### Port Configuration

The `UVICORN_PORT` environment variable controls the port the service listens on inside the container. This is useful when running multiple services on the same host or behind a load balancer:

```bash
docker run -e UVICORN_PORT=9000 -p 9000:9000 objects-checker:1.1.0
```

If not set, the service uses its default port (8000 or 8080 depending on the service).

### Storage Provider

The Objects check uses S3 as the storage backend for staging or production:

| Variable | Description |
|----------|-------------|
| `COSMOS_EVALUATOR_ENV` | Set to `production` or `staging` |
| `COSMOS_EVALUATOR_STORAGE_TYPE` | Storage backend: `s3` (default) or `local` |
| `COSMOS_EVALUATOR_STORAGE_URL` | Target address, e.g. `https://my-bucket.s3.us-west-2.amazonaws.com` |
| `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY` | S3 access key ID (**optional** — see note below) |
| `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` | S3 secret access key, or the Azure account key (**optional** for S3 — see note below) |

> **Note:** `COSMOS_EVALUATOR_STORAGE_TYPE=local` is not recommended for cloud deployments.

> **Credentials are optional.** The access/secret key variables can be omitted. When they are unset, the S3 provider falls back to boto3's default credential chain (`AWS_*` env vars → `~/.aws/credentials` → container/task credentials → **EC2 IMDS instance role**), so an attached instance profile supplies credentials automatically — the recommended pattern on AWS. Set them only when you need static keys (e.g. an external S3-compatible store). On EC2, remember the [IMDS hop limit](#aws-quick-start) must be `2` for containers to reach the instance role.

### API Keys

The Attribute Verification check requires API keys when its model endpoints use authentication. Role-specific keys are
recommended so the LLM and VLM credentials can be configured and rotated independently:

| Variable | Used By | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | Attribute Verification | Recommended API key for the question-generation LLM endpoint |
| `VLM_API_KEY` | Attribute Verification | Recommended API key for the visual-verification VLM endpoint |
| `BUILD_NVIDIA_API_KEY` | Attribute Verification | Legacy shared fallback when the corresponding role-specific key is unset |

If both endpoints accept the same credential, set that value in both recommended variables. A model configuration may
instead set `api_key_env` to the name of a custom environment variable; that variable must also be injected into the
Attribute Verification container. Local unauthenticated endpoints do not require a key.

### Multistorage Configuration

The Hallucination, Attribute Verification, and Physical Plausibility checks use [NVIDIA Multistorage](https://nvidia.github.io/multi-storage-client/references/configuration.html) to access video inputs from cloud storage. Configure it via the `MULTISTORAGECLIENT_CONFIGURATION` environment variable in `~/.cosmos_evaluator/.env`.

| Variable | Used By | Description |
|----------|---------|-------------|
| `MULTISTORAGECLIENT_CONFIGURATION` | Hallucination, Attribute Verification, Physical Plausibility | JSON configuration for storage backend connectivity |

The value is a JSON object that defines storage profiles and path mappings.

When setting this in the `.env` file, compact the JSON onto a single line and wrap it in single quotes to avoid parsing issues.

For more information, see the [Multistorage Configuration Example](getting_started.md#multistorage-configuration-example).

## Running in Production

### Objects (GPU required)

Set `OBJECTS_PROCESS_CONCURRENCY_LIMIT` to control the maximum number of concurrent `/process` requests (default: 3) based on the load your cloud machine can handle concurrently. Requests beyond this limit are rejected immediately with a 503 status.

```bash
docker run \
  --gpus all \
  --env-file ~/.cosmos_evaluator/.env \
  -e OBJECTS_PROCESS_CONCURRENCY_LIMIT=1 \
  -p 8000:8000 \
  objects-checker:1.1.0
```

> Requires [Storage Provider](#storage-provider) configuration in the env file.

### Hallucination

```bash
docker run \
  --env-file ~/.cosmos_evaluator/.env \
  -p 8080:8080 \
  hallucination-checker:1.1.0
```

> Requires [`MULTISTORAGECLIENT_CONFIGURATION`](#multistorage-configuration) in the env file.

### Attribute Verification

```bash
docker run \
  --env-file ~/.cosmos_evaluator/.env \
  -p 8080:8080 \
  attribute-verification-checker:1.1.0
```

> With the default authenticated endpoints, set [`LLM_API_KEY` and `VLM_API_KEY`](#api-keys). Remote media also requires
> [`MULTISTORAGECLIENT_CONFIGURATION`](#multistorage-configuration). The legacy `BUILD_NVIDIA_API_KEY` remains supported.

### Physical Plausibility

Set the batch and concurrency limits to values that fit the available GPU memory. The service defaults to four
admitted jobs and queue batches of up to four requests. Videos within each batch are encoded individually.

To use the published `1.1.1` image, first export a compatible classifier bundle using the
[training notebook](tutorials/train_physical_plausibility_checker.ipynb), or provide an existing compatible bundle.
Create a `.env` file containing:

```dotenv
PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI=/models/checker.pt
MULTISTORAGECLIENT_CONFIGURATION=<your-multistorage-client-JSON-configuration>
```

Replace the configuration placeholder with your [Multistorage configuration](#multistorage-configuration) and
the credentials required to read the remote video. Mount the absolute path to the exported classifier file:

```bash
docker run --rm --gpus all --env-file .env \
  -v /absolute/path/to/checker.pt:/models/checker.pt:ro \
  -e COSMOS_EVALUATOR_STORAGE_TYPE=local \
  -p 8000:8000 \
  nvcr.io/nvidia/cosmos/physical-plausibility-checker:1.1.1
```

Access to the published image is required. The classifier bundle is separate from the public video encoder,
which downloads from GitHub and Meta on first use. The `local` storage setting configures the framework's storage
provider; remote inputs still use Multistorage. For local video inputs, mount the video directory and omit the
Multistorage configuration if the checkpoint is also local.

After model initialization, submit a video:

```bash
curl -sS -X POST http://localhost:8000/process \
  -H 'Content-Type: application/json' \
  --data '{
    "clip_id": "example-clip",
    "video_url": "s3://<bucket-name>/path/to/video.mp4",
    "config": {"bad_threshold": 0.4}
  }'
```

Omit `config.bad_threshold` to use the startup configuration or the checkpoint's saved threshold. The result
includes the threshold used. See the [checker guide](checks/physical_plausibility.md#run-a-published-image-with-an-s3-video)
for the full published-image workflow, including the Linux host-network option.

If you built the image from this checkout, use the local `1.1.0` tag instead:

```bash
docker run --rm \
  --gpus all \
  --env-file ~/.cosmos_evaluator/.env \
  -e COSMOS_EVALUATOR_STORAGE_TYPE=local \
  -e PHYSICAL_PLAUSIBILITY_MAX_BATCH_SIZE=4 \
  -p 8000:8000 \
  physical-plausibility-checker:1.1.0
```

> The default classifier is hosted in a public Hugging Face repository and does not require `HF_TOKEN`. Alternatively,
> supply a compatible checkpoint with `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI`; mount the model directory when using
> a local path. The encoder downloads separately from GitHub and Meta. Remote inputs require
> [Multistorage configuration](#multistorage-configuration). See the
> [Physical Plausibility Check guide](checks/physical_plausibility.md#build-and-run-the-container) for a complete local example.

### Verifying the Service

All services expose a `/health` endpoint for liveness and readiness checks:

```bash
curl http://localhost:8000/health
```

Each service also provides a Swagger UI at `/docs` for browsing the API documentation and testing endpoints from a browser:

```
http://localhost:8000/docs
```

## Orchestration Layer

The orchestration layer lets a single request fan out to multiple checkers and records every result durably. It adds
three containers on top of the checker services. For a conceptual overview (architecture, dependency graph,
per-camera fan-out), see the [Orchestration Layer guide](services/orchestration.md).

| Component | Image Tag | Build Target | GPU Required | Container Port |
|-----------|-----------|--------------|:------------:|:--------------:|
| Arbitrator | `arbitrator:1.1.0` | `//services/arbitrator:image_load` | No | 8000 |
| Database REST API | `database:1.1.0` | `//services/database:image_load` | No | 8000 |
| PostgreSQL | `database-postgres:1.2.0` | `//database:image_load` | No | 5432 |

### Building the Orchestration Images

```bash
source tools/env_setup.sh

dazel run //services/arbitrator:image_load
dazel run //services/database:image_load
dazel run //database:image_load
```

### Tagging and Pushing to a Registry

```bash
# Retag for your registry, then push
docker tag arbitrator:1.1.0 your-registry.example.com/cosmos-evaluator/arbitrator:1.1.0
docker tag database:1.1.0 your-registry.example.com/cosmos-evaluator/database-rest-api:1.1.0        # //services/database
docker tag database-postgres:1.2.0 your-registry.example.com/cosmos-evaluator/postgres:1.2.0        # //database

docker push your-registry.example.com/cosmos-evaluator/arbitrator:1.1.0
docker push your-registry.example.com/cosmos-evaluator/database-rest-api:1.1.0
docker push your-registry.example.com/cosmos-evaluator/postgres:1.2.0
```

### Environment Configuration

Add these variables to `~/.cosmos_evaluator/.env` (or pass them per container). The PostgreSQL container uses its own
`POSTGRES_*` contract rather than the `COSMOS_EVALUATOR_*` settings — see the
[PostgreSQL container README](../database/README.md).

**PostgreSQL container**

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Application role to create (limited privileges) |
| `POSTGRES_PASSWORD` | Password for the application role |
| `POSTGRES_DB` | Target database name to create / restore into |
| `BACKUP_FILE` | Optional path to a `pg_dump -Fc` archive to restore on first start |

**Database REST API**

| Variable | Description |
|----------|-------------|
| `DATABASE_DB_CONFIG` | JSON connection blob: `{ "host", "port", "database", "user", "password" }` (matching the Postgres role above) |
| `DATABASE_READ_KEY` | API key granting read access (mandatory in staging/production) |
| `DATABASE_ADMIN_KEY` | API key granting write access (mandatory in staging/production) |

**Arbitrator**

| Variable | Description |
|----------|-------------|
| `COSMOS_EVALUATOR_CHECKER_ENDPOINTS` | JSON object mapping checker base name to base URL (required) |
| `COSMOS_EVALUATOR_DATABASE_API_URL` | Base URL of the Database REST API (empty disables recording) |
| `ARBITRATOR_DATABASE_API_KEY` | API key sent to the Database REST API (must match its `DATABASE_ADMIN_KEY`) |
| `ARBITRATOR_QUEUE_CAPACITY` | Optional cap on combined queued + in-flight requests per replica |

### Running in Production

Start the containers in dependency order: **PostgreSQL → Database REST API → checkers → Arbitrator**. The Arbitrator
probes each checker's `/health` and requires the Database REST API to be reachable before it will accept requests.

```bash
# 1. PostgreSQL
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=cosmos_evaluator \
  -v postgres-data:/var/lib/postgresql/data \
  database-postgres:1.2.0

# 2. Database REST API
docker run -d --name database-rest-api \
  --env-file ~/.cosmos_evaluator/.env \
  -p 8087:8000 \
  database:1.1.0   # the //services/database image

# 3. Checker services (see the sections above), then the Arbitrator
docker run -d --name arbitrator \
  --env-file ~/.cosmos_evaluator/.env \
  -p 8080:8000 \
  arbitrator:1.1.0
```

> The Arbitrator requires [`COSMOS_EVALUATOR_CHECKER_ENDPOINTS`](#environment-configuration) and a reachable
> [`COSMOS_EVALUATOR_DATABASE_API_URL`](#environment-configuration) in the env file; the Database REST API requires
> [`DATABASE_DB_CONFIG`](#environment-configuration) and its API keys.

Submit work to the Arbitrator with `POST /process/async` and poll `GET /executions/{request_id}` (see the
[Orchestration Layer guide](services/orchestration.md#arbitrator)). All orchestration services expose `/health` and a
Swagger UI at `/docs`, the same as the checker services.
