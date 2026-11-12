# Tutorial: Building a Custom Checker

This tutorial walks through building a complete custom checker — a **Brightness Check** that scores whether a generated video has the expected brightness level. It's intentionally simple so you can focus on the framework patterns rather than complex evaluation logic.

By the end, you'll have:
- A standalone CLI tool that runs the check locally
- A REST API microservice that wraps the check
- Integration with the Cosmos Evaluator service framework

## Overview

Our Brightness Check will:
1. Sample frames from a video
2. Calculate the average brightness (luminance) of each frame
3. Compare against an expected brightness level (dark, medium, bright)
4. Return a score from 0.0 to 1.0

## Step 1: Project Structure

Create the following directory structure:

```
checks/brightness/
├── BUILD.bazel
├── brightness_processor.py     # Core evaluation logic
├── api.py                      # Public API function
├── run.py                      # CLI entry point
└── tests/
    ├── BUILD.bazel
    └── brightness_processor_test.py

services/brightness/
├── BUILD.bazel
├── models.py                   # Pydantic request/response models
├── service.py                  # ServiceBase implementation
├── settings.py                 # Service configuration
├── rest_api_common.py          # FastAPI app definition
└── rest_api.py                 # Entry point
```

## Step 2: Core Evaluation Logic

The processor contains your evaluation algorithm. Keep it independent of the service framework — it should work as a plain Python function.

**`checks/brightness/brightness_processor.py`**:

```python
"""Brightness evaluation processor."""

import logging
from typing import Any, Dict, Optional

import cv2
import numpy as np

from checks.utils.video import get_video_fps, get_video_frame_count, iter_video_frames

logger = logging.getLogger(__name__)

# Expected luminance ranges for each brightness level
BRIGHTNESS_LEVELS = {
    "dark": (0, 80),
    "medium": (80, 170),
    "bright": (170, 255),
}


def process_brightness(
    video_path: str,
    expected_brightness: str,
    keyframe_interval_s: float = 2.0,
    trial_frames: Optional[int] = None,
) -> Dict[str, Any]:
    """Evaluate video brightness against an expected level.

    Args:
        video_path: Path to the video file.
        expected_brightness: Expected level — "dark", "medium", or "bright".
        keyframe_interval_s: Seconds between sampled frames.
        trial_frames: If set, process at most this many frames.

    Returns:
        Dictionary with score, per-frame details, and metadata.
    """
    if expected_brightness not in BRIGHTNESS_LEVELS:
        raise ValueError(
            f"Invalid brightness level: {expected_brightness}. "
            f"Must be one of: {list(BRIGHTNESS_LEVELS.keys())}"
        )

    expected_min, expected_max = BRIGHTNESS_LEVELS[expected_brightness]

    # Video I/O goes through the repo's ffmpeg-based helpers, NOT cv2.VideoCapture: the vendored
    # opencv-python-headless is built WITH_FFMPEG=OFF, so cv2 has no video backend (see the note below).
    # cv2 image ops (cvtColor, resize, ...) still work, so we keep cv2 for the grayscale conversion.
    fps = get_video_fps(video_path)
    total_frames = get_video_frame_count(video_path)
    if fps is None or total_frames is None:
        raise ValueError(f"Cannot open video: {video_path}")

    frame_interval = max(1, int(fps * keyframe_interval_s))

    frame_scores = []

    # iter_video_frames yields BGR uint8 frames (same layout as cv2.VideoCapture.read); `step` subsamples to every
    # `frame_interval`-th frame and `max_frames` caps a trial run (counted after subsampling).
    for sample_idx, frame in enumerate(
        iter_video_frames(video_path, max_frames=trial_frames, step=frame_interval)
    ):
        frame_idx = sample_idx * frame_interval

        # Convert to grayscale and compute mean luminance
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        luminance = float(np.mean(gray))

        # Score: 1.0 if within range, scaled down by distance from range
        if expected_min <= luminance <= expected_max:
            score = 1.0
        else:
            distance = min(abs(luminance - expected_min), abs(luminance - expected_max))
            score = max(0.0, 1.0 - distance / 128.0)

        frame_scores.append({
            "frame_idx": frame_idx,
            "luminance": round(luminance, 1),
            "score": round(score, 3),
        })

        logger.debug("Frame %d: luminance=%.1f, score=%.3f", frame_idx, luminance, score)

    if not frame_scores:
        raise ValueError(f"No frames could be extracted from: {video_path}")

    scores = [f["score"] for f in frame_scores]
    mean_score = float(np.mean(scores))

    return {
        "mean_score": round(mean_score, 3),
        "min_score": round(float(np.min(scores)), 3),
        "max_score": round(float(np.max(scores)), 3),
        "frames_evaluated": len(frame_scores),
        "total_video_frames": total_frames,
        "expected_brightness": expected_brightness,
        "frame_details": frame_scores,
    }
```

