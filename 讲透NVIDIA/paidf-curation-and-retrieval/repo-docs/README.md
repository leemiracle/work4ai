<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Curation and Retrieval

**Product:** `cdf-curation-and-retrieval` · **Version:** 1.2.0

## About Curation and Retrieval

The Cosmos Data Factory (CDF) Curation and Retrieval workflow turns raw
video and image collections into training-ready datasets for physical AI. It
unifies three GPU-accelerated NVIDIA engines behind a single, reproducible
operator interface: **Cosmos Curator** for video and image curation, **Cosmos
Dataset Search** for embedding ingest and retrieval, and **Data Mining** for
embeddings and nearest-neighbor retrieval.

Every capability is driven through **Make** targets backed by versioned
cookbook YAML and pinned runtime images. That gives operators a consistent,
auditable contract from a laptop smoke test to scheduled, large-scale
orchestration, with no second CLI to learn.

## What It Does

- **Curate video and image** with Cosmos Curator: split, caption, classify,
  filter, Segment Anything Model 3 (SAM3) track-grounded event captioning,
  dedup, and WebDataset sharding. Each stage is driven by cookbook YAML
  (`split` / `dedup` / `shard` / `image`).
- **Generate embeddings and mine**: CLIP/SigLIP image and text embeddings,
  then nearest-neighbor and unique-neighbor matching.
- **Hand off deterministically** from Curator embedding parquets (Cosmos-Embed1
  (CE1) / InternVideo2) into Data Mining (Path C), with the model backend pinned on
  both sides.
- **Index and search curated video** with Cosmos Dataset Search (Path D): ingest
  Cosmos-Embed1 clips, then retrieve by text query.
- **Stay reproducible**: image tags pinned in the Makefile / `.env`, integration logic
  isolated in `packages/` `adapters/` `apps/`, and validated by offline unit
  tests (`uv run pytest tests/unit`).

Runnable domain recipes ship in [`cookbook/`](cookbook/README.md); the customer
guide lives in [`docs/user-guide/`](docs/user-guide/README.md).

## Engines and Entry Points

| Engine | Role | Entry points |
|--------|------|--------------|
| **Cosmos Curator** | Video / image curation | `make pull` · `make run-pipeline` · `make run_image_pipeline` |
| **Data Mining** | Image and text embeddings; nearest neighbors; unique neighbor matching | `make pull-data-mining` · `make run-image-embeddings` · `make run-text-embeddings` · `make run-data-mining-select` · `make run-data-mining-unique-match` |
| **Cosmos Dataset Search** | CE1 ingest and text-to-clip search | `make pull-dataset-search` · `make up-dataset-search` · `make ds-health` · `make ingest-curator` · `make search` |

Overall curation-and-retrieval architecture (Cosmos Curator, Cosmos Dataset
Search, and Data Mining):

![CDF Curation and Retrieval Architecture](docs/assets/CDF-CC-CDS-TDM.png)

---

## Documentation

Full customer guide:

**[docs/user-guide/README.md](docs/user-guide/README.md)** ·
**[CHANGELOG.md](CHANGELOG.md)**

| Need | Page |
|------|------|
| Get Started | [Get Started](docs/user-guide/getting-started.md) |
| Install and host requirements | [Installation](docs/user-guide/installation.md) |
| Sample clips and cookbooks | [Samples and Cookbooks](docs/user-guide/samples-and-cookbooks.md) |
| Run Cosmos Curator | [Cosmos Curator](docs/user-guide/operations-curator.md) |
| Run embeddings and Data Mining | [Data Mining](docs/user-guide/operations-tao-mining.md) |
| Cosmos Dataset Search (Path D) | [Cosmos Dataset Search](docs/user-guide/operations-cds.md) |
| VLM and LLM endpoints | [VLM and LLM Endpoints](docs/user-guide/vlm-llm-endpoints.md) |
| Fix failures | [Troubleshooting](docs/user-guide/troubleshooting.md) |

Cookbooks: [`cookbook/README.md`](cookbook/README.md).

---

## Access

Before clone or the first `docker pull`:

- NGC login (`docker login nvcr.io`) for Cosmos Curator and the public
  Path D images (`nvcr.io/nvidia/blueprint/cosmos-dataset-search` and
  `nvcr.io/nvidia/blueprint/cosmos-embed1-oss`)
- Access to pull TAO Data Services from NGC
  (`nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services`;
  refer to [Installation](docs/user-guide/installation.md))

```bash
git clone https://github.com/NVIDIA/cdf-curation-and-retrieval.git
cd cdf-curation-and-retrieval
cp .env.example .env
uv sync --extra dev
docker login nvcr.io
```

---

## Get Started

