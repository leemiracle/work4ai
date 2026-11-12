<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Data Mining

1. [About Curation and Retrieval](README.md)
2. [Installation](installation.md)
3. [Samples and Cookbooks](samples-and-cookbooks.md)
4. [Get Started](getting-started.md)
5. [Cosmos Curator](operations-curator.md)
6. [Data Mining](operations-tao-mining.md)
7. [Cosmos Dataset Search](operations-cds.md)
8. [VLM and LLM Endpoints](vlm-llm-endpoints.md)
9. [Troubleshooting](troubleshooting.md)

Run image and text embeddings and nearest-neighbor mining with Make.

Product context (Curator producers feeding mining):
[Developer architecture](../developer/architecture.md) ·
[`../assets/CDF-CC-CDS-TDM.png`](../assets/CDF-CC-CDS-TDM.png).

Prerequisites: `make pull-data-mining` and `make check-data-mining-image`.
Keep all data and local model artifacts under `DATA_DIR` (mounted at `/data`).

**S** is the query set (matches **for** these rows). **B** is the candidate
pool (search **in** these rows). Typical layout:

```text
data/nearest-neighbor-mining/
  S.parquet
  B.parquet
```

## Image Embeddings

```bash
make image-embeddings-build \
  DATA_DIR=$PWD/data/images \
  IMAGE_EMBEDDING_JSON=$PWD/data/images/rows.json \
  IMAGE_EMBEDDING_INPUT=$PWD/data/images/input.parquet

make image-embeddings-validate-input \
  DATA_DIR=$PWD/data/images \
  IMAGE_EMBEDDING_INPUT=$PWD/data/images/input.parquet

make run-image-embeddings \
  DATA_DIR=$PWD/data/images \
  IMAGE_EMBEDDING_INPUT=$PWD/data/images/input.parquet \
  IMAGE_EMBEDDING_OUTPUT=$PWD/data/images/output.parquet \
  IMAGE_EMBEDDING_MODEL_TYPE=clip \
  IMAGE_EMBEDDING_MODEL=openai/clip-vit-base-patch32

make image-embeddings-validate-output \
  DATA_DIR=$PWD/data/images \
  IMAGE_EMBEDDING_INPUT=$PWD/data/images/input.parquet \
  IMAGE_EMBEDDING_OUTPUT=$PWD/data/images/output.parquet
```

Input JSON: unique non-empty `filepath` per row; paths must resolve under
`DATA_DIR`. Do not pre-declare the reserved `embedding` column. Set
`IMAGE_EMBEDDING_DRY_RUN=1` to emit Docker args without starting the job.

## Text Embeddings

Input parquet must include a non-empty `text` column and must not include
`embedding`.

```bash
make text-embeddings-validate-input \
  DATA_DIR=$PWD/data/captions \
  TEXT_EMBEDDING_INPUT=$PWD/data/captions/captions.parquet

make run-text-embeddings \
  DATA_DIR=$PWD/data/captions \
  TEXT_EMBEDDING_INPUT=$PWD/data/captions/captions.parquet \
  TEXT_EMBEDDING_OUTPUT=$PWD/data/captions/text_embeddings.parquet \
  TEXT_EMBEDDING_MODEL=clip \
  TEXT_EMBEDDING_MODEL_PATH=openai/clip-vit-base-patch32

make text-embeddings-validate-output \
  DATA_DIR=$PWD/data/captions \
  TEXT_EMBEDDING_INPUT=$PWD/data/captions/captions.parquet \
  TEXT_EMBEDDING_OUTPUT=$PWD/data/captions/text_embeddings.parquet
```

`TEXT_EMBEDDING_MODEL` accepts `clip`, `siglip`, or `siglip2`.

## Nearest Neighbors

Make default `TDM_EMBEDDING_BACKEND` is `ce1`. Override with `iv2`, `clip`,
or `siglip` to match the embedding producer.

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TMM_CONFIG_FILE=cookbook/nearest-neighbor-mining/tmm.yaml \
  TDM_EMBEDDING_BACKEND=ce1
```

Direct Make flags (no YAML):

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TARGET_SUBDIR=S.parquet \
  SOURCE_SUBDIR=B.parquet \
  TOPN=3 \
  DISTANCE_THRESHOLD=1.5 \
  FILTER_BY_LABEL=1 \
  SOURCE_EMBED_COLUMN_NAME=source_vec \
  TARGET_EMBED_COLUMN_NAME=target_vec \
  TDM_EMBEDDING_BACKEND=iv2 \
  OUTPUT_SUBDIR=out
```

Preflight validates non-empty selections, finite vectors, one dimension per
side, and matching dimensions across S and B.

## Unique Neighbor Matching

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  TMM_UNM_CONFIG_FILE=cookbook/unique-neighbor-matching/unm.yaml
```

Global policy:

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  DESIRED_UNIQUE_COUNT=100 \
  ALLOCATION_POLICY=global \
  UNM_OUTPUT_SUBDIR=unm_out \
  DATA_MINING_METRIC=euclidean
```

