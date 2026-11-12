# Warehouse safety cookbook

Experiment kit for Cosmos Curator on warehouse / distribution-center video.
YAML is the recipe. `DATA_DIR` is the media tree.

## What ships

```text
warehouse-safety/
  videos/SDG-Warehouse-01.mp4 .. 04.mp4
  split-minimal.yaml              Path A: /data/videos, limit: 1 (processes 01)
  split.yaml
  event_caption_prompt.txt
  dedup.yaml
  shard.yaml
  output/                             run artifacts (gitignored)
```

Clips come from the NGC VSS developer sample pack
(`nvidia/vss-developer/dev-profile-sample-data:3.1.0`). They are for trying the
recipe, not qualification evidence.

YAML I/O is `/data/...`. Make bind-mounts `DATA_DIR` at `/data` (and at the
host path). Keep docs **outside** `videos/`; Curator treats every file in that
directory as input media.

## Video samples

| File | Duration | Format | Source clip |
|------|----------|--------|-------------|
| `videos/SDG-Warehouse-01.mp4` | ~25 s | H.264 1920×1080 10 fps | `warehouse_safety_0001.mp4`; Path A (`limit: 1`) |
| `videos/SDG-Warehouse-02.mp4` | ~30 s | H.264 1920×1080 10 fps | `warehouse_safety_0002.mp4` |
| `videos/SDG-Warehouse-03.mp4` | ~135 s | H.264 1920×1080 10 fps | `sample-warehouse-ladder.mp4` |
| `videos/SDG-Warehouse-04.mp4` | ~210 s | H.264 1842×1080 30 fps | `warehouse_sample.mp4` |

`split.yaml` and `split-minimal.yaml` both read `videos/` (`/data/videos`).
`split-minimal.yaml` sets `limit: 1`, so it processes `SDG-Warehouse-01.mp4`
first.

## Run on the shipped clips

```bash
DATA=$PWD/cookbook/warehouse-safety
MODELS=/path/to/models

make run-pipeline \
  CONFIG_FILE=cookbook/warehouse-safety/split-minimal.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg
```

**Success:** `$DATA/output/split-minimal/iv2_embd_parquet/` has at least one
parquet. On a shared GPU host pass `GPUS='"device=N"'`.

Remove `$DATA/output/split-minimal` before a clean re-run; Curator skips clips
it already processed.

## Full recipe (caption + classifier + SAM3 + IV2)

Needs live VLM/LLM endpoints:
[VLM and LLM Endpoints](../../docs/user-guide/vlm-llm-endpoints.md).
SAM3 needs `PIXI_ENV=sam3` and SAM3 weights.

```bash
DATA=$PWD/cookbook/warehouse-safety
MODELS=/path/to/models

make run-pipeline \
  CONFIG_FILE=cookbook/warehouse-safety/split.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg \
  PIXI_ENV=sam3

make run-pipeline \
  CONFIG_FILE=cookbook/warehouse-safety/dedup.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg

make run-pipeline \
  CONFIG_FILE=cookbook/warehouse-safety/shard.yaml \
  DATA_DIR=$DATA \
  MODELS_DIR=$MODELS \
  FFMPEG_DIR=$HOME/cosmos-curator-ffmpeg
```

## Point the same YAML at other media

Keep `CONFIG_FILE` here and put clips in a work directory:

```text
my-warehouse/
  videos/   MP4s; split-minimal uses the first file (limit: 1)
```

`split-minimal.yaml` processes the first file in `videos/` (shipped
`SDG-Warehouse-01.mp4`).
