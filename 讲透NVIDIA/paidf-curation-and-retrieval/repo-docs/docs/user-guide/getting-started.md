<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Get Started

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Four paths. Path A has two first-runs. The public interface is Make only.

If [Installation](installation.md) is already done, start at Path A Cosmos
Curator Generic. Path A also needs sample clips from
[Samples and Cookbooks](samples-and-cookbooks.md).

| Path | What | Notes |
|------|------|-------|
| **A generic** | Any MP4s in `videos/` (traffic or warehouse) | Needs models and FFmpeg; first-run: `split-minimal.yaml` |
| **A AV multi-cam** | PhysicalAI-AV four-camera sessions | Gated Hugging Face extract; first-run: `caption-multicam.yaml` |
| **B Data Mining** | Nearest neighbors on S/B parquets | No Curator models; three still images are enough |
| **C Curation and Mining** | Path A embeddings into Path B mining | Same dimension and matching `TDM_EMBEDDING_BACKEND` |
| **D Curation and Dataset Search** | Path A Cosmos-Embed1 (CE1) into Cosmos Dataset Search (CDS) ingest and text search | Public generally available (GA) 1.2.0; collection **id**; `make search`; not supported on Blackwell GPUs; refer to [Cosmos Dataset Search](operations-cds.md) |

## Path A Cosmos Curator Generic

Download the NGC Video Search and Summarization (VSS) sample pack and copy
clips into each cookbook `videos/` folder first. Traffic first-run uses
`split-minimal.yaml` on both shipped clips and writes Qwen3-VL captions plus
Cosmos-Embed1 embeddings. It does **not** enable classifier, Segment Anything
Model 3 (SAM3), or enhance. Warehouse first-run still uses `limit: 1` and
skips captions.

`make setup` runs `make pull`, `make ffmpeg-install`, and `make check-setup`.

```bash
make setup
make download-models MODELS_DIR=/path/to/models

make run-pipeline \
  CONFIG_FILE=cookbook/traffic-video-analytics/split-minimal.yaml \
  DATA_DIR=$PWD/cookbook/traffic-video-analytics \
  MODELS_DIR=/path/to/models \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg
```

**Success:** `cookbook/traffic-video-analytics/output/split-minimal/ce1_embd_224p_parquet/`
exists. On a shared GPU host, pass `GPUS='"device=N"'`.

Full caption recipes: [VLM and LLM Endpoints](vlm-llm-endpoints.md). Next:
[Cosmos Curator](operations-curator.md).

## Path A Cosmos Curator AV Multi-Cam

PhysicalAI-AV does not ship MP4s. Accept the Hugging Face license, then
extract one session into `videos/<clip-uuid>/` (four cameras). First-run
uses `caption-multicam.yaml`: fixed-stride, AV captions, CE1 embeddings,
no classifier or SAM3. It needs vision-language model (VLM) endpoints or
in-process 30B weights. To check the setup without a VLM, run the generic
Path A traffic first-run above. Caption and embed stages use the primary
camera only (`primary_camera_keyword: front_wide`). Full
`split-multicam.yaml` (SAM3 and event captions):
[`../../cookbook/physical-ai-av/README.md`](../../cookbook/physical-ai-av/README.md).

```bash
DATA=$PWD/cookbook/physical-ai-av

hf auth login
uv pip install physical_ai_av

python -m adapters.physical_ai_av.prepare_sessions \
  --output-dir "$DATA" \
  --cache-dir "$DATA/.hf-cache" \
  --max-sessions 1

make setup
make download-models MODELS_DIR=/path/to/models

make run-pipeline \
  CONFIG_FILE=cookbook/physical-ai-av/caption-multicam.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=/path/to/models \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg
```

If camera zips are already on disk, pass `--chunk-dir /path/to/zips` and
`--skip-download` instead of `--cache-dir`.

**Success:** `$DATA/output/caption-multicam/ce1_embd_224p_parquet/`
exists and `$DATA/output/caption-multicam/clips/<clip-uuid>/` has
one MP4 per camera. On a shared GPU host, pass `GPUS='"device=N"'`.

Next: [Cosmos Curator](operations-curator.md).

## Path B Data Mining

| File | Role |
|------|------|
| `S.parquet` | Targets (queries) |
| `B.parquet` | Candidates (pool) |

Copy any three JPEGs and keep the filenames in the JSON below.