Public UX is Make only. Pick the path that matches your goal:

- **Path A Cosmos Curator Generic**: curate any MP4s in `videos/`
  (traffic and warehouse cookbooks). Needs GPU, FFmpeg, and Curator
  models (hours on first run).
- **Path A Cosmos Curator AV Multi-Cam**: PhysicalAI-AV four-camera
  sessions. Gated Hugging Face extract, then `caption-multicam.yaml`.
- **Path B Data Mining**: embeddings and nearest-neighbor
  retrieval only. No Curator models. This is the fastest way to get a result.
- **Path C Curation and Mining**: curate first, then mine the embeddings.
- **Path D Curation and Dataset Search**: curate first, then ingest Cosmos-Embed1 (CE1) into
  Cosmos Dataset Search (CDS) and retrieve by query.

Details: [Get Started](docs/user-guide/getting-started.md).

### Path A Cosmos Curator Generic

Needs GPU, FFmpeg sidecar, and Curator models (`MODELS_DIR`). First model
download is large (~90GB). Sample MP4s are **not** in this repository: download
NGC `nvidia/vss-developer/dev-profile-sample-data:3.2.0` and copy traffic /
warehouse clips into `cookbook/*/videos/` first. Refer to
[Samples and Cookbooks](docs/user-guide/samples-and-cookbooks.md). Traffic
first-run uses `split-minimal.yaml` on both shipped clips and writes Qwen3-VL
captions plus Cosmos-Embed1 embeddings. It does not enable classifier, Segment
Anything Model 3 (SAM3), or enhance. Full caption, SAM3, and classifier:
`cookbook/traffic-video-analytics/split.yaml` after
[VLM and LLM Endpoints](docs/user-guide/vlm-llm-endpoints.md).
PhysicalAI-AV multi-cam first-run is the next Path A section.

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