> **Video decoding with the vendored ffmpeg-less OpenCV.** This repo vendors a custom `opencv-python-headless` wheel built with `-DWITH_FFMPEG=OFF` (strict LGPL — no bundled FFmpeg). As a result, `cv2.VideoCapture` / `cv2.VideoWriter` have **no backend and fail at runtime**, while all cv2 *image* ops (`cvtColor`, `resize`, `imencode`, ...) keep working. For video I/O, use the helpers in [`checks/utils/video.py`](../../checks/utils/video.py), which shell out to the repo's vendored LGPL ffmpeg binary:
>
> - `iter_video_frames(video_path, max_frames=..., start_frame=..., step=...)` — a `cv2.VideoCapture` read-loop replacement that yields BGR `uint8` frames (same layout as `cap.read()`).
> - `read_video_frame(video_path, frame_idx)` — frame-accurate single-frame read (replaces `cap.set(CAP_PROP_POS_FRAMES, i)` + `cap.read()`).
> - `get_video_fps`, `get_video_frame_count`, `get_video_dimensions` — ffprobe-backed replacements for the `cv2.CAP_PROP_*` queries.
> - `VideoWriter` — pipes frames to ffmpeg (replaces `cv2.VideoWriter`).

## Step 3: Public API

Wrap the processor in a clean API function that handles configuration loading.

**`checks/brightness/api.py`**:

```python
"""Public API for the brightness check."""

from typing import Any, Dict, Optional

from checks.brightness.brightness_processor import process_brightness


def run_brightness_check(
    video_path: str,
    expected_brightness: str,
    keyframe_interval_s: float = 2.0,
    trial_frames: Optional[int] = None,
) -> Dict[str, Any]:
    """Run brightness evaluation on a video.

    Args:
        video_path: Path to the video file.
        expected_brightness: Expected brightness level ("dark", "medium", "bright").
        keyframe_interval_s: Seconds between sampled frames.
        trial_frames: If set, process at most this many frames.

    Returns:
        Result dictionary with scores and metadata.
    """
    return process_brightness(
        video_path=video_path,
        expected_brightness=expected_brightness,
        keyframe_interval_s=keyframe_interval_s,
        trial_frames=trial_frames,
    )
```

## Step 4: CLI Entry Point

**`checks/brightness/run.py`**:

```python
"""CLI entry point for the brightness check."""

import argparse
import json
import logging
import sys
from pathlib import Path

from checks.brightness.api import run_brightness_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Brightness Check")
    parser.add_argument("--video_path", required=True, help="Path to video file")
    parser.add_argument(
        "--expected_brightness",
        required=True,
        choices=["dark", "medium", "bright"],
        help="Expected brightness level",
    )
    parser.add_argument("--output_dir", required=True, help="Output directory")
    parser.add_argument("--keyframe_interval_s", type=float, default=2.0)
    parser.add_argument("--trial", type=int, default=None, help="Process only N frames")
    parser.add_argument(
        "--verbose",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.verbose))

    result = run_brightness_check(
        video_path=args.video_path,
        expected_brightness=args.expected_brightness,
        keyframe_interval_s=args.keyframe_interval_s,
        trial_frames=args.trial,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "brightness.results.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {result['mean_score']:.3f} (evaluated {result['frames_evaluated']} frames)")
    print(f"Results written to: {output_file}")


if __name__ == "__main__":
    main()
```

## Step 5: Bazel BUILD File for the Check

**`checks/brightness/BUILD.bazel`**:

```python
py_library(
    name = "brightness_processor",
    srcs = ["brightness_processor.py"],
    visibility = ["//visibility:public"],
    deps = [
        "//checks/utils:video",
        "@opencv_python_headless",
        "@pypi//numpy",
    ],
)

py_library(
    name = "api",
    srcs = ["api.py"],
    visibility = ["//visibility:public"],
    deps = [":brightness_processor"],
)

py_binary(
    name = "run",
    srcs = ["run.py"],
    deps = [":api"],
)
```

At this point, you can run the check locally:

```bash
dazel run //checks/brightness:run -- \
  --video_path /path/to/video.mp4 \
  --expected_brightness medium \
  --output_dir /tmp/brightness_results
```

## Step 6: Service Models

Now let's wrap the check as a REST API microservice.

**`services/brightness/models.py`**:

```python
"""Request and response models for the brightness service."""

from pydantic import BaseModel, Field


class BrightnessRequest(BaseModel):
    """Request model for brightness check."""

    video_path: str = Field(..., description="Path to the video file")
    expected_brightness: str = Field(
        ...,
        description="Expected brightness level",
        pattern="^(dark|medium|bright)$",
    )
    keyframe_interval_s: float = Field(default=2.0, gt=0, description="Seconds between keyframes")
    trial_frames: int | None = Field(default=None, gt=0, description="Max frames to process")


class BrightnessResult(BaseModel):
    """Response model for brightness check."""

    mean_score: float = Field(..., description="Mean brightness score (0-1)")
    min_score: float = Field(..., description="Minimum frame score")
    max_score: float = Field(..., description="Maximum frame score")
    frames_evaluated: int = Field(..., description="Number of frames evaluated")
    total_video_frames: int = Field(..., description="Total frames in video")
    expected_brightness: str = Field(..., description="Expected brightness level")
```

## Step 7: Service Implementation

**`services/brightness/service.py`**:

```python
"""Brightness check service implementation."""

import asyncio
from typing import Any, Dict

from checks.brightness.api import run_brightness_check
from services.brightness.models import BrightnessRequest, BrightnessResult
from services.framework.service_base import ServiceBase


class BrightnessService(ServiceBase[BrightnessRequest, BrightnessResult]):
    """Service wrapper for the brightness check."""

    async def validate_input(self, request: BrightnessRequest) -> bool:
        """Validate the request. Pydantic handles most validation via the model."""
        return True

    async def process(self, request: BrightnessRequest) -> BrightnessResult:
        """Run the brightness check."""
        loop = asyncio.get_running_loop()

        # Run the synchronous check in a thread pool to avoid blocking the event loop
        result = await loop.run_in_executor(
            None,
            lambda: run_brightness_check(
                video_path=request.video_path,
                expected_brightness=request.expected_brightness,
                keyframe_interval_s=request.keyframe_interval_s,
                trial_frames=request.trial_frames,
            ),
        )

        return BrightnessResult(**result)

    @staticmethod
    async def get_default_config() -> Dict[str, Any]:
        return {
            "keyframe_interval_s": 2.0,
            "brightness_levels": ["dark", "medium", "bright"],
        }
```

## Step 8: Service Settings

**`services/brightness/settings.py`**:

```python
"""Settings for the brightness service."""

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from services.settings_base import SettingsBase


class Settings(SettingsBase):
    """Brightness service settings."""

    model_config = SettingsConfigDict(
        env_prefix="BRIGHTNESS_",
        extra="ignore",
        case_sensitive=False,
        frozen=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings(_env_file=SettingsBase.get_env_files())
```

## Step 9: REST API

**`services/brightness/rest_api_common.py`**:

```python
"""FastAPI application for the brightness service."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.brightness.models import BrightnessRequest
from services.brightness.service import BrightnessService
from services.brightness.settings import get_settings
from services.framework.response_formatters.json_response_formatter import JsonResponseFormatter

service: BrightnessService | None = None
formatter = JsonResponseFormatter()
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    global service
    service = BrightnessService()
    yield


app = FastAPI(title="Brightness Check Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return await formatter.format_success({
        "service": "brightness",
        "status": "healthy",
    })


@app.post("/process")
async def process(request: BrightnessRequest):
    assert service is not None
    start = time.time()
    try:
        await service.validate_input(request)
        result = await service.process(request)
        duration_ms = int((time.time() - start) * 1000)
        return await formatter.format_success(
            result.model_dump(),
            metadata={"duration_ms": duration_ms},
        )
    except ValueError as e:
        return await formatter.format_error(e, status_code=400)
    except Exception as e:
        return await formatter.format_error(e, status_code=500)


@app.get("/config")
async def config():
    assert service is not None
    default_config = await service.get_default_config()
    return await formatter.format_success({"default_config": default_config})
```

**`services/brightness/rest_api.py`**:

```python
"""Entry point for the brightness service."""

import argparse

import uvicorn

from services.brightness.rest_api_common import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Brightness Check Service")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main()
```

## Step 10: Service BUILD File

**`services/brightness/BUILD.bazel`**:

```python
py_library(
    name = "models",
    srcs = ["models.py"],
    visibility = ["//visibility:public"],
    deps = ["@pypi//pydantic"],
)

py_library(
    name = "service",
    srcs = ["service.py"],
    visibility = ["//visibility:public"],
    deps = [
        ":models",
        "//checks/brightness:api",
        "//services/framework:service_base",
    ],
)

py_library(
    name = "settings",
    srcs = ["settings.py"],
    visibility = ["//visibility:public"],
    deps = [
        "//services:settings_base",
        "@pypi//pydantic_settings",
    ],
)

py_library(
    name = "rest_api_common",
    srcs = ["rest_api_common.py"],
    visibility = ["//visibility:public"],
    deps = [
        ":models",
        ":service",
        ":settings",
        "//services/framework/response_formatters:json_response_formatter",
        "@pypi//fastapi",
    ],
)

py_binary(
    name = "rest_api",
    srcs = ["rest_api.py"],
    deps = [
        ":rest_api_common",
        "@pypi//uvicorn",
    ],
)
```

