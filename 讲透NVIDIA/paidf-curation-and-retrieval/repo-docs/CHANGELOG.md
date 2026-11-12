<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Changelog

All notable changes to **Cosmos Data Factory — Curation and Retrieval**
(`cdf-curation-and-retrieval`) are recorded here.

Version numbers follow `pyproject.toml` product semver. Container image tags
are separate pins; see [Installation](docs/user-guide/installation.md).

**Baseline note:** git tag `v1.0.0` (`6bd8af3`, 2026-06-01) is the first
shippable operator surface for this repository. That commit was originally
published under the incorrect tag name `v0.3.0` (now removed). Changes below
for `[1.1.0]` are relative to `v1.0.0`, not to the interim pyproject `1.0.0`
string that appeared later without a matching git tag. Changes for `[1.2.0]`
are relative to git tag `v1.1.0`.

## [1.2.0] — 2026-10-20

Target product cut after `1.1.0`. Scope is the full delta versus
git tag `v1.1.0` (Path D / CDS work plus the PhysicalAI-AV cookbook). Glue
`pyproject.toml` is `1.2.0`.

### Added

- **Path D (Cosmos Dataset Search)** operator surface: pull, compose
  bring-up, health, collection create/get, CE1 ingest, and text search
  (`make pull-dataset-search`, `up-dataset-search`, `ds-health`,
  `ds-create-collection`, `ingest-curator`, `search`).
- Dataset Search glue: `adapters/dataset_search/`,
  `apps/cli/dataset_search_cmds.py`, `apps/workflows/dataset_search.py`.
- Local compose stack for Path D (`deploy/compose/`) with a public GA
  profile and an `internal` profile (`CDS_PROFILE=internal`) whose image
  pins live in a gitignored `local.env`. After ingest, search with
  `make search`.
- Lab document ingest (`ALLOW_LAB_DOCUMENT_FALLBACK=1`) as the supported
  local-compose smoke path; GA bulk ingest (`PARQUET_URI=s3://…`)
  documented separately.
- Curator caption handoff: convert Curator metas to CDS caption parquet
  (`make caption-from-curator`) plus caption build / validate /
  readiness / search / stats / get / rewrite / upload / bulk-insert
  targets (`adapters/cosmos_curator/caption_export.py`).
- Path D operator docs: README Path D, `docs/user-guide/operations-cds.md`,
  Getting Started / Installation / Configuration / Troubleshooting
  updates, and skill references
  (`skills/cdf-curation-and-retrieval/references/cosmos-dataset-search.md`).
- PhysicalAI-AV cookbook: `cookbook/physical-ai-av/` (gated Hugging Face
  download via `python -m adapters.physical_ai_av.prepare_sessions`, then
  the caption / event recipes, or full `split-singlecam.yaml` /
  `split-multicam.yaml` with the SAM3 vocabulary). Every
  AV recipe needs a VLM; the no-VLM setup check is the traffic
  `split-minimal.yaml`.
- Unit tests for CDS adapter / compose / caption export / Path D
  docs / integration CLI and Makefile contracts.

### Changed

- Product / glue version bumped from `1.1.0` to `1.2.0` (`pyproject.toml`,
  README, skill cards).
- README and user guide now treat Cosmos Dataset Search as Path D (1.1.0
  listed CDS as out of scope for product claims).
- Skills pack expanded for CDS ingest, search, and caption handoff.
- Traffic `split-minimal` cookbook aligned for CE1 Path D handoff
  (captions + embeddings).
- PhysicalAI-AV event captions report the events that constrain ego
  progress, anchored on the SAM3 tracks, as an `events[]` array carrying
  `start_time` and `end_time` on each event
  (`av_event_caption_prompt.txt`). Event categories and the SAM3
  vocabulary live in `taxonomy_av.yaml`. The clip-level ego-behavior
  classifier is not part of this cut. Scene captions stay stop-capped
  AV prose.
- Default `make download-models` list now includes `bert`
  (`google-bert/bert-large-uncased`). InternVideo2 does not vendor that
  tokenizer, and a fresh cache failed init without it. `t5_xxl` reduction
  runs in the Curator `default` pixi env because `model-download` has no
  `torch`.

### Known limitations

- Compose Path D is a **lab smoke** path (collection **id** required;
  local compose cannot read host parquet via GA `/insert-data`).
- Cluster CDS is out of scope for this repository. Deploy CDS by whichever
  route its own repository supports, then point `CDS_URL` at that API; every
  Path D operation takes `--cds-url` and `make ds-health` confirms it.
- Caption keyword FTS on local compose is incomplete (missing
  `pg_textsearch` / `search_vector`; empty-result LRU cache).

## [1.1.0] — 2026-08

Changes relative to git tag `v1.0.0`.

### Added

- Rebrand to **Cosmos Data Factory — Curation and Retrieval**
  (`cdf-curation-and-retrieval`), with Make-only operator UX and pull-first
  NGC runtime images (Cosmos Curator `2.3.0`, TAO DS
  `nvcr.io/nvidia/tao/tao-toolkit:7.2.0-data-services`).
- Layered code layout: `packages/`, `adapters/`, `apps/` (Make invokes an
  internal CLI; no second public CLI).
- Curator config-file pipelines: `configs/split.yaml`, `dedup.yaml`,
  `shard.yaml`, `image.yaml`; `make run-pipeline`, `make run_image_pipeline`,
  `make pull`, FFmpeg sidecar (`make ffmpeg-install`).
