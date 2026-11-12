# Hallucination Check

This checker looks for hallucinated movement in an augmented video. It compares movement masks between original and augmented videos and penalizes augmented dynamic pixels that are far from any dynamic region in the original. It is a pixel-motion consistency check rather than an object detector, and it does not identify motion that exists only in the original video.

## How it works

The hallucination check compares an augmented video against its paired original video and focuses on **dynamic pixels** rather than object categories.

The processing pipeline is:

1. **Loading Videos**: Load the original and augmented videos.
2. **Frame Alignment**: Compare the streams frame-by-frame over their shared length. If their frame counts differ, log the exact unmatched tail and ignore it for scoring.
3. **Dynamic Mask Construction**: Compute dynamic masks frame-to-frame for each aligned video stream.
4. **Hallucinated Pixel Counting**: Count augmented dynamic pixels farther than `dist_tol_px` from original dynamic regions.
5. **Score Computation**: Compute a score:
   `score = max(0.0, 1.0 - total_hallucinated_dynamic_pixels / total_augmented_dynamic_pixels)`
6. **Pass/Fail Decision**: Mark the clip as pass/fail using the configured `threshold`.

The implementation is split across:

- `processor.py`, which computes the final score
- `frame_processing.py`, which contains the low-level dynamic-mask comparison utilities
- `run.py`, which provides CLI config loading, execution, and result serialization

## Prerequisites and Compute Requirements

* **S3 Bucket and Credentials**: S3 is used to store the input videos for the hallucination checker. Set up the hallucination `.env` file with this information if you haven't already by following the instructions in the [Getting Started Guide](../getting_started.md#hallucination-check).
* **Checker Compute Requirements**: This checker container is CPU-only, and any linux machine will be able to run it. This checker is rather CPU-heavy, so machines with a more powerful CPU and more available CPU cores will be able to complete the checks faster, and run more requests in parallel.

## Inputs

The check requires a **paired set of videos**:

* **Original video**: the baseline video used as the reference
* **Augmented video**: the generated video being evaluated for motion hallucinations

It is simplest to use remote URIs such as `s3://...` for video inputs when testing locally. Supported remote schemes are `s3://`, `gs://`, `azure://`, `msc://`, and `https://`; unencrypted `http://` inputs are rejected.


## Configuration

Configuration lives in `checks/cosmos_evaluator.yaml` under `metropolis.hallucination`.

This file acts as both the default configuration file for the CLI, as well as provides the default configuration values for the service container.

An explanation of each config value is below:
* **blur_ksize**: Gaussian blur kernel size applied to the frame difference image before thresholding. Larger values smooth more noise but can suppress small motion details. Default: `7`.
* **dist_tol_px**: Distance tolerance, in pixels, used when comparing augmented motion against original motion. Augmented dynamic pixels farther than this from any original dynamic region are counted as hallucinated. Default: `7.0`.
* **grad_thresh**: Pixel-difference threshold used to convert the blurred frame-to-frame difference image into a binary dynamic mask. Higher values make motion detection less sensitive. Default: `10.0`.
* **morph_k**: Morphological opening kernel size applied to the binary dynamic mask to remove small noisy regions. Default: `3`.
* **max_frames**: Adds a cap on the number of frames from the videos to be processed for hallucination detection. Videos that are too large will be cut short once `max_frames` has been reached.
* **threshold**: Pass/fail cutoff for the final hallucination score. A clip passes when `score >= threshold`. Default: `0.682`.


The service request also accepts an optional `verbose` value of `DEBUG`, `INFO`, `WARNING`, or `ERROR`.

## Local CLI Testing

### Run the Checker

> Note: Before running this command, ensure that you have already gone through the steps from the [Getting Started](../getting_started.md) and [Customization](../customization.md) guides. Both the .env file and the build system setup must be complete before this command will work.

From the `cosmos-evaluator` (repo root) directory, run this command:

```bash
dazel run //checks/hallucination:run -- \
  --original-video-path s3://<bucket_name>/path/to/original.mp4 \
  --augmented-video-path s3://<bucket_name>/path/to/augmented.mp4
```

The documented CLI supports these options:

- **--clip-id** (optional): Clip identifier for the run. If omitted, the CLI generates a UUID automatically.
- **--augmented-video-path** (required): URI to the augmented video file being evaluated.
- **--original-video-path** (required): URI to the original reference video.
- **--config** (optional): Configuration file name to load, without the `.yaml` extension. Defaults to `cosmos_evaluator`.
- **--config-dir** (optional): Optional path to the directory containing the configuration file.
- **--verbose** (optional): Logging level for the run. Supported values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Defaults to `INFO`.
- **--env-file** (optional): Path to the `.env` file to load before processing. Defaults to `checks/hallucination/.env`.
- **--output-dir** (optional): Directory where the JSON results file is written. Defaults to `outputs`.

### Interpret the Output

The checker produces:

* A **score** in the range `[0, 1]`.
* A **pass/fail** result computed as `passed = (score >= threshold)`.
* A **duration** in seconds covering input download, decoding, and processing.
* A console summary with the score, threshold, pass/fail result, frame count, and pixel totals.
* A JSON results file named `{clip_id}.hallucination.results.json` under `--output-dir` with the above information.

The JSON results will look like this (score calculated as `1 - total_hallucinated / total_augmented`):

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

Higher scores indicate better agreement between the original and augmented motion patterns. Lower scores indicate more augmented motion away from the original video's dynamic regions. When video lengths differ, `total_frames` is the number of aligned frames scored; unmatched tail frames are reported in a warning and ignored.

## Building and Running the Service Container

The hallucination service wraps `HallucinationProcessor` behind a standardized REST API for containerized deployment.

The service exposes these endpoints:

- `GET /health` for health and version status
- `GET /config` to retrieve the default hallucination configuration
- `POST /process` to process one clip and return hallucination metrics

The `POST /process` request body includes:

* **clip_id** (required): This can be set to any arbitrary string, and is used to identify the video in the results
* **original_video_url** (required): Remote path (or local/mounted path) for the original video
* **augmented_video_url** (required): Remote path (or local/mounted path) for the augmented video
* **config** (optional): Dictionary with any config values which should be altered from the default value. Defaults to {}.
* **verbose** (optional): Logging level for the run. Supported values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Defaults to `INFO`.


### Build and Run the Container

First, build the container:

```bash
dazel build //services/hallucination:image
```

Next, load the built container into the local docker instance:

```bash
dazel run //services/hallucination:image_load
```

Finally, run the loaded container:

```bash
docker run --env-file=checks/hallucination/.env -p 8080:8080 hallucination-checker:1.1.0
```
