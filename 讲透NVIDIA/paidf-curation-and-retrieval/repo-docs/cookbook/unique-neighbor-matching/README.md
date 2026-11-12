# Unique neighbor matching

Run unique neighbor matching through Make (`tmm unique_neighbor_matching`).

## S and B

| Role | File | Meaning |
|------|------|---------|
| **S (target)** | `S.parquet` | Demand / query set |
| **B (source)** | `B.parquet` | Candidate pool |

Outcome: greedy unique assignment into `UNM_OUTPUT_SUBDIR` (validated
`final_unique_files.parquet` after successful live runs).

## Prerequisites

```bash
make pull-data-mining
```

Image registry/tag come from the Makefile / campaign env (`make pull-data-mining`
is the source of truth).

## Layout

```text
data/unique-neighbor-matching/
  S.parquet   # target embeddings (filepath + embedding)
  B.parquet   # source embeddings (filepath + embedding)
```

## Run with cookbook YAML

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  TMM_UNM_CONFIG_FILE=cookbook/unique-neighbor-matching/unm.yaml
```

## Run with Make variables (generated temporary spec)

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  DESIRED_UNIQUE_COUNT=100 \
  ALLOCATION_POLICY=global \
  UNM_OUTPUT_SUBDIR=unm_out \
  DATA_MINING_METRIC=euclidean
```

### Class-stratified (COCO JSON files)

`DETECTION_FORMAT=coco` requires a single JSON **file** per role:

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  ALLOCATION_POLICY=class_stratified \
  SOURCE_DETECTION_FILE=detections/source.json \
  TARGET_DETECTION_FILE=detections/target.json \
  DETECTION_FORMAT=coco \
  RARE_CLASS_LIST=person,bicycle \
  EXCLUDE_PATH=exclude.parquet \
  SAVE_EMBEDDINGS=1 \
  VISUALIZE=0
```

### Class-stratified (KITTI label directories)

`DETECTION_FORMAT=kitti` requires a **directory** of per-image `.txt` labels:

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  ALLOCATION_POLICY=class_stratified \
  SOURCE_DETECTION_FILE=labels_source \
  TARGET_DETECTION_FILE=labels_target \
  DETECTION_FORMAT=kitti \
  RARE_CLASS_LIST=person,bicycle
```

Optional column overrides: `SOURCE_EMBEDDING_COLUMN`, `TARGET_EMBEDDING_COLUMN`,
`SOURCE_FILEPATH_COLUMN`, `TARGET_FILEPATH_COLUMN`.

## Outputs

Under `UNM_OUTPUT_SUBDIR` (container `/data/<subdir>`):

- `final_unique_files.parquet` (validated after successful non-dry-run)
- `summary.json`
- per-iteration parquet artifacts
- optional visualization PNGs when `VISUALIZE=1` / `visualize: true`

## Notes

- `class_stratified` requires detection files, `DETECTION_FORMAT=coco|kitti`,
  and a non-empty `RARE_CLASS_LIST` (Make/CLI or YAML).
- Existing `nearest_neighbors` path remains available via
  `make run-data-mining-select` (`cookbook/nearest-neighbor-mining/`).
- Operator guide:
  [Data Mining operations](../../docs/user-guide/operations-tao-mining.md).
