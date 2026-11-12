Good. Here’s the implementation checklist I’d use.

## Non-negotiable end-state

Before touching code, lock these rules in:

- **`refresh-dataset` is the only canonical writer for raw/latest dataset state**
- **`publish-analysis-artifacts` is the canonical writer for expensive published analysis**
- **dataset repo stores canonical published state**
- **bucket stores mutable operational state only**
- **`analysis-state/` is never published to the dataset repo**
- **`analysis/current/` is the stable canonical serving alias for the blessed hybrid analysis**
- **archived published analyses live under `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/`**
- **if canonical current-analysis files exist, they are authoritative for default serving**
- **if canonical current-analysis metadata exists but required files are missing, return 404 rather than silently falling back**
- **API reads one materialized snapshot view, not a second ad hoc analysis directory**
- **dataset materialization resolves one Hub revision/SHA and downloads a self-consistent view**
- **no `pr-search.meta.json` sidecar metadata if DuckDB already owns the truth**
- **late-published analysis updates the archived snapshot manifest for that snapshot**
- **bucket cache sync uses supported `hf buckets sync`, not custom sync logic**
- **Space volume management uses supported `hf spaces volumes` or `HfApi.set_space_volumes`, not raw HTTP**
- **remove legacy publish paths that blur these boundaries**

## Explicit deltas from `04-18-publish_approach.md`

This cleanup plan intentionally tightens two parts of the earlier approach:

- keep `analysis/current/` as the stable canonical serving alias, but back it with an explicit
  `manifest.json` and immutable archived analysis runs under
  `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/`
- replace the proposed `pr-search.meta.json` sidecar with DuckDB active-run metadata
  plus the remote `snapshots/latest.json` pointer

## Post-merge adjustments

The merge left the repo in a valid transitional state, but it clarified three cleanup items that
should now be explicit in this plan:

- **contributor artifacts are first-class published layout**, not incidental side outputs
- **materialized snapshots must carry contributor report artifacts as part of the canonical read
  surface**
- **the contributor contract is now intentionally split**, so cleanup should preserve that split:
  snapshot-backed contributor detail stays on `/contributors/{login}`, while indexed pull context
  stays on `/contributors/{login}/pulls` and `/pulls/{number}/contributor`

---

# Concrete implementation checklist

## 1. Canonicalize published-layout helpers in the existing snapshot path module family

### Canonical home
Prefer the existing path helper module:
- `src/slop_farmer/data/snapshot_paths.py`

If that file becomes unwieldy, split a sibling helper module under the same package
(`src/slop_farmer/data/`) rather than inventing a second competing place for layout rules.

### Move into it
All canonical filenames and repo-relative paths now hardcoded across:
- `src/slop_farmer/app/dataset_refresh.py`
- `src/slop_farmer/data/snapshot_materialize.py`
- `src/slop_farmer/reports/analysis_service.py`
- `src/slop_farmer/app/dataset_status.py`

### It should own
- raw table filenames
- viewer split filenames
- cheap artifact filenames
- expensive analysis filenames
- contributor artifact filenames (`new_contributors.parquet`,
  `new-contributors-report.json`, `new-contributors-report.md`)
- `snapshots/latest.json`
- `analysis/current/manifest.json`
- helpers:
  - `snapshot_artifact_path(snapshot_id, filename)`
  - `analysis_run_artifact_path(snapshot_id, analysis_id, filename)`
  - `current_analysis_artifact_path(filename)`
  - `repo_key(repo_slug)`
  - `model_key(model)`
- manifest schema helpers:
  - build/load/validate current-analysis manifest payload
  - build/load/validate archived analysis-run manifest payload

### Remove
- duplicated filename tuples
- duplicated path-building logic
- duplicated variant-to-filename maps

### Specific code to delete/move
- `ANALYSIS_REPORT_FILENAMES` from `reports/analysis_service.py`
- hardcoded artifact tuples in `snapshot_materialize.py`
- inline `artifacts = {...}` path strings in `dataset_refresh.py`

### Tests
Add:
- `tests/test_published_layout.py`

Should verify:
- exact canonical filenames
- snapshot path generation
- current-analysis manifest payload validity
- repo/model key normalization is stable and path-safe
- manifest schema versioning so future shape changes stay explicit

---

