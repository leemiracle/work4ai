# Repository rules

## Packaging boundaries

Keep imports directional:

- `slop_farmer.app` may import from `slop_farmer.data` and `slop_farmer.reports`
- `slop_farmer.reports` may import from `slop_farmer.data`
- `slop_farmer.data` must not import from `slop_farmer.reports`
- `slop_farmer.data` must not import from `slop_farmer.app`
- `slop_farmer.reports` must not import from `slop_farmer.app`

Enforce this with:

- `uv run python scripts/enforce_packaging.py`

This check belongs in CI and in the local pre-commit/pre-push validation flow.

## Required validation before commit

Run:

- `uv run python scripts/enforce_packaging.py`
- `uv run python scripts/check_hf_cli_secrets.py`
- `uv run --extra dev ruff format --check src tests scripts jobs`
- `uv run --extra dev ruff check src tests scripts jobs`
- `uv run --extra dev ty check src tests scripts jobs`
- `uv run --extra dev pytest -q`

## Search discipline

When inspecting this repository, never search outside the workspace root unless the user explicitly asks.

### Default search scope

For code, job, pipeline, and API review, search only:

- `src`
- `tests`
- `scripts`
- `jobs`
- `docs`
- `README.md`
- `AGENTS.md`

### Default exclusions

Do not search generated, cached, or artifact-heavy paths unless the user explicitly asks:

- `.git`
- `.venv`
- `build`
- `dist`
- `data`
- `runs`
- `hub`
- `eval_data`
- `.fast-agent/sessions`
- `__pycache__`

Also exclude large generated or binary files by default:

- `*.parquet`
- `*.jsonl`
- `*.duckdb`
- `*.arrow`
- `*.feather`
- `*.pyc`

### Search command rules

- Never include `/` as a search path unless the user explicitly asks to search the full filesystem.
- Prefer targeted path lists over broad recursive search.
- Prefer multiple focused searches over one very broad regex.
- For known files, use `read_text_file` instead of ripgrep.
- For complex repo discovery, prefer the structured ripgrep helper over ad hoc shell search.
- Avoid noisy regexes like `run|api|hf` unless they are narrowed by path and purpose.