The command above uses the default `MODEL_LIST` (Path A traffic), which
includes the InternVideo2 BERT sidecar. OCR, shard (`t5_xxl`), and SeedVR2
need extra tokens. Refer to
[Cosmos Curator](docs/user-guide/operations-curator.md#models).

**Success:** `cookbook/traffic-video-analytics/output/split-minimal/ce1_embd_224p_parquet/`
exists.

### Path A Cosmos Curator AV Multi-Cam

PhysicalAI-AV does not ship MP4s. Accept the Hugging Face license, then
extract one session into `videos/<clip-uuid>/` (four cameras). First-run
uses `caption-multicam.yaml`: fixed-stride, AV captions, CE1 embeddings,
no classifier / SAM3. It needs VLM endpoints or in-process 30B weights;
the generic Path A traffic first-run above checks the setup without a
VLM. Full `split-multicam.yaml` (SAM3 + AV
events): [PhysicalAI-AV cookbook](cookbook/physical-ai-av/README.md).

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
one MP4 per camera.

### Path B Data Mining

No Curator models required. The mining image provides both image/text
embeddings and nearest-neighbor mining. This example embeds
one query image and two candidate images with CLIP, then mines the nearest
candidate.

| File | Role |
|------|------|
| `S.parquet` | Targets (queries): find neighbors **for** these rows |
| `B.parquet` | Candidates (pool): search **in** these rows |

Copy any three JPEGs into the working directory and keep the
`images/*.jpg` names below (used by the JSON manifests).

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

Build the two TAO input manifests and generate embeddings with the same model:

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

Mine B for the nearest neighbor of each S row:

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

### Path C Curation and Mining

Curator **does** generate video embedding parquets (InternVideo2 (IV2) or CE1). It does
**not** emit TAO mining `S.parquet` / `B.parquet` names. Those are a mining
layout you stage from Curator embedding output.

1. **Run Path A** with embeddings on (`generate_embeddings: true`,
   `embedding_algorithm: "cosmos-embed1-224p"`; warehouse cookbook still
   uses `"internvideo2"`). Fill the cookbook’s split output path
   (`output_clip_path` / placeholder). Curator writes embedding parquet(s)
   below it in `ce1_embd*_parquet/` or `iv2_embd_parquet/`.

2. **Stage for TAO mining.** Same model and vector dimension on both sides:
   - **S** = query clips (neighbors **for** these)
   - **B** = candidate pool (search **in** these)

   Typical pattern: one Curator embedding parquet (or a row subset) as S,
   another (or the full set) as B:

```bash
mkdir -p data/curated-mine
# Paths below are Curator embedding parquet outputs from Path A
cp /path/to/curator_query_embeddings.parquet data/curated-mine/S.parquet
cp /path/to/curator_pool_embeddings.parquet  data/curated-mine/B.parquet
```

3. **Mine** with the backend that matches the Curator producer:

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/curated-mine \
  TARGET_SUBDIR=S.parquet \
  SOURCE_SUBDIR=B.parquet \
  TOPN=5 \
  TDM_EMBEDDING_BACKEND=ce1 \
  OUTPUT_SUBDIR=out
```

Use `TDM_EMBEDDING_BACKEND=iv2` when Curator used InternVideo2 (warehouse).

**Success:** `data/curated-mine/out/mined.parquet` exists. More detail:
[Get Started](docs/user-guide/getting-started.md).

### Path D Curation and Dataset Search

Finish Path A with `cookbook/traffic-video-analytics/split-minimal.yaml` so
CE1 parquet exists under
`cookbook/traffic-video-analytics/output/split-minimal/ce1_embd_224p_parquet/`.
Do not point CDS at warehouse InternVideo2 output.

Path D requires an x86_64 host.

**Blackwell (B-series) GPUs are not supported for Path D.** The published
Cosmos-Embed1 container has no kernels for compute capability 10.0 (`sm_100`:
B100, B200, GB200) or 12.0 (`sm_120`: RTX PRO 6000 Blackwell); the CDS API
does not use the GPU. Run
Path D on Hopper (e.g. H100), Ada (e.g. L40), or Ampere (e.g. A100)
class GPUs with 16GB+ VRAM. This limit is CDS-only: Curator and TAO do run on
Blackwell, so Paths A, B, and C are unaffected.

Follow the recipe on [Cosmos Dataset Search](docs/user-guide/operations-cds.md).
Public generally available (GA) 1.2.0 is the supported customer path. A CDS
you deployed yourself is covered on that page.

---

## System Requirements

| Component | Minimum |
|-----------|---------|
| **GPU (Paths A–C)** | NVIDIA A40 / A100 / H100 class (48GB+ VRAM for full Curator); Blackwell supported |
| **GPU (Path D, CDS)** | Hopper / Ada / Ampere class, 16GB+ VRAM. **Blackwell (B-series) not supported** |
| **CPU** | 16+ cores |
| **RAM** | 64GB |
| **Storage** | 500GB SSD (+ ~90GB for Curator models) |
| **OS** | Ubuntu 22.04 / 24.04 LTS |
| **Software** | Docker 20.10+, NVIDIA Container Toolkit, `uv`, Python 3.10–3.12 |

TAO Data Services (default pin `7.2.0-data-services`) documents driver
floor `595.45.04`. Curator has separate image/GPU compatibility requirements;
qualify the selected Curator image independently. Full matrix:
[Installation](docs/user-guide/installation.md).

---

## Project Structure

```text
cdf-curation-and-retrieval/
├── .env.example            Image pin template + CDS_PROFILE
├── adapters/               Curator, Dataset Search HTTP, Data Mining, Docker
├── apps/                   Orchestration helpers (invoked by Make)
├── packages/               Domain types, ports, analytics
├── configs/                Full Curator reference YAMLs
├── cookbook/               Domain recipes (Curator + TMM)
├── deploy/compose/         Dataset Search compose (laptop Path D)
├── docs/user-guide/        Customer documentation
├── docs/developer/         Contributor architecture notes
├── docs/assets/            Architecture diagrams
├── skills/                 Agent skill for operator workflows
├── tests/unit/             Unit tests (no live GPU required)
├── Makefile                Operator UX
└── pyproject.toml          uv project (version 1.2.0)
```

---

## Agent Skills

| Skill | Scope |
|-------|--------|
| `cdf-curation-and-retrieval` | Cosmos Curator configs, cookbooks, Data Mining handoffs, Dataset Search |

Customer guide: [docs/user-guide/](docs/user-guide/).

---

## Development

This project is currently not accepting contributions.
Refer to [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format .
uv run pytest tests/unit -q
```

Development uses conventional commits (`feat:`, `fix:`, `chore:`,
`docs:`). Never commit secrets, `local.env`, or private registry hosts.

---

## Responsible Use of AI Models

[Responsible Use](./RESPONSIBLE_USE.md)

---

## Notice

**NOTICE AND DISCLAIMER:** This software automatically retrieves, accesses or
interacts with external materials. Those retrieved materials are not
distributed with this software and are governed solely by separate terms,
conditions and licenses. You are solely responsible for finding, reviewing and
complying with all applicable terms, conditions, and licenses, and for
verifying the security, integrity and suitability of any retrieved materials
for your specific use case. This software is provided "AS IS", without
warranty of any kind. The author makes no representations or warranties
regarding any retrieved materials, and assumes no liability for any losses,
damages, liabilities or legal consequences from your use or inability to use
this software or any retrieved materials. Use this software and the retrieved
materials at your own risk.
