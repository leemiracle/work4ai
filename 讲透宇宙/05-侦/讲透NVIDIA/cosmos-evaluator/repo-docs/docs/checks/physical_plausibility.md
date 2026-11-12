# Physical Plausibility Check

This checker evaluates whether motion in a generated video is temporally plausible. It uses a pretrained video encoder and a learned classifier to return a plausibility score and a pass/fail result. It requires only the video being evaluated, without a reference video or annotations.

The score reflects the classifier's training labels. It does not measure a specific physical quantity or guarantee that a video obeys physical laws. The default classifier was trained on FineVideo quality labels: quality1 is considered bad, and quality2/useful and quality3/artifact-free are considered good. Validate this definition against your use case.

## How it works

The processing pipeline is:

1. **Loading Video**: Load the video from a local path or supported remote URI.
2. **Frame Sampling**: Sample 64 distinct frames across the video, including its first and last frames. Videos with fewer than 64 frames are rejected.
3. **Frame Preprocessing**: Resize and pad each frame to 384 × 384 pixels while preserving its aspect ratio, then apply ImageNet normalization.
4. **Feature Extraction**: Use the frozen, pinned V-JEPA 2.1 ViT-L/16 video encoder to extract tokens with layout `[32, 24, 24, 1024]`. Exclude fully padded regions and weight partially padded regions by their visible area.
5. **Score Computation**: Apply the checkpoint's fixed feature normalization, then pool all space-time tokens with a learned query into a 1024-dimensional vector and apply a linear classifier. Compute `bad_score = sigmoid(bad_logit)` and `plausibility_score = 1 - bad_score`.
6. **Pass/Fail Decision**: Compare the result against the checkpoint's saved threshold or an explicit `bad_threshold` override. Lower bad scores indicate more plausible videos.

The implementation is split across:

- `processor.py`, which loads the classifier and computes scores and pass/fail results
- `model.py` and `features.py`, which load the video encoder and preprocess frames
- `attention.py`, which implements attention pooling and validates classifier checkpoints
- `run.py`, which provides CLI config loading, execution, and result serialization

## Prerequisites and Compute Requirements

Complete the build system setup in the [Getting Started Guide](../getting_started.md) before running the CLI or building the service container.

