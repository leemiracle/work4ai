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

# AGENTS.md

Canonical instructions for AI coding agents; `CLAUDE.md` imports this file.
Humans: start with [README.md](README.md). Depth lives in docs to read on demand:
- Coding standards (Python/shell detail, linting): [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md)
- Architecture, design decisions, error patterns, recent work: [docs/CONTEXT.md](docs/CONTEXT.md) — read before non-trivial work; update it afterward.

## Delegation (mandatory)

You MUST run every independent task (searches, reviews, checks, per-file work)
as concurrent sub-agents, maximizing parallelism. Give each the most
cost-efficient model that can do it well.

## What this is

Shell and Python tooling that runs distributed storage benchmarks across a fleet
of client nodes and turns the raw output into readable tables and plots. It
orchestrates third-party benchmark binaries (elbencho for filesystem/network,
Warp for S3-compatible object storage) as **separate processes** — they are
**never bundled or vendored** into this repo; users download or build them.

## Architecture

- `storage-tests/{fs,object,network}/` — test entry points with `ssh/` and
  `sbatch/` substrate code; filesystem tests also have `kubectl/`.
- `lib/` — shared Bash libraries (`env_*.sh`, `_*_functions.sh`) + a few Python helpers.
- `utils/` — self-bootstrapping Python result tools (`extract-*.py`) and build helpers (`build_tarball.sh`, `build/`).
- `tests/` — `pytest` unit tests (Python and shell).
- `integration-tests/` — kind-based real-infrastructure lifecycle (see its README).
- `docs/` — user guides (`*_TESTING.md`, `MACHINE_READABLE_RESULTS.md`, `VERSIONING.md`), `KUBERNETES_ELBENCHO_LIFECYCLE.md`, `DESIGN.md`, `REQUIREMENTS.md`, `ARCHITECTURE_DIAGRAMS.md`, `CONTEXT.md`, `CODING_STANDARDS.md`, `plans/` (unimplemented proposals only).
- Config is environment-driven (`env.sh`); `EXECUTION_SUBSTRATE` explicitly
  selects Slurm, passwordless SSH, or kubectl for filesystem sweeps.

## Setup

```bash
cp env.sh.template env.sh        # then edit for your environment
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt  # matplotlib, numpy, PyYAML, zstandard
./validate_env.sh                # iterate until it runs cleanly
```

See the README "Getting started" section for the full quickstart and
[BENCHMARK_RECIPES_FILESYSTEM.md](BENCHMARK_RECIPES_FILESYSTEM.md) for tuned settings.

## Checks (run before committing)

CI lint and pytest must find nothing these checks missed. Commit or push only
after the full script exits 0; judge it by exit status and full output, never a
grep of the score. Report any failure you cannot fix.

```bash
./utils/run_ci_checks.sh
```

After changing `.github/`, parse every `.yml`/`.yaml` beneath it with a YAML
parser. After changing shell traps or signals, also run pytest as non-root
under CI's bash 5.2 (e.g. an `ubuntu:24.04` container); trap semantics differ
across bash versions.

Install any missing check tool into the repo's local environment and rerun;
never skip required tooling.

The script reuses `.venv-ci` with the pinned tools. Pass `lint`, `compliance`,
`shellcheck`, `black`, `pylint`, or `pytest` to run one check. Set
`CI_CHECK_JOBS=1` in a constrained sandbox; in a network-restricted one, set
`CI_BOOTSTRAP=0` and use `CI_PYTHON`/`CI_SHELLCHECK`. Run tests and lint only
through this script or an environment populated from both requirements files;
ambient tooling, preloaded sandbox packages, and `.venv-ci` do not prove CI
readiness. When changing runtime imports or CI entry points, also reproduce the
workflow's dependency bootstrap and smoke-test its command in a clean
environment.

`black` must be 25.9.0+; `pylint` must report zero messages (its score rounds
to 10.00 despite a warning). Details: [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md).

## Key conventions (non-obvious; don't restate linter-enforced rules)

- **Do not vendor third-party binaries or code** (elbencho is GPL-3.0, Warp is
  AGPL-3.0). They are invoked as separate processes; keep it that way.
- **License header**: every text file carries the NVIDIA Apache-2.0 header (the
  block at the top of this file) in its comment syntax; copy it verbatim.
  `LICENSE` is exempt; `README.md` carries the notice in its Copyright section
  at the bottom.
- **elbencho behavior**: do not rely on elbencho source older than **3.0.37**;
  prefer a local checkout at `tmp/elbencho-src` when present over web snippets.
- **Python**: keep each function's cognitive complexity <= 15 (not linter-enforced);
  avoid duplicating a literal string 3+ times (use a constant).
- **Kubernetes probe diagnosis**: `kubectl exec` returning `-9` does not prove
  OOM or broken Pod networking. Check OOM evidence, then run the socket operation
  from a Pod-resident script. If only exec-carried socket code is killed, keep
  network I/O in the Pod and use exec for bounded request/result transfer.

## Pull requests

Wrap commit-message lines at about 72 characters.

No external contributions currently. Maintainer PRs: stay focused, pass the
checks above, and update `README.md`/`docs/` when behavior or configuration
changes.
