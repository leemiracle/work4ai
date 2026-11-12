<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# PhysicalAI-AV

Curator recipes for
[NVIDIA PhysicalAI-Autonomous-Vehicles](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles).
Unlike traffic and warehouse, this cookbook does **not** ship MP4s. You
download a gated Hugging Face chunk, extract inputs, then run the same
`make run-pipeline` contract.

Prepare once, then pick a recipe. Single-cam input: `videos-single/`.
Multi-cam input: `videos/<uuid>/`.

| YAML | Stages | Output dir |
|------|--------|------------|
| `split-singlecam.yaml` | Captions, SAM3, SAM3 events, CE1 | `output/split-singlecam` |
| `split-multicam.yaml` | Same as single-cam, primary camera only | `output/split-multicam` |
| `caption-windows-multicam.yaml` | AV captions, 60-frame windows, CE1 | `output/caption-windows-multicam` |
| `caption-multicam.yaml` | AV captions, one 600-frame window, CE1 | `output/caption-multicam` |
| `caption-windows-events-multicam.yaml` | One 20 s clip, AV captions (2 s), SAM3, events, CE1 | `output/caption-windows-events-multicam` |
| `caption-events-multicam.yaml` | One 20 s clip, one scene caption, SAM3, events, CE1 | `output/caption-events-multicam` |

## Prompts and taxonomy

| File | Used for |
|------|----------|
| `av_caption_prompt.txt` | Scene captions (inlined as `captioning_prompt_text`) |
| `av_event_caption_prompt.txt` | Ego-centric AV event captions (`event_caption_prompt_file`); copy into `DATA_DIR` |
| `taxonomy_av.yaml` | Reference event categories and SAM3 `objects_of_interest` (recipes inline these) |

Scene captions stay stop-capped AV prose. Event captions report the
events that constrain ego progress -- path encroachment, braking, hazard
onsets, and clearance, anchored on the SAM3 tracks -- as an `events[]`
array. Each entry carries its own `start_time` and `end_time` on the
event object itself, plus a category from `taxonomy_av.yaml`. Uneventful
stretches get no entry, so a ~20 s clip yields as many events as it has.
Event selection comes from the prompt, not from a recipe knob, so
changing it means editing `av_event_caption_prompt.txt`.
Caption-only A/B recipes leave `sam3` and `event_captioning` off. Both
event recipes keep each ~20 s session as one clip and enable event
captioning via `event_caption_prompt_file` (`event_caption_prompt` stays
null so the file is used). They differ only in scene-caption windowing:
`caption-events-multicam.yaml` uses one 600-frame window,
`caption-windows-events-multicam.yaml` uses 60-frame windows. Event
recipes need `PIXI_ENV=sam3`.

The dataset stores cameras as zip chunks (up to 100 clips each). The
prepare helper converts those zips into the two layouts above.

## 1. Hugging Face access

1. Create a Hugging Face account and accept the NVIDIA AV Dataset license
   on the [dataset card](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles).