- **GPU**: The default configuration uses an NVIDIA GPU with `device: cuda`. Start the service container with `--gpus all`.
- **Classifier checkpoint**: The configured default is a compatible attention bundle in the public [physical-plausibility-evaluator model repository](https://huggingface.co/nvidia/physical-plausibility-evaluator). It does not require `HF_TOKEN`. You can also supply your own compatible bundle; the [training notebook](../tutorials/train_physical_plausibility_checker.ipynb) includes scratch training, fine-tuning, and calibration.
- **Video encoder downloads**: On first use, the checker downloads pinned V-JEPA source from GitHub and an approximately 5.15 GB encoder checkpoint from Meta. These downloads are public and separate from the classifier checkpoint.
- **Storage and caches**: Allow writable Hugging Face and Torch caches and space for temporary downloads. The service image sets `HF_HOME=/cache/huggingface` and `TORCH_HOME=/cache/torch`. Persist these directories with permissions suitable for the container user to reuse downloaded models.
- **Remote input credentials**: Set `MULTISTORAGECLIENT_CONFIGURATION` for MSC-backed video or checkpoint URIs. Local files do not require this configuration. Hugging Face checkpoints use `HF_TOKEN` when authentication is required.

### Model Setup

The default classifier is pinned to this revision:

```text
hf://nvidia/physical-plausibility-evaluator@a427d8a37cba9200df31190a4130e60c209acd41/finevideo-attention-linear-v1/model.pt
```

Its expected SHA-256 is `3e9c138560df5958f01c5f8629a3221f0d53e2c0459d013d353bc9fbe2c889e9`.

To select a different classifier, set `checkpoint_uri` in the checker configuration. The CLI's `--checkpoint-uri` and the service's `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI` override that setting. Supported checkpoint locations are:

- A Hugging Face model file: `hf://namespace/repository[@revision]/path/to/model.pt`
- An MSC-backed URI, such as `s3://bucket/model.pt` or `msc://models/model.pt`
- A local path, such as `/models/checker.pt`

Pin Hugging Face revisions for reproducible deployments. The checker validates the bundle schema, tensor names and shapes, numeric values, and preprocessing fingerprint. Checkpoints must match the encoder and feature pipeline; arbitrary PyTorch checkpoints are not compatible.

For a locally trained classifier, export a compatible attention bundle using the [training notebook](../tutorials/train_physical_plausibility_checker.ipynb) or the instructions supplied with your training package. Record the absolute path to the exported file (for example, `checker.pt`); mount that file into the service container as shown below. The classifier bundle is separate from the public video encoder checkpoint, which the service still downloads on first use.

The source archive and encoder checkpoint are SHA-256 verified before use. Missing artifacts or checksum mismatches prevent model initialization. Both CLI and REST launches initialize the model, including when the legacy `enabled` field is `false`.

## Inputs

The check requires one **generated video** with at least 64 frames. Frame sampling spans the full video but evaluates only the sampled frames, so brief events between samples may be missed. No reference video or annotations are required.

Local files and remote URIs with `s3://`, `gs://`, `azure://`, `msc://`, and `https://` schemes are supported through NVIDIA Multistorage. Use secure remote URIs; the REST service rejects unencrypted `http://` inputs. For containers, local video and checkpoint paths must be mounted and readable inside the container.

## Configuration

Configuration lives in [`checks/cosmos_evaluator.yaml`](../../checks/cosmos_evaluator.yaml) under `metropolis.physical_plausibility`. This file provides the default configuration for both the CLI and the service container.

The following example selects a local classifier checkpoint:

```yaml
metropolis.physical_plausibility:
  enabled: true
  deps: []
  checkpoint_uri: "/models/checker.pt"
  cap: 0.3
  device: "cuda"
  # bad_threshold: null  # use the checkpoint's saved threshold
```

- **checkpoint_uri**: Location of the compatible classifier bundle. Defaults to the pinned FineVideo bundle described above.
- **cap**: Selects a saved threshold by its validation good-rejection cap. Default: `0.3`. This means a threshold selected to reject at most 30% of acceptable videos on the validation set; it is not a guarantee on new videos. The selected cap must exist in the bundle, even when using a score threshold override.
- **device**: PyTorch device for model inference. Default: `cuda`.
- **bad_threshold**: Optional score cutoff in `[0, 1]`. When explicitly set, a clip passes when `bad_score < bad_threshold`; equality fails. Defaults to the checkpoint's saved threshold.
- **enabled**: Legacy configuration field. Default: `true`. It does not gate model initialization for direct CLI or REST launches.
- **deps**: Checker dependencies used by the Arbitrator. Default: `[]`.

Threshold precedence is the per-run or per-request override, then the configuration override, then the checkpoint threshold selected by `cap`. Saved checkpoint thresholds compare `bad_logit < bad_logit_threshold` to preserve decisions when sigmoid scores saturate. Explicit `bad_threshold` overrides compare scores instead.

## Local CLI Testing

### Run the Checker

From the `cosmos-evaluator` repository root, run:

```bash
dazel run //checks/physical_plausibility:run -- \
  --video-path /absolute/path/to/video.mp4 \
  --clip-id clip-123 \
  --checkpoint-uri /models/checker.pt \
  --output-dir outputs
```

Replace the video and model paths with readable files in your environment. Omit `--checkpoint-uri` to use the configured checkpoint, as described in [Model Setup](#model-setup).

The CLI supports these options:

- **--video-path** (required): Local path or supported remote URI to the video being evaluated.
- **--clip-id** (optional): Clip identifier for the run. Defaults to a generated UUID.
- **--bad-threshold** (optional): Per-run score threshold override in `[0, 1]`. Defaults to the configuration or checkpoint threshold.
- **--checkpoint-uri** (optional): Classifier bundle URI or local path. Defaults to the YAML value.
- **--config** (optional): Configuration filename without `.yaml`. Defaults to `cosmos_evaluator`.
- **--config-dir** (optional): Directory containing the configuration file. Defaults to the bundled configuration directory.
- **--verbose** (optional): Logging level: `DEBUG`, `INFO`, `WARNING`, or `ERROR`. Defaults to `INFO`.
- **--env-file** (optional): Dotenv file loaded before processing. Defaults to `checks/physical_plausibility/.env`.
- **--output-dir** (optional): Directory for the JSON results file. Defaults to `outputs`.

### Interpret the Output

The checker produces:

- A **bad score** in `[0, 1]`; lower values indicate more plausible videos.
- A **plausibility score** equal to `1 - bad_score`; higher values indicate more plausible videos.
- A **pass/fail** result and a `good` or `bad` prediction.
- The threshold and raw classifier logit used to interpret the decision.
- A JSON results file named `{clip_id}.physical_plausibility.results.json` under `--output-dir`. Unsafe filename characters in `clip_id` are replaced with underscores.

A result using an explicit `bad_threshold: 0.4` override looks like this:

```json
{
  "clip_id": "clip-123",
  "passed": true,
  "bad_score": 0.18,
  "plausibility_score": 0.82,
  "bad_threshold": 0.4,
  "prediction": "good",
  "bad_logit": -1.5163474893680884,
  "bad_logit_threshold": null,
  "fingerprint": "<token-contract-sha256>"
}
```

`bad_logit` is the classifier output before sigmoid; higher values indicate less plausible motion. `bad_logit_threshold` contains the saved logit cutoff, or `null` when an explicit score threshold overrides it. `fingerprint` identifies the pinned encoder and preprocessing contract.

Scores rank videos and are not guaranteed calibrated probabilities. Validate custom thresholds on data representative of your use case.

## Building and Running the Service Container

The service wraps `PhysicalPlausibilityProcessor` behind a standardized REST API. It loads the encoder and classifier once at startup and keeps them resident for subsequent requests.

The service exposes these endpoints:

- `GET /health` for readiness, service identity, version, and slot usage
- `GET /config` to retrieve the default checker configuration
- `GET /metrics` for Prometheus metrics
- `POST /process` to evaluate one video
- `GET /docs` for interactive OpenAPI documentation

The `POST /process` request body includes:

- **clip_id** (required): String identifier echoed in the result.
- **video_url** (required): Supported remote URI or local/mounted path for the video.
- **config** (optional): Dictionary containing a per-request `bad_threshold` override. Other keys are accepted for compatibility with shared Arbitrator configuration but do not change this checker's behavior. Checkpoint and device settings are fixed at startup.
- **output_storage_prefix** (optional): Accepted for compatibility with the shared service framework. The checker returns metrics and does not upload artifacts.

The success response contains the fields described in [Interpret the Output](#interpret-the-output) inside the standard [service response envelope](../services/framework.md).

### Build and Run the Container

First, build the container:

```bash
dazel build //services/physical_plausibility:image
```

Next, load it into the local Docker instance:

```bash
dazel run //services/physical_plausibility:image_load
```

Run the container with a local checkpoint and video directory mounted:

```bash
docker run --rm --gpus all \
  -e COSMOS_EVALUATOR_STORAGE_TYPE=local \
  -e PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI=/models/checker.pt \
  -v /absolute/path/to/models:/models:ro \
  -v /absolute/path/to/videos:/videos:ro \
  -p 8088:8000 \
  physical-plausibility-checker:1.1.0
```

Replace the host directories with directories containing `checker.pt` and your video. `COSMOS_EVALUATOR_STORAGE_TYPE=local` configures the shared framework's storage provider for standalone local use.

Submit the mounted video:

```bash
curl -X POST http://localhost:8088/process \
  -H 'Content-Type: application/json' \
  --data '{
    "clip_id": "clip-123",
    "video_url": "/videos/video.mp4",
    "config": {"bad_threshold": 0.4}
  }'
```

For remote videos or authenticated Hugging Face checkpoints, add `--env-file "$HOME/.cosmos_evaluator/.env"` to the Docker command and configure `MULTISTORAGECLIENT_CONFIGURATION` and/or `HF_TOKEN` as needed. To use the default classifier, omit the local checkpoint override. See the [Deployment Guide](../deployment.md) for shared environment settings.

### Run a Published Image with an S3 Video

The following example uses the published `1.1.1` image from the tested deployment instructions. This is separate from the version built by the current checkout in the example above. Ensure you have access to that image.

Create a `.env` file containing:

```dotenv
PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI=/models/checker.pt
MULTISTORAGECLIENT_CONFIGURATION=<your-multistorage-client-JSON-configuration>
```

Replace the configuration placeholder with the JSON configuration for your storage backend, including the credentials needed to read the video. See [Multistorage Configuration](../deployment.md#multistorage-configuration). This variable is only needed for remote inputs or MSC-backed checkpoints.

Start the container with the absolute path to your exported classifier file:

```bash
docker run --rm --gpus all --env-file .env \
  -v /absolute/path/to/checker.pt:/models/checker.pt:ro \
  -e COSMOS_EVALUATOR_STORAGE_TYPE=local \
  -p 8000:8000 \
  nvcr.io/nvidia/cosmos/physical-plausibility-checker:1.1.1
```

On Linux, `--network host` can replace `-p 8000:8000` to match the tested host-network setup. Add `sudo` if your Docker installation requires it. The `local` storage setting selects the framework's storage provider; remote video inputs still use the supplied Multistorage configuration.

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

Omit `config.bad_threshold` to use the startup configuration or the checkpoint's saved threshold. The threshold can differ between trained bundles; the returned result includes the threshold used for that request.

### Concurrency and Dynamic Batching

The service groups concurrent requests in a queue. Within each group, videos are encoded and scored individually; increasing the queue batch size does not create a batched encoder forward pass.

| Environment variable | Default | Description |
|----------------------|---------|-------------|
| `PHYSICAL_PLAUSIBILITY_PROCESS_CONCURRENCY_LIMIT` | `4` | Maximum simultaneous admitted jobs per replica. |
| `PHYSICAL_PLAUSIBILITY_MAX_BATCH_SIZE` | `4` | Maximum requests in a queue batch; cannot exceed the concurrency limit. |
| `PHYSICAL_PLAUSIBILITY_MAX_BATCH_WAIT_MS` | `10.0` | Maximum wait to collect a batch. |
| `PHYSICAL_PLAUSIBILITY_CHECKPOINT_URI` | YAML value | Classifier bundle URI or local path selected at startup. |
| `PHYSICAL_PLAUSIBILITY_CONFIG_DIR` | unset | Optional checker configuration directory. |

Size concurrency and batch limits for the available GPU memory. Reuse model caches to reduce cold-start downloads.

## Training and Calibration

The [training notebook](../tutorials/train_physical_plausibility_checker.ipynb) provides scratch training, pretrained fine-tuning, threshold-only calibration, and held-out evaluation. Use labels `1 = good/acceptable` and `0 = bad/reject` to define your task. The encoder remains frozen.

Run the common setup and only your chosen training or calibration path, followed by evaluation. Keep related clips together and separate from held-out data. Source-model overlap checks identify identical video files by hash; use source-dataset provenance and group IDs to exclude related scenes or re-encoded clips as well.
