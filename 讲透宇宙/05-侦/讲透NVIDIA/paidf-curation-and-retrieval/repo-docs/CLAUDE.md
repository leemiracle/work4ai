# Cosmos Data Factory — Curation and Retrieval

**Product / repo:** `cdf-curation-and-retrieval`

Integration and operator environment for CDF Curation and Retrieval. Pipeline
logic stays in vendor images (Cosmos Curator and Data Mining). This
repository exposes **Make** as the supported local operator UX.
The installed `cdf_curation_and_retrieval` CLI is a non-interactive helper for
Make targets, orchestrators, and tests; do not present it as a separate public
product UX.

## Project Layout

```text
.env.example               Image pins
adapters/                  Curator, Data Mining, and Docker runtime integration
apps/                      Click delivery, workflow modules, composition root
packages/                  Domain types, ports, analytics
configs/                   Full Curator reference YAMLs (split, dedup, shard, image)
cookbook/                  Scenario recipes
docs/                      Operator user-guide and architecture
skills/                    Agent skills (SKILL.md per skill)
tests/unit/                Unit tests
.external/                 Ignored optional upstream source checkouts
```

Customer documentation: `docs/user-guide/README.md`.

## How It Works

1. Copy env and sync deps:
   - `cp .env.example .env`
   - `uv sync`
2. Pull vendor images (never build them in the normal path):
   - `make pull` — Cosmos Curator
   - `make pull-data-mining` — Data Mining
3. Curator host FFmpeg sidecar: `make ffmpeg-install` then `make check-setup`
4. Run engines via Make:
   - Curator: `make run-pipeline CONFIG_FILE=…` / `make run_image_pipeline`
   - Image embeddings: `make run-image-embeddings …`
   - Text embeddings: `make run-text-embeddings …`
   - Mining: `make run-data-mining-select TMM_CONFIG_FILE=…`
   - Unique match: `make run-data-mining-unique-match TMM_UNM_CONFIG_FILE=…`

Cookbooks: `cookbook/README.md`.

## Operator Entry Points (Make)

| Command | Purpose |
|---------|---------|
| `make help` | Show targets and configuration |
| `make check-setup` | Prerequisites (Docker, NVIDIA, FFmpeg sidecar) |
| `make pull` | Pull Curator image and retag locally |
| `make pull-data-mining` | Pull `tao-toolkit` image |
| `make ffmpeg-install` | Install host FFmpeg sidecar (conda-forge LGPL) |
| `make download-models` | Download Curator model weights (~90GB) |
| `make run-pipeline` | Run Curator video pipeline in Docker |
| `make run_image_pipeline` | Run Curator image annotate (upstream config-file mode) |
| `make shell` | Interactive shell in Curator container |
| `make run-data-mining-select` | TAO `tmm nearest_neighbors` |
| `make run-data-mining-unique-match` | TAO `tmm unique_neighbor_matching` |
| `make run-image-embeddings` | TAO `embedding image_embeddings` |
| `make run-text-embeddings` | TAO `embedding text_embeddings` |
| `make format` | Format with ruff |
| `make clean` | Clean up (preserves images and models) |
| `make clone-curator` / `make build` | Optional Curator source build only |

Default Curator / Data Mining / CDS image pins: root `Makefile`
(override via `.env` / `local.env`).

## Internal Automation CLI

Make targets call the installed helper:

```bash
uv run cdf_curation_and_retrieval ...
```

Canonical helper groups are:

- `cdf_curation_and_retrieval integration ...` for finite TAO Data Services
  image-embedding handoffs.

Keep operator documentation Make-first. Use direct `cdf_curation_and_retrieval`
commands only for
automation, tests, or orchestration contracts.

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format .
uv run pytest tests/unit -q
```

- Python 3.10+, ruff line-length 100, double quotes.
- Engines ship inside pulled Docker images; do not redeclare engine-only
  packages in this project's dependencies.

## Configuration

**Curator:** prefer flat YAML with `snake_case` keys matching upstream argparse
`dest` names. CDF preflight also accepts a nested `args` mapping and flattens
it before invoking Curator. Upstream fills omitted keys from parser defaults.

Templates in `configs/`: `split.yaml`, `dedup.yaml`, `shard.yaml`, `image.yaml`.

Cookbook scenarios under `cookbook/` hold minimal recipe overrides.

**Mining:** Make targets + TAO experiment YAML (`tmm.yaml`) — see `cookbook/`.

## Environment Variables

Image pins: copy `.env.example` → `.env`.

Object-store credentials are injected at runtime by the selected operator
deployment mechanism. Handoff commands accept credential environment-variable
names (`OBJECT_STORE_ACCESS_KEY_ENV`, `OBJECT_STORE_SECRET_KEY_ENV`) rather
than credential values. Never commit or document secret values.

Model weights: set `model_weights_path` in Curator config or `MODELS_DIR`.

## Skills

Skills are in `skills/`. Each has a `SKILL.md` with progressive
disclosure via `references/` subdirectories.

| Skill | Purpose |
|-------|---------|
| `cdf-curation-and-retrieval` | Cosmos Curator split / dedup / shard / image annotate: configure, run, troubleshoot, KPI and distribution-aware curation |

Scope notes:
- Data Mining ops are covered by `make help` / cookbooks, not by
  expanding this Curator-focused skill into a second product surface.

## Domain Catalogs

Domain catalogs in `.agents/references/catalogs/` define canonical event
taxonomies with tiered severity levels, alias remap tables, and keyword
lists. Supported domains: traffic safety, warehouse, construction,
parking facility video analytics, retail store video analytics, facility
incident analytics, logistics, and workplace visual safety.

## Conventions

- Never hardcode machine-specific paths in config YAMLs; use placeholders.
- Commit messages follow conventional commits (`feat:`, `fix:`, `chore:`,
  `docs:`).
- Operator UX is Make-first; keep `cdf_curation_and_retrieval` documented as an
  internal automation helper, not a separate public UX.
- Never commit secrets, `local.env`, or private registry hosts.