```bash
make pull-data-mining
make check-data-mining-image

mkdir -p data/tao-mine/images
cp /path/to/query.jpg      data/tao-mine/images/query.jpg
cp /path/to/candidate-1.jpg data/tao-mine/images/candidate-1.jpg
cp /path/to/candidate-2.jpg data/tao-mine/images/candidate-2.jpg

printf '%s\n' '[{"filepath":"images/query.jpg"}]' \
  > data/tao-mine/S.json
printf '%s\n' \
  '[{"filepath":"images/candidate-1.jpg"},{"filepath":"images/candidate-2.jpg"}]' \
  > data/tao-mine/B.json
```

Create S (queries):

```bash
make image-embeddings-build \
  DATA_DIR=$PWD/data/tao-mine \
  IMAGE_EMBEDDING_JSON=$PWD/data/tao-mine/S.json \
  IMAGE_EMBEDDING_INPUT=$PWD/data/tao-mine/S-input.parquet
make run-image-embeddings \
  DATA_DIR=$PWD/data/tao-mine \
  IMAGE_EMBEDDING_INPUT=$PWD/data/tao-mine/S-input.parquet \
  IMAGE_EMBEDDING_OUTPUT=$PWD/data/tao-mine/S.parquet \
  IMAGE_EMBEDDING_MODEL_TYPE=clip \
  IMAGE_EMBEDDING_MODEL=openai/clip-vit-base-patch32
```

Create B (candidate pool):

```bash
make image-embeddings-build \
  DATA_DIR=$PWD/data/tao-mine \
  IMAGE_EMBEDDING_JSON=$PWD/data/tao-mine/B.json \
  IMAGE_EMBEDDING_INPUT=$PWD/data/tao-mine/B-input.parquet
make run-image-embeddings \
  DATA_DIR=$PWD/data/tao-mine \
  IMAGE_EMBEDDING_INPUT=$PWD/data/tao-mine/B-input.parquet \
  IMAGE_EMBEDDING_OUTPUT=$PWD/data/tao-mine/B.parquet \
  IMAGE_EMBEDDING_MODEL_TYPE=clip \
  IMAGE_EMBEDDING_MODEL=openai/clip-vit-base-patch32
```

Mine:

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/tao-mine \
  TARGET_SUBDIR=S.parquet \
  SOURCE_SUBDIR=B.parquet \
  TOPN=1 \
  TDM_EMBEDDING_BACKEND=clip \
  OUTPUT_SUBDIR=out
```

**Success:** `data/tao-mine/out/mined.parquet` exists.

On a shared GPU host, pass `GPUS='"device=N"'` on the embedding and mining
targets (default is `GPUS=all`).

Optional cookbook YAML:
`TMM_CONFIG_FILE=cookbook/nearest-neighbor-mining/tmm.yaml`.

Next: [Data Mining](operations-tao-mining.md).

## Path C Curation and Mining

Curator generates video embedding parquets (InternVideo2 (IV2) or CE1). Stage
them as `S.parquet` / `B.parquet` before mining.

```bash
mkdir -p data/curated-mine
cp /path/to/ce1_embd_224p_parquet/query.parquet data/curated-mine/S.parquet
cp /path/to/ce1_embd_224p_parquet/pool.parquet  data/curated-mine/B.parquet

make run-data-mining-select \
  DATA_DIR=$PWD/data/curated-mine \
  TARGET_SUBDIR=S.parquet \
  SOURCE_SUBDIR=B.parquet \
  TOPN=5 \
  TDM_EMBEDDING_BACKEND=ce1 \
  OUTPUT_SUBDIR=out
```

Use `iv2` when Curator used InternVideo2.

**Success:** `data/curated-mine/out/mined.parquet` exists. Dimension mismatches:
[Troubleshooting](troubleshooting.md).

## Path D Curation and Dataset Search

Do this only after Path A produced CE1 parquet under
`cookbook/traffic-video-analytics/output/split-minimal/ce1_embd_224p_parquet/`.

Follow [Cosmos Dataset Search](operations-cds.md). That page opens with
Choose a Path for public GA or a CDS you deployed yourself.

**Success:** `make search COLLECTION=<id>` returns a JSON array of clips.
For a CDS you
deployed elsewhere, skip Compose and set `CDS_URL` at that API
([Using a CDS You Deployed Yourself](operations-cds.md#using-a-cds-you-deployed-yourself)).