## 2. Make dataset materialization understand published analysis, not `analysis-state`

### Update
- `src/slop_farmer/data/snapshot_materialize.py`

### New behavior
When materializing a dataset repo, download:
- raw root tables
- `manifest.json`
- `state/watermark.json` if needed
- `snapshots/latest.json`
- cheap artifacts like `pr-scope-clusters.json`
- contributor artifacts:
  - `new_contributors.parquet`
  - `new-contributors-report.json`
  - `new-contributors-report.md`
- `analysis/current/manifest.json`
- canonical current-analysis files
- archived analysis-run manifests and artifacts needed for explicit run selection

### Consistency rule
Resolve the dataset repo to one concrete Hub revision/SHA up front and download all files for that
materialization from that resolved revision. Do not fetch `analysis/current/manifest.json` and
associated artifacts from a moving branch tip independently.

### Local materialized shape
Preserve repo-relative structure for published analysis:

```text
<local_snapshot>/
  manifest.json
  pr-scope-clusters.json
  analysis/
    current/
      manifest.json
      analysis-report-hybrid.json
      analysis-report-hybrid.llm-reviews.json
  snapshots/
    <snapshot_id>/
      analysis-runs/
        <analysis_id>/
          manifest.json
          analysis-report-hybrid.json
          analysis-report-hybrid.llm-reviews.json
```

### Remove
Dataset materialization of `analysis-state/`

### Delete from `snapshot_materialize.py`
- `_download_hf_analysis_state_files`
- `_hf_analysis_state_path_pairs`

### Why
`analysis-state/` is mutable cache, not canonical published data.

### Tests to update/remove
Remove or rewrite tests that expect dataset materialization to pull:
- `analysis-state/hybrid-review-cache-manifest.json`

Specifically update:
- `tests/test_analysis.py`
  - the materialization tests around remote `analysis-state`
- replace them with tests for:
  - `analysis/current/manifest.json`
  - canonical current-analysis file download
  - archived run manifest/artifact download

---

## 3. Simplify analysis serving to one source of truth

### Update
- `src/slop_farmer/reports/analysis_service.py`

### New serving order
For a materialized snapshot:
1. if no explicit historical run is requested, look for `analysis/current/manifest.json`
2. serve canonical current hybrid artifacts from `analysis/current/`
3. if the canonical manifest exists but required files are missing, return 404
4. if `snapshot_id` + `analysis_id` are requested, resolve
   `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/`
5. if no canonical current analysis exists, fall back to active snapshot-local report files
6. otherwise unavailable

### Remove
The separate `analysis_root` / `owner/name/current` tree logic

### Delete/simplify
- `analysis_root` parameter from:
  - `get_analysis_status`
  - `get_pr_analysis`
  - `list_analysis_meta_bugs`
  - `get_analysis_meta_bug`
  - `list_analysis_duplicate_prs`
  - `get_analysis_best`
- add optional `snapshot_id` / `analysis_id` selectors to the analysis-service entrypoints so
  callers can request an archived run explicitly instead of the canonical current alias
- `_candidate_analysis_dirs(...)` should be replaced by explicit:
  - canonical current-analysis lookup
  - archived run lookup
  - snapshot-local fallback

### Expected result
The service becomes inspectable:
- active snapshot dir
- published canonical current-analysis alias
- archived analysis-run directories
- snapshot fallback

No second analysis location to reason about.
Broken published current-analysis state fails loudly instead of being masked by snapshot-local
files.

### Tests
Update:
- `tests/test_pr_search_api.py`

Remove:
- `test_pr_search_api_analysis_prefers_current_bucket_style_artifacts`

Replace with:
- a test that materialized `analysis/current/` wins over snapshot-local
- a test that archived `snapshot_id` + `analysis_id` lookup resolves correctly
- a test that snapshot-local still works when canonical current analysis is absent
- a test that missing canonical current files return 404 cleanly with no snapshot-local fallback

---

## 4. Remove `analysis_dir` from the API completely

### Update
- `src/slop_farmer/app/pr_search_api.py`
- `scripts/deploy_pr_search_space.sh`
- README deploy docs

### Status
- `PrSearchApiSettings.analysis_dir` removed
- `ANALYSIS_DIR` env handling removed from the API
- API analysis routes no longer pass `analysis_root`
- `test_pr_search_api_analysis_prefers_current_bucket_style_artifacts` removed
- contributor detail route remains snapshot-backed only

