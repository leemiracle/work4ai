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

# NVIDIA Storage Scale Test — Repository Context

Non-obvious repository behavior and invariants; not a changelog. Authoritative
guides for narrower scopes:

- [README.md](../README.md): launcher setup, substrate configuration, and validation.
- [Filesystem](FILESYSTEM_TESTING.md), [object](OBJECT_STORAGE_TESTING.md), and
  [network](NETWORK_TESTING.md) guides: workload operation and reporting.
- [docs/KUBERNETES_ELBENCHO_LIFECYCLE.md](KUBERNETES_ELBENCHO_LIFECYCLE.md):
  normative Kubernetes state machines, invariants, retry limits, and faults.
- [docs/REQUIREMENTS.md](REQUIREMENTS.md): normative requirements and status.
- [docs/DESIGN.md](DESIGN.md): detailed design and interfaces.
- [docs/ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md): deployment and
  network relationships.
- [docs/CODING_STANDARDS.md](CODING_STANDARDS.md): coding and validation rules.
- [integration-tests/README.md](../integration-tests/README.md): fixture,
  scenarios, and on-demand CI.
- [SECURITY.md](../SECURITY.md): vulnerability reporting and security policy.
- [ROADMAP.md](../ROADMAP.md): incomplete and proposed work.

## Project boundary

The lowercase repository, package, tarball, and directory identifier is
`storage-scale-test`; shell configuration uses `SCALE_TEST_BASE` as the
repository or extracted deployment root. Releases are source-only: users build
deployment tarballs locally and own the binaries they include.

`EXECUTION_SUBSTRATE` has no default. Benchmark processes require Linux; macOS
with Homebrew Bash and coreutils may initiate SSH or kubectl sweeps, and kubectl
also needs Homebrew GNU tar and `flock`.

## Integration fixture

`integration-tests/` provisions kind, RWX storage, SSH workers, and Slinky
Slurm; operation and CI are in its README. Invariants:

- Pod work runs as UID/GID 2000 to match the all-squashed NFS export and the
  Slurm account.
- Restart the Slinky login Pod, never its operator-managed Deployment: the
  operator can revert rollout annotations and kill an in-flight probe.
- GNU tar cannot restore `.` on SBX virtiofs, so control uploads keep
  precreated staging-directory metadata.
- `apt-get update` can exit 0 on failed indexes;
  `integration-tests/lib/apt-build.sh` inspects its output instead.
- `.venv-ci` is not a runtime bootstrap; fixture lifecycle and smoke checks
  install `requirements.txt`.
- On-demand CI shard manifests must cover the unsharded plan exactly; only the
  SSH shard (and an unsharded run) repeats setup and fixture stop/start.

## Entry points

| Benchmark | Entry point | Analyzer | Slurm dispatch | SSH dispatch | Kubernetes dispatch |
|---|---|---|---|---|---|
| Filesystem IO | `storage-tests/fs/nv-elbencho-sweep.sh` | `utils/extract-elbencho.py` | One maximum-sized coordinator allocation per sweep | One local sequential dispatcher per sweep | One coordinator Job per namespace segment |
| Filesystem metadata | `storage-tests/fs/nv-mdtest-elbencho.sh` | `utils/extract-mdtest-elbencho.py` | One maximum-sized coordinator allocation per sweep | One sequential dispatcher per sweep | One coordinator Job per namespace segment |
| Object storage | `storage-tests/object/nv-warp-sweep.sh` | `utils/extract-warp.py` | One job per node count | One remote invocation per node count | Unsupported |
| Network | `storage-tests/network/nv-netbench.sh` | `utils/extract-netbench.py` | One job per node count | One remote invocation per node count | Unsupported |

## Configuration

`env.sh` sources `lib/env_base.sh`; `validate_env.sh` checks the resolved
configuration before expensive work. Non-obvious invariants:

- `SLURM_EXTRA_ARGS` is an array and keeps embedded spaces; the flattened
  `SBATCH_OPTIONS`/`SRUN_OPTIONS` strings are best effort for interactive use.
- Only the main allocation's `sacct` row decides a Slurm job's result.
- The `TEST_DIRS` device probe (`stat -c %d` against `/`) proves distinct
  backing storage on that node, not that the path is itself the mountpoint.
