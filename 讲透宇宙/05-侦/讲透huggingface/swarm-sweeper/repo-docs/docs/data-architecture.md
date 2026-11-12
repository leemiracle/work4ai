# Data architecture

Canonical storage model:

| thing | role |
| --- | --- |
| `repo` | upstream GitHub repo to scrape |
| `dataset_id` | canonical Hugging Face dataset repo for latest published data |
| `workspace` | local cache and local outputs |
| HF bucket | mutable operational cache only |
| Space | dashboard or API deployment target |

Canonical writers:

- `refresh-dataset` = canonical raw/latest dataset writer
- `publish-analysis-artifacts` = canonical expensive hybrid analysis writer

Operational cache writers:

- `save-cache` = upload snapshot-local `analysis-state/` to repo-root `analysis-state/`
- `publish-analysis-artifacts --save-cache` = publish canonical analysis and refresh the
  mutable hybrid cache source in one step

## Recommended modes

### Canonical upkeep

Use the canonical remote writer:

```bash
uv run slop-farmer --config configs/openclaw.yaml refresh-dataset
```

Or schedule it with an HF Job:

```bash
SCHEDULE='@hourly' CONFIG_PATH=configs/openclaw.yaml scripts/submit_dataset_job.sh
```

This flow:

- resumes from remote `state/watermark.json`
- merges against the current remote dataset snapshot
- regenerates contributor artifacts
- uploads the refreshed latest dataset back to `dataset_id`

Expensive hybrid analysis is published separately:

```bash
uv run slop-farmer --config configs/openclaw.yaml publish-analysis-artifacts \
  --canonical \
  --save-cache
```

Published analysis layout:

- canonical current alias: `analysis/current/`
- canonical current manifest: `analysis/current/manifest.json`
- immutable archived runs: `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/...`
- mutable hybrid cache source: repo-root `analysis-state/`

### Canonical readers

These commands are remote-first when `dataset_id` is configured:

```bash
uv run slop-farmer --config configs/openclaw.yaml analyze
uv run slop-farmer --config configs/openclaw.yaml pr-scope
uv run slop-farmer --config configs/openclaw.yaml pr-search refresh
uv run slop-farmer --config configs/openclaw.yaml new-contributor-report
uv run slop-farmer --config configs/openclaw.yaml dashboard-data
uv run slop-farmer --config configs/openclaw.yaml deploy-dashboard
uv run slop-farmer --config configs/openclaw.yaml dataset-status
```

Pass `--snapshot-dir` to force a local snapshot instead.

## Dashboard generation contract

`dashboard-data` and `deploy-dashboard` read the same materialized snapshot view as the API.

Default analysis selection is:

1. published `analysis/current/manifest.json`
2. published `analysis/current/analysis-report-hybrid.json`
3. snapshot-local fallback only when canonical current analysis is absent

If the canonical current manifest exists but the required artifact is missing, dashboard export
fails loudly rather than silently drifting to snapshot-local analysis.

Contributor and PR-scope defaults remain snapshot-local within the materialized published view:

- `new-contributors-report.json`
- `pr-scope-clusters.json`

## API serving contract

The PR API reads one materialized dataset view.

- canonical current analysis is authoritative for default serving when present
- archived analysis requires explicit `snapshot_id` + `analysis_id`
- dataset repo is canonical published state
- HF bucket is optional mutable operational cache only
- Space disk is ephemeral runtime storage

### Local experimentation

Use `scrape` for local-only iteration:

```bash
uv run slop-farmer --config configs/openclaw.yaml scrape
```

Canonical publication lives in:

- `refresh-dataset` for raw tables and cheap artifacts
- `publish-analysis-artifacts` for expensive published analysis
- `save-cache` for mutable hybrid review cache refreshes

## Repo registry

| config | repo | dataset_id | dashboard Space | API Space | canonical writer |
| --- | --- | --- | --- | --- | --- |
| `configs/transformers.yaml` | `huggingface/transformers` | `evalstate/transformers-pr` | `evalstate/transformers-dashboard` | `evalstate/transformers-pr-api` | `refresh-dataset` |
| `configs/openclaw.yaml` | `openclaw/openclaw` | `evalstate/openclaw-pr` | `evalstate/openclaw-pr-report` | `evalstate/openclaw-pr-api` | `refresh-dataset` |
| `configs/diffusers.yaml` | `huggingface/diffusers` | `evalstate/diffusers-pr` | `evalstate/diffusers-dashboard` | `evalstate/diffusers-pr-api` | `refresh-dataset` |
