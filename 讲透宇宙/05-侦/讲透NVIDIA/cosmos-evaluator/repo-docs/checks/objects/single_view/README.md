# Objects Single-View Processing

This module provides single-camera objects correspondence analysis between AV World Model and Cosmos generated video output.

## Architecture

The system is built with a modular design consisting of several core components:

### Modules

- **`cuboid.py`**: `Cuboid` - 3D geometry and projection operations for objects cuboids
- **`seg_helper.py`**: `SegHelper` - Instance segmentation model and mask processing
- **`processor.py`**: `ObjectsProcessor` - Main orchestrator for the entire pipeline
- **`importance_filter.py`**: `ImportanceFilter` - Filters objects based on distance, oncoming, and lane criteria
- **`visualization_helper.py`**: `VisualizationHelper` - Frame visualization with object overlays and filter markers

### Entry Point

- **`run.py`**: Main entry point with command line interface and configuration management
- **`api.py`**: Core processing logic that runs both static and dynamic processors

## Features

- **Modular Design**: Clean separation of concerns with reusable components
- **Configuration Management**: Uses `cosmos_evaluator.yaml` for configurable thresholds and parameters
- **Comprehensive Logging**: Detailed progress tracking and error handling with DEBUG mode support
- **Advanced Visualization**: Generates frame-by-frame visualizations with:
  - Green contours for scored objects
  - Filter markers for unprocessed objects (red dots for distance, blue crosses for oncoming, blue circles for lanes, orange crosses for occluded)
  - Track IDs in DEBUG mode
  - Frame index and legend
