# Scenario Recipes

Part of Cosmos Data Factory (CDF) Curation and Retrieval
(`cdf-curation-and-retrieval`).

Cookbooks ship **engine-native configs** (`*.yaml`, prompts). Release-facing
recipes cover Cosmos Curator and Data Mining.

Human overview + diagram: repo [`README.md`](../README.md). There is no shared
scheduler or cross-step state in this repository; the `apps.workflows`
package owns behavior-preserving handoff logic used by Make and the
`cdf_curation_and_retrieval` helper. Validate
with `uv run pytest tests/unit`.

## How to Run

### Cosmos Curator Video

Traffic is the experiment kit with shipped VSS sample clips. YAML I/O is
`/data/...`. Pass `DATA_DIR` as the cookbook directory (or a work dir with a
`videos/` folder). Warehouse uses the same contract.

```bash
MODELS=/path/to/models
DATA=$PWD/cookbook/traffic-video-analytics

make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/split-minimal.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/split.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/dedup.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/shard.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
```

`split-minimal.yaml` is split + Cosmos-Embed1 only (Path A / Path D). Full
`split.yaml` needs VLM endpoints. Warehouse `split-minimal.yaml` still uses
InternVideo2 (Path C / TMM). Details:
[`cookbook/traffic-video-analytics/README.md`](traffic-video-analytics/README.md).

### Data Mining

Nearest neighbors (`nearest-neighbor-mining/tmm.yaml`):

```bash
make run-data-mining-select \
  DATA_DIR=$PWD/data/nearest-neighbor-mining \
  TMM_CONFIG_FILE=cookbook/nearest-neighbor-mining/tmm.yaml
```

Unique neighbor matching (`unique-neighbor-matching/unm.yaml`):

```bash
make run-data-mining-unique-match \
  DATA_DIR=$PWD/data/unique-neighbor-matching \
  TMM_UNM_CONFIG_FILE=cookbook/unique-neighbor-matching/unm.yaml
```

Prepare host data under `DATA_DIR`:

```text
data/nearest-neighbor-mining/   (or data/unique-neighbor-matching/)
  S.parquet      # targets (query set)
  B.parquet      # candidates (source pool)
```

Customer guide: [`docs/user-guide/`](../docs/user-guide/).
Samples: [`docs/user-guide/samples-and-cookbooks.md`](../docs/user-guide/samples-and-cookbooks.md).

## Domain Curator Cookbooks

Each domain subdirectory contains **minimal override** YAML configs for the
three cosmos-curator video pipelines (`split`, `dedup`, `shard`).

Only keys that **differ** from the full reference templates in `configs/` are
listed. Omitted keys receive their parser defaults automatically via
`fill_default_args`.

### Usage

1. Traffic and warehouse: run against the shipped clips (`DATA_DIR` = the
   cookbook directory). PhysicalAI-AV: download and extract sessions first
   (`python -m adapters.physical_ai_av.prepare_sessions`); see
   [`physical-ai-av/README.md`](physical-ai-av/README.md). To try other MP4s,
   copy them into a work directory with `videos/` and pass that as `DATA_DIR`.
   Keep `CONFIG_FILE` pointing at the cookbook YAML.

2. For local paths, pass `DATA_DIR=<dir>` so Make bind-mounts the host
   directory at `/data`.

3. Run the stages sequentially:

   ```bash
   MODELS=/path/to/models
   DATA=$PWD/cookbook/traffic-video-analytics

   make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/split-minimal.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
   make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/split.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
   make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/dedup.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
   make run-pipeline CONFIG_FILE=cookbook/traffic-video-analytics/shard.yaml MODELS_DIR=$MODELS DATA_DIR=$DATA
   ```

   Warehouse: same commands with `cookbook/warehouse-safety` and
   `DATA=$PWD/cookbook/warehouse-safety`.

## Available Scenarios

| Directory                   | Kind   | Description |
| --------------------------- | ------ | ----------- |
| `traffic-video-analytics`   | Recipe | Experiment kit: two VSS traffic clips; `split-minimal.yaml` (split + CE1 + captions) and full `split.yaml` (captions, classifier, SAM3, CE1), plus dedup and shard |
| `warehouse-safety`          | Recipe | Experiment kit: four VSS warehouse clips; `split-minimal.yaml` and full `split.yaml` (captions, classifier, SAM3, IV2), plus dedup and shard |
| `physical-ai-av`            | Recipe | Gated PhysicalAI-AV: download/extract, then minimal CE1, full SAM3 event split, or caption A/B YAMLs |
| `nearest-neighbor-mining`   | Recipe | Nearest neighbors via `tmm.yaml` |
| `unique-neighbor-matching`  | Recipe | Unique neighbor matching via `unm.yaml` |

Domain Curator recipes include:

- `split-minimal.yaml` — split + embeddings, minimal enrichment (Path A
  first-run); embedding backend and captioning vary per scenario as listed above
- `split.yaml` — split + caption + embed + classify/filter (consumed by the pipeline)
- `dedup.yaml` — semantic deduplication on split output
- `shard.yaml` — WebDataset sharding of deduplicated clips
- `input_config.json` — agent-emitted override manifest (mirrors `split.yaml`
  in compact JSON form; metadata only, not consumed by the pipeline). Its image
  version describes the compatible Curator component; runtime image selection
  still comes from the repository environment configuration.
- `prompt.md` — reference text for a custom VLM captioning prompt; copy its
  prompt text into `split.yaml` as `captioning_prompt_text` to enable it
- `classification_events.yaml` — event taxonomy and objects of interest
  (used as reference for the video classifier allow-list in `split.yaml`)

Host secrets stay in ignored `.env` / `local.env` — never in cookbook configs.