2. Create a [user access token](https://huggingface.co/settings/tokens).
3. Authenticate (do not commit the token):

```bash
hf auth login
```

4. Install the dataset client in the CDF environment:

```bash
uv pip install physical_ai_av
# or: pip install physical_ai_av
```

`physical_ai_av` is not a core CDF dependency. Skip this install if
the camera zips are already on disk and you pass `--chunk-dir`.

## 2. Download and extract

`prepare_sessions` is an optional one-time helper, not a pipeline stage. No
Make target calls it, and Curator never invokes it: it only produces the
`videos/<clip-id>/<camera>.mp4` tree that the recipes below read from
`DATA_DIR`. If that tree already exists, skip this whole section.

From the repository root. Default `--layout both` writes one session for
each YAML. The Hugging Face pull is still a full camera chunk (about 6 GB
for four cameras; single-cam-only download is the front-wide chunk).

```bash
DATA=$PWD/cookbook/physical-ai-av
# Set CACHE to a disk with room for the chunk downloads, otherwise the
# default below puts them under the repository.

python -m adapters.physical_ai_av.prepare_sessions \
  --output-dir "$DATA" \
  --cache-dir "${CACHE:-$DATA/.hf-cache}" \
  --max-sessions 1
```

Reuse zips that are already downloaded (no Hugging Face call):

```bash
python -m adapters.physical_ai_av.prepare_sessions \
  --output-dir "$DATA" \
  --chunk-dir /path/to/physical-ai-av \
  --skip-download \
  --max-sessions 1
```

`--layout single` or `--layout multicam` writes only that tree.
`--chunk-dir` is searched recursively for `camera_*.chunk_*.zip`.

Resulting layout (do not put a README under the video dirs):

```text
cookbook/physical-ai-av/
  videos/<clip-uuid>/                         # multi-cam
    camera_front_wide_120fov.mp4              # primary
    camera_front_tele_30fov.mp4
    camera_cross_left_120fov.mp4
    camera_cross_right_120fov.mp4
  videos-single/                              # single-cam
    <clip-uuid>.camera_front_wide_120fov.mp4
  output/                                     # created by Curator
```

Default clip when present: `030c760c-ae38-49aa-9ad8-f5650a545d26`.
Override with `--clip-id <uuid>` (repeatable).

## 3. Run Cosmos Curator

```bash
DATA=$PWD/cookbook/physical-ai-av
MODELS=/path/to/models

# AV captions + CE1 on a four-camera session (no SAM3)
make run-pipeline \
  CONFIG_FILE=cookbook/physical-ai-av/caption-multicam.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS

# Captions, SAM3 tracks, SAM3-grounded event captions, CE1
cp cookbook/physical-ai-av/av_event_caption_prompt.txt \
  "$DATA/av_event_caption_prompt.txt"

make run-pipeline \
  CONFIG_FILE=cookbook/physical-ai-av/split-singlecam.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  PIXI_ENV=sam3

make run-pipeline \
  CONFIG_FILE=cookbook/physical-ai-av/split-multicam.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  PIXI_ENV=sam3
```

YAML I/O is `/data/...`. Pass `DATA_DIR` as this directory. Every recipe
here needs VLM/LLM endpoints or in-process 30B weights. Refer to
[VLM and LLM Endpoints](../../docs/user-guide/vlm-llm-endpoints.md). To
check mounts, models, and the FFmpeg sidecar without a VLM, run
`cookbook/traffic-video-analytics/split-minimal.yaml` first.

Kitchen-sink `split-singlecam.yaml` / `split-multicam.yaml` omit `limit`,
split on a 10 s stride, and turn SAM3 on. Caption
recipes (`caption-multicam.yaml`, `caption-windows-multicam.yaml`,
`caption-events-multicam.yaml`, `caption-windows-events-multicam.yaml`)
use `limit: 100` and keep each ~20 s session as one clip.

Multi-cam extras:

| Knob | Value | Why |
|------|--------|-----|
| `multi_cam` | `true` | Time-align cameras in each session |
| `primary_camera_keyword` | `front_wide` | Must be unique; `front` matches wide and tele |
| `splitting_algorithm` | `fixed-stride` | Multi-cam does not use TransNet |

**Success (captions multi-cam):** `$DATA/output/caption-multicam/ce1_embd_224p_parquet/`
and `clips/<clip-uuid>/` has one MP4 per camera.

**Success (full split):** `$DATA/output/split-singlecam/` or
`$DATA/output/split-multicam/` also has `sam3_instances/`, `sam3_objects/`,
`sam3_tracked/`, and `sam3_events/` when SAM3 + event captioning finish.

Delete the matching `output/` directory before a clean re-run so
Curator does not skip already-processed inputs.

## Limits

- Gated dataset; agree to the license before download.
- One clip still pulls a whole camera chunk (front-wide ~1.5 GB; four
  cameras ~6 GB).
- Multi-cam caption / classifier / SAM3 / embed stages use the primary
  camera only.
- Image pipeline has no multi-cam mode.
- This recipe does not map Maglev session IDs. PhysicalAI-AV clip UUIDs
  become the Curator session directory names (multi-cam) or MP4 prefixes
  (single-cam).

Path D (index CE1 in Cosmos Dataset Search):
[Cosmos Dataset Search](../../docs/user-guide/operations-cds.md).
`CURATOR_DIR` is any recipe's output directory, for example
`output/caption-multicam`.