- Domain cookbooks: `cookbook/traffic-video-analytics/`,
  `cookbook/warehouse-safety/` (Path A `split-minimal`, full split with
  classifier/SAM3/event captions, dedup, shard), plus Git LFS sample MP4s.
- TAO Data Services **image embeddings** (`make run-image-embeddings`,
  validate-input / validate-output).
- TAO Data Services **text embeddings** end to end (`make run-text-embeddings`,
  validate-input / validate-output, Make and CLI wiring).
- Data Mining **nearest neighbors** (`make run-data-mining-select`) with
  operator knobs: `DISTANCE_THRESHOLD`, `FILTER_BY_LABEL`, custom source/target
  embedding and filepath column names, S/B (target/source) parquet staging.
- Data Mining **unique neighbor matching** (`make run-data-mining-unique-match`)
  with `global` and `class_stratified` allocation policies.
- UNM operator knobs: detection files, `DETECTION_FORMAT=coco|kitti`
  (format-aware path validation), `RARE_CLASS_LIST`, `EXCLUDE_PATH`, column
  overrides, `SAVE_EMBEDDINGS`, `VISUALIZE`.
- Mining cookbooks: `cookbook/nearest-neighbor-mining/` and `cookbook/unique-neighbor-matching/`.
- Operator user guide under `docs/user-guide/` (Getting Started through
  Limitations), including VLM/LLM endpoint launch and wiring.
- README Quick Start covers Path A (Curator), Path B (Mining), and Path C
  (Curator embeddings into mining) with short copy-paste examples.
- CDF skill pack: `skills/cdf-curation-and-retrieval/` (Curator, mining, SAM3,
  FFmpeg, handoffs).
- Mining CLI/workflow **evidence** (generated experiment spec; UNM output
  validation paths).
- Spec-contract unit tests pinning generated YAML keys to the TAO DS RC36
  schema.
- Optional SeedVR2 / SAM3 model download paths (`MODEL_LIST`,
  `make download-seedvr2`).
- GitHub publish dry-run (`python scripts/github_publish.py`): allowlist
  export (`plan`, `scrub-check`, `export`) driven by
  `scripts/github-publish.toml`. Does not tag `v1.1.0` or push.

### Changed

- Replaced the v1.0.0 submodule **build** model (`cosmos-curate` +
  `make build` / `make build-data-curation` / Jupyter notebook path) with
  pulled Curator images and per-stage YAML recipes.
- Removed legacy host pipeline / screening CLI surface (`run-screen`,
  `run-batch`, `run-pipeline-host`, `scripts/pipeline`, unified
  `curation_pipeline_config.yaml` workflow).
- README rewritten as a documentation hub; deep operator procedures live in
  `docs/user-guide/` (numbered `docs/0x_*.md` guides retired).
- Custom embedding/filepath column names honored during TMM parquet preparation
  (no longer hardcoded to `embedding` / `filepath` only).
- Skills relocated from `.claude/skills/data-curation-skill/` to
  `skills/cdf-curation-and-retrieval/` and expanded for image **and** text
  embeddings, UNM, and S/B terminology.
- Traffic Path A / cookbook embeddings default to **Cosmos-Embed1** where Path C
  handoff is intended; warehouse full split documents SAM3 **box** overlays
  (`sam3_region: box`) vs traffic **contour**.
- Mining cookbooks renamed from `cookbook/tmm-mine/` and `cookbook/tmm-unm/`
  to `cookbook/nearest-neighbor-mining/` and
  `cookbook/unique-neighbor-matching/`. Make variables (`TMM_CONFIG_FILE`,
  `TMM_UNM_CONFIG_FILE`) and TAO CLI module `tmm` are unchanged.

### Fixed

- UNM detection validation: COCO accepts a JSON file only; KITTI accepts a
  label directory of `.txt` files only (both direct and config paths).
- Raise the `pymdown-extensions` uv constraint to `>=11.0.1` (CVE-2026-67422
  ReDoS in caret, tilde, betterem, and magiclink).

### Known limitations

- Cosmos Dataset Search (CDS) remains out of scope for product claims.
- Upstream `tmm default_specs` / `embedding default_specs` are broken in the
  RC36 image and are not exposed by Make.

## [1.0.0] — 2026-06-01 (git tag `v1.0.0`)

First shippable operator surface for this repository. This commit was first
published as git tag `v0.3.0` (incorrect name; removed) and is now tagged
`v1.0.0`. At the tag, `pyproject.toml` still read `name = "data-curation"` /
`version = "0.2.0"` and the README branded the product as the **NVIDIA
Metropolis Data Curation Pipeline**.

### Surface at this release

- Two host/container workflows: **video event screening** and a **unified data
  curation pipeline** (chunking, VLM captions, MCQs) driven by
  `configs/curation_pipeline_config.yaml`.
- Make targets centered on submodule builds and local runs: `build`,
  `build-data-curation`, `download-models`, `notebook`, `run-pipeline`,
  `run-pipeline-host`, `run-screen`, `run-batch`, plus test/format helpers.
- Cosmos Curator consumed via the **`cosmos-curate` git submodule** and image
  build (`make build`), not via the later pull-first NGC pin model.
- Claude skill pack under `.claude/skills/data-curation-skill/` with domain
  event catalogs; numbered docs under `docs/01_SETUP.md` … `docs/07_…`.
- **Not included:** TAO Data Services / Data Mining, cookbooks, CDF
  `packages/`/`adapters/`/`apps/` layout, per-stage Curator YAML
  (`split`/`dedup`/`shard`/`image`), or `docs/user-guide/`.

Prefer `git checkout v1.0.0` when you need the exact 1.0.0 tree.