Remaining work in this step is to finish the serving-model cleanup underneath the API
(`analysis_service.py`) and keep docs aligned with the new contract.

### Remove
From `PrSearchApiSettings`:
- `analysis_dir`

From env handling:
- `ANALYSIS_DIR`

From API calls:
- passing `analysis_root=settings.analysis_dir`

### Add
Optional query parameters on analysis endpoints:
- `snapshot_id`
- `analysis_id`

### Contributor endpoint contract
Adopt the split contract explicitly:

- report-backed surface:
  - `/contributors/status`
  - `/contributors`
  - `/contributors/{login}`
  - `/contributors/{login}/risk`
- indexed pull-context surface:
  - `/contributors/{login}/pulls`
  - `/pulls/{number}/contributor`

`/contributors/{login}` should remain purely materialized-snapshot backed.
Do not reintroduce a merge shim that stitches indexed pull context into that route.

Default behavior stays simple:
- no explicit ids => serve canonical current hybrid analysis
- explicit ids => resolve archived run `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/`

### Why
The API should read the currently materialized dataset view, not a second independently-managed analysis tree.

### Space deployment note
`scripts/deploy_pr_search_space.sh` should stop using raw HTTP volume configuration now that the
latest HF CLI supports:

```bash
hf spaces volumes set "$SPACE_ID" -v "hf://buckets/$BUCKET_ID:$VOLUME_MOUNT_PATH"
hf spaces volumes ls "$SPACE_ID"
```

If the script stays in Python for this piece, use `HfApi.set_space_volumes(...)`, not a private HTTP
call. Remember that `set` replaces the full mounted-volume list, so the script must own the desired
final volume configuration.

### Tests
Update API startup/config tests accordingly.

---

## 5. Add an explicit `publish-analysis-artifacts` command

### Add
- `src/slop_farmer/app/publish_analysis.py`
- new CLI command in `src/slop_farmer/app/cli.py`
- new options type in `src/slop_farmer/config.py`

Suggested dataclass:
- `PublishAnalysisArtifactsOptions`

### Command responsibility
Given a snapshot dir:
- validate manifest/snapshot id
- require `analysis_id`
- discover available hybrid analysis outputs
- upload an immutable archived run to:
  - `snapshots/<snapshot_id>/analysis-runs/<analysis_id>/...`
- if `--canonical` is set, write/update:
  - `analysis/current/manifest.json`
  - `analysis/current/analysis-report-hybrid.json`
  - `analysis/current/analysis-report-hybrid.llm-reviews.json`
- update the archived snapshot manifest at:
  - `snapshots/<snapshot_id>/manifest.json`

### Manifest semantics
Late-published expensive analysis should be reflected in the archived manifest for the
snapshot it belongs to.

- update `snapshots/<snapshot_id>/manifest.json` so it records published analysis runs for that
  snapshot and which archived run, if any, is currently blessed as canonical
- do **not** rewrite root raw tables
- do **not** treat the root `manifest.json` as the source of truth for late-published
  analysis attached to an older snapshot

### Current canonical manifest
Use a stable current alias with explicit metadata:

```json
{
  "schema_version": 1,
  "repo": "openclaw/openclaw",
  "snapshot_id": "20260418T120000Z",
  "analysis_id": "hybrid-gpt54mini-v3",
  "variant": "hybrid",
  "channel": "canonical",
  "model": "gpt-5.4-mini",
  "published_at": "2026-04-18T12:34:56Z",
  "artifacts": {
    "hybrid": "analysis/current/analysis-report-hybrid.json",
    "hybrid_reviews": "analysis/current/analysis-report-hybrid.llm-reviews.json"
  },
  "archived_artifacts": {
    "hybrid": "snapshots/20260418T120000Z/analysis-runs/hybrid-gpt54mini-v3/analysis-report-hybrid.json",
    "hybrid_reviews": "snapshots/20260418T120000Z/analysis-runs/hybrid-gpt54mini-v3/analysis-report-hybrid.llm-reviews.json"
  }
}
```

### Archived run manifest
Each immutable archived run gets its own manifest:

```json
{
  "schema_version": 1,
  "repo": "openclaw/openclaw",
  "snapshot_id": "20260418T120000Z",
  "analysis_id": "hybrid-gpt54mini-v3",
  "variant": "hybrid",
  "channel": "canonical",
  "model": "gpt-5.4-mini",
  "published_at": "2026-04-18T12:34:56Z",
  "artifacts": {
    "hybrid": "snapshots/20260418T120000Z/analysis-runs/hybrid-gpt54mini-v3/analysis-report-hybrid.json",
    "hybrid_reviews": "snapshots/20260418T120000Z/analysis-runs/hybrid-gpt54mini-v3/analysis-report-hybrid.llm-reviews.json"
  }
}
```

### Publisher rules
- publish only files that exist
- never upload `analysis-state/`
- never rewrite root raw tables
- never re-upload whole snapshot folders just to publish analysis
- `--canonical` updates the stable `analysis/current/` alias
- comparison publishes archive under `analysis-runs/<analysis_id>/` without touching current

### Use Hub APIs explicitly
Do **not** implement this as a sequence of `upload_file` or `hf upload` calls. The canonical
publisher should create **one atomic Hub commit** containing:

- archived analysis-run additions/updates
- canonical `analysis/current/` files when `--canonical` is set
- archived snapshot manifest update

Use `HfApi.create_commit(...)` with explicit commit operations for the real command path.

Notes:
- `upload_folder` is wrong here because it republishes too much state.
- sequential `upload_file` calls are wrong because they can expose a broken intermediate state.
- `hf upload` remains useful for manual repair or one-off operator backfills, but not for the
  canonical publisher implementation.

### Alias tradeoff
This plan intentionally keeps a duplicated stable current alias because the product mental model is
that there is one blessed “current hybrid analysis” used for serving. The cost is some duplicated
published paths; the benefit is a one-step fetch contract for the API, sibling CLI, and operators.

### Tests
Add:
- `tests/test_publish_analysis.py`

Should cover:
- hybrid publish
- archived run publish
- comparison-run publish without `--canonical`
- canonical current alias update
- archived manifest update
- missing optional llm reviews
- no accidental `analysis-state` upload

---

## Cleanup scope adjustment

Steps 6–8 are still cleanup, but steps 6–7 are no longer purely optional follow-up. If the new
published-analysis model lands while `publish-snapshot` and `scrape --publish` still work, the
codebase still has multiple canonical-writing paths. That keeps the storage model ambiguous.

So:

- steps **1–5, 6–7, 9–12** belong in the first wave, or
- steps **6–7** must at least be hard-deprecated so they cannot publish the legacy mixed model

Step 8 (`full-pipeline`) can remain follow-up if needed.

## 6. Replace whole-folder publishing with explicit canonical publishing

This is important cleanup.

### Current confusing area
`src/slop_farmer/app/publish.py` uploads an arbitrary snapshot directory wholesale.

That conflicts with the new model because it can publish:
- `analysis-state/`
- other local-only clutter
- anything else sitting in the snapshot dir

### Decision
Do **not** keep a generic “upload whatever is in this folder” publisher as a public command.

### Replace with
If checkpoint import still needs publish support:
- create an internal helper like:
  - `src/slop_farmer/app/publish_dataset_snapshot.py`
- make it publish only the canonical dataset layout

### Remove
Public CLI command:
- `publish-snapshot`

### Delete/update
- `src/slop_farmer/app/publish.py`
- `tests/test_publish.py`
- `publish-snapshot` parser/runner/defaults from:
  - `src/slop_farmer/app/cli.py`
  - `src/slop_farmer/app_config.py`
  - `tests/test_config.py`

### If needed for checkpoint import
Update:
- `src/slop_farmer/app/hf_checkpoint_import.py`

So it uses the new explicit canonical dataset publisher helper, not whole-folder upload.

---

## 7. Remove `scrape --publish`

### Current problem
This creates a second canonical-writing path and makes the codebase harder to reason about.

### Decision
`scrape` becomes local-only.
Canonical publication lives in:
- `refresh-dataset`
- `publish-analysis-artifacts`

### Update
- `src/slop_farmer/app/cli.py`
- `src/slop_farmer/config.py`
- `src/slop_farmer/app/pipeline.py`
- tests
- docs
- scripts

### Remove
- `--publish` from `scrape`
- `--hf-repo-id` / private publish args from `scrape` if only used for publish
- `PipelineOptions.publish`
- dataset publication logic from `run_pipeline`

