# slop-farmer

Pipeline for managing PR's in high volume GitHub repositories. 

Scrapes PR, Issue and Contributor data in to a dataset, performs analysis and publishes a dashboard.

The pipeline stages are:
 1. Scrape - Collect data from the Github Repository
 1. Contributor Report - Look at contributors recent history.
 1. Analyze - Cluster PRs and Issues on 
 1. Scope - Cluster PRs on overlapping repository areas.
 1. Dashboard Export - Export data in JSON format to populate a browsing dashboard
 1. Publish Dashboard - Build a dashboard and deploy it in a Hugging Face Space.



## Scrape

To run a scrape you need to configure:

1. The GitHub Repository ID
1. A valid GitHub PAT with API access.

`uv run slop-farmer scrape --repo huggingface/diffusers --output-dir runs/diffusers/data`

## Contributor Report

This scans the dataset for Contributors and provides a short profile of their recent public commit history and merged PR rate.

## Analyze

Cluster PRs and Issue Content. Choice of deterministic or LLM supplemented algorithm.

When `ranking_backend=hybrid`, analysis writes reusable LLM review cache entries under
`<snapshot>/analysis-state/`. If you enable YAML config setting
`analysis.cached_analysis: true`, `analyze` will automatically copy `analysis-state/`
forward from the previous snapshot when the new snapshot does not already have it, then
log a cache-hit summary for the run. This is useful for incremental scrapes where many
review units are unchanged and can safely reuse cached hybrid decisions.

To push that local cache back to the dataset repo for future remote-first runs, use either:

- `publish-analysis-artifacts --save-cache` during canonical analysis publication
- `save-cache` to upload `analysis-state/` on its own

Hybrid review execution is bounded-parallel. Use `--hybrid-llm-concurrency N` or
`analysis.hybrid_llm_concurrency: N` to cap concurrent review units. `1` keeps the
lowest provider pressure; higher values can reduce wall-clock time at the cost of more
provider pressure.

## Scope

Cluster PRs by touched repository areas.

## Dashboard Export / Publish

Export the report, and publish a dashboard.



## Quickstart

```bash
uv run slop-farmer scrape \
  --repo huggingface/transformers \
  --output-dir data \
  --max-issues 200 \
  --max-prs 50
```

To refresh the canonical dataset repo:

```bash
uv run slop-farmer --config configs/transformers.yaml refresh-dataset
```

`refresh-dataset` publishes raw tables plus cheap artifacts like:

- `new_contributors.parquet`
- `new-contributors-report.json`
- `new-contributors-report.md`
- `pr-scope-clusters.json`

To publish expensive hybrid analysis artifacts after a local `analyze` run:

```bash
uv run slop-farmer --config configs/transformers.yaml publish-analysis-artifacts \
  --canonical \
  --save-cache
```

This writes an immutable archived run under
`snapshots/<snapshot_id>/analysis-runs/<analysis_id>/...` and, with `--canonical`,
updates the stable `analysis/current/` alias. With `--save-cache`, it also uploads the
snapshot-local `analysis-state/` directory to repo-root `analysis-state/` as mutable
operational cache for future hybrid runs.

If `--analysis-id` is omitted, slop-farmer derives a stable default from the
analysis backend, model, and snapshot id.

To upload only the cache without publishing canonical analysis:

```bash
uv run slop-farmer --config configs/transformers.yaml save-cache \
  --snapshot-dir runs/transformers-recent-60d/data/snapshots/20260418T170534Z
```

## Nightly incremental runs

The scraper now stores a local watermark at `data/state/watermark.json` and resumes from it by default when `--since` is not provided.

```bash
uv run slop-farmer scrape \
  --repo huggingface/transformers \
  --output-dir data \
  --fetch-timeline
```

On the first run, this creates a full snapshot. On later runs against the same `--output-dir`, it uses the last successful watermark, fetches only changed records, merges them into the previous snapshot locally, and writes a new full latest snapshot.

To ignore the watermark and force a fresh full run:

```bash
uv run slop-farmer scrape \
  --repo huggingface/transformers \
  --output-dir data \
  --no-resume
```

Authentication defaults:

- GitHub: `GITHUB_TOKEN`, then `gh auth token`
- Hugging Face: `HF_TOKEN`, otherwise existing `hf auth` login