## Step 11: Run It

### As a CLI tool

```bash
dazel run //checks/brightness:run -- \
  --video_path /path/to/video.mp4 \
  --expected_brightness medium \
  --output_dir /tmp/brightness_results
```

### As a REST API

```bash
# Start the service
dazel run //services/brightness:rest_api

# In another terminal:
# Health check
curl http://localhost:8090/health
```

> **Note on port 8090:** this tutorial's port is not registered in [`services/local_ports.bzl`](../../services/local_ports.bzl), so dazel does not auto-port-map it the way it does for the built-in services. That is fine here because dazel runs with `--network host` (`DAZEL_NETWORK="host"`), so the container shares the host network and `localhost:8090` reaches the service directly. If you later wire this checker into the multi-service stack, add its port to `local_ports.bzl`.

```bash
# Continue in the second terminal:

# Run evaluation
curl -X POST http://localhost:8090/process \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/path/to/video.mp4",
    "expected_brightness": "medium"
  }'

# Get default config
curl http://localhost:8090/config
```

### Expected output

```json
{
  "success": true,
  "data": {
    "mean_score": 0.847,
    "min_score": 0.712,
    "max_score": 0.963,
    "frames_evaluated": 15,
    "total_video_frames": 450,
    "expected_brightness": "medium"
  },
  "metadata": {
    "duration_ms": 1234
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Step 12: Write Tests

**`checks/brightness/tests/brightness_processor_test.py`**:

```python
"""Tests for the brightness processor."""

from pathlib import Path

import numpy as np
import pytest

from checks.brightness.brightness_processor import process_brightness
from checks.utils.video import VideoWriter


def _create_test_video(path: str, brightness: int, num_frames: int = 30, fps: float = 30.0) -> None:
    """Create a solid-color test video with the given brightness (via the repo's ffmpeg-backed VideoWriter)."""
    frame = np.full((240, 320, 3), brightness, dtype=np.uint8)
    writer = VideoWriter(Path(path), fps=fps, frame_width=320, frame_height=240)
    writer.open()
    for i in range(num_frames):
        writer.write_frame(frame, i)
    writer.release()


class TestBrightnessProcessor:
    def test_bright_video_scores_high_for_bright(self, tmp_path: Path) -> None:
        video_path = str(tmp_path / "bright.mp4")
        _create_test_video(video_path, brightness=200, num_frames=30)

        result = process_brightness(video_path, "bright", keyframe_interval_s=0.5)

        assert result["mean_score"] > 0.8
        assert result["expected_brightness"] == "bright"
        assert result["frames_evaluated"] > 0

    def test_dark_video_scores_low_for_bright(self, tmp_path: Path) -> None:
        video_path = str(tmp_path / "dark.mp4")
        _create_test_video(video_path, brightness=30, num_frames=30)

        result = process_brightness(video_path, "bright", keyframe_interval_s=0.5)

        assert result["mean_score"] < 0.5

    def test_invalid_brightness_level_raises(self, tmp_path: Path) -> None:
        video_path = str(tmp_path / "test.mp4")
        _create_test_video(video_path, brightness=128)

        with pytest.raises(ValueError, match="Invalid brightness level"):
            process_brightness(video_path, "invalid_level")

    def test_trial_frames_limits_processing(self, tmp_path: Path) -> None:
        video_path = str(tmp_path / "test.mp4")
        _create_test_video(video_path, brightness=128, num_frames=300)

        result = process_brightness(video_path, "medium", keyframe_interval_s=0.1, trial_frames=5)

        assert result["frames_evaluated"] == 5
```

**`checks/brightness/tests/BUILD.bazel`**:

```python
py_test(
    name = "brightness_processor_test",
    srcs = ["brightness_processor_test.py"],
    deps = [
        "//checks/brightness:brightness_processor",
        "//checks/utils:video",
        "@pypi//numpy",
        "@pypi//pytest",
    ],
)
```

Run tests:

```bash
dazel test //checks/brightness/tests:all
```

## Next Steps

From here you could extend this checker by:

- **Adding cloud support** — Download videos from S3 using the `StorageProvider`, upload results back
- **Adding visualization** — Generate an annotated video showing brightness over time
- **Adding to the Arbitrator** — Add your service's base name and URL to the Arbitrator's `COSMOS_EVALUATOR_CHECKER_ENDPOINTS` so it can be orchestrated alongside other checks (see the [Orchestration Layer guide](../services/orchestration.md))
- **Adding configuration to `cosmos_evaluator.yaml`** — Define defaults under a new config key

The Objects service in `services/objects/single_view/` demonstrates these advanced patterns.
