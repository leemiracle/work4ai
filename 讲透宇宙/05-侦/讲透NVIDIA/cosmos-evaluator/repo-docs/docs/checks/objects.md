# Objects Check

The Objects check evaluates whether dynamic objects (vehicles, pedestrians, motorcycles, bicycles) in a Cosmos-generated video appear at the positions specified by the RDS-HQ ground truth annotations. It uses semantic segmentation to measure how well detected objects in the generated video correspond to their expected locations from the driving dataset.

## How It Works

The check uses a **SegFormer** semantic segmentation model (the dynamic processor) to analyze dynamic objects — vehicles, pedestrians, motorcycles, and bicycles — in a driving scene. It requires the generated video and an RDS-HQ dataset as inputs. The static processor additionally runs the **CWIP** (Contrastive World-Image Pre-training) model to detect per-patch object presence: two-stream (scoring camera-to-world consistency) when a world-model video is supplied, and camera-only otherwise.

For each frame, the check:
1. Projects 3D object cuboids from the RDS-HQ ground truth into the camera's image space
2. Runs the segmentation model on the generated video frame
3. Measures the overlap between the projected ground truth and the detected segments
4. Produces a per-object, per-frame correspondence score (0.0 to 1.0)

The check also includes a **hallucination detector** that identifies false positive objects — segments in the generated video that don't correspond to any ground truth object.

## Model Setup

### SegFormer Model (Dynamic Processor)