- Kubernetes `TEST_DIRS` keys are `[namespace/]claim:path`
  ([below](#storage-targets-and-claims)).

### Target and workload override files

Filesystem launchers accept repeatable `--target` and `--env-override` files
([usage](FILESYSTEM_TESTING.md#workload-override-files)):

- Target settings (`TEST_DIRS`, `STORAGE_TARGET_NAME`, `FS_MAX_*`) come only
  from `env.sh` or `--target`; workload settings only from `env.sh` or
  `--env-override`. Per group, the target applies first, then overrides in
  command-line order.
- `env_base.sh` is not idempotent (modules, PATH, Slurm queries), so it is
  never re-sourced.
- Slurm coordinators re-source `env.sh` and then `env_used.sh`, so only names
  recorded in `env_used.sh` can be overridden.
- Target and override provenance is always written to `env_used.sh` (empty
  without a file), so sequentially sourced groups cannot inherit it.
- `env.sh`, `OBJ_AUTH_FILE`, target and override files, `env_used.sh`, and
  `executions/*.sh` are sourced as Bash: executable trusted input.

### Storage targets and claims

- One namespace per target: a Pod mounts claims only from its own namespace.
- Pods mount each claim at `/mnt/storage-scale-test/<claim>`. A namespace's
  control root is the lexically first normalized root of every group in it.
- One Lease per claim, acquired in byte order and released in reverse.
- One segment per namespace; the sequencer exists only across namespaces.
  Limits: 32 claims and 16 segments per attempt.

## Execution architecture

Slurm and SSH wrappers establish node context and call the same benchmark
functions in `lib/`. SSH nodes need neither the repository nor the results
filesystem: the launch host copies binaries and libraries, sends Bash over
`ssh host /bin/bash -s`, and streams results back as `tar`.

### Filesystem reification and resume

Both filesystem launchers reify every sweep cell into `OUTPUT_DIR/executions/`
before dispatch:

- Each cell has a stable `-${DS}-e${execution_id}` test-path suffix, so retries
  reuse its paths without colliding with other cells.
- Dispatch stops after the first failed cell.
- `--resume` sources the saved `env_used.sh`, resets stale `RUNNING` cells to
  `PENDING`, skips `SUCCESS`, and runs the rest in order.
- A dispatch lock prevents concurrent coordinators or resume loops on one
  execution directory.
- Slurm resume refuses to reset work while the saved coordinator may be
  active; if `squeue` no longer knows the job, Slurm accounting must confirm
  its terminal state.
- Resume sources `env_used.sh` and `executions/*.sh`, so protect the whole
  result directory from untrusted modification.

### Kubernetes execution

One submission is the whole sweep; `--status`, `--cancel`, and `--collect`
operate on that attempt. Every `--status` prints `NEXT_ACTION` and a
successful query exits 0 whatever the benchmark outcome. Until collection,
progress comes from claim-resident ledgers; zero running cells do not imply
terminality. Collect before `--resume`, which starts a new attempt and keeps
successful cells. On Kubernetes, `--read-from` also accepts the Pod path that
`--write-only` printed. `KUBECTL_ELBENCHO_IMAGE` defaults to the pinned image.
Progress strings are `P R S F[ ID]`, ID the first failed cell (`FAILED_*`
keys); every reader must accept the optional fifth field.

- Coordinator, worker, helper, and validation Pods carry no API token. Only the
  sequencer Job (and the `validate_env.sh --sequencer` probe), used only for
  batches spanning namespaces, mounts a ServiceAccount token, limited to
  get/patch of that attempt's named coordinator Jobs.
- Pods use ordinary Pod networking and attempt-scoped NetworkPolicy, never host
  networking, host ports, or Services; frozen worker endpoints are revalidated.
- Lost creates are retried only after an exact GET proves absence; objects
  absent past the ambiguity horizon are never adopted; the
  `app.kubernetes.io/name` label never proves ownership.
- Elbencho validation, worker, and coordinator Pods use `Unconfined` seccomp
  for Linux AIO; other helpers keep `RuntimeDefault`.
- Release gates: Docker SBX for the supported kind profile, dual-architecture
  NFS CI, and a separately authorized external-cluster run.

`validate_env.sh` on kubectl checks settings and claim identity, then lists
owned objects alone (so it never reports its own Jobs), then runs the sequencer
and node/runtime branches concurrently and replays their output in a fixed
order. The runtime Job stops early on image-pull failure or a failed mount.
Output is a summary unless `--verbose`; Pod/Job dumps go under `LOGS_DIR`. On
Slurm it uses one sbatch and one srun probe; on SSH, one session.

## Filesystem IO workload models

Operation is in [FILESYSTEM_TESTING.md](FILESYSTEM_TESTING.md). Invariants:

- Write phases never pass `--norandalign`: elbencho's aligned random default
  writes each block once; unaligned writes can leave files short.
- Worker-directory layout with one weight-1 root and direct IO runs timed;
  buffered IO, several roots, or `--run-to-completion` select completion mode.
  The effective mode is recorded per cell and never reinterpreted on resume.
- Generated shared-directory phases are exact-completion operations judged by
  JSON file, byte, and entry counters, not exit status: a zero exit does not
  prove a time-limited phase finished its dataset.
- The JSON parser tolerates Elbencho v3.2-1 streamed phase objects (adjacent,
  newline-separated, or followed by blank lines) but requires exactly one
  record of the expected phase.
- Generated targets are removed with `rmdir` after verified distributed
  deletion; recursive removal is only for identity-checked failure and signal
  cleanup.
- Compound IO sizes such as `1M,r4K` keep write and read order separate; one
  `random_io` value cannot describe them.
- `--read-from` publishes `.storage-scale-test-elbencho-treefile.txt`
  atomically after a successful read and reuses it; the operator must remove
  it after changing the dataset.
- All phases of a cell append to one CSV (later phases use `--nocsvlabels`);
  `extract-elbencho.py` also parses headerless Elbencho CSV.

## Other benchmark contracts

### Filesystem metadata

- Because elbencho appends to result files, a retry removes every
  per-iteration `.out`/`.csv` pair before target preparation.
- A cell succeeds only with nonempty, nonsymlink result pairs and an atomic
  completion marker written after all phases and cleanup.
- When a metadata ledger exists, the analyzer counts only `SUCCESS` cells;
  legacy result directories without one remain readable.
- Metadata phases use `-s 0` without `-b 0`: Elbencho 3.2 rejects zero block
  sizes even for zero-byte files.

### Batches

Prepared batches seal their manifest before the first external mutation. One
global ledger owns statuses, while group snapshots and artifacts stay isolated
through dispatch, collection, resume, and reporting. Batch preflight checks
each group's saved completion policy, not current settings. On Kubernetes,
collect before resume.

### Object storage and network

- The Warp bucket is destructive benchmark state and must hold no valuable
  objects.
- Static `WARP_PREFIXES` need the NVIDIA fork
  (`https://github.com/NVIDIA/warp-minio`).
- Network testing is beta; Elbencho netbench has no native timeout, so
  external execution limits are the operator's concern.
- Raw and live histograms sum repeated buckets so no observation is lost.

## Results and analysis

- Analyzer help and version run before the `.venv` bootstrap; object and
  network launcher help also precedes configuration and credential guards.
- Report versions stay out of metric models ([VERSIONING.md](VERSIONING.md)).
- Plot color maps are built before plotting so non-contiguous equivalent
  series share a color.
- Batch `reports.txt` exists only with at least two eligible owned reports;
  filtered runs rebuild it from fresh and retained owned reports, excluding
  failed or unowned ones.
- `--to-json` fragments are internal; `report_batch` assembles the document.
  Filters and failed groups never drop executions. Every execution carries
  `coordinates` and `coordinate_key`; `dataset`/`results` only when parsed.
- Live fairness ends the steady window at elbencho `[first]` and compares
  clients by ratio to the fleet median, not z-scores; analysis streams the
  live CSV in at most three passes.

Inspect large JSON/JSON.zst without printing complete datasets:

```bash
zstd -dc result.json.zst | python3 utils/compress_json_for_context.py
python3 utils/compress_json_for_context.py < result.json
```

## Deployment and supply chain

`utils/build_tarball.sh` downloads pinned upstream elbencho `v3.2-1` and
verifies per-architecture SHA-256 values; existing custom binaries stay unless
`--force-download`. Warp is never downloaded: existing binaries are included,
or users build them with `utils/build/build_warp_from_source.sh`. Archives
exclude credential files. Users own source and toolchain selection,
provenance, licenses, and validation of the tarball they build.

## Security and trust model

Policy and threat model: [SECURITY.md](../SECURITY.md). Non-obvious invariants:

- There is no authorization boundary between mutually untrusted users; test
  paths and buckets must be dedicated and disposable.
- Benchmark listeners are not authentication boundaries.
- SSH mode copies `OBJ_AUTH_FILE` into the remote work directory, which is
  therefore credential-bearing.
- `--read-from` and `--delete-only` paths are trusted operator input;
  delete-only also enforces a strict descendant of the configured test root.

## Development invariants

- Keep benchmark behavior shared between Slurm and SSH in `lib/`; wrappers
  establish context and transport, not core semantics.
- Shell tests use `lib/_platform_functions.sh` adapters for GNU coreutils on
  Linux and Homebrew `g`-prefixed coreutils on macOS; benchmark execution
  stays shell-only.
- `pytest.ini` collects only `tests/`.
