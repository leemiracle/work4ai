# Reorg 1: coarse package split, boundary cleanup, and snapshot-path consolidation

## Context

The codebase now passes:

- `ruff format --check`
- `ruff check`
- `ty check`

but top-level package navigation is still noisy. `src/slop_farmer/` currently mixes:

- CLI/app wiring
- config/default parsing and shared option types
- GitHub/network/data ingestion
- snapshot/materialization/storage helpers
- analysis/report/dashboard logic
- duplicate-PR synthesis/orchestration

There are also duplicated snapshot-resolution helpers and at least one thin adapter that should be removed rather than preserved.

This project is unpublished and has **no backward-compatibility constraints**, so we should optimize for clarity, directness, and future maintenance rather than import stability.

## Goals

1. Make `src/slop_farmer/` navigable at a glance.
2. Group modules by coarse responsibility, not by micro-domain.
3. Eliminate repeated snapshot path resolution logic.
4. Remove thin wrapper APIs that do not add meaning.
5. Keep the split intentionally shallow: **3 subpackages max**.
6. Fix current layer boundaries **before** moving files so the package split reflects real responsibilities.

## Working rules for implementation

These are execution rules for the refactor itself:

1. **Boundary cleanup before moves.**
   - Do not start by relocating files.
   - First fix shared helpers, private cross-module imports, and mixed-responsibility seams.
2. **Small, phase-aligned commits.**
   - Each commit should leave the repo usable.
   - Prefer one commit per coherent step, not one giant churn commit.
3. **Move + import rewrite together.**
   - Do not create a broken intermediate state where files move in one commit and imports are fixed later.
4. **Change CLI/script entrypoints late.**
   - Update `pyproject.toml` script targets only after package moves and import rewrites are stable.
5. **Move resources with their owning module.**
   - Prompts, schemas, and templates should move in the same phase as the code that loads them.
6. **Keep each phase green.**
   - Run checks after every phase, not only at the end.
7. **Do not force cosmetic top-level purity.**
   - If one tiny shared top-level module remains useful, keep it.
   - Honest dependencies matter more than an artificially empty package root.

## Non-goals

- preserving old import paths
- preserving existing internal module layout
- building an elaborate compatibility shim layer
- introducing many tiny subpackages
- broad behavior changes unrelated to structure

## Key design corrections before moving files

The previous version of this reorg plan was directionally right but too optimistic about a few modules. In particular:

- `config.py` is currently both:
  - CLI/config-file/default parsing, and
  - shared option dataclasses / repo refs / token helpers
- `pipeline.py` is not a pure data-layer module; it orchestrates downstream behavior
- `hf_checkpoint_import.py` is not obviously pure data either
- `duplicate_prs.py` mixes:
  - report/gating logic, and
  - app/repo mutation/publish orchestration
- `pr_scope.py` still reaches into private `analysis.py` helpers

So this reorg should be:

1. **boundary cleanup first**
2. **package move second**

not just a bulk file relocation.

## Proposed package structure

### `slop_farmer.app`

Purpose: command entrypoints, orchestration, mutation of external systems, and user-facing wiring.

Planned contents:

- `cli.py`
- `workflow.py`
- `deploy.py`
- `publish.py`
- `snapshot_state.py`
- duplicate-PR merge/publish orchestration module
- possibly `pipeline.py` unless it is split first
- possibly `hf_checkpoint_import.py` unless it is split first
- app-side config/default loading module

Why:

- these modules are mostly about command execution and application flow
- they are the least reusable “core logic” pieces
- repo mutation and PR publication belong here, not in reports

### `slop_farmer.data`

Purpose: fetch, normalize, materialize, load, and persist repository snapshot data.

Planned contents:

- `http.py`
- `github_api.py`
- `normalize.py`
- `links.py`
- `parquet_io.py`
- new shared snapshot/path helper module
- any pure snapshot loading/materialization helpers extracted during cleanup

Why:

- these modules form the extraction/materialization substrate
- they deal with GitHub payloads, parquet rows, snapshots, and IO
- they should not depend on reports or app orchestration

### `slop_farmer.reports`

Purpose: analysis, reviewer-facing reporting, and post-snapshot interpretation.

Planned contents:

- `analysis.py`
- `analysis_cache.py`
- `dashboard.py`
- `new_contributor_report.py`
- `user_activity.py`
- `canonical_duplicate_pr.py`
- `pr_scope.py`
- `pr_heuristics.py`
- duplicate-PR analysis/gating logic if split from orchestration
- prompt/schema resources associated with report logic

Why:

- these modules consume snapshot data to derive higher-level outputs
- they are conceptually downstream from `data`
- they are what a maintainer will browse for report logic and review heuristics

## Top-level package after reorg

`src/slop_farmer/` should become minimal:

- `__init__.py`
- `app/`
- `data/`
- `reports/`

Optional:

- one tiny shared top-level module **only if it clearly serves all packages**

Examples of acceptable top-level shared modules if needed:

- `shared_types.py`
- `auth.py`

But avoid recreating the current clutter at the top level.

If report resources remain package-local, move them alongside the report package, e.g.:

- `reports/prompts/`
- `reports/schemas/`

## Structural changes

### 1. Split shared config/types from CLI/default parsing

Do **not** move the current `config.py` wholesale into `app`.

Reason:

- `data` and `reports` both currently depend on shared option dataclasses and helpers
- if all of `config.py` moves to `app`, that creates `data -> app` and `reports -> app` coupling
- that conflicts with the intended dependency direction

Recommended split:

- app-side config/default parsing module:
  - pyproject defaults
  - YAML config loading
  - CLI config extraction
- shared types/helpers module:
  - option dataclasses
  - `RepoRef`
  - token/auth helpers if still broadly used

Possible shapes:

- `slop_farmer.app.config`
- `slop_farmer.shared_types` and/or `slop_farmer.auth`

Exact naming is less important than keeping shared types out of `app`.

### 2. Consolidate snapshot path resolution

We currently have multiple copies of snapshot resolution logic:

- `analysis._resolve_snapshot_dir`
- `dashboard._resolve_snapshot_dir`
- `new_contributor_report._resolve_snapshot_dir`
- `publish._resolve_snapshot_dir`
- indirect reuse through `pr_scope`

These should be replaced by one shared helper module in `slop_farmer.data`.

Recommended new module:

- `slop_farmer.data.snapshot_paths`

Recommended functions:

- `resolve_snapshot_dir_from_output(output_dir: Path, snapshot_dir: Path | None) -> Path`
- `load_latest_snapshot_pointer(output_dir: Path) -> Path | None`

Guideline:

- keep the helpers **path-focused**, not option-object-focused, where possible
- avoid writing a giant options-driven utility that recreates module coupling

Preferred shape:

```py
def resolve_snapshot_dir_from_output(output_dir: Path, snapshot_dir: Path | None) -> Path: ...
```

and callers adapt locally from their options object.

This keeps the shared function simple and reusable.

### 3. Extract shared snapshot loading helpers before moving report modules

`pr_scope.py` currently imports private helpers from `analysis.py`.

That coupling should be removed before broad package moves.

Plan:

- extract shared snapshot loading/path behavior into `data`
- make `pr_scope` depend on that shared helper instead of `analysis._...`

Reason:

- moving files without fixing this would preserve a bad cross-package private import

### 4. Remove `build_pr_scope_clusters_from_snapshot`

This currently looks like an unnecessary adapter:

```py
build_pr_scope_clusters_from_snapshot(snapshot)
-> build_pr_scope_clusters(snapshot.pull_requests, snapshot.pr_files, ...)
```

That is an antipattern here because:

- it adds another near-duplicate API surface
- it does not encapsulate meaningful behavior
- it makes navigation slightly worse by pretending two entrypoints are needed

Plan:

- delete `build_pr_scope_clusters_from_snapshot`
- call `build_pr_scope_clusters(snapshot.pull_requests, snapshot.pr_files, ...)` directly

If a snapshot-shaped adapter is ever needed later, reintroduce it only if it earns its existence.

### 5. Split duplicate-PR analysis from duplicate-PR orchestration

The new duplicate-PR feature makes current layering problems explicit.

Today `duplicate_prs.py` mixes:

- hybrid report resolution
- mergeability gating
- cluster packet construction
- git worktree creation
- Codex execution
- branch validation
- fork remote management
- `gh pr create`

That should not move as one lump without thought.

Recommended split:

- **reports-side duplicate-PR logic**
  - ensure/load hybrid report
  - select mergeable duplicate clusters
  - assess mergeability
  - build packets used for gating
- **app-side duplicate-PR orchestration**
  - stage run bundle
  - create worktree
  - invoke Codex
  - validate branch constraints
  - push and open PR

If the split feels too large for this reorg, then place `duplicate_prs.py` in `app` temporarily and schedule a follow-up split.

But do not pretend it is a pure report module.

### 6. Reassess `pipeline.py` and `hf_checkpoint_import.py` before classifying them as `data`

These modules should not be moved into `data` merely because they touch snapshots.

Questions to answer first:

- do they only materialize/load/persist data?
- or do they orchestrate downstream publishing/report steps?

If they orchestrate:

- they belong in `app`, or
- they should be split into pure data helpers plus app orchestration

Rule:

- `data` should be boring and reusable
- if a module coordinates multiple higher-level steps, it is probably `app`

### 7. Audit other thin wrappers while moving files

Likely acceptable to keep:

- `run_analysis`
- `run_pipeline`
- `run_dashboard_data`
- `run_new_contributor_report`
- `run_publish_snapshot`
- `run_deploy_dashboard`

These are useful module-level command entrypoints.

Possible simplification candidates:

- `canonical_duplicate_pr._build_github_client`
- any remaining `_resolve_snapshot_dir` wrappers after centralization

Rule:

- keep wrappers that define a module boundary
- remove wrappers that just rename a single call with no policy/value added

## Import policy after reorg

Keep imports directional:

- `app` may import from `data` and `reports`
- `reports` may import from `data`
- shared top-level pure modules may be imported by all
- `data` should not import from `reports`
- `data` should not import from `app`
- `reports` should not import from `app`

This avoids cycles and makes responsibilities obvious.

## Practical dependency direction

- `app` -> `data`
- `app` -> `reports`
- `reports` -> `data`
- shared pure modules -> imported by all as needed
- never `data` -> `reports`
- never `data` -> `app`
- never `reports` -> `app`

## Migration plan

### Phase 0: stabilize current behavior

Before moving files:

1. run:
   - `uv run --extra dev ruff format --check src tests scripts jobs`
   - `uv run --extra dev ruff check src tests scripts jobs`
   - `uv run --extra dev ty check src tests scripts jobs`
   - `uv run --extra dev pytest -q`
2. fix any current failures first

Reason:

- structural work is much easier when the baseline is green
- each later phase should be compared to a known-good baseline

### Phase 1: boundary cleanup before package moves

Do these before moving modules:

1. split config/default parsing from shared types/helpers
2. add shared snapshot path helpers in `data`
3. extract any shared snapshot loading helpers needed by both `analysis` and `pr_scope`
4. stop `pr_scope` importing private `analysis` helpers
5. decide the target shape for:
   - `duplicate_prs.py`
   - `pipeline.py`
   - `hf_checkpoint_import.py`

This is the most important correction to the earlier plan.

Commit guideline for this phase:

- split large cleanup into small commits
- for example:
  - shared snapshot-path helpers
  - pr-scope import cleanup
  - config/type split
  - duplicate-PR reclassification or split

### Phase 2: add the new package directories

Create:

- `src/slop_farmer/app/__init__.py`
- `src/slop_farmer/data/__init__.py`
- `src/slop_farmer/reports/__init__.py`

Do not move everything at once without package scaffolding.

### Phase 3: centralize shared snapshot resolution

Create a new shared module in `slop_farmer.data`, for example:

- `src/slop_farmer/data/snapshot_paths.py`

Move the common resolution behavior there first.

Update these callers:

- analysis
- dashboard
- new contributor report
- publish
- pr scope
- any other snapshot-oriented command that should reuse the same policy

This should happen **before** broad module moves so imports get simpler, not harder.

### Phase 4: move pure `data` modules

Move only modules that are actually data-layer after cleanup:

- `http.py` -> `data/http.py`
- `github_api.py` -> `data/github_api.py`
- `normalize.py` -> `data/normalize.py`
- `links.py` -> `data/links.py`
- `parquet_io.py` -> `data/parquet_io.py`
- any extracted snapshot loading/path helpers -> `data/...`

Then update imports across:

- app
- reports
- tests
- scripts

Expected benefit:

- lower-level implementation imports now come from a single subtree

### Phase 5: move `reports` modules

Move:

- `analysis.py` -> `reports/analysis.py`
- `analysis_cache.py` -> `reports/analysis_cache.py`
- `dashboard.py` -> `reports/dashboard.py`
- `new_contributor_report.py` -> `reports/new_contributor_report.py`
- `user_activity.py` -> `reports/user_activity.py`
- `canonical_duplicate_pr.py` -> `reports/canonical_duplicate_pr.py`
- `pr_scope.py` -> `reports/pr_scope.py`
- `pr_heuristics.py` -> `reports/pr_heuristics.py`
- duplicate-PR report/gating logic module if split

During this phase:

- remove `build_pr_scope_clusters_from_snapshot`
- update report imports to use explicit `data.*` dependencies
- move prompt/schema resources with their owning report logic if appropriate

### Phase 6: move `app` modules

Move:

- `cli.py` -> `app/cli.py`
- `workflow.py` -> `app/workflow.py`
- `deploy.py` -> `app/deploy.py`
- `publish.py` -> `app/publish.py`
- `snapshot_state.py` -> `app/snapshot_state.py`
- duplicate-PR orchestration module -> `app/...`
- app-side config/default parsing module -> `app/...`
- `pipeline.py` and `hf_checkpoint_import.py` only if they still classify as app/orchestration

Then update:

- `pyproject.toml` script target
- any direct imports in tests/scripts

Do this only after source moves and import rewrites are already passing checks.

