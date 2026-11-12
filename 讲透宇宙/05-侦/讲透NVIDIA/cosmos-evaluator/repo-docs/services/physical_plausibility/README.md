# Physical Plausibility Service

This service evaluates motion in a generated video and returns plausibility metrics and pass/fail status. It wraps `PhysicalPlausibilityProcessor` behind a standardized REST API and keeps the video encoder and classifier resident between requests.

See the [Physical Plausibility Check guide](../../docs/checks/physical_plausibility.md) for model setup, configuration, score interpretation, and a complete local Docker example.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Return readiness, service identity, version, and slot usage. |
| GET | `/config` | Return the default checker configuration. |
| GET | `/metrics` | Return Prometheus metrics. |
| POST | `/process` | Evaluate one video and return plausibility metrics. |
| GET | `/docs` | Interactive OpenAPI documentation. |

## Request Model (`POST /process`)

```json
{
  "clip_id": "clip-123",
  "video_url": "s3://bucket/video.mp4",
  "config": {
    "bad_threshold": 0.4
  }
}
```

- **clip_id** (required string): Identifier echoed in the result.
- **video_url** (required string): Local/mounted path or supported remote URI for a video with at least 64 frames.
- **config** (optional object): Per-request `bad_threshold` override in `[0, 1]`. Other fields are accepted for compatibility with shared Arbitrator configuration but do not change processing. Checkpoint and device settings are fixed at startup.
- **output_storage_prefix** (optional string): Accepted for compatibility with the shared framework. The checker returns metrics without uploading artifacts.

Local files and `s3://`, `gs://`, `azure://`, `msc://`, and `https://` video URIs are supported. Configure NVIDIA Multistorage for remote inputs. Unencrypted `http://` inputs are rejected.

## Response Model (`POST /process`)

The standard service response envelope contains the clip identifier, pass/fail decision, bad score, plausibility score, prediction, thresholds, raw logit, and preprocessing fingerprint. See [Interpret the Output](../../docs/checks/physical_plausibility.md#interpret-the-output) for a JSON example and field semantics.

With an explicit score override, a clip passes when `bad_score < bad_threshold`; equality fails. Without an override, the checker uses the saved logit cutoff selected by `cap` in the startup configuration.

## Environment Settings

The service inherits common [deployment settings](../../docs/deployment.md) and supports:

| Variable | Default | Description |
|----------|---------|-------------|
| `PHYSICAL_PLAUSIBILITY_PROCESS_CONCURRENCY_LIMIT` | `4` | Maximum admitted jobs per replica. |
| `PHYSICAL_PLAUSIBILITY_MAX_BATCH_SIZE` | `4` | Maximum requests grouped in a queue batch; no greater than the concurrency limit. |
| `PHYSICAL_PLAUSIBILITY_MAX_BATCH_WAIT_MS` | `10.0` | Maximum wait to collect a batch. |
| `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI` | Checker YAML value | Compatible classifier bundle URI or local path. |
| `PHYSICAL_PLAUSIBILITY_CONFIG_DIR` | unset | Optional checker configuration directory. |

The service groups concurrent requests, then encodes and scores each video individually. The batch size controls queue grouping, not a batched encoder forward pass.

The default Hugging Face classifier is public and does not require `HF_TOKEN`. For custom authenticated Hugging Face checkpoints, set `HF_TOKEN` with repository read access. Remote videos and MSC-backed checkpoints require `MULTISTORAGECLIENT_CONFIGURATION`. For standalone local use, set `COSMOS_EVALUATOR_STORAGE_TYPE=local`.

Optional queue claiming uses `PHYSICAL_PLAUSIBILITY_DATABASE_API_URL` and `PHYSICAL_PLAUSIBILITY_DATABASE_WORKER_KEY`. Set both to enable claiming or neither for standalone REST use. See [Provisioning worker keys](../database/README.md#provisioning-worker-keys).

## Run the REST API Locally

After completing model and build setup:

```bash
dazel run //services/physical_plausibility:rest_api
```

Settings are loaded from the shared environment files, including `~/.cosmos_evaluator/.env`. Set `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI` there to use your own classifier bundle.

## Release and Deployment

See the [checker guide](../../docs/checks/physical_plausibility.md#building-and-running-the-service-container) for building and running the image with local model and video mounts. See the [Deployment Guide](../../docs/deployment.md) for registry and deployment instructions.
