<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Installation

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Install Curation and Retrieval so you can run a cookbook. This is the product
install path for customers.

If you are changing the code, do this install first, then continue with
[Developer Docs](../developer/README.md).

## Requirements

Install only what the chosen path needs.

| Item | Minimum |
|------|---------|
| OS | Ubuntu 22.04 or 24.04 LTS (Linux) |
| Docker | 20.10+ |
| NVIDIA Container Toolkit | Installed and working with Docker |
| GPU | NVIDIA data-center GPU (A40 / A100 / H100 class recommended) |
| CPU | 16+ cores |
| RAM | 64GB system RAM |
| Storage | 500GB SSD; add ~90GB for Curator models |
| Python | `>=3.10,<3.13` using [`uv`](https://github.com/astral.sh/uv); 3.12 recommended |
| Make | GNU Make |

| Path | Extra requirements |
|------|-------------------|
| Path B Data Mining | One GPU is enough for smoke runs; no Curator weights or FFmpeg |
| Path A Curator | FFmpeg sidecar (`make ffmpeg-install`); `MODELS_DIR` (~90GB+) |
| Full Curator video recipes | 48GB+ VRAM; vision-language model (VLM) and large language model (LLM) endpoints for caption cookbooks |
| Path D Cosmos Dataset Search (CDS) | x86_64 (amd64) host; CDS has no ARM64 build. Refer to [Limitations](#limitations) |
| Sample clips | NGC CLI 4.10.0+ and an API key. Refer to [Samples and Cookbooks](samples-and-cookbooks.md) |

TAO Toolkit Data Services documents driver `595.45.04` as a floor. Qualify the
selected Curator image independently.

Never put credentials on Make command lines, in cookbook YAML, or in logs.

## Clone and Sync

```bash
git clone https://github.com/NVIDIA/cdf-curation-and-retrieval.git
cd cdf-curation-and-retrieval
cp .env.example .env
uv sync --extra dev
docker login nvcr.io
```

Install `uv` from the
[standalone installer](https://docs.astral.sh/uv/getting-started/installation/).
The Ubuntu snap build is not supported: a snap-confined `uv` cannot create
the project virtual environment. `command -v uv` must not point at
`/snap/bin/uv`.

This repository **pulls** published vendor images. It does not build or push
vendor images as part of the supported path.

### Cosmos Curator Path A

`make setup` runs `make pull`, `make ffmpeg-install`, and `make check-setup`.

```bash
make setup
make download-models MODELS_DIR=/path/to/models
```

The default FFmpeg sidecar path is `$HOME/cosmos-curator-ffmpeg`.

Model tokens and optional SeedVR2 / Segment Anything Model 3 (SAM3) notes:
[Cosmos Curator](operations-curator.md).

**Success signals**

- `make check-setup` validates Docker, GPU visibility, and the FFmpeg sidecar
- Models directory populated under `MODELS_DIR`

### Data Mining Path B

```bash
make pull-data-mining
make check-data-mining-image
```

**Success signals**

- `docker pull` completes without auth errors
- `make check-data-mining-image` exits 0

### Cosmos Dataset Search Path D

```bash
make pull-dataset-search \
  CDS_PROFILE=public \
  DATASET_SEARCH_REGISTRY=nvcr.io/nvidia/blueprint/cosmos-dataset-search \
  DATASET_SEARCH_TAG=1.2.0
make check-dataset-search-image \
  DATASET_SEARCH_TAG=1.2.0
```

If `.env` or gitignored `local.env` sets `CDS_PROFILE` to a value other than
`public`, you **must** pass the Make arguments above for public generally
available (GA). On the default public profile, image pins in those files are
ignored. Refer to
[Cosmos Dataset Search](operations-cds.md).

**Expected success signals**

- Local image `cosmos-dataset-search:1.2.0` exists
- After `make up-dataset-search` with the matching profile, `make ds-health`
  prints `{"status": "OK"}` (retry until gunicorn is up)
- `curl -sS http://localhost:8888/v1/pipelines` shows
  `cosmos_video_search_milvus` with `"enabled": true`

### Pull All Published Images

```bash
make pull-all
```

`pull-all` pulls Curator, Dataset Search, and Data Mining images. Starting
Compose, waiting for health, ingest, and search:
[Cosmos Dataset Search](operations-cds.md).

### Verify GPU Visibility

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

If installation fails, refer to [Troubleshooting](troubleshooting.md).

## Image Pins

Authoritative defaults live in the root `Makefile`. Override locally through
`.env` or command-line Make variables.

| Runtime | Makefile variables | Default pattern |
|---------|--------------------|-----------------|
| Cosmos Curator | `COSMOS_CURATOR_REGISTRY`, `COSMOS_CURATOR_TAG` | `nvcr.io/nvidia/cosmos/cosmos-curator:2.3.0` |
| Cosmos Dataset Search | `DATASET_SEARCH_REGISTRY`, `DATASET_SEARCH_TAG` | `nvcr.io/nvidia/blueprint/cosmos-dataset-search:1.2.0` |
| Cosmos-Embed1 (CE1 OSS) | `COSMOS_EMBED_IMAGE` | `nvcr.io/nvidia/blueprint/cosmos-embed1-oss:1.2.0` |
| Data Mining | `DATA_MINING_REGISTRY`, `DATA_MINING_TAG` | `nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services` |

Product version `1.2.0` (`pyproject.toml`) describes this repository.
Container tags are separate pins.

### Cosmos-Embed1 Weights

From CDS `1.2.0` the query embedder runs as a container that `make
up-dataset-search` starts for you, and the image cannot download its own
weights (`COSMOS_EMBED_ALLOW_HF_DOWNLOAD=false`). Point
`COSMOS_EMBED_MODELS_DIR` at a local snapshot:

```bash
hf download nvidia/Cosmos-Embed1-224p \
  --revision 787e0b996f5260a71ad474a283c90539a2e12986 \
  --local-dir /path/to/Cosmos-Embed1-224p
```

Specify the revision. CE1 OSS `1.2.0` verifies the snapshot against a
checksum manifest that ships inside the image and refuses to serve any other
revision. A mismatched snapshot leaves the container unhealthy and reports
`CE1 snapshot checksum mismatch`. Re-download the weights at the pinned
revision whenever the CDS version changes.

## Credentials

| Need | When |
|------|------|
| NGC / `nvcr.io` Docker login | Pulling Curator and TAO images |
| NGC CLI API key | Downloading Video Search and Summarization (VSS) sample clips |
| Hugging Face token | Gated Curator weights (for example SAM3) |
| OpenAI-compatible VLM and LLM keys | Caption cookbooks. Refer to [VLM and LLM Endpoints](vlm-llm-endpoints.md) |

Keep secrets in the environment or gitignored `.env` / `local.env`. Do not
put API keys on Make argv.

Hugging Face token file (Curator):

```bash
mkdir -p ~/.config/cosmos_curator
chmod 600 ~/.config/cosmos_curator/hf_token.txt
```

## Limitations

- Cosmos Dataset Search Path D is local Compose only. Refer to
  [Cosmos Dataset Search](operations-cds.md).
- **CDS does not run on ARM.** The CDS API and Cosmos-Embed1 images are
  published as single-arch `linux/amd64`, so an ARM64/aarch64 host
  (Grace, Thor, Jetson) cannot run Path D no matter which NVIDIA GPU is
  attached. Milvus and TAO Toolkit do ship `arm64` variants; CDS does not,
  and no emulation path is supported.
- **CDS does not support Blackwell (B-series) GPUs.** The published
  Cosmos-Embed1 container has no kernels for compute capability 10.0
  (`sm_100`: B100, B200, GB200) or 12.0 (`sm_120`: RTX PRO 6000
  Blackwell); the CDS API does not use the GPU.
  The "Other Ampere+ GPUs" entry in the
  upstream CDS prerequisites excludes Blackwell. Qualify Path D on Hopper
  (H100, H20), Ada (L40S, L4, L20), or Ampere (A100, A40) class GPUs with
  16GB+ VRAM; 24GB+ is recommended. This limit applies to CDS only.
  Cosmos Curator and TAO are separate images that do run on Blackwell, so
  Paths A, B, and C are unaffected.
- Building or pushing vendor images is not supported; pull only.
- There is no in-repo scheduler. Sequence Make targets yourself.
- Make is the public interface; the helper CLI is an implementation detail.
- TAO mining does not generate embeddings. Run Curator or TAO `embedding` first.
- Metric `l2` is not accepted; use `euclidean`.
- `coco` detections must be a single JSON file; `kitti` must be a label
  directory.
- The repository does not publish a performance SLA. Time a short clip or a few
  parquet rows on your host before you scale.

Optional Curator source builds (`make clone-curator` / `make build`) are
developer-only. Refer to [Developer Docs](../developer/README.md).