Likely script target update:

```toml
[project.scripts]
slop-farmer = "slop_farmer.app.cli:main"
```

### Phase 7: shrink top-level package

After import updates are complete:

- delete the old top-level module files
- keep only package directories and any deliberately shared tiny top-level modules

Do **not** leave compatibility re-export stubs unless they materially help the refactor.

Given zero compatibility requirements, prefer a clean cut.

## Specific cleanup tasks during the move

### A. Replace option-coupled helpers with path-focused helpers

Bad pattern:

```py
_resolve_snapshot_dir(options)
```

Preferred:

```py
resolve_snapshot_dir_from_output(output_dir, snapshot_dir)
```

Then each command module can do the tiny options-to-path translation itself.

### B. Prefer direct calls over pass-through wrappers

Example:

- remove `build_pr_scope_clusters_from_snapshot`
- directly call `build_pr_scope_clusters(snapshot.pull_requests, snapshot.pr_files, ...)`

### C. Keep `run_*` command boundaries

These are good:

- `run_analysis`
- `run_pipeline`
- `run_dashboard_data`
- `run_new_contributor_report`

They give modules one obvious command entrypoint.

### D. Reassess `workflow.py`

`workflow.py` is a true orchestration layer and should likely stay as a coarse app module rather than being expanded.

No need to split it further unless it becomes much larger.

## Risks

### Import churn

This will touch many files:

- source modules
- tests
- scripts
- `pyproject.toml`

Mitigation:

- do the move in package-sized phases
- run full checks after each phase
- avoid broad opportunistic cleanup in the same commit as structural moves

### Hidden cyclic imports

Likely hotspots:

- config/types placement
- pipeline/orchestration modules
- report modules reaching into app-level code
- duplicate-PR code if not split cleanly

Mitigation:

- enforce the dependency direction above
- move shared pure helpers to `data` or a tiny shared top-level module if needed
- do the boundary cleanup before mass moves

### Script breakage

Shell/Python scripts may import old top-level modules directly.

Mitigation:

- grep for `from slop_farmer...`
- update scripts in the same phase as moves

### Resource path breakage

Prompt/schema/template resources may break if their owning module moves but resource paths do not.

Mitigation:

- move prompts/schemas alongside the owning module
- update tests that assert those resource paths
- do not defer resource path fixes to a later commit

## Suggested execution sequence

1. get the baseline green
2. split shared config/types from app config/default parsing
3. add package directories
4. add shared snapshot path helper
5. extract shared snapshot loading helpers used by both analysis and pr-scope
6. update callers to use the shared helper
7. decide and, if practical, split `duplicate_prs.py`
8. reclassify `pipeline.py` / `hf_checkpoint_import.py` based on actual responsibility
9. move pure `data/*`
10. move `reports/*`
11. remove `build_pr_scope_clusters_from_snapshot`
12. move `app/*`
13. update script entrypoint in `pyproject.toml`
14. delete old top-level modules
15. run full checks

## Per-phase validation rule

At minimum after each phase, run:

- `uv run --extra dev ruff check src tests scripts jobs`
- `uv run --extra dev ty check src tests scripts jobs`
- `uv run --extra dev pytest -q`

If a full run is too expensive during an intermediate step, run the relevant targeted tests immediately and return to the full suite before starting the next major phase.

## Acceptance criteria

The reorg is done when:

- top-level `src/slop_farmer/` contains only coarse package directories plus any deliberately tiny shared module(s)
- duplicated snapshot resolution helpers are gone
- `pr_scope` no longer imports private `analysis` helpers
- `build_pr_scope_clusters_from_snapshot` is removed
- duplicate-PR orchestration clearly lives in `app` and duplicate-PR analysis/gating is not pretending to be pure app wiring
- imports follow the intended direction
- `ruff format --check` passes
- `ruff check` passes
- `ty check` passes
- `pytest -q` passes

## Nice-to-have follow-up after reorg

Once the move is complete, consider a small second cleanup pass:

- finish splitting any still-mixed module that was moved pragmatically first
- extract a shared snapshot loading/path utility if both `analysis` and reports still duplicate that shape
- simplify any remaining “build client lazily” helpers that no longer pull their weight
- trim large command handlers if any remain confusing after the package split

## Bottom line

This should be a **coarse, opinionated, one-way reorg**:

- `app`
- `data`
- `reports`

but only after a small amount of boundary cleanup so those packages are honest.

The crucial principles are:

- one shared snapshot-path resolver
- no backward-compatibility shim layer
- no redundant snapshot adapter methods like `build_pr_scope_clusters_from_snapshot`
- no pretending that shared config/types belong entirely to `app`
- no pretending that duplicate-PR orchestration is a pure report module

That gives the biggest navigation win for the least structural complexity.