## Canonical dataset upkeep

`dataset_id` is the canonical latest dataset repo.

Use the remote-first writer:

```bash
uv run slop-farmer --config configs/transformers.yaml refresh-dataset
```

Or submit the generic HF Job wrapper:

```bash
scripts/submit_dataset_job.sh
```

By default this creates a scheduled HF Job that:

- reads `CONFIG_PATH` (defaults to `configs/transformers.yaml`)
- refreshes `dataset_id` incrementally against the current Hub dataset state
- regenerates the new contributor report
- uploads the updated snapshot back to the dataset repo

Useful overrides:

```bash
# fire once immediately instead of creating a schedule
MODE=run scripts/submit_dataset_job.sh

# change the cron schedule
SCHEDULE="0 */6 * * *" scripts/submit_dataset_job.sh

# optionally mount a writable HF bucket for temp files
SCRATCH_BUCKET=evalstate/slop-farmer-scratch \
  scripts/submit_dataset_job.sh
```

Buckets are best treated here as optional scratch space via `TMPDIR`, not as the canonical
published dataset. The repo's local analysis and PR-scope tooling already knows how to
materialize versioned Hub **dataset repos**; it does not currently read HF buckets directly.

Compatibility wrappers remain available:

- `scripts/submit_transformers_dataset_job.sh`
- `scripts/submit_diffusers_dataset_job.sh`
- `scripts/submit_openclaw_dataset_job.sh`
- `scripts/submit_transformers_analysis_job.sh`
- `scripts/submit_openclaw_analysis_job.sh`

For the current storage model and recommended modes, see
[`docs/data-architecture.md`](docs/data-architecture.md).

## Analyze a Hub dataset

You can analyze the published Hugging Face dataset directly without scraping GitHub again:

```bash
uv run slop-farmer analyze \                           
  --snapshot-dir eval_data/snapshots/gh-live-latest-1000x1000 \
  --ranking-backend hybrid \
  --model "gpt-5.4-mini?service_tier=flex" \
  --output /tmp/gh-live-latest-1000x1000-hybrid.json
```

This materializes the dataset-viewer parquet export into a local snapshot cache under
`eval_data/snapshots/` and writes a local analysis report next to it. Publishing
canonical hybrid analysis is a separate `publish-analysis-artifacts` step, and updating
the remote hybrid cache source is `publish-analysis-artifacts --save-cache` or
standalone `save-cache`.

Repo-local defaults for `analyze` can be stored in `pyproject.toml` under `[tool.slop-farmer.analyze]`. This repo currently defaults to:

- `dashboard-data.output-dir = "web/public/data"`

For repo-specific remote-first analysis, prefer a YAML config with `dataset_id`, e.g.:

```bash
uv run slop-farmer --config configs/openclaw.yaml analyze
```

## Cluster open PRs by code scope

You can also build holistic PR scope clusters from an existing snapshot:

```bash
uv run slop-farmer pr-scope \
  --snapshot-dir data/snapshots/20260324T150154Z
```

By default this writes `pr-scope-clusters.json` next to the snapshot.

## Merge duplicate PR clusters

List only the duplicate PR clusters that pass the mergeability gate:

```bash
uv run slop-farmer duplicate-prs list \
  --report eval_data/snapshots/gh-live-latest-1000x1000/analysis-report-hybrid.json
```

Then synthesize and publish one minimal upstream PR from the top-ranked mergeable cluster:

```bash
uv run slop-farmer duplicate-prs merge \
  --report eval_data/snapshots/gh-live-latest-1000x1000/analysis-report-hybrid.json \
  --repo-dir /path/to/transformers
```

If your local checkout uses a fork as `origin`, point the merge flow at the upstream remote explicitly and relax the file policy when needed:

```bash
uv run slop-farmer duplicate-prs merge \
  --report eval_data/snapshots/gh-live-latest-1000x1000/analysis-report-hybrid.json \
  --repo-dir /path/to/transformers \
  --upstream-repo huggingface/transformers \
  --upstream-remote upstream \
  --fork-repo YOURNAME/transformers-minimal \
  --fork-remote origin \
  --file-policy allow-docs
```

## Import a historical HF checkpoint as a clean local snapshot

