# Hallucination Detection

This check detects motion hallucinations by comparing dynamic pixels in an augmented video against a paired original video.

## Architecture

Core modules:

- **`processor.py`**: Implements `HallucinationProcessor` and computes the final score.
- **`frame_processing.py`**: Contains low-level utilities for dynamic-mask comparison.
- **`run.py`**: CLI entry point for config loading, execution, and result serialization.

## Features

- Config-driven parameters via `checks/cosmos_evaluator.yaml` (`metropolis.hallucination`)
- Supports local files and secure remote URIs (`s3://`, `gs://`, `azure://`, `msc://`, and `https://`)
- Structured JSON output per clip
- Logging control with `--verbose`

## Processing Pipeline

1. Load original and augmented videos.
2. Align the streams frame-by-frame over their shared length, warning when either stream has unmatched tail frames.
3. Compute dynamic masks frame-to-frame for each aligned stream.
4. Count augmented dynamic pixels that are farther than `dist_tol_px` from original dynamic regions.
5. Compute final score:
   `score = max(0.0, 1.0 - total_hallucinated_dynamic_pixels / total_augmented_dynamic_pixels)`
6. Mark pass/fail using configured `threshold`.

## Usage

### Prerequisites

- Create `checks/hallucination/.env` from `.env.example` and set credentials if using private remote storage. For information related to setting up multistorage, see https://nvidia.github.io/multi-storage-client/references/configuration.html. Use JSON as the data format when building the configuration.
- Ensure both video paths are valid and accessible.

### Command Line Interface

```bash
usage: run.py [-h] [--clip-id CLIP_ID] --augmented-video-path AUGMENTED_VIDEO_PATH --original-video-path ORIGINAL_VIDEO_PATH [--config CONFIG]
              [--config-dir CONFIG_DIR] [--verbose {DEBUG,INFO,WARNING,ERROR}] [--env-file ENV_FILE] [--output-dir OUTPUT_DIR]

Hallucination Detection Tool

options:
  -h, --help            show this help message and exit
  --clip-id CLIP_ID     Clip ID for processing (default: 25db94dd-16ea-458d-a4fe-76d224b5a226)
  --augmented-video-path AUGMENTED_VIDEO_PATH
                        Path to the augmented video file (default: None)
  --original-video-path ORIGINAL_VIDEO_PATH
                        Path to the original video file (default: None)
  --config CONFIG       Configuration file name (without .yaml extension, defaults to 'cosmos_evaluator') (default: cosmos_evaluator)
  --config-dir CONFIG_DIR
                        Path to the configuration directory (default: None)
  --verbose {DEBUG,INFO,WARNING,ERROR}
                        Set logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)
  --env-file ENV_FILE   Path to the .env file to load (default: checks/hallucination/.env)
  --output-dir OUTPUT_DIR
                        Path to the output directory (default: outputs)
```

### Example Command

```bash
dazel run --auto_output_filter=none //checks/hallucination:run -- \
  --original-video-path s3://omniverse-metropolis-sdg-dev-us-west-2/common/cosmos_evaluator/test_inputs/hallucination/original.mp4 \
  --augmented-video-path s3://omniverse-metropolis-sdg-dev-us-west-2/common/cosmos_evaluator/test_inputs/hallucination/augmented.mp4
```

## Output

- **Score**: `1 - (total_hallucinated_dynamic_pixels / total_augmented_dynamic_pixels)` in `[0, 1]`
- **Pass/Fail**: `passed = (score >= threshold)`
- **Duration**: elapsed download, decode, and processing time in seconds
- **JSON file**: `{clip_id}.hallucination.results.json` under `--output-dir`
- **Console summary**: score, threshold, pass/fail, frame count, and pixel totals

### JSON Results Format

```json
{
  "clip_id": "55e7790f-8548-410d-a7de-8328bfc51c78",
  "passed": true,
  "threshold": 0.682,
  "score": 0.8255804747848313,
  "total_frames": 31,
  "total_hallucinated_dynamic_pixels": 15422,
  "total_augmented_dynamic_pixels": 88419,
  "duration_seconds": 2.418
}
```

## Troubleshooting

### Common Issues

1. **Missing credentials**: Confirm `checks/hallucination/.env` is configured when using protected remote paths.
2. **Invalid paths**: Verify both `--original-video-path` and `--augmented-video-path` point to readable videos.
3. **Frame-count warnings**: The checker scores only aligned frames and ignores the unmatched tail of the longer video.
4. **Unexpected score changes**: Check `metropolis.hallucination.threshold` and related params in `checks/cosmos_evaluator.yaml`.
