# Linting

Tool that checks code for linting violations and can automatically fixes some issues:
* Displays lint violation content to see what lines of code are causing the violations
* Some violations cannot be auto-fixed with the `--apply-patches` argument. Please manually fix any remaining violations.

**Recommendation: Run `dazel fix` before submitting an MR. Manually fix any violations that remain.**

## Usage

The linter can be run directly or with the convenience command `dazel lint`:

```text
Usage: linter.sh [OPTIONS] [TARGETS...]

Run linters on Bazel targets

Options:
  --apply-patches           Auto-fix violations by applying patches (default: false)
  --fail-on-violation       Fail the build when a linter warning is present (default: false)
  --no-buildifier           Disable buildifier BUILD formatting/lint (default: false)
  --no-gazelle              Disable Gazelle BUILD dependency checks (default: false)
  --no-mypy                 Disable mypy type checking (default: false)
  --output-base=PATH        Set the output_base directory for dazel/bazel (default: none)

Arguments:
  TARGETS                   Bazel target patterns to lint (e.g., //... or //checks/...)
                            (default: //...)

Examples:
  linter.sh                              # Check for violations (default)
  linter.sh //checks/...                 # Check specific targets
  linter.sh --apply-patches              # Fix violations in everything
  linter.sh --apply-patches //checks/... # Fix violations in specific targets
  linter.sh --fail-on-violation          # Check and fail if violations exist
  linter.sh --no-mypy                    # Run only ruff, Gazelle, and buildifier (skip mypy)
  linter.sh --no-buildifier              # Run only ruff, mypy, and Gazelle (skip buildifier)
  linter.sh --no-gazelle                 # Run without Gazelle BUILD checks
```

### Examples

The linter script lives at `tools/lint/linter.sh`, relative to the repository root. Most users invoke it
via the convenience commands in the next section instead of calling the script directly.

```bash
# View lint violations (default behavior)
tools/lint/linter.sh                 # Check all targets
tools/lint/linter.sh //checks/...    # Check specific targets

# Fail with non-zero exit code if violations found (useful for automated builds)
tools/lint/linter.sh --fail-on-violation

# Auto-fix violations by applying patches
tools/lint/linter.sh --apply-patches
tools/lint/linter.sh --apply-patches //checks/...
```

### Convenience Commands

```bash
# Using dazel lint (shows violations without applying fixes)
dazel lint                    # Check all targets (//...)
dazel lint //checks/...       # Check targets under //checks/...

# Using dazel fix (applies patches and runs formatter)
dazel fix                     # Apply patches and format all targets
dazel fix //checks/...        # Apply patches and format only targets under //checks/...
```

## Gazelle

[Gazelle](https://rules-python.readthedocs.io/en/latest/gazelle/docs/installation_and_usage.html) keeps Python BUILD file `deps` in sync with imports. It runs automatically as part of `dazel fix` (`gazelle update`) and `dazel lint` (`gazelle update -mode diff`). BUILD formatting and Starlark lint remain the job of buildifier.

```bash
# Refresh BUILD dependencies after editing Python imports
dazel run //:gazelle -- update

# After changing requirements.txt, refresh the Gazelle pip manifest
dazel run //:gazelle_python_manifest.update
```

Disable Gazelle with `--no-gazelle` on the linter script, or scope with target patterns (e.g. `dazel lint //checks/...`).