# hlh-server

Standalone private server repo for Humanity's Last Hackathon.

Intented for use with the [Humanity's Last Hackathon](https://github.com/gpu-mode/humanitys-last-hackathon) client.


## Requirements

- Python 3.12+
- `popcorn` CLI installed and authenticated on the server host with `popcorn auth`
- Hugging Face credentials configured on the server host for bundle upload

## Install

```bash
pip install -e .
```

## Environment

Configure server-side credentials before running the service:

```bash
popcorn auth
```

`popcorn auth` is used to validates incoming `X-Popcorn-Cli-Id` values against Popcorn and runs `popcorn submit` server-side.

```bash
export HF_TOKEN=hf_...
```

`HF_TOKEN` is used to upload submission bundles to a private Hugging Face Bucket.

<details>
<summary><strong>[Optional] Configure Service host/port</strong></summary>

```bash
export HLH_SERVICE_HOST=127.0.0.1
export HLH_SERVICE_PORT=8788
```

</details>

<details>
<summary><strong>[Optional] Artifact upload configuration</strong></summary>

```bash
# Whether clients should sent artifacts
export HLH_UPLOAD_TOP_SUBMISSION_BUNDLE=1

# Whether artifacts should be submitted to HF
export HLH_SUBMIT_BUNDLE_ENABLED=1

# Private store of artifacts
export HLH_SUBMIT_BUNDLE_BUCKET_TEMPLATE="{hf_user}/humanitys-last-hackathon"
export HLH_SUBMIT_BUNDLE_HF_TOKEN_ENV=HF_TOKEN
```

</details>

<details>
<summary><strong>[Optional] GitHub-backed profile runner</strong></summary>

```bash
export HLH_PROFILE_RUNNER=github
export HLH_PROFILE_WORKFLOW_FILE=main.yml
export HLH_PROFILE_WORKFLOW_REF=main
export HLH_PROFILE_POLL_SECONDS=5
export HLH_PROFILE_TIMEOUT_SECONDS=600
```

`HLH_PROFILE_RUNNER=github` is the default and dispatches the bundled GitHub Actions workflow through `gh`.

`HLH_PROFILE_RUNNER=service` profiles on the server host directly for testing.

</details>

## Run

```bash
hlh-server
```

## Endpoints

### `GET /health`

Liveness probe. Returns `{"status": "ok"}` with no authentication required. Use this for load-balancer or orchestrator health checks.

### `POST /v1/hlh/profile`

Accepts a kernel source file as a multipart upload and returns a structured JSON profiling report (execution time, GPU memory, kernel-level stats).

The server supports two profiling backends controlled by `HLH_PROFILE_RUNNER`:

- **`github`** — (default) - Dispatches the kernel to a GitHub Actions workflow via `gh workflow run`, polls the run until completion, and extracts the profiling JSON from the workflow logs. This path requires an authenticated `gh` CLI with permission to dispatch and inspect workflow runs. A unique `request_id` is embedded in the dispatch so the server can correlate the run, and a configurable timeout (`HLH_PROFILE_TIMEOUT_SECONDS`) bounds the poll loop.
- **`service`** - Runs the kernel locally on the server host in a sandboxed subprocess. The subprocess uses Apple Metal / MPS profiling to capture GPU memory allocation, wall-clock duration, and optional Metal GPU trace artifacts (`gputrace`). Results are emitted as JSON on stdout and parsed by the server.

### `POST /v1/hlh/submit`

Accepts a kernel file along with `leaderboard` and `gpu` form fields. The server writes the kernel to a temporary file and invokes `popcorn submit` in leaderboard mode as a server-side subprocess. The structured JSON output from `popcorn` is parsed (from its output file, stdout, or stderr as fallback) and returned to the client alongside the raw stdout/stderr, exit code, and a score summary.

If the submission succeeds and `HLH_UPLOAD_TOP_SUBMISSION_BUNDLE` is enabled, the response includes `should_upload_submission_bundle: true`, signaling the client to follow up with a bundle upload to `/v1/hlh/submit/bundle`.

### `POST /v1/hlh/submit/bundle`

Accepts a `tar.gz` archive containing submission artifacts, a `submission_id`, and a `kernel_filename`. The server extracts the archive into a temporary directory (with path-traversal protection), then uploads every extracted file to a private Hugging Face bucket via the `HfApi`. The destination bucket is resolved from a configurable template (`HLH_SUBMIT_BUNDLE_BUCKET_TEMPLATE`) and created automatically if it does not exist. This endpoint is gated by the `HLH_SUBMIT_BUNDLE_ENABLED` flag and requires a valid `HF_TOKEN` on the server.

### Authentication

All endpoints except `/health` require a valid `X-Popcorn-Cli-Id` header. The server validates CLI IDs by calling the upstream Popcorn API and caches successful results for a configurable TTL (default 5 minutes) to reduce round-trips.
