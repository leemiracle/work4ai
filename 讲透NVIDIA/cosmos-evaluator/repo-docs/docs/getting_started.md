# Getting Started with Cosmos Evaluator

## Prerequisites

- **Docker** — Required for the Dazel (Bazel-in-Docker) build system
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/)
  - macOS: [Colima](https://github.com/abiosoft/colima) with QEMU (see [macOS Setup](customization.md#macos-setup) for more information)
- **NGC API Key** — Required to pull the prebuilt docker images for the checkers
  - Click links for [create or login to an NGC account](https://ngc.nvidia.com/signin), and [create an API key](https://org.ngc.nvidia.com/setup/api-keys).
  - Docker login to nvcr.io by following the steps found in [create an API key](https://org.ngc.nvidia.com/setup/api-keys).
- **NVIDIA GPU with CUDA** — Required for the default Objects and Physical Plausibility configurations. CPU mode is available but significantly slower.
- **Git** — To clone the repository
- **Git LFS** — Required for the repo’s sample data under `checks/sample_data/` **and the Objects check models** (SegFormer under `checks/utils/models/segformer/` and CWIP under `checks/utils/models/cwip/checkpoints/`). Those files are stored as LFS pointers; without `git lfs pull`, checkers see small pointer files instead of the real assets and fail with opaque errors (e.g. FFmpeg “moov atom not found” for videos, or a checkpoint-loading error for the models).
- **Storage Provider Credentials** — Checkers require a connection to a storage provider (S3 is recommended) to store video and data inputs. Ensure you have an S3 bucket set up and have credentials with read access to S3.
- **Endpoints for LLM and VLM** — The attribute verification checker requires connections to a _deployed_ LLM and VLM.
  - See the [Setting up your LLM and VLM API key](#setting-up-your-llm-and-vlm-api-key) section to get free, limited access to these endpoints for testing through [build.nvidia.com](https://build.nvidia.com/).
  - See the [Deploy Cosmos Reason 2 NIM](https://build.nvidia.com/nvidia/cosmos-reason2-8b/deploy) to deploy Cosmos Reason 2 or any other VLM on your own infrastructure and leverage these endpoints.

## Clone the repo
```bash
git clone https://github.com/NVIDIA/cosmos-evaluator.git
cd cosmos-evaluator
```

Pull the LFS-tracked assets — the sample data in `checks/sample_data/` and the Objects check models (SegFormer + CWIP) under `checks/utils/models/` — with Git LFS:

```bash
# Install Git LFS if it isn't already (Debian/Ubuntu shown; use brew/dnf on other platforms)
sudo apt-get install -y git-lfs

git lfs install
git lfs pull
```

Without this step, those files remain LFS pointers and checks will fail (e.g. “moov atom not found” when processing sample video, or a checkpoint-loading error when the Objects check tries to load the SegFormer/CWIP models).

## Repo Setup

### Minimum Requirements

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| **Python 3** | 3.10+ | Must be available as `python3` |
| **Docker** | 28.1.1+ | [Docker Engine](https://docs.docker.com/engine/install/) on Linux, [Colima](https://github.com/abiosoft/colima) on macOS |
| **Git** | 2.49.0 (recommended) | For cloning and LFS support. Not a hard minimum — older versions (e.g. 2.34.1 on the stock AWS Deep Learning GPU AMI) clone and build fine; `env_setup.sh` only *warns* below this version. |
| **Git LFS** | 3.0+ | Required for `checks/sample_data/` (video and other binaries) and the Objects check models (SegFormer + CWIP) |
| **NVIDIA GPU Driver** | 570.124.06+ | Required for GPU-accelerated checks (Objects and Physical Plausibility) |
| **NVIDIA Container Toolkit** | 1.16.2+ | Required for `--gpus` flag in Docker |

GPU-related requirements are only needed for checks that use GPU inference (Objects and Physical Plausibility by default). The Hallucination and Attribute Verification checks can run without a GPU.

### Build Environment

Cosmos Evaluator uses **Dazel** (Bazel-in-Docker) for hermetic, reproducible builds. All build commands (`dazel build`, `dazel test`, `dazel run`) execute Bazel inside a Docker container, so you don't need to install Bazel locally.

To set up the build environment, source the setup script from the repo root:

```bash
. tools/env_setup.sh
```

This script:
1. Validates that all required tools are installed and meet minimum version requirements
2. Registers the `dazel` command in your shell (with tab completion for bash/zsh)
3. Sets the `COSMOS_EVALUATOR_ROOT` environment variable

You need to re-source this script in each new terminal session. Verify the setup by running:

```bash
dazel info
```

For macOS-specific setup (Colima, `user.dazelrc`), see the [Customization Guide](customization.md#macos-setup).

### Objects Check Models (Git LFS)

The Objects check uses two models, both **bundled with the repository** via [Git LFS](https://git-lfs.com/) — no separate download is required, and each is loaded automatically at runtime:

- **SegFormer** (dynamic processor) — an ONNX semantic-segmentation model at `checks/utils/models/segformer/cityformer_final_1024_dynamic_input_v11_sim.onnx`.
- **CWIP** (static processor) — Contrastive World-Image Pre-training weights in HuggingFace format (`config.json` + `model.safetensors`) at `checks/utils/models/cwip/checkpoints/`, used when a world-model video is supplied.

Make sure Git LFS is installed before cloning (or run `git lfs pull` in an existing clone) so the model files are materialized instead of being left as pointers.

### Building and Testing

Build all targets in the repo:

```bash
dazel build //...
```

> **First build is slow.** The initial hermetic build pulls a multi-GB build image and compiles everything from cold, so expect roughly **10–15 minutes** (network-dependent). Subsequent warm-cache builds/relaunches typically complete in **~2–3 minutes**.

Run the full test suite:

```bash
dazel test //...
```

`dazel` is a drop-in replacement for `bazel` — any `bazel` command you see in documentation or tutorials works the same way by substituting `dazel`. For more information on available commands and target syntax, see the [Bazel documentation](https://bazel.build/run/build).

## Run the Full Local Stack

The bundled multi-service target launches the Arbitrator, Database REST API, and its included checker services on `localhost` in a single command, using the local machine's CPU/GPU.

```bash
# One-time per shell: register the `dazel` command and bootstrap the local database image
. tools/env_setup.sh

# Launch the bundled services concurrently
dazel run //services:rest_apis
```

`. tools/env_setup.sh` also runs `dazel run //database:image_load` once (per version bump) to build the local PostgreSQL image that backs the Arbitrator's result recording.

> **Before you launch — set two things in `~/.cosmos_evaluator/.env`:**
> 1. **Storage type**, or Objects Single View won't start. With no storage configured it defaults to S3 and aborts at startup with `Storage URL is empty for 's3' storage`, so the health loop below only ever reaches **4/5** services healthy. For a purely local run set `COSMOS_EVALUATOR_STORAGE_TYPE=local`; to read/write real S3 inputs instead, set `COSMOS_EVALUATOR_STORAGE_URL` (credentials are optional — see the [storage credentials](#storage-and-credentials) appendix).
> 2. **Local database credentials**, or the Arbitrator's `POST /process/async` returns `503 Database is not available` — see [Enable the local database](#enable-the-local-database-required-for-the-arbitrator) below.

The services listen on the following ports (defined in `services/local_ports.bzl` and set per service via `UVICORN_PORT`):

| Service | Port | URL |
|---------|------|-----|
| Arbitrator (entrypoint) | 8080 | http://localhost:8080 |
| Objects Single View | 8082 | http://localhost:8082 |
| Hallucination | 8085 | http://localhost:8085 |
| Attribute Verification | 8086 | http://localhost:8086 |
| Database REST API | 8087 | http://localhost:8087 |

Wait for every service to report healthy before sending requests:

```bash
for p in 8080 8082 8085 8086 8087; do
  until curl -sf -o /dev/null "http://localhost:$p/health"; do sleep 2; done
  echo "port $p healthy"
done
```

Submit an end-to-end evaluation to the Arbitrator with `POST /process/async`, then poll `GET /executions/{request_id}` (see the [Arbitrator Service](../services/arbitrator/README.md) and the [Orchestration Layer Guide](services/orchestration.md)).

### Enable the local database (required for the Arbitrator)

The Arbitrator records every client, execution, and checker execution through the Database REST API. If the local database is not wired up, all services still report healthy, but `POST /process/async` fails at runtime with a `503 Database is not available` error (no `request_id` can be issued). The individual checker services (`POST /process` on ports 8082/8085/8086) do **not** need the database — only the Arbitrator's `POST /process/async` orchestration flow does.

To enable it, set local-database credentials in `~/.cosmos_evaluator/.env` **before** launching the stack:

```bash
mkdir -p ~/.cosmos_evaluator
cat >> ~/.cosmos_evaluator/.env << 'EOF'
COSMOS_EVALUATOR_LOCAL_DB_USER=cosmos
COSMOS_EVALUATOR_LOCAL_DB_PASSWORD=change-me
EOF
```

With these credentials set (and the `database` image loaded by `. tools/env_setup.sh`), `dazel run //services:rest_apis` auto-starts a `cosmos-eval-local-db` PostgreSQL sidecar and points the Database REST API at it. If the credentials are absent, the sidecar is skipped **silently**, so set them before your first `POST /process/async`. To reset the local database, run `docker rm -f cosmos-eval-local-db && docker volume rm cosmos-eval-local-db-data`.

## Test the Checkers

This section documents how to configure and run the prebuilt docker image for an **individual** checker — an alternative to the [full local stack](#run-the-full-local-stack) above when you only need one checker in isolation.

All services provide a Swagger UI at `/docs` on their own port for browsing the API documentation and testing endpoints from a browser. When running the [full local stack](#run-the-full-local-stack) use the per-service port (e.g., `http://localhost:8082/docs` for Objects Single View); when running a standalone checker container it defaults to `http://localhost:8000/docs`.

### Hallucination Check

#### Setup Environment Variables

The Hallucination check requires the NVIDIA Multistorage configuration to be set. Multistorage is used to connect the checker to various different storage backends through a single, unified configuration.

To set up the environment variable, first copy the `.env.example` template from the hallucination check:

```bash
cp checks/hallucination/.env.example checks/hallucination/.env
```

then update the file with your Multistorage configuration. See the [Multistorage Configuration Example](#multistorage-configuration-example) section for an example of how this can be done for an S3 bucket, or the [Official Multistorage Documentation](https://nvidia.github.io/multi-storage-client/references/configuration.html) for the full configuration reference.

When setting the Multistorage environment variable in the ENV file, compact the JSON onto the same line to avoid parsing issues. This ENV should also be wrapped in single quotes (e.g. `'{/* your config json here */}'`).

#### Start the Service:

```bash
docker run --env-file=checks/hallucination/.env -p 8080:8080 nvcr.io/nvidia/cosmos/hallucination-checker:1.1.0
```

Verify that the service is running:

```bash
curl http://localhost:8080/health
```

#### Test the service

> Note: Before running the hallucination checker, one must upload their input to a storage provider, and add Multistorage configuration

```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: application/json" \
  -d '{
    "clip_id": "my_clip",
    "original_video_url": "s3://<bucket-name>/path/to/original.mp4",
    "augmented_video_url": "s3://<bucket-name>/path/to/augmented.mp4"
  }'

```

### Objects Check

> **This check has no prebuilt container.** It requires a local build via `dazel` and an NVIDIA GPU driver >=570. See the details below before attempting to run.

The Objects check uses the SegFormer ONNX model (dynamic processor) and the CWIP model (static processor), both bundled with the repository via Git LFS (see [Objects Check Models (Git LFS)](#objects-check-models-git-lfs) above) — no separate download is required.

See the [Objects Check docs](checks/objects.md) for more details of building and running this container.

### Physical Plausibility Check

The Physical Plausibility check uses a pinned V-JEPA video encoder and trained temporal classifier, and requires an
NVIDIA GPU with the default configuration. The default classifier is hosted in a public Hugging Face repository
and does not require `HF_TOKEN`; you can also provide your own compatible checkpoint. The pinned
encoder source and weights are downloaded separately from GitHub and Meta. Input videos must contain at least
64 frames. Remote video inputs also require `MULTISTORAGECLIENT_CONFIGURATION`.

To run the published `nvcr.io/nvidia/cosmos/physical-plausibility-checker:1.1.1` image with your own classifier,
export a compatible attention bundle using the [training notebook](tutorials/train_physical_plausibility_checker.ipynb),
mount it into the container, and set `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI` to the mounted path. Follow
[Run a Published Image with an S3 Video](checks/physical_plausibility.md#run-a-published-image-with-an-s3-video)
for the environment file, Docker command, and example request. Access to the published image is required.

See the [Physical Plausibility Check docs](checks/physical_plausibility.md) for model setup, configuration, CLI usage,
result interpretation, and instructions for building and running the service container.

### Attribute Verification Check

#### Setup Environment Variables

The attribute verification check requires NVIDIA Multistorage configuration to be set, and also requires an API key to be set for the VLM and LLM connections.

To set up the environment variable, first copy the `.env.example` template from the attribute verification check:

```bash
cp checks/attribute_verification/.env.example checks/attribute_verification/.env
```

then update the file with your Multistorage configuration and API key.

To set the Multistorage configuration, see the [Multistorage Configuration Example](#multistorage-configuration-example) section for an example of how this can be done for an S3 bucket, or the [Official Multistorage Documentation](https://nvidia.github.io/multi-storage-client/references/configuration.html) for the full configuration reference.

When setting the Multistorage environment variable in the ENV file, compact the JSON onto the same line to avoid parsing issues. This ENV should also be wrapped in single quotes (e.g. `'{/* your config json here */}'`).

To set the API key, see [Setting up your LLM and VLM API key](#setting-up-your-llm-and-vlm-api-key). The same key is shared between LLM and VLM calls. You can also use an API key for any endpoint with an OpenAI-compatible interface. If an API key is not needed, this variable can be left empty or unset.

The LLM and VLM endpoint and model can be configured in the default config for the services, or overridden in the checker /process request. See [LLM and VLM model setup](checks/attribute_verification.md#model-setup) for more information on setting the LLM and VLM endpoints and model.

#### Start the Service:

```bash
docker run --env-file=checks/attribute_verification/.env -p 8080:8080 nvcr.io/nvidia/cosmos/attribute-verification-checker:1.1.0
```

Verify that the service is running:

```bash
curl http://localhost:8080/health
```

#### Test the service

> Note: Before running the attribute verification checker, one must upload their input to a storage provider, and add Multistorage configuration.

```bash
# Verify whether the augmented video shows a scene with a sunny morning, by checking attributes for weather and time of day
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: application/json" \
  -d '{
    "clip_id": "my_clip",
    "augmented_video_url": "s3://<bucket-name>/path/to/augmented.mp4",
    "config": {
      "selected_variables": {
        "weather": "sunny",
        "time_of_day": "morning"
      },
      "variable_options": {
        "weather": [
          "sunny",
          "cloudy",
          "rainy",
          "snowy"
        ],
        "time_of_day": [
          "morning",
          "night"
        ]
      },
      "question_generation": {
          "llm": {
              "endpoint": "https://integrate.api.nvidia.com/v1",
              "model": "qwen/qwen3.5-397b-a17b"
          }
      },
      "vlm_verification": {
          "vlm": {
              "endpoint": "https://integrate.api.nvidia.com/v1",
              "model": "qwen/qwen3.5-397b-a17b"
          }
      }
    }
  }'


```

## Next Steps

- Visit the [Deployment Guide](deployment.md) for instructions on building, tagging, pushing, and running containers in production.
- Visit the [Customization Guide](customization.md) for instructions on getting started with local development.
- Visit the [Orchestration Layer Guide](services/orchestration.md) to coordinate multiple checkers with the Arbitrator and Database REST API.

## Appendix

### Storage and Credentials

Cosmos Evaluator has **two independent storage stacks**, and which one a checker uses depends on the checker:

| Stack | Used by | Configured with |
|-------|---------|-----------------|
| `StorageProvider` framework | Objects, Arbitrator (AV orchestration) | `COSMOS_EVALUATOR_STORAGE_*` environment variables |
| NVIDIA Multistorage client | Hallucination, Attribute Verification, Physical Plausibility | `MULTISTORAGECLIENT_CONFIGURATION` (see [example](#multistorage-configuration-example)) |

For local development, both stacks load settings from `~/.cosmos_evaluator/.env` and `~/.aws/.env` (in that order).

#### `StorageProvider` (`COSMOS_EVALUATOR_STORAGE_*`)

The Objects check and the Arbitrator download inputs and upload outputs through the [StorageProvider framework](../services/framework/storage_providers/README.md). It is configured with:

| Variable | Required | Description |
|----------|----------|-------------|
| `COSMOS_EVALUATOR_STORAGE_TYPE` | No | Backend: `s3` (default), `azure`, or `local`. The type is not inferred from the URL, so an Azure URL needs `azure` here. Split per direction with `COSMOS_EVALUATOR_INPUT_STORAGE_TYPE` / `COSMOS_EVALUATOR_OUTPUT_STORAGE_TYPE`. |
| `COSMOS_EVALUATOR_STORAGE_URL` | Yes, unless `local` | Addresses the output bucket and how to reach it: `https://my-bucket.s3.us-west-2.amazonaws.com` for AWS, `https://pbss.s8k.io/my-bucket` for an S3-compatible store (PBSS, SwiftStack, MinIO), or `https://myacct.blob.core.windows.net/my-container` for Azure. Split per direction with `COSMOS_EVALUATOR_INPUT_STORAGE_URL` / `COSMOS_EVALUATOR_OUTPUT_STORAGE_URL`. |
| `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY` | No | S3 access key ID. Unused by Azure. |
| `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` | No | S3 secret access key, or, with `azure`, the Azure account key. |
| `COSMOS_EVALUATOR_STORAGE_SESSION_TOKEN` | No | S3 session token, or, with `azure`, a SAS token used in place of an account key. Azure requires one of this or the account key. |

Any storage field can be retargeted for a single service by prefixing it with that service's env prefix — e.g. `OBJECTS_STORAGE_URL` overrides `COSMOS_EVALUATOR_STORAGE_URL` for the Objects service only. See the [storage providers README](../services/framework/storage_providers/README.md) for the full alias precedence.

**Authenticating to AWS without static keys.** The access/secret key variables are **optional**. When no `COSMOS_EVALUATOR_STORAGE_*` credential is set, S3 falls back to `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN`, including from `~/.aws/.env`; Azure never reads them. When those are unset too, the S3 provider leaves credentials out of its config entirely, which hands resolution to boto3's default credential chain — so the shared config files, an EC2 instance profile, an ECS task role, or an EKS IRSA / IMDSv2 role all work as they normally would. This is the recommended pattern for cloud deployments: provide `COSMOS_EVALUATOR_STORAGE_URL` and let the instance role supply credentials.

#### Multistorage (`MULTISTORAGECLIENT_CONFIGURATION`)

The Hallucination, Attribute Verification, and Physical Plausibility checks resolve remote video URIs with the [NVIDIA Multistorage client](https://nvidia.github.io/multi-storage-client/references/configuration.html) instead of the `StorageProvider` framework. There are two ways to supply the configuration:

- **Inline JSON (`MULTISTORAGECLIENT_CONFIGURATION`)** — set it to a compact, single-quoted JSON string (see the [Multistorage Configuration Example](#multistorage-configuration-example) below). At startup each service materializes this JSON to a temporary file and points the client at it via `MSC_CONFIG`. This works for `docker run --env-file` (the deployment path). **However, when running via `dazel run`, the inline JSON is forwarded to the container as `docker -e MULTISTORAGECLIENT_CONFIGURATION=<value>` and its quoting is mangled.** For `dazel run`, use the file form below instead.
- **Config file (`MSC_CONFIG`) — recommended for `dazel run`.** `multistorageclient` reads `MSC_CONFIG` (a path to a JSON file) natively, and the service leaves a pre-set `MSC_CONFIG` untouched when `MULTISTORAGECLIENT_CONFIGURATION` is unset. Because `~/.cosmos_evaluator/` is bind-mounted into the dazel container at the **same absolute path** as on the host, you can write the config to a file there and point `MSC_CONFIG` at that path (a plain, quote-free path survives env forwarding intact):

```bash
# Write the MSC config (same JSON as the example below) to a file in the mounted dir
cat > ~/.cosmos_evaluator/msc.json << 'EOF'
{ "profiles": { ... }, "path_mapping": { ... } }
EOF

# Point MSC_CONFIG at it in the env file, and leave MULTISTORAGECLIENT_CONFIGURATION unset.
# Use the absolute path (the mount preserves it inside the container); the .env is read
# literally, so do NOT rely on ~ or $HOME expansion — write the resolved path:
echo "MSC_CONFIG=$HOME/.cosmos_evaluator/msc.json" >> ~/.cosmos_evaluator/.env
```

  So `MSC_CONFIG` **is** a variable you can set yourself (to a file path). When you use the inline `MULTISTORAGECLIENT_CONFIGURATION` form instead, `MSC_CONFIG` is generated internally and any value you see referenced in logs is that internally-derived temp path.

### Multistorage Configuration Example

To create a multistorage configuration for an S3 bucket, you will need:
* Bucket name
* AWS access key ID
* AWS secret access key

The Multistorage configuration should be constructed like this:
```json
{
  "profiles":{
    "<bucket-name>":{
      "storage_provider":{
        "type":"s3",
        "options":{
          "base_path":"<bucket-name>"
        }
      },
      "credentials_provider":{
        "type":"S3Credentials",
        "options":{
          "access_key":"<access-key>",
          "secret_key":"<secret-key>"
        }
      }
    }
  },
  "path_mapping":{
    "s3://<bucket-name>/":"msc://<bucket-name>/"
  }
}
```

**On AWS, prefer the instance role over static keys.** Omit the `credentials_provider` block entirely and `multistorageclient` falls back to its own default AWS credential chain (`AWS_*` env vars → `~/.aws` → **EC2 IMDS instance role**), just like the `StorageProvider` stack:

```json
{
  "profiles":{
    "<bucket-name>":{
      "storage_provider":{
        "type":"s3",
        "options":{
          "base_path":"<bucket-name>"
        }
      }
    }
  },
  "path_mapping":{
    "s3://<bucket-name>/":"msc://<bucket-name>/"
  }
}
```

On EC2 the [IMDS hop limit](deployment.md#aws-quick-start) must be `2` for the container to reach the instance role.

When setting the Multistorage environment variable in the ENV file, compact the JSON onto the same line to avoid parsing issues. This ENV should also be wrapped in single quotes (e.g. `'{/* your config json here */}'`).

### Setting up your LLM and VLM API key

All checkers use OpenAI-compatible endpoints for the LLM and VLM endpoints. By default, the checkers will point to [build.nvidia.com](https://build.nvidia.com/) for these endpoints. While this is a great way to get started with the checkers, it is not recommended to use the [build.nvidia.com](https://build.nvidia.com/) endpoints for production use. For production, please either download the LLM and VLM NIMs and run them locally, or connect to a stable external endpoint of your choice.

> **Important:** The key must be generated from the specific model's page, not from your NGC account settings. A key from account settings will authenticate to `GET /v1/models` (health checks pass) but return **403** on inference calls (`POST /v1/chat/completions`).

Generate credentials for the configured LLM and VLM endpoints:

1. Go to the model page on build.nvidia.com (e.g. [Qwen 3.5-397B](https://build.nvidia.com/qwen/qwen3.5-397b-a17b))
2. Click **View Code**, then click **Generate API Key**
3. Copy the key (it starts with `nvapi-`) into `LLM_API_KEY` for an LLM or `VLM_API_KEY` for a VLM. Repeat for the
   other role when it uses a different credential. If one key works for both endpoints, assign it to both variables.

For example, in `~/.cosmos_evaluator/.env`:

```dotenv
LLM_API_KEY=<key-for-question-generation>
VLM_API_KEY=<key-for-visual-verification>
```

`BUILD_NVIDIA_API_KEY` remains supported as a legacy shared fallback, but new configurations should use the
role-specific variables.

Verify the key works for inference (not just model listing):

```bash
curl -s -w "\n%{http_code}\n" \
  -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $VLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen/qwen3.5-397b-a17b", "messages": [{"role": "user", "content": "say hello"}], "max_tokens": 10}'
```

The response body prints first, followed by the HTTP status code on its own line. A `200` confirms the key has inference entitlement. A `403` means the key was generated from account settings — regenerate it from the model page. A transient `5xx` (e.g. `502`/`503`) is usually a temporary upstream hiccup — retry before assuming the key is bad.