If an older dataset keeps its richest data under `_checkpoints/<snapshot_id>/`,
you can promote one of those checkpoints into a normal local snapshot:

```bash
uv run slop-farmer import-hf-checkpoint \
  --source-repo-id burtenshaw/transformers-pr-slop-dataset \
  --output-dir eval_data
```

By default this selects the latest viable checkpoint, writes a clean snapshot
under `eval_data/snapshots/`, and regenerates `links.parquet`,
`issue_comments.parquet`, and `pr_comments.parquet`.

## Render markdown from an analysis JSON

You can turn an existing analysis report into a human-readable markdown file without rerunning clustering:

```bash
uv run slop-farmer markdown-report \
  --input eval_data/snapshots/hf-latest-100x100/analysis-report-hybrid.json
```

By default this writes `analysis-report-hybrid.md` next to the JSON and uses the JSON parent directory as the snapshot source for issue and PR titles, links, and latest-activity ordering.

## Render a new contributor report

You can also render a reviewer-facing markdown report for contributors who are still new to the repo snapshot:

```bash
uv run slop-farmer new-contributor-report \
  --snapshot-dir data/snapshots/20260324T000000Z
```

By default this writes:

- `new_contributors.parquet`
- `new-contributors-report.md`
- `new-contributors-report.json`

next to the snapshot, including GitHub profile links, repo issue/PR search links, and example authored artifacts.

## Recommended end-to-end sequence

For canonical upkeep, prefer the explicit sequence:

1. `refresh-dataset`
2. `analyze`
3. `publish-analysis-artifacts --save-cache`
4. `dashboard-data`
5. deploy dashboard and API if needed

## Validation checks

Before committing or wiring new package moves into automation, run:

```bash
uv run python scripts/enforce_packaging.py
uv run python scripts/check_hf_cli_secrets.py
uv run --extra dev ruff format --check src tests scripts jobs
uv run --extra dev ruff check src tests scripts jobs
uv run --extra dev ty check src tests scripts jobs
uv run --extra dev pytest -q
```

`scripts/enforce_packaging.py` verifies the coarse package boundaries:

- `data` must not import `app`
- `data` must not import `reports`
- `reports` must not import `app`

`scripts/check_hf_cli_secrets.py` rejects `hf ... --secrets NAME=value` so access
tokens cannot be exposed via process argv.

## YAML config-driven runs

You can keep repo-specific pipeline defaults in a YAML file and apply them to all
commands with `--config`.

Example: `configs/diffusers.yaml`

```yaml
repo: huggingface/diffusers
workspace: runs/diffusers
dataset_id: evalstate/diffusers-pr

pull-requests:
  template_cleanup:
    mode: merge_defaults
    line_patterns:
      - '^d(?:o not merge|ontmerge)\.?$'
  cluster_suppression_rules:
    - id: diffusers_post_release
      title_patterns:
        - '\bpost[- ]release\b'

dashboard:
  space_id: evalstate/diffusers-dashboard
  title: Diffusers Dashboard
  window_days: 60
  contributor_window_days: 60
  contributor_max_authors: 0

analysis:
  model: gpt-5.4-mini
  ranking_backend: hybrid
  cached_analysis: true

scrape:
  fetch-timeline: true
```

Then commands stay aligned without repeating repo/workspace/window settings:

```bash
uv run slop-farmer --config configs/diffusers.yaml refresh-dataset
uv run slop-farmer --config configs/diffusers.yaml analyze
uv run slop-farmer --config configs/diffusers.yaml pr-scope
uv run slop-farmer --config configs/diffusers.yaml pr-search refresh
uv run slop-farmer --config configs/diffusers.yaml new-contributor-report
uv run slop-farmer --config configs/diffusers.yaml dashboard-data
uv run slop-farmer --config configs/diffusers.yaml deploy-dashboard --refresh-contributors
uv run slop-farmer --config configs/diffusers.yaml dataset-status
```

Those reader commands default to `dataset_id` when configured. Pass `--snapshot-dir` to force
an explicit local snapshot instead.

`analysis-state/` is mutable operational cache only. You can upload it to the dataset
repo with `save-cache` or `publish-analysis-artifacts --save-cache`, but it is still not
the canonical analysis read surface.

## Export static dashboard data

You can export a slim JSON bundle for the React dashboard:

