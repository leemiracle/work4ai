# Nearest neighbor mining

Select similar source clips for a target set using GPU k-NN
(`tmm nearest_neighbors`).

## S and B

| Role | File | Meaning |
|------|------|---------|
| **S (target)** | `S.parquet` | Items you want neighbors **for** |
| **B (source)** | `B.parquet` | Candidate pool to search **in** |

Outcome: for each S row, up to `topn` closest B rows under the chosen metric.

## Prerequisites

```bash
make pull-data-mining
```

Prepare embeddings as parquet with `filepath` (or `file_name`) + `embedding`
(or custom column names you declare):

```text
data/nearest-neighbor-mining/
  S.parquet    # targets
  B.parquet    # sources
```

## Run (recommended — engine-native YAML)

Edit `tmm.yaml` for paths and mining parameters, then:

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TMM_CONFIG_FILE=cookbook/nearest-neighbor-mining/tmm.yaml \
  TDM_EMBEDDING_BACKEND=ce1
```

## Run (Make flags only)

When you omit `TMM_CONFIG_FILE`, Make passes individual inputs to the CLI. The
runner validates them, writes a temporary TAO experiment YAML, mounts it
read-only, and invokes `tmm nearest_neighbors -e <spec>`.

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TARGET_SUBDIR=S.parquet \
  SOURCE_SUBDIR=B.parquet \
  OUTPUT_SUBDIR=out \
  TOPN=5 \
  DATA_MINING_METRIC=cosine \
  DISTANCE_THRESHOLD=-1.0 \
  FILTER_BY_LABEL=0 \
  SOURCE_EMBED_COLUMN_NAME=embedding \
  TARGET_EMBED_COLUMN_NAME=embedding \
  TDM_EMBEDDING_BACKEND=ce1 \
  GPUS=all \
  DATA_MINING_SHM_SIZE=16g
```

Supported `knn_metric` values: `cosine`, `euclidean`, and `manhattan`.
Optional `DISTANCE_THRESHOLD` (float; `-1.0` disables distance filtering) is
accepted by the RC36+ Data Services image. Set `FILTER_BY_LABEL=1` to drop
pairs whose `label` values disagree (skipped with a warning if either side
lacks `label`). Optional
`SOURCE_EMBED_COLUMN_NAME` / `TARGET_EMBED_COLUMN_NAME` rename embedding
columns when parquet schemas are non-default. In engine-native YAML,
`filter_by_label` must be the quoted string `"true"` or `"false"`.

For unique-assignment mining see `cookbook/unique-neighbor-matching/`.
Full operator guide:
[Data Mining operations](../../docs/user-guide/operations-tao-mining.md).