- **Performance Profiling**: Automatic timing statistics for segmentation, processing, and visualization
- **Statistics**: Provides detailed statistics on correspondence scores
- **Trial Mode**: Process limited frames for quick testing and debugging
- **Camera-only mode**: Run the static (CWIP) check on the camera stream alone, without a world-model reference video (see [Camera-only mode](#camera-only-mode) below)
- **JSON Output**: Results automatically saved to `{clip_id}.static.objects.results.json` and `{clip_id}.dynamic.objects.results.json` with compact array formatting
- **Error Handling**: Comprehensive error handling with clear error messages for missing data and invalid inputs

## Usage

### Command Line Interface

Both static (CWIP) and dynamic (SegFormer) processors run together in a single invocation.
If `--world_video_path` is omitted, the static (CWIP) check runs **camera-only** on the camera stream alone
(see [Camera-only mode](#camera-only-mode)).

```bash
# Two-stream: static uses the world-model reference
dazel run //checks/objects/single_view:run -- \
  --input_data /path/to/rds_hq/ \
  --clip_id <clip_id> \
  --camera_name camera_front_wide_120fov \
  --video_path /path/to/camera.mp4 \
  --world_video_path /path/to/world.mp4 \
  --output_dir /tmp/results

# Camera-only: omit --world_video_path and the static check derives presence from the type head
dazel run //checks/objects/single_view:run -- \
  --input_data /path/to/rds_hq/ \
  --clip_id <clip_id> \
  --camera_name camera_front_wide_120fov \
  --video_path /path/to/camera.mp4 \
  --output_dir /tmp/results
```

For inputs that live in object storage rather than on disk, use the REST service instead: it takes URLs, downloads
them, and runs the same processors. See [the service README](../../../services/objects/single_view/README.md).

### Inference Caching (SegFormer and CWIP)

Both the dynamic (SegFormer) and static (CWIP) processors cache their inference outputs to disk by default.  This is
useful for evaluation runs that re-process the same video multiple times, since inference accounts for the majority of
runtime and depends only on the video content, not on world model metadata.

Caches are stored automatically — no configuration needed. Pass `--no_cache` to
disable caching (e.g. when testing with a modified model).

Cache layout:
- `~/.cache/cosmos_evaluator/inference/<clip_id>/`

| Processor | Cached artifact | Cache key | File layout |
|-----------|----------------|-----------|-------------|
| Dynamic (SegFormer) | Per-frame resized segmentation masks | `SHA-256(resolved_camera_video_path)[:16]` | `<cache_dir>/<video_hash>/frame_<N>.pt` |
| Static (CWIP) | Full inference result (similarity indices, type indices, raw type logits) | `SHA-256(resolved_camera_path + "\|" + resolved_world_path)[:16]` | `<cache_dir>/<pair_hash>/inference.pt` |

**Cache key note**: Both caches use the *resolved absolute path string* as the key,
not the file contents.  Two runs pointing at the same path always share a cache entry;
the same file accessed via a different path (symlink, re-download) will produce a cache
miss.

```bash
# First run: inference is executed and results are cached to ~/.cache/cosmos_evaluator/inference/<clip_id>/
dazel run //checks/objects/single_view:run -- \
  --video_path /data/clip.mp4 --world_video_path /data/world.mp4 <other args>

# Subsequent runs: both SegFormer masks and CWIP outputs are loaded from cache
dazel run //checks/objects/single_view:run -- \
  --video_path /data/clip.mp4 --world_video_path /data/world.mp4 <other args with different WM>

# Disable caching (e.g. after updating a model)
dazel run //checks/objects/single_view:run -- \
  --video_path /data/clip.mp4 --world_video_path /data/world.mp4 --no_cache <other args>
```

### Configuration

The system uses `cosmos_evaluator.yaml` by default for configuration:

```yaml
av.objects_single_view:
  overlap_check:
    vehicle:
      method: ratio                        # scoring method: ratio | cluster
      bottom_occlusion_abstain_frac: 0.5   # abstain (NaN) when only the cuboid top is visible; dynamic only, 0 disables
      min_in_frame_fraction: 0.5           # abstain (NaN) when the frame edge truncates the cuboid below this
                                           # fraction of its projected bbox; occlusion-independent, 0/absent disables
    pedestrian:
      method: cluster
      bottom_occlusion_abstain_frac: 0.5
      min_in_frame_fraction: 1.0
    motorcycle:
      method: cluster
      bottom_occlusion_abstain_frac: 0.5
      min_in_frame_fraction: 1.0
    traffic_light:
      method: ratio
      min_projection_area: 200             # skip frames whose post-occlusion visible area is below this (pixels²)
      min_in_frame_fraction: 0.0           # existence deliberately ungated for lights
      state_min_in_frame_fraction: 1.0     # gates only the state / multi-color scores
    traffic_sign:
      method: ratio
      min_projection_area: 300
    lane_line:
      method: spine                        # centerline scoring; see below
      min_projection_area: 50
      spine_match_tolerance_px: 0          # dilate the class mask by this before matching; 0 = exact
      spine_min_ribbon_width_px: 0         # stop scoring where the ribbon is too thin to resolve; 0 = off
    road_boundary:
      method: spine
      min_projection_area: 50
      spine_match_tolerance_px: 0
      spine_min_ribbon_width_px: 0

  hallucination_detector:
    classes:
      lane_line:
        min_cluster_area: 16
        tracker: bev_ground                # group detections in world space, not by per-frame bbox overlap
        min_track_frames: 5                # distinct frames, not a consecutive run
      road_boundary:                       # both polyline classes are enabled
        min_cluster_area: 32
        tracker: bev_ground
        min_track_frames: 5
    bev_resolution_m: 0.1                  # bird's-eye grid for tracker: bev_ground
    bev_thickness_px: 7                    # stroke width; bridges the gap between dashes without reaching
                                           # the next lane, ~3 m away

  importance_filter:
    distance_threshold_m: 50.0
    skip_oncoming_objects: true
    relevant_lanes: ["ego", "left", "right"]
```

#### Scoring methods

`ratio` divides matched pixels by the projected silhouette's area and `cluster` by the area of the segmentation
components the projection intersects. Both suit geometry whose projected extent is its real extent.

`spine` is for the polyline types (`lane_line`, `road_boundary`, `wait_line`) and scores the fraction of the
projected, undilated **centerline** that carries the class label. An area metric mis-serves a polyline because
its silhouette is the `Polyline.half_width_meters` ribbon — 0.4 m wide by decree, against roughly 0.10–0.15 m of
real paint — so a perfectly reproduced line cannot score near 1, and the metric reports that half-width as much
as the world model. The centerline has no such invented width. Setting `spine` on a cuboid or surface type has
no effect: those geometries have no centerline and fall back to `ratio`.

Two knobs shape it, both shipped at `0` because a baseline clip cannot justify a value — it measures how the
score moves, which cannot separate "the metric improved" from "the low scores were excluded". Tuning them wants
the polyline perturbation KPI, where a deleted line gives a true positive to trade against:

- `spine_match_tolerance_px` dilates the class mask before matching, to absorb the few-pixel quantization of the
  nearest-neighbor-upsampled segmentation mask. Image-space, because that error is constant in pixels while the
  polyline's world-space half-width shrinks with range.
- `spine_min_ribbon_width_px` stops the scored centerline where the ribbon projects narrower than the mask can
  resolve, so a long line is not penalised for a far field that could only ever score 0. Pixels rather than
  meters, so the cutoff moves with focal length, image size and `half_width_meters` instead of being pinned to
  one camera.

`min_projection_area` still applies to the polyline types even though the spine score never reads it. Ribbon
area is length × apparent width, and apparent width is what decides whether the segmentation can resolve the
line at all: below ~250 px² a road-boundary centerline matches on essentially no frame, above it 1–6% do. A
centerline-length gate was tried instead and does not discriminate — the frames that score nothing are long and
thin, not short.

**Changing config values.** Edit `cosmos_evaluator.yaml` under `av.objects_single_view` (or point `--config` at an
alternate file). Over the REST service, a non-empty `config` in the request **replaces** the defaults entirely — if
you send one it must be the **full** configuration, so each run is self-describing with no assumed defaults. Omitting
`config`, or sending `null` or an empty `{}`, is treated identically and uses the image defaults; call the `/config`
endpoint to retrieve them as a starting point.

**Debug dump (opt-in).** Set `debug_dump: true` under `av.objects_single_view` to persist the static processor's raw
CWIP output and hallucination intermediates to `<output_dir>/debug/` (per-frame `hallucination_masks/frame_*.npz` and
a compact `cwip_compact.npz`); when that `debug/` tree exists the REST service best-effort tars and uploads it
alongside the results and, on success, publishes its location in the response as `debug_artifacts_url` /
`debug_artifacts_presigned_url` (a tar/upload failure is logged and leaves those fields null, without failing the
request). It is **off by default** (zero overhead when unset). Set `debug_dump_full_logits: true` to additionally dump the full-fidelity float
`cwip_inference.pt` (~GB/clip) instead of the compact npz.

```yaml
av.objects_single_view:
  debug_dump: true
  debug_dump_full_logits: false
```

### Camera-only mode

The static (CWIP) check normally consumes both the camera video and a world-model reference and derives every
static signal from the CWIP **similarity** head (the per-patch MATCH / EXTRA / MISSING labels), which needs the
reference. Camera-only mode runs CWIP on the camera stream alone: the similarity head is unavailable, so the
per-class **presence mask** that correspondence and hallucination read is derived from the **type** head instead.
It is selected by **not supplying a world-model video**: omit `--world_video_path` on the CLI, or omit
`world_model_video_url` on a REST request. The type-head mask is configured by the `presence` block (see
[Presence layer](#presence-layer)), which two-stream runs share.

The semantics shift accordingly: correspondence measures "class detected in the rendered frame" rather than
"agrees with the world reference", so a low-but-nonzero score no longer means "disagrees with the world" —
missing-object (score ≈ 0) stays meaningful. The static results record `camera_only` (`true`/`false`) so downstream readers can tell a camera-only run apart from a two-stream one — otherwise indistinguishable now that an absent world video selects camera-only automatically.

### Presence layer

Correspondence and hallucination read layer 0 of the class-mask tensor, a per-patch presence mask, from one of two
sources: the similarity head (MATCH patches for correspondence, EXTRA patches for hallucination; two-stream only) or the
type-head mask. The `presence` block configures both modes:

- `source` selects how a two-stream run builds the layer: the similarity verdict, the type-head mask, or their union
  (the default) or intersection. The choice applies to both checks. A camera-only run has no similarity head and always
  uses the type-head mask.
- `type_mask` configures the type-head mask, used by camera-only runs and by every two-stream source except
  `similarity`.
- `hallucination_overrides` tightens the hallucination tracker per class whenever the hallucination layer includes
  type-head-only patches: camera-only runs and two-stream `type` / `union`. The type-head mask over-produces small,
  short-lived clusters relative to the similarity mask. `similarity` and `intersection` cannot add such patches and take
  no overrides. The shared `hallucination_detector.classes` knobs are untouched.

```yaml
av.objects_single_view:
  presence:
    # Two-stream runs only; a camera-only run always uses the type mask.
    #   similarity   - MATCH for correspondence, EXTRA for hallucination
    #   type         - the type-head mask for both checks, as in a camera-only run
    #   union        - the similarity verdict OR the type-head mask (default)
    #   intersection - the similarity verdict AND the type-head mask
    source: union
    type_mask:
      #   confidence - a patch is present when its top type-class probability >= confidence_threshold
      #   argmax     - every patch is present; the class filter alone selects the queried type (threshold-free)
      gate: confidence
      confidence_threshold: 0.5         # global probability gate in [0, 1] for gate=confidence
      per_class_thresholds: {}          # optional per-class overrides, e.g. {traffic_light: 0.6}
    # Applied for camera-only, and for two-stream type / union. min_cluster_area is enforced in the detector, so an
    # offline sweep over recorded results can only raise it; min_track_frames stays sweepable in either direction.
    hallucination_overrides:
      traffic_sign:
        min_cluster_area: 300
        min_track_frames: 5
```

The block is validated on every processor construction: an unknown key, source, or gate, a probability outside
`[0, 1]`, or an override for a class without a static hallucination-detector entry fails the job rather than silently
taking no effect. Objects-config keys named `camera_only` or `two_stream` are rejected for the same reason.

The static results record the presence source as `presence_source` (`presence.source` for a two-stream run, `type` for
a camera-only run) and every presence setting the scores depend on as `presence`: the source, the type-mask settings
(`null` for `similarity`), and the hallucination overrides applied.

The `confidence` gate needs the patch-resolution type logits, which a compact debug dump does not store. The compact
dump is accompanied by the run's type-head presence masks instead (`type_presence.npz`: bit-packed, on the grid the
frame loop scores, with the type-mask settings that produced them), so a replay reproduces the run's presence layers
exactly. A replay whose type-mask settings differ from the dumped ones, or
of a dump without the masks, fails with a `ValueError` before any data is loaded; `source=similarity` (two-stream) and
`type_mask.gate=argmax` replay without them.

To inspect the masks a setting produces on a clip before running the check, the CWIP inference tool writes them with
`--save_presence_masks`, taking the same options as flags (see
[presence masks](../../utils/models/cwip/tools/README.md#presence-masks---save_presence_masks)).

## Processing Pipeline

1. **Data Loading**: Load camera poses, intrinsics, and object data from the dataset
2. **Video Processing**: Process video frames through instance segmentation model
3. **Object Analysis**: For each frame, analyze correspondence between:
   - World model cuboids (projected to image space)
   - Segmentation masks (detected objects in image)
4. **Importance Filtering**: Apply filters for distance, oncoming, and lane-based criteria
5. **Score Computation**: Calculate correspondence scores based on overlap
6. **Matrix Building**: Build 2D score matrix (frames × track_ids) with NaN for missing observations
7. **Statistics**: Compute overall statistics using robust NaN-aware methods
8. **Performance Profiling**: Track timing for segmentation, processing, and visualization steps

## Output

- **Score Matrix**: 2D NumPy array (frames × track_ids) with correspondence scores
- **JSON Results**: Results saved to `{clip_id}.static.objects.results.json` and `{clip_id}.dynamic.objects.results.json` with compact array formatting
- **Statistics**: Console output with processing statistics (mean, std, min, max)
- **Track IDs**: Set of all unique track IDs processed
- **Tracks Summary**: Unified list of tracks, each with `track_id`, `object_type`, `object_type_index` (static objects only), `lane_style` (lane lines whose RDS-HQ attributes record a style: the most common value of the line's per-vertex `styles`, which selects a dashed line's existence cutoff), and `processor_output` (integer counts aligned to `processor_output_labels`)
- **Detailed Results**: Optional verbose output with detailed results
- **Performance Summary**: Timing statistics for segmentation, processing, and visualization
- **Visualization**: Frame-by-frame visualization with object overlays and filter markers
- **Log Files**: Detailed logs with DEBUG information when verbose mode is enabled

### JSON Results Format

Results are automatically saved to `{clip_id}.static.objects.results.json` and `{clip_id}.dynamic.objects.results.json`:

```json
{
  "processed_frames": 150,
  "track_ids": [5,12,23,45,67],
  "processed_frame_ids": [0,5,10,15,20],
  "processor_output_labels": ["scored", "occluded", "distance_threshold_m (100m)"],
  "tracks": [
    {
      "track_id": 5,
      "object_type": "Car",
      "processor_output": [10, 2, 10]
    },
    {
      "track_id": 12,
      "object_type": "Pedestrian",
      "processor_output": [8, 0, 0]
    },
    {
      "track_id": 1001,
      "object_type": "LaneLine",
      "object_type_index": 19,
      "lane_style": "LONG_DASHED_SINGLE",
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
  "mean_score": 0.723,
  "std_score": 0.234,
  "min_score": 0.001,
  "max_score": 0.998
}
```

Note: The `object_type_index` field is only present for static objects (lane lines, road boundaries, traffic lights, traffic signs, wait lines, crosswalks) and corresponds to the CWIP model's object type classification.

## Example Output

```bash
Configuration loaded successfully:
  - Overlap check: {'vehicle': {'method': 'bev', 'threshold': 0.5}, ...}
  - Importance filter: {'distance_threshold_m': 50.0, ...}
  - Model device: cuda

Processing with arguments:
  - Input data: ~/rds_hq/
  - Clip ID: cc998c05-705c-4f3a-ae9a-f1dd3cb0e3f0_563770219000
  - Camera name: camera_front_wide_120fov
  - Video path: ~/rendered_wm/cc998c05-705c-4f3a-ae9a-f1dd3cb0e3f0_563770219000_Original.mp4
  - World video path: ~/rendered_wm/cc998c05-705c-4f3a-ae9a-f1dd3cb0e3f0_563770219000_WM.mp4
  - Output directory: /tmp/masks_cc998c05-705c-4f3a-ae9a-f1dd3cb0e3f0_563770219000
  - Log level: INFO

Starting object processing...
INFO: Loading data for clip cc998c05-705c-4f3a-ae9a-f1dd3cb0e3f0_563770219000
INFO: Starting frame processing
INFO: Processed frame 0
INFO: Processed frame 10
...

============================================================
PERFORMANCE PROFILING SUMMARY
============================================================
segmentation:
  Total: 12.345s (45.2%)
  Average: 0.082s
  Count: 150
  Range: 0.075s - 0.095s
processing:
  Total: 10.234s (37.5%)
  Average: 0.068s
  Count: 150
  Range: 0.062s - 0.078s
visualization:
  Total: 4.789s (17.3%)
  Average: 0.032s
  Count: 150
  Range: 0.028s - 0.041s

Total processing time: 27.368s
============================================================

Processing complete!

=== STATIC Processor Results ===
  - Total frames processed: 150
  - Unique track IDs: 23
  - Score matrix shape: (150, 24)
  - Mean correspondence score: 0.723
  - Score range: 0.000 - 1.000
  - Standard deviation: 0.234

=== DYNAMIC Processor Results ===
  - Total frames processed: 150
  - Unique track IDs: 23
  - Score matrix shape: (150, 24)
  - Mean correspondence score: 0.812
  - Score range: 0.000 - 1.000
  - Standard deviation: 0.189
```

## Error Handling

The system provides comprehensive error handling:
- **Data Loading**: Clear error messages for missing camera data or invalid model types
- **Configuration**: Validation of config file paths and parameters
- **Processing**: Graceful handling of missing object data and invalid inputs

## Troubleshooting

### Common Issues

1. **Missing Camera Data**: Ensure camera intrinsics files exist in the dataset
2. **Invalid Model Types**: Use "pinhole" or "ftheta" for camera model types
3. **Memory Issues**: Use trial mode (`--trial N`) for large videos
4. **CUDA Errors**: Fallback to CPU processing if GPU unavailable

### Debug Mode

Use `--verbose DEBUG` for detailed logging and visualization with track IDs.

## Development

### Adding New Object Types

To add support for new object types (e.g., trucks, motorcycles):

1. Update the configuration in `cosmos_evaluator.yaml` under `av.objects_single_view.overlap_check`
2. Modify `ObjectsProcessor._get_objects_by_class()` to map new object types
3. Add corresponding segmentation class support in `SegHelper.get_class_mask()`

### Extending Importance Filters

To add new filtering criteria:

1. Add new filter methods to `ImportanceFilter` class
2. Update the filter configuration in `cosmos_evaluator.yaml`
3. Modify `ImportanceFilter.should_process_object()` to include new checks

### Debugging and Logging

The system provides comprehensive debugging capabilities:

- **DEBUG Mode**: Use `--verbose DEBUG` to enable detailed logging including:
  - Ego position and orientation in world coordinates
  - Object positions in both ego and world coordinates
  - Track IDs displayed on visualization
  - Detailed filter reasoning
- **Trial Mode**: Use `--trial N` to process only the first N frames for quick testing
- **Performance Profiling**: Automatic timing statistics for segmentation, processing, and visualization
- **Log Files**: Clean log files (cleared at each run) with detailed processing information

### Performance Optimization

- The system uses CUDA for model inference when available
- Consider batch processing for multiple clips
- Profile and optimize data loading for large datasets