Class-stratified (COCO JSON files):

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  ALLOCATION_POLICY=class_stratified \
  SOURCE_DETECTION_FILE=detections/source.json \
  TARGET_DETECTION_FILE=detections/target.json \
  DETECTION_FORMAT=coco \
  RARE_CLASS_LIST=person,bicycle
```

Class-stratified (KITTI label directories):

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  ALLOCATION_POLICY=class_stratified \
  SOURCE_DETECTION_FILE=labels_source \
  TARGET_DETECTION_FILE=labels_target \
  DETECTION_FORMAT=kitti \
  RARE_CLASS_LIST=person,bicycle
```

Successful non-dry-run UNM validates `final_unique_files.parquet` under the
output directory.

## Evidence and Status

Mining Make targets invoke a helper CLI that emits JSON including:

- `status`: `dry-run` or `completed`
- `command`: Docker argv evidence
- `evidence`: generated experiment spec (and UNM output validation paths)

Treat every nonzero exit as failure.

## Make Variables

Do not mix a vendor config file with the corresponding direct
input/output/model variables on the same run.

### Image Embedding Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `IMAGE_EMBEDDING_JSON` | | Rows JSON for `image-embeddings-build` |
| `IMAGE_EMBEDDING_INPUT` | | Input parquet path under `DATA_DIR` |
| `IMAGE_EMBEDDING_OUTPUT` | | Output parquet path |
| `IMAGE_EMBEDDING_CONFIG` | | Vendor YAML; mutually exclusive with direct vars |
| `IMAGE_EMBEDDING_MODEL_TYPE` | | `clip` or `siglip` |
| `IMAGE_EMBEDDING_MODEL` | | HF id or TAO checkpoint under `DATA_DIR` |
| `IMAGE_EMBEDDING_MODEL_CONFIG` | | Required for a TAO CLIP `.ckpt` / `.pth` file |
| `IMAGE_EMBEDDING_BATCH_SIZE` | `64` | Positive integer |
| `IMAGE_EMBEDDING_DRY_RUN` | `0` | `1` to dry-run |

### Text Embedding Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `TEXT_EMBEDDING_INPUT` | | Parquet with `text` column |
| `TEXT_EMBEDDING_OUTPUT` | | Output parquet |
| `TEXT_EMBEDDING_CONFIG` | | Vendor YAML; mutually exclusive with direct vars |
| `TEXT_EMBEDDING_MODEL` | | `clip`, `siglip`, or `siglip2` |
| `TEXT_EMBEDDING_MODEL_PATH` | | HF id or local model under `DATA_DIR` |
| `TEXT_EMBEDDING_BATCH_SIZE` | `64` | Positive integer |
| `TEXT_EMBEDDING_DRY_RUN` | `0` | `1` to dry-run |

### Nearest Neighbor Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `TMM_CONFIG_FILE` | | Vendor YAML; when set, preferred over direct path knobs |
| `TARGET_SUBDIR` | `S` | Target selection under `DATA_DIR` |
| `SOURCE_SUBDIR` | `B` | Source selection under `DATA_DIR` |
| `OUTPUT_SUBDIR` | `divknn_out` | Output directory for `mined.parquet` |
| `TOPN` | `5` | Neighbors per target |
| `DATA_MINING_METRIC` | `cosine` | `cosine`, `euclidean`, `manhattan` (`l2` is not valid) |
| `DISTANCE_THRESHOLD` | `-1.0` | Float; `-1.0` disables |
| `FILTER_BY_LABEL` | `0` | `1` enables label filtering |
| `SOURCE_EMBED_COLUMN_NAME` | `embedding` | Custom source embed column |
| `TARGET_EMBED_COLUMN_NAME` | `embedding` | Custom target embed column |
| `TDM_EMBEDDING_BACKEND` | `ce1` | `iv2`, `ce1`, `clip`, or `siglip` |
| `DATA_MINING_SHM_SIZE` | `16g` | Container `/dev/shm` |

Nearest neighbors uses `*_EMBED_COLUMN_NAME`. UNM uses `*_EMBEDDING_COLUMN`.

### Unique Neighbor Matching Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `TMM_UNM_CONFIG_FILE` | | Vendor YAML |
| `UNM_OUTPUT_SUBDIR` | `unm_out` | Output directory |
| `DESIRED_UNIQUE_COUNT` | `100` | Positive integer |
| `ALLOCATION_POLICY` | `global` | `global` or `class_stratified` |
| `CANDIDATE_EXPANSION_FACTOR` | `5` | Positive integer |
| `SOURCE_DETECTION_FILE` | | Required for `class_stratified` |
| `TARGET_DETECTION_FILE` | | Required for `class_stratified` |
| `DETECTION_FORMAT` | | `coco` (JSON file) or `kitti` (label dir) |
| `RARE_CLASS_LIST` | | Comma-separated; required for stratified |
