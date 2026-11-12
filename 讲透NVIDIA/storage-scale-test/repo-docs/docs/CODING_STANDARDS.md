<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Coding standards

Detailed coding standards for `storage-scale-test`. Referenced from
[AGENTS.md](../AGENTS.md); read this when doing substantial Python or shell
work. `AGENTS.md` carries the lean, always-on summary; this file holds the
depth.

## Running repository checks

Run the same validation commands used by CI from the repository root:

```bash
./utils/run_ci_checks.sh
```

The script works on Linux and macOS, creates and reuses `.venv-ci`, and installs
the exact versions in `requirements.txt` and `requirements-ci.txt`. Pass
`lint` to run all static checks, or pass `compliance`, `shellcheck`, `black`,
`pylint`, or `pytest` to run one check. The lint target runs its four checks
concurrently, buffers each check's diagnostics, and reports every result. Set
`CI_CHECK_JOBS` to control total concurrency; local runs default to the host's
logical CPU count. The default `all` target runs lint and pytest concurrently,
buffers their output separately, and splits that CPU budget between them.
Pytest uses `pytest-xdist` to distribute tests across its assigned workers. The
script uses `uv` when already installed and otherwise uses Python's standard `venv`.
For a sandbox with preinstalled tools but no package-index access, set
`CI_BOOTSTRAP=0`; `CI_PYTHON` and `CI_SHELLCHECK` can select the executables.
A few tests build with real Docker BuildKit on the fixture's digest-pinned
base images. Without Docker, or when a pinned base is not already present
locally, they skip. `CI_REQUIRE_DOCKER=1` (set by the CI pytest job) makes
them pull and verify the pinned bases and fail rather than skip.
On macOS, unit tests require Homebrew's Bash and GNU coreutils; install both
with `brew install bash coreutils` and put Homebrew's bin directory first on
`PATH`.

## Python

Python 3.12 or newer is required for repository Python tools and their pinned
dependencies.

### Cognitive complexity (<= 15 per function)
Most of these are enforced by tooling, but cognitive complexity is not, so apply
it deliberately when writing new code:
- Break complex logic into small helper functions BEFORE writing.
- Each helper should do ONE thing (parse, validate, transform, etc.).
- Nested conditionals and loops add complexity — extract them to helpers.
- Use early returns to reduce nesting depth.
- Data-driven approaches (dicts, lists of handlers) reduce branching.

```python
# BAD: nested conditionals
def process_data(data):
    for item in data:
        if item.type == "A":
            if item.valid:
                ...  # many lines
        elif item.type == "B":
            ...  # more nested logic

# GOOD: extract helpers, dispatch by table
def _process_type_a(item): ...
def _process_type_b(item): ...

def process_data(data):
    handlers = {"A": _process_type_a, "B": _process_type_b}
    for item in data:
        handler = handlers.get(item.type)
        if handler:
            handler(item)
```

### String constants
Never duplicate a literal string 3+ times — define a module-level
`UPPER_SNAKE_CASE` constant near the top of the file (e.g.
`GITHUB_PREFIX = "github.com/"`). When modifying code, check whether a new
literal duplicates an existing one.

### Linting / formatting
1. `black` 25.9.0+ (default line length 88), required after any Python change.
   If `black` or another required check tool is unavailable, install it into
   the repo's local environment and rerun the check.
2. `pylint` must report zero messages. The 10.00/10 score rounds up, so a
   single warning still prints 10.00/10 while the check fails; trust the exit
   status and the listed messages, not the score. If it reports any, either fix the issue or add the
   check to the `.pylintrc` disable list only when the repository policy should
   exclude that check.
3. `.pylintrc` is canonical. It gates enabled fatal/error/warning checks plus
   exactly `C0200`, `C0411`, `R0801`, and `R1704`; all other C/R checks are
   disabled by category. For `R0801`, move reusable production helpers into
   `lib/` and repeated test infrastructure into a shared test helper.
4. Run combined checks with `./utils/run_ci_checks.sh lint`. In a constrained
   sandbox, set `CI_CHECK_JOBS=1` to disable parallel execution.
5. Prefer the alternate quote character inside f-string expressions when it
   improves readability; Python 3.12 supports either form.
6. Run analysis tools through their executable Python entry points (e.g.
   `utils/extract-elbencho.py`). They bootstrap the pinned runtime environment
   automatically; `--help` and `--version` use only the standard library.

## Shell

### Always run shellcheck (entire repo)
After modifying ANY `.sh` file:

```bash
./utils/run_ci_checks.sh shellcheck
```

Fix all errors and warnings. For intentional exceptions, add
`# shellcheck disable=SCXXXX` with an explanatory comment. This command is safe
to run in the sandbox without requesting permissions.

Shell unit tests that do not require benchmark binaries run on Linux and
macOS; binary-dependent tests skip when elbencho is unavailable. GNU coreutils
commands use their unprefixed names on Linux and Homebrew's `g`-prefixed names
on macOS.

### Best practices
- **Quoting**: always quote variables (`"$var"`); the only exception is
  intentional word splitting.
- **Error handling**: `cd ... || exit` / `cd ... || return`; check exit codes
  directly (`if ! command; then`); separate declaration from command
  substitution to avoid masking return values:
  ```bash
  local result
  result=$(some_command)   # good
  # local result=$(some_command)  # bad: SC2155 masks the return value
  ```
- **Sourced files**: use `# shellcheck shell=bash` instead of a shebang;
  `# shellcheck disable=SC2154` for caller-set variables;
  `# shellcheck disable=SC1091` for external sourcing.
- **Arrays**: `"${array[@]}"` for separate words, `"${array[*]}"` for a single
  word (e.g. error messages); never use unquoted `$@` / `$*`.
- **Traps**: single quotes — `trap 'cleanup' EXIT`, not `trap "cleanup" EXIT`
  (SC2064).
- **String constants**: same 3-occurrence rule as Python — extract a
  `readonly NAME="value"` constant and reference `"$NAME"`.

### Common patterns
1. **Remote scriptlets** (executed over SSH): export all variables, add shebang
   `#!/usr/bin/env bash`.
2. **Sourced library files** (`_*_functions.sh`): apply the "Sourced files"
   rules above.
3. **SSH/Slurm wrappers**: handle `cd` failures with `|| exit` / `|| return`.

## Maintaining docs/CONTEXT.md

[docs/CONTEXT.md](CONTEXT.md) is the WHAT/WHY knowledge base: architecture,
design decisions, invariants, and error patterns. It describes the repository's
current state, not its history — it is explicitly not a changelog or an
implementation journal. Update it after significant work.

**When**: multi-step tasks (3+ edits across files); non-obvious component
relationships; tricky bug fixes / error patterns; architectural guidance or
design decisions; significant features/refactors/benchmarking; new tool/command
patterns.

**How**: add or revise entries under the appropriate section so the document
keeps describing how the repository behaves today. Correct or delete statements
that a change has made obsolete rather than appending a note that supersedes
them. Keep entries concise (1-4 sentences) and specific (file and function
names, concrete examples); flag uncertainties with "Note:" / "Verify:". Keep
filenames in backticks and snippets in code blocks.