```bash
uv run slop-farmer dashboard-data \
  --snapshot-dir data/snapshots/20260324T150154Z \
  --output-dir web/public/data \
  --window-days 14
```

This writes:

- `summary.json`
- `clusters.json`
- `prs.json`
- `contributors.json`

The dashboard is intentionally summary-first and links out to GitHub for deep detail.

When `--analysis-input` is omitted, `dashboard-data` now prefers:

1. `analysis/current/manifest.json`
2. `analysis/current/analysis-report-hybrid.json`
3. snapshot-local fallback only when canonical current analysis is absent

If the canonical current manifest exists but the required artifact is missing, dashboard export
fails loudly instead of silently drifting to snapshot-local analysis.

## Deploy a dashboard to a Hugging Face Space

Use the generic deploy script:

```bash
SPACE_ID=evalstate/openclaw-pr-report \
PIPELINE_DATA_DIR=runs/openclaw/data \
SNAPSHOT_DIR=runs/openclaw/data/snapshots/20260324T233649Z \
SPACE_TITLE="OpenClaw PR Report" \
DATASET_ID=evalstate/openclaw-pr \
scripts/deploy_dashboard_space.sh
```

Repo-specific wrappers are also available:

- `scripts/deploy_transformers_dashboard_space.sh`
- `scripts/deploy_openclaw_dashboard_space.sh`

Or use the CLI wrapper with a YAML config:

```bash
uv run slop-farmer --config configs/diffusers.yaml deploy-dashboard --refresh-contributors
```

## Deploy the PR similarity API to a Hugging Face Docker Space

The repo includes the FastAPI service for the read-oriented PR similarity surface.
The standalone `pr-search` client now lives in the downstream `pr-search-cli`
package.

Repo-specific wrappers are available for the current deployed APIs:

```bash
scripts/update_diffusers_pr_search_api.sh
scripts/update_transformers_pr_search_api.sh
scripts/update_openclaw_pr_search_api.sh
```

Or use the generic deploy script directly:

```bash
SPACE_ID=evalstate/transformers-pr-api \
SPACE_TITLE="Transformers PR API" \
DEFAULT_REPO=huggingface/transformers \
GHR_BASE_URL=https://ghreplica.dutiful.dev \
HF_REPO_ID=evalstate/transformers-pr \
BUCKET_ID=evalstate/transformers-pr-api-data \
scripts/deploy_pr_search_space.sh
```

This deploy flow:

- creates or updates a Docker Space
- uploads a minimal app bundle with a generated Space `README.md`
- sets runtime variables for the API
- mounts the configured HF bucket at `/data` as mutable operational cache only

Serving defaults:

- dataset repo = canonical published state
- API materializes one self-consistent dataset view
- canonical `analysis/current/` is the default analysis surface when present
- archived analysis is selectable explicitly with `snapshot_id` + `analysis_id`

After the Space is live, you can query it either through the in-repo admin CLI:

```bash
uv run slop-farmer pr-search status --repo huggingface/transformers
uv run slop-farmer pr-search similar 44940 --repo huggingface/transformers
```

Or through the downstream `pr-search-cli` package, which owns the standalone
`pr-search` executable.

## Transformers migration cheat sheet

To move Transformers onto the current architecture:

### 1. Recreate the scheduled dataset refresh job with the generic wrapper

```bash
CONFIG_PATH=configs/transformers.yaml \
LABEL=transformers-dataset-refresh \
SCHEDULE='@daily' \
scripts/submit_transformers_dataset_job.sh
```

This is the canonical scheduled writer for raw/latest dataset state.

### 2. Run analysis and publish canonical hybrid analysis

```bash
MODE=run scripts/submit_transformers_analysis_job.sh
```

That sequence:

- refreshes the canonical dataset
- runs `analyze` with config-driven defaults
- publishes canonical `analysis/current/`
- saves repo-root `analysis-state/` for future hybrid cache reuse
- restarts the Transformers API Space so it materializes the newest published state

### 3. Deploy the Transformers API Space

```bash
scripts/update_transformers_pr_search_api.sh
```

Optional runtime bucket:

- default wrapper bucket id: `evalstate/transformers-pr-api-data`
- treat it as mutable operational cache only, not canonical published storage