### Update scripts that still use it
These currently need rewriting:
- `scripts/update_transformers_dashboard.sh`
- `scripts/update_diffusers_dashboard.sh`

Rewrite to use the explicit sequence:
1. `refresh-dataset`
2. `analyze`
3. `publish-analysis-artifacts`
4. `dashboard-data`
5. deploy if needed

### Tests
Update:
- `tests/test_pipeline_checkpoint_resume.py`
- CLI/config tests for removed flags

---

## 8. Remove `full-pipeline` unless there is a real external consumer

### Why
It mixes:
- scrape
- publish
- analyze
- markdown
- dashboard export

That hides responsibilities and duplicates the canonical job model.

### In-tree usage check
Current in-repo references are basically:
- docs
- `src/slop_farmer/app/workflow.py`
- CLI wiring

If there is no real automation consumer, remove it.

### Remove
- `full-pipeline` command
- `src/slop_farmer/app/workflow.py`
- `FullPipelineOptions` from `config.py`
- defaults from `app_config.py`
- CLI wiring/tests/docs

### If you must keep it
Then strip all publication semantics out of it and make it a local orchestration helper only.

But my recommendation is: **delete it**.

---

## 9. Keep hybrid cache sync outside report code

### Do not add bucket logic to
- `src/slop_farmer/reports/analysis.py`
- `src/slop_farmer/reports/analysis_cache.py`

### Keep those modules local-only
They should only read/write:
- local snapshot
- local `analysis-state/`

### Add instead
A thin wrapper script for operational use, e.g.
- `scripts/run_analysis_with_bucket_cache.sh`

### Script responsibilities
- compute canonical bucket prefix using shared Python helpers
- sync bucket cache prefix down to local `analysis-state/`
- run:
  - `analyze`
  - `publish-analysis-artifacts`
- sync updated `analysis-state/` back up

### Preferred implementation
Use the supported CLI directly:

```bash
hf buckets sync "hf://buckets/$BUCKET_ID/$PREFIX" "$SNAPSHOT_DIR/analysis-state"
hf buckets sync "$SNAPSHOT_DIR/analysis-state" "hf://buckets/$BUCKET_ID/$PREFIX"
```

For destructive reconciliation, prefer a reviewed plan/apply flow:

```bash
hf buckets sync "$SNAPSHOT_DIR/analysis-state" "hf://buckets/$BUCKET_ID/$PREFIX" --plan sync-plan.jsonl
hf buckets sync --apply sync-plan.jsonl
```

Default to **no `--delete`** unless you explicitly want mirror semantics. Buckets are mutable and
non-versioned, so accidental deletes are real deletes.

### Bucket path convention
Use the shared key helpers from `published_layout.py`:
- `analysis-cache/<repo_key>/<variant>/<model_key>/`

### Cache compatibility note
Cache identity is not the same as published analysis identity. The bucket prefix or local manifest
for cache reuse should encode any inputs that materially affect hybrid review reuse, such as:

- model
- prompt/review schema version
- template-cleanup rules version
- any clustering policy version that changes review-unit semantics

Published `analysis_id` identifies a run for provenance and comparison. Cache keys identify
compatibility for reuse. Multiple published runs may legitimately reuse the same cache.

### Why script, not Python command
It keeps HF bucket mechanics out of core application code.

### Docs
Document this as the operational path for expensive analysis jobs.

---

## 10. Add API staleness check using DuckDB + remote latest snapshot only

### Update
- `src/slop_farmer/app/pr_search_api.py`
- possibly small helper in:
  - `src/slop_farmer/data/hf_dataset_repo.py`

### Logic
If `hf_repo_id` is configured:
- read active run from DuckDB
- read remote `snapshots/latest.json`
- compare snapshot ids
- rebuild if different

### Do not add
- `pr-search.meta.json`

### Why
This intentionally replaces the earlier `pr-search.meta.json` idea. DuckDB already stores
the active run and snapshot identity.

### Tests
Add:
- stale index triggers rebuild when snapshot id changed
- no rebuild when ids match
- missing remote latest pointer degrades cleanly

---

## 11. Tighten `dataset-status` to reflect the new model

### Update
- `src/slop_farmer/app/dataset_status.py`