The dynamic processor uses the SegFormer ONNX model for semantic segmentation. The model is **bundled with the repository** at `checks/utils/models/segformer/cityformer_final_1024_dynamic_input_v11_sim.onnx` (tracked via [Git LFS](https://git-lfs.com)), so no separate download is required — it is loaded automatically at runtime.

> **Note:** Because the model is stored via Git LFS, make sure Git LFS is installed before cloning (or run `git lfs pull` in an existing clone) so the `.onnx` file is materialized rather than left as a pointer.

### CWIP Model (Static Processor)

The static processor uses the CWIP (Contrastive World-Image Pre-training) model, which projects a camera frame and a world-model frame into a joint embedding space to score camera-to-world consistency and emit per-patch object-presence and object-type classifications. The weights are **bundled with the repository** in HuggingFace format (`config.json` + `model.safetensors`) at `checks/utils/models/cwip/checkpoints/` (tracked via [Git LFS](https://git-lfs.com)), so no separate download is required — they are loaded automatically at runtime. The static processor runs two-stream when a world-model video is provided (`--world_video_path` on the CLI / `world_model_video_url` on the REST path) and camera-only otherwise — without a world reference the similarity head is unavailable, so the per-patch presence mask is derived from the type head instead.

> **Note:** Because the weights are stored via Git LFS, make sure Git LFS is installed before cloning (or run `git lfs pull` in an existing clone) so `model.safetensors` is materialized rather than left as a pointer.

To run the CWIP model on its own — outside the Objects check, e.g. for a standalone camera/world video pair with visualizations — see the [CWIP model README](../../checks/utils/models/cwip/README.md).

## Data Inputs

| Input | Description |
|-------|-------------|
| RDS-HQ dataset | Directory containing ground truth annotations, camera poses, and intrinsics in [WebDataset](https://github.com/webdataset/webdataset) `.tar` format |
| Generated video | The Cosmos-generated camera video to evaluate (MP4) |

### RDS-HQ Dataset Structure

The RDS-HQ dataset directory should have the following layout:

```
dataset_dir/
├── all_object_info/               # Dynamic object annotations
│   └── {clip_id}.tar
├── pose/                          # Camera poses (30 FPS)
│   └── {clip_id}.tar
├── pinhole_intrinsic/             # Pinhole camera intrinsics
│   └── {clip_id}.tar              #   Contains: pinhole_intrinsic.{camera_name}.npy
├── ftheta_intrinsic/              # Fisheye camera intrinsics (if applicable)
│   └── {clip_id}.tar              #   Contains: ftheta_intrinsic.{camera_name}.npy
├── 3d_traffic_lights/             # Static traffic light cuboids
│   └── {clip_id}.tar
├── 3d_traffic_signs/              # Static traffic sign cuboids
│   └── {clip_id}.tar
├── 3d_lanelines/                  # Lane line polylines
│   └── {clip_id}.tar
├── 3d_road_boundaries/            # Road boundary polylines
│   └── {clip_id}.tar
├── 3d_wait_lines/                 # Wait line polylines
│   └── {clip_id}.tar
└── 3d_crosswalks/                 # Crosswalk surfaces
    └── {clip_id}.tar
```

Each `.tar` file uses the [WebDataset](https://github.com/webdataset/webdataset) format.

#### Clip ID

The `clip_id` is used to locate the correct `.tar` files in each RDS-HQ subdirectory (e.g., `all_object_info/{clip_id}.tar`). It must match the base name of the `.tar` files in the dataset.

In the standard RDS-HQ format, the clip ID follows the pattern `{session_uuid}_{start_timestamp_us}` (e.g., `0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000`). The session UUID is extracted from the portion before the first underscore, and the start timestamp (in microseconds) is parsed from the portion after it. The timestamp is used to derive the clip's time range.

## Usage

### CLI

The CLI operates on local filesystem paths only — all inputs (RDS-HQ dataset, video file) must be available on disk.

First, extract the sample RDS-HQ dataset:

```bash
unzip checks/sample_data/morning/rds_hq.zip -d checks/sample_data/morning/
```

Run the objects check directly from the command line. With no `--world_video_path`, the dynamic processor runs
and the static (CWIP) check runs **camera-only** (add `--world_video_path <world.mp4>` to run it two-stream):

```bash
dazel run //checks/objects/single_view:run -- \
  --input_data $(pwd)/checks/sample_data/morning/rds_hq/ \
  --clip_id 01ce78ad-9e9a-4df9-95d1-1d50e41a04ce_764657799000_764677799000 \
  --camera_name camera_front_wide_120fov \
  --video_path $(pwd)/checks/sample_data/morning/01ce78ad-9e9a-4df9-95d1-1d50e41a04ce_764657799000_764677799000_0_Morning.30fps.mp4 \
  --output_dir $(pwd)/output_dir
```

> **Note:** Pass file and directory arguments as **absolute paths** (the `$(pwd)/` prefix above). `dazel run` executes the binary from its Bazel runfiles directory rather than your shell's working directory, so relative paths like `checks/sample_data/...` are resolved against the wrong root and fail with a "does not exist" error. The repo is bind-mounted into the dazel container at the same absolute path, so `$(pwd)/...` paths resolve correctly inside the container.

To run the static (CWIP) processor **two-stream** instead of camera-only, add `--world_video_path` pointing at the world-model video for the same clip and camera. The repo bundles a matching sample set — RDS-HQ dataset, camera (augmented) video, and world-model video for clip `0d21d408-…` — under `checks/sample_data/`. First extract its single-clip RDS-HQ dataset:

```bash
unzip checks/sample_data/rds_hq_single_clip.zip -d checks/sample_data/rds_hq_single_clip/
```

Then run both processors:

```bash
dazel run //checks/objects/single_view:run -- \
  --input_data $(pwd)/checks/sample_data/rds_hq_single_clip/ \
  --clip_id 0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028189000 \
  --camera_name camera_front_wide_120fov \
  --video_path $(pwd)/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --world_video_path $(pwd)/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4 \
  --output_dir $(pwd)/output_dir
```

> **Note:** The `--clip_id` timestamp (`…189000`) is the one baked into the RDS-HQ tar filenames, which differs from the timestamp in the video filenames (`…200000`). Match `--clip_id` to the RDS-HQ dataset; the video paths are passed explicitly and their filenames need not match the `clip_id`.

The check produces both `{clip_id}.dynamic.objects.results.json` and `{clip_id}.static.objects.results.json`. With `--world_video_path` supplied the static results are two-stream; without it they are camera-only.

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--input_data` | Yes | — | Path to the RDS-HQ dataset directory |
| `--clip_id` | Yes | — | Clip identifier in the format `{session_uuid}_{start_timestamp_us}` (e.g., `0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000`). Used to locate the correct `.tar` files in each RDS-HQ subdirectory and to derive the session UUID and clip time range. |
| `--camera_name` | Yes | — | Camera stream name (e.g., `camera_front_wide_120fov`) |
| `--video_path` | Yes | — | Path to the generated video file (MP4) |
| `--output_dir` | Yes | — | Directory to write results, logs, and visualizations |
| `--world_video_path` | No | None | Path to the world model video used by the static (CWIP) processor. If omitted, the static check runs camera-only (no world-model reference) instead of two-stream. |
| `--model_device` | No | `cuda` | Device for model inference: `cuda` or `cpu` |
| `--trial` | No | None | Evaluate only the first N steps of the 10 fps object-check timeline (for debugging) |
| `--verbose` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `--config` | No | `cosmos_evaluator` | Name of the config file to load (without the `.yaml` extension) |

### Docker Container

#### Build the Container

```bash
dazel run //services/objects/single_view:image_load
```

This builds the OCI image and loads it into the local Docker daemon as `objects-checker:<version>`.

#### Setup Environment Variables

The Objects check uses the [StorageProvider framework](../../services/framework/storage_providers/factory.py) to download input files (RDS HQ data, augmented video) from URLs provided in the `/process` request, and to upload output files (result JSONs, visualization videos) back to storage.

Storage is configured through the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COSMOS_EVALUATOR_STORAGE_TYPE` | No | `s3` | Storage backend: `s3`, `azure`, or `local` |
| `COSMOS_EVALUATOR_STORAGE_URL` | Yes, unless `local` | — | Target address for the output bucket or container; an AWS URL must name its region |
| `COSMOS_EVALUATOR_STORAGE_ACCESS_KEY` | No | — | S3 access key ID (unset falls back to `AWS_ACCESS_KEY_ID`, then boto3's own chain) |
| `COSMOS_EVALUATOR_STORAGE_SECRET_KEY` | No | — | S3 secret access key, or the Azure account key |

For convenience, create a `~/.cosmos_evaluator/.env` file with your storage configuration so it is automatically loaded at startup:

```bash
mkdir -p ~/.cosmos_evaluator
cat > ~/.cosmos_evaluator/.env << 'EOF'
COSMOS_EVALUATOR_STORAGE_TYPE=s3
COSMOS_EVALUATOR_STORAGE_URL=https://my-bucket.s3.us-west-2.amazonaws.com
COSMOS_EVALUATOR_STORAGE_ACCESS_KEY=your_access_key
COSMOS_EVALUATOR_STORAGE_SECRET_KEY=your_secret_key
EOF
```

If you already have AWS credentials in a `~/.aws/.env` file (passed via `--env-file` below), S3 storage falls back to `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` when no `COSMOS_EVALUATOR_STORAGE_*` credential is set. Only the credentials fall back: `AWS_DEFAULT_REGION` is not read, so `COSMOS_EVALUATOR_STORAGE_URL` is still required and must name the region. Azure never reads the `AWS_*` variables.

The storage type also determines how input URLs in the `/process` request are resolved. With `s3`, input URLs can be `s3://` URIs, presigned URLs, or any HTTPS URL. With `local`, input paths are mounted filesystem paths. Output storage follows the same provider — S3 uploads for `s3`, local file copies for `local`.

#### Start the Service

```bash
# Running in local mode with sample data mounted at /data and output at /tmp/output
docker run --gpus all --env-file ~/.cosmos_evaluator/.env \
  -e COSMOS_EVALUATOR_STORAGE_TYPE=local \
  -v $(pwd)/checks/sample_data:/data \
  -v $(pwd)/output_dir:/tmp/output \
  -p 8000:8000 objects-checker:1.1.0
```

Verify that the service is running:

```bash
curl http://localhost:8000/health
```

#### Test the Service

> **The `/process` path auto-derives the `clip_id` from the RDS-HQ archive, so the archive must contain exactly one clip with its layer folders at the top level.** After download, the service unzips `rds_hq_url` and derives `clip_id` from the first `*.tar` it finds; the RDS loader then resolves each layer as `<layer>/<clip_id>.tar` (e.g. `pose/<clip_id>.tar`) directly under the extraction root. A multi-clip archive makes the derived `clip_id` ambiguous, and an archive whose layer folders sit under an extra wrapper directory (e.g. `rds_hq/pose/...`) will not resolve. The shipped `checks/sample_data/morning/rds_hq.zip` is both multi-clip and wrapped in an `rds_hq/` directory, so it is intended for the [CLI](#cli) path (which takes an explicit `--input_data` and `--clip_id`), not this REST example. Note also that `world_model_video_url` is optional on the REST path just as `--world_video_path` is on the CLI: omit it to run the static check camera-only.
>
> The repo ships a ready-made REST fixture — `checks/sample_data/rds_hq_single_clip.zip` — a flat, single-clip archive (clip `0d21d408-...189000`) that pairs with the `0d21d408` world-model (`_0.mp4`) and augmented (`_rgb.mp4`) sample videos, all for the `camera_front_wide_120fov` camera. The example below uses it directly.

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "camera_name": "camera_front_wide_120fov",
    "rds_hq_url": "/data/rds_hq_single_clip.zip",
    "augmented_video_url": "/data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4",
    "world_model_video_url": "/data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4",
    "output_storage_prefix": "/tmp/output"
  }'
```

**Example output** (illustrative dynamic visualization, rendered from a different sample clip): [01ce78ad-9e9a-4df9-95d1-1d50e41a04ce_764657799000_764677799000.dynamic.object.mp4](../assets/01ce78ad-9e9a-4df9-95d1-1d50e41a04ce_764657799000_764677799000.dynamic.object.mp4)

**Request fields:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `rds_hq_url` | Yes | — | URL (or mounted filesystem path) to the RDS-HQ dataset archive. The `clip_id` is auto-derived from the archive and is not accepted as a request field. |
| `augmented_video_url` | Yes | — | URL or mounted filesystem path to the generated video (e.g. `/data/video.mp4`) |
| `world_model_video_url` | No | None | URL or mounted filesystem path to the world-model video used for two-stream static (CWIP) processing. Optional: omit it to run the static check camera-only. |
| `camera_name` | Yes | — | Camera stream name (e.g., `camera_front_wide_120fov`) |
| `config` | No | None | **Full** configuration dictionary that **replaces** the defaults from `checks/cosmos_evaluator.yaml` — if you send a non-empty `config` it must be complete (no partial configs, no assumed defaults), so each run is self-describing. Omitting it, or sending `null` or an empty `{}`, is treated identically and uses the image defaults; use the `/config` endpoint to retrieve them as a starting point. |
| `trial_frames` | No | None | Process only the first N frames (useful for debugging) |
| `verbose` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `output_storage_prefix` | No | `{service_name}/{clip_id}/` | Storage prefix for outputs. For cloud storage this is a key prefix and any leading slash is stripped before being used as a key. For local storage this is a directory path: an absolute path (e.g. `/tmp/output`) anchors uploads at the filesystem root, while a relative path resolves against the service's working directory. The storage backend itself (S3 vs local) and bucket / region are picked up from environment variables; service-specific overrides (e.g. `OBJECTS_*`) take precedence over the global defaults. |

**Other endpoints:**

```bash
# Health check
curl http://localhost:8000/health

# Get default configuration
curl http://localhost:8000/config
```

## Configuration

Configuration is managed through `checks/cosmos_evaluator.yaml` under the `av.objects_single_view` key. You can modify the defaults or pass a custom config dict via the API.

### Importance Filter

Controls which objects are included in the evaluation:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `allow_all_static_objects` | `true` | Include all static objects (infrastructure) regardless of other filters |
| `distance_threshold_m` | `100` | Maximum distance (meters) from ego vehicle. Objects beyond this are excluded. |
| `relevant_lanes` | `[ego, left, right]` | Only evaluate objects in these lane positions relative to the ego vehicle |
| `skip_oncoming_objects` | `false` | If true, exclude vehicles traveling in the opposite direction |

### Overlap Check Methods

Per-class scoring method configuration. Each object class uses one of two methods:

| Method | Description | Best For |
|--------|-------------|----------|
| `ratio` | `overlap_pixels / projected_area_pixels`. Simple area ratio. | Large, well-defined objects (vehicles, infrastructure) |
| `cluster` | Connected component analysis. Selects the largest connected region overlapping the projected cuboid, avoiding over-scoring from background segments. | Smaller objects that may be near similar-class objects (pedestrians, motorcycles) |

Default assignments:

```yaml
overlap_check:
  vehicle:        { method: ratio,   bottom_occlusion_abstain_frac: 0.5, min_in_frame_fraction: 0.5 }
  pedestrian:     { method: cluster, bottom_occlusion_abstain_frac: 0.5, min_in_frame_fraction: 1.0 }
  motorcycle:     { method: cluster, bottom_occlusion_abstain_frac: 0.5, min_in_frame_fraction: 1.0 }
  bicycle:        { method: cluster }
  traffic_light:  { method: ratio,   min_projection_area: 200, min_in_frame_fraction: 0.0, state_min_in_frame_fraction: 1.0 }
  traffic_sign:   { method: ratio,   min_projection_area: 300 }
  lane_line:      { method: ratio,   min_projection_area: 50 }
  road_boundary:  { method: ratio,   min_projection_area: 50 }
  wait_line:      { method: ratio,   min_projection_area: 50 }
  crosswalk:      { method: ratio,   min_projection_area: 200 }
```

### Frame-Edge Truncation Abstain

A cuboid that projects partly outside the image is cut off by the frame edge. The remaining sliver carries too
little signal to score: segmentation cannot match it, and a clipped traffic light exposes only part of its bulb
housing, so its color mass is measured over an arbitrary crop. Scoring either as a near-zero correspondence
would produce a false "missing" verdict, so the detector **abstains** — it leaves the per-frame score `NaN`
(excluded from the per-track mean), exactly as for an out-of-frame object.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_in_frame_fraction` | `1.0` (pedestrian, motorcycle), `0.5` (vehicle), `0.0` (traffic_light) | Abstain on a frame when the fraction of the object's projected bounding box lying inside the image is strictly below (`<`) this value, for the **correspondence** score. Accepts `0.0`–`1.0`: `1.0` requires the projection to be fully in-frame, so any single clipped pixel abstains; `0` or absent disables the gate. Values above `1.0` gate every frame (the measured fraction is capped at `1.0`); negative values behave like `0` and disable the gate. |
| `state_min_in_frame_fraction` | `1.0` (traffic_light); unused elsewhere | The same gate applied to the traffic-light **state** and multi-color scores. Same range and disable semantics. Independent of `min_in_frame_fraction` — there is no fallback in either direction. |

Notes:

- **Occlusion is deliberately not considered.** The fraction is computed from the object's own projected
  geometry against the image rectangle, ignoring the scene depth buffer — it asks "does this cuboid cross the
  image edge?", not "how much of it can be seen?". A cuboid fully hidden behind a nearer object still reports
  `1.0`. Use `bottom_occlusion_abstain_frac` and `min_projection_area` for occlusion-aware gating.
- Applies to **static and dynamic classes alike**. Only cuboids can be truncated; polyline and surface types
  (`lane_line`, `road_boundary`, `wait_line`, `crosswalk`) inherit the `RDSGeometry` default of `1.0`, so
  setting the key on them has no effect at any threshold within the valid range.
- **Correspondence and traffic-light state are gated separately, and traffic-light correspondence is ungated
  by default.** A clipped cuboid is far more damaging to reading bulb colors — a red bulb cut off at the frame
  edge can read as green — than to deciding whether a box is present at all. Correspondence also doubles as the
  **existence** verdict downstream (`collect_track_scores` feeds the `missing` / `detected` / `observed` buckets
  in `kpi/automotive/`), and a track gated in every frame has no valid scores at all, so
  it leaves the in-FOV denominator rather than counting as either present or missing. Gating existence to
  protect color reading would therefore move a metric that has nothing to do with color, which is why
  `traffic_light` ships `min_in_frame_fraction: 0.0` and `state_min_in_frame_fraction: 1.0`.
- Gated state frames record nothing, so they are excluded from the per-track `traffic_light_state_score` and
  `traffic_light_multi_color_score` means.
- `traffic_sign` intentionally has no threshold today, leaving the gate off for signs.

### Top-Only Occlusion Abstain

A dynamic object can be occluded from the bottom up by a nearer object so that only the top of its cuboid stays
visible. Scoring that thin sliver as a near-zero correspondence would produce a false "missing" verdict, so the
detector instead **abstains** — it leaves the per-frame score `NaN` (excluded from the per-track mean), exactly as
for an out-of-frame object — once the bottom-up occluded fraction reaches a threshold.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bottom_occlusion_abstain_frac` | `0.5` (vehicle, pedestrian, motorcycle) | Abstain on a frame when the cuboid is occluded from its ground-contact bottom upward by greater than or equal to this fraction (`>=`) of its projected height. `0` or absent disables the gate. Applies to dynamic classes only and requires the scene rasterizer (occlusion is computed cuboid-vs-cuboid); when the rasterizer is absent the object is scored normally. |

### Hallucination Detector

Detects false positive objects in the generated video that don't correspond to any ground truth:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Enable/disable hallucination detection |
| `max_cluster_per_frame` | `100` | Maximum clusters to analyze per frame |
| `classes.<class>.min_cluster_area` | varies | Minimum pixel area for a cluster to be considered a hallucination. Smaller values catch more detections but may increase false positives. |

Default minimum cluster areas:

| Class | Min Area (pixels) |
|-------|-------------------|
| vehicle | 5000 |
| motorcycle | 3000 |
| bicycle | 2000 |
| pedestrian | 1000 |
| traffic_light | 1000 |
| traffic_sign | 1000 |

### Visualization

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Generate overlay visualization videos showing projected cuboids and segmentation masks |

## Output Format

The check produces one JSON result file per processor that runs:

- `{clip_id}.dynamic.objects.results.json` — Dynamic processor results (always produced)
- `{clip_id}.static.objects.results.json` — Static (CWIP) processor results (always produced: two-stream when a world-model video is supplied — `--world_video_path` on the CLI, `world_model_video_url` on a `/process` request — and camera-only when it is omitted)

If visualization is enabled, corresponding video files are also generated:

- `{clip_id}.dynamic.object.viz.mp4`
- `{clip_id}.static.object.viz.mp4`

### JSON Structure

```json
{
  "processed_frames": 150,
  "total_video_frames": 300,
  "track_ids": [5, 12, 23, 45, 67],
  "processed_frame_ids": [0, 5, 10, 15, ...],

  "mean_score": 0.723,
  "std_score": 0.234,
  "min_score": 0.001,
  "max_score": 0.998,

  "processor_output_labels": [
    "scored",
    "occluded",
    "distance_threshold_m (100m)",
    "relevant_lanes (['ego', 'left', 'right'])"
  ],

  "tracks": [
    {
      "track_id": 5,
      "object_type": "Car",
      "processor_output": [10, 2, 10]
    },
    {
      "track_id": 1001,
      "object_type": "LaneLine",
      "object_type_index": 19,
      "processor_output": [150, 0, 0]
    }
  ],

  "score_matrix": {
    "format": "sparse",
    "shape": [150, 5],
    "data": [
      {"frame_idx": 0, "track_idx": 0, "score": 0.85},
      {"frame_idx": 0, "track_idx": 1, "score": 0.72}
    ]
  },

  "metadata": {
    "matrix_format": "sparse",
    "version": "1.0"
  }
}
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `processed_frames` | Number of frames where at least one object was evaluated |
| `total_video_frames` | Total frames in the input video |
| `track_ids` | List of unique object track IDs evaluated |
| `processed_frame_ids` | Frame indices that were processed |
| `mean_score` | Mean correspondence score across all valid (object, frame) pairs |
| `std_score` | Standard deviation of scores |
| `min_score` / `max_score` | Range of scores |
| `processor_output_labels` | Labels for the `processor_output` array in each track |
| `tracks[].track_id` | Unique object identifier |
| `tracks[].object_type` | Object class name |
| `tracks[].processor_output` | Per-label counts (e.g., [scored, occluded, filtered_by_distance]) |
| `score_matrix` | Sparse matrix of per-frame, per-track scores |

### Reconstructing the Score Matrix

The score matrix is stored in sparse format for efficiency. To reconstruct it:

```python
import json
import numpy as np

with open("results.json") as f:
    results = json.load(f)

matrix = results["score_matrix"]
scores = np.full(matrix["shape"], np.nan)

for entry in matrix["data"]:
    scores[entry["frame_idx"], entry["track_idx"]] = entry["score"]

# scores[i, j] = correspondence score for frame i, track j
# NaN means the object was not visible/evaluated in that frame
```

## Score Interpretation

| Score Range | Meaning |
|-------------|---------|
| **0.8 – 1.0** | Strong correspondence. The object appears where expected with good shape alignment. |
| **0.3 – 0.8** | Partial correspondence. The object is present but may be shifted, partially occluded, or have shape differences. |
| **0.0 – 0.3** | Poor correspondence. The object may be missing, severely misplaced, or incorrectly rendered. |

The `mean_score` across all objects and frames provides an overall quality metric for the generated video.

## Troubleshooting

### CUDA Out of Memory

The check runs a GPU model. If you encounter OOM errors:
- Reduce video resolution before processing
- Use `--trial N` to process fewer frames

### CPU Mode

If no GPU is available, use `--model_device cpu`. Processing will be significantly slower but functionally identical.

### Debug Logging

Use `--verbose DEBUG` for detailed frame-by-frame processing logs, including object projections, overlap calculations, and filtering decisions.