### Add reporting for
- `analysis/current/manifest.json` presence
- which snapshot and `analysis_id` the canonical current analysis represents
- whether that differs from remote latest snapshot
- whether archived runs exist for the current snapshot
- cheap artifact presence
- no mention of `analysis-state` as published data

### Remove
Any lingering assumptions that contributor/artifact presence is inferred only from root or old layout quirks if layout helper can resolve it centrally.

---

## 12. Rewrite docs so the model is unambiguous

### Update
- `README.md`
- `docs/data-architecture.md`
- possibly `docs/pr-scope-clustering.md`
- any deploy/runbook docs
- remove/replace plan references if they contradict reality

### Remove from docs
- `scrape --publish`
- `publish-snapshot`
- statements implying `analysis-state/` gets uploaded as canonical data
- API `ANALYSIS_DIR` style dual-location explanation
- bucket described as “scratch only” if it now holds durable mutable operational cache

### Replace with
Clear model:

- **dataset repo = canonical published state**
- **bucket = mutable operational cache/state**
- **Space disk = ephemeral**
- **refresh-dataset = canonical raw + cheap artifacts**
- **publish-analysis-artifacts = canonical expensive analysis**
- **analyze = local/materialized computation**
- **bucket wrapper = hybrid cache persistence**

---

# Explicit deletion checklist

These are the code paths I would actively try to remove, not preserve.

Items tied to step 8 are follow-up cleanup. Items tied to steps 6–7 should be removed in the
first wave or hard-deprecated so they cannot publish the legacy mixed model.

## Remove outright
- `publish-snapshot` CLI command
- `src/slop_farmer/app/publish.py`
- `tests/test_publish.py`
- `scrape --publish`
- whole-folder snapshot upload as a public behavior
- API `analysis_dir` / `ANALYSIS_DIR`
- materialized dataset download of `analysis-state/`
- `pr-search.meta.json` idea before it lands
- `full-pipeline` and `src/slop_farmer/app/workflow.py` if no real external consumer

## Remove if unused after rewrites
- repo-specific scripts that only wrap now-obsolete publish flows
- config defaults for deleted commands
- docs sections describing manual publish backfill as normal workflow

---

# Order of implementation

Do it in this order to avoid churn.

## Phase 1
- published layout module
- refactor constants/path builders to use it

## Phase 2
- materializer update
- analysis service update
- API remove `analysis_dir`

## Phase 3
- implement `publish-analysis-artifacts`
- tests for canonical alias + archived-run publishing

## Phase 4
- remove or hard-deprecate legacy publish paths:
  - `publish-snapshot`
  - `scrape --publish`
- rewrite scripts that still rely on them

## Phase 5
- stale index check via DuckDB + remote latest pointer

## Phase 6
- bucket cache wrapper script
- docs for operational analysis job

## Phase 7 (follow-up cleanup)
- maybe delete `full-pipeline`

## Phase 8 (follow-up cleanup)
- docs cleanup
- config/tests/script cleanup
- run full validation

---

# First-wave definition of done

The first implementation wave is done when all of these are true:

- there is exactly **one** canonical raw-data writer: `refresh-dataset`
- there is exactly **one** canonical expensive-analysis publisher: `publish-analysis-artifacts`
- the dataset repo contains no published `analysis-state/`
- `analysis/current/` is the stable canonical serving alias for hybrid analysis
- canonical current analysis records both `snapshot_id` and `analysis_id`
- dataset materialization is pinned to one resolved Hub revision/SHA per run
- if canonical current-analysis metadata exists and required files are missing, the API returns 404
- the API reads from one materialized snapshot view only
- there is no second “current analysis directory” concept in the API
- there is no DuckDB sidecar metadata duplicating run identity
- archived snapshot manifests are updated when expensive analysis is published later
- bucket cache sync is documented around `hf buckets sync`
- Space volume management no longer relies on raw HTTP
- `publish-snapshot` and `scrape --publish` are removed or hard-error deprecated
- docs describe one coherent storage model

## Follow-up cleanup definition of done

The cleanup follow-up is done when all of these are also true:

- there is no whole-folder public publish command
- there is no `scrape --publish`
- obsolete codepaths are deleted, not merely ignored

If you want, I can next turn this into a **PR-by-PR execution plan with exact file diffs per PR**.
