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

# NVIDIA Storage Scale Test — Design Document

**Last Updated**: 2026-10-16\
**Status**: Documents the design and architecture of the existing implementation.

---

## Table of Contents

1. [Design Goals](#1-design-goals)
2. [Deployment Packaging](#2-deployment-packaging)
3. [Configuration](#3-configuration)
4. [Execution Architecture](#4-execution-architecture)
5. [Benchmark Worker Lifecycle](#5-benchmark-worker-lifecycle)
6. [Sweep Loop Structure](#6-sweep-loop-structure)
7. [Benchmark Tool Invocation](#7-benchmark-tool-invocation)
8. [Results & Output Structure](#8-results--output-structure)
9. [Reporting & Analysis](#9-reporting--analysis)
10. [Validation and Release](#10-validation-and-release)
11. [Security Considerations](#11-security-considerations)

---

## 1. Design Goals

The overarching design priorities:

1. **Minimal friction for the end user.** One prepared tarball to transfer, one file to edit, one validation command to run before testing.
2. **Run anywhere.** Support Slurm-managed clusters, bare SSH-accessible nodes,
   and Kubernetes clusters from a single codebase.
3. **Non-root operation.** No operation requires root or sudo.
4. **Self-contained benchmark execution.** Once the user has prepared a complete
   deployment tarball with the required benchmark binaries, benchmark execution
   does not require internet access, package installation, or compilation on the
   target system. Reporting has separate Python dependencies; its executable
   Python tools create a virtual environment and install them when necessary,
   so reporting may instead be run on a connected analysis host after the results
   are copied out.
5. **Reproducible and resumable results.** Every run is timestamped and isolated.
   Configuration snapshots accompany filesystem results, and filesystem IO sweeps
   persist per-execution state so interrupted work can be resumed. Analysis scripts
   consume directories, not individual files, making re-analysis and comparison
   straightforward.

---

## 2. Deployment Packaging

### 2.1 User-Created Deployment Tarball

The user can package this repository as a single `.tar.gz` deployment tarball
for transfer to a target environment. The repository does not contain prebuilt
third-party benchmark binaries, and NVIDIA does not publish benchmark binaries or
ready-made deployment tarballs for this project. A user-created deployment tarball
contains the scripts plus any user-provided, helper-downloaded, or helper-built
binaries present when `utils/build_tarball.sh` runs:

```
storage-scale-test/
├── env.sh.template          # Configuration template
├── validate_env.sh          # Configuration validator
├── storage-tests/           # Orchestrator + dispatch scripts
│   ├── fs/                  # Filesystem (elbencho IO, mdtest-elbencho metadata)
│   ├── object/              # Object storage (warp)
│   └── network/             # Network (elbencho netbench)
├── lib/                     # Shared shell libraries
├── utils/
│   ├── elbencho             # User-provided or downloaded upstream binary (x86_64)
│   ├── elbencho.aarch64     # User-provided or downloaded upstream binary (ARM64)
│   ├── warp                 # User-provided or source-built binary (x86_64)
│   ├── warp.aarch64         # User-provided or source-built binary (ARM64)
│   ├── s3test               # Helper-built S3 connectivity test (x86_64)
│   ├── s3test.aarch64       # Helper-built S3 connectivity test (ARM64)
│   ├── extract-*.py         # Self-bootstrapping analysis entry points
│   └── summarize-elbencho.py
└── README.md
```

The user creates this deployment tarball, copies it to the target host, extracts
it, and runs validation. If the required binaries were successfully provided,
downloaded, or built before packaging, benchmark execution needs no second
download, compilation, or package manager on the target system.

**Rationale:** Benchmark environments are often air-gapped, behind firewalls, or
lack package management. Preparing the tarball before entering that environment
keeps target-side deployment simple, while leaving binary acquisition, build,
license, and vulnerability decisions with the user.

### 2.2 Architecture Support

When binaries are present, x86_64 and aarch64 variants live side-by-side using
a `.aarch64` suffix convention. At runtime, `lib/env_base.sh` detects the
architecture via `uname -m` and selects the correct binary path:

```
ELBENCHO="${SCALE_TEST_BASE}/utils/elbencho${arch_suffix}"
WARP="${SCALE_TEST_BASE}/utils/warp${arch_suffix}"
```

The `client_arch` variable in `env.sh` can override auto-detection for
cross-architecture setups (e.g., running orchestration from x86_64 against
ARM64 compute nodes). `validate_env.sh` verifies that the selected binaries
exist and match the target architecture using `file`.

### 2.3 Binary Preparation Helpers

`utils/build_tarball.sh` is convenience tooling for creating a local deployment
tarball, not a binary supply-chain guarantee. It continues to create the tarball
when optional helper steps fail, while warning which tests will not work without
the missing binaries.

Current helper behavior:

- **elbencho:** reuses existing `utils/elbencho` and `utils/elbencho.aarch64`
  binaries or attempts to download pinned upstream static release binaries.
- **Warp:** does not download or bundle NVIDIA-provided Warp binaries. Missing
  `utils/warp` or `utils/warp.aarch64` causes a warning and points users at
  `utils/build/build_warp_from_source.sh`, which defaults to the NVIDIA Warp
  fork's `nv-main-oss` branch and can also build from a chosen upstream HTTPS
  or SSH repository URL plus tag, branch, or commit SHA.
- **s3test:** builds `utils/s3test` and `utils/s3test.aarch64` from the in-tree
  `utils/build/s3-test.c` when missing or stale, trying local compilers first
  and Docker/Buildx next.

Users are responsible for validating binaries on their target architectures and
for satisfying any license, source-offer, SBOM, or vulnerability-management
requirements that apply to binaries they include in a deployment tarball.

---

## 3. Configuration

### 3.1 Single Configuration File

All test parameters live in `env.sh`, copied from `env.sh.template`. The
template has a clearly-marked editable section bounded by:

```
########### vvvvvvvvvv ONLY EDIT THESE vvvvvvvvvv
...
########### ^^^^^^^^^^ ONLY EDIT THESE ^^^^^^^^^^
```

followed by `source lib/env_base.sh` which applies defaults and backward
compatibility. This design means:

- The user edits one file; filesystem launchers can layer `--target` files
  (what to test) and `--env-override` files (how to test) on top (§3.5).
- Defaults are set once in `env_base.sh`, not scattered across scripts.
- Every orchestrator script sources `env.sh` as its first action, giving it the
  full configuration.

### 3.2 Configuration Categories

| Category | Key Variables | Purpose |
|----------|--------------|---------|
| Output | `RESULTS_DIR`, `LOGS_DIR` | Where results and logs are written |
| Execution | `EXECUTION_SUBSTRATE`, `SSH_HOST_LIST`, Slurm account/partition/reservation | Explicitly selects SSH, Slurm, or kubectl mode |
| Filesystem | `TEST_DIRS` (associative array with weights) | One storage target: its roots (mount paths on SSH/Slurm, `[namespace/]claim:path` on Kubernetes) and load-balancing weights |
| Object storage | `OBJ_BUCKET`, `OBJ_HOST`, `OBJ_AUTH_FILE` | S3-compatible endpoint and credentials |
| Elbencho IO | `ELBENCHO_SCALE_IO_SIZES`, `ELBENCHO_SCALE_THREAD_LIST`, `ELBENCHO_IODEPTH_LIST`, `ELBENCHO_SCALE_READ_WRITE_DURATION` | Filesystem IO sweep parameters |
| Elbencho file layout | `ELBENCHO_FILE_LAYOUT`, `ELBENCHO_FILES_PER_NODE`, `ELBENCHO_FILE_SIZE` | Legacy worker-directory or completion-based shared-directory workload |
| Elbencho single file | `ELBENCHO_SINGLE_BIG_FILE`, `ELBENCHO_SINGLE_BIG_FILE_SIZE`, `ELBENCHO_ALL_NODES_ACCESS_ALL_DATA` | Cooperative or all-nodes-access single-file workload |
| Metadata | `MDTEST_BRANCH_FACTOR`, `MDTEST_ITEMS_PER_DIR`, `MDTEST_ITERATIONS` | Branched metadata test parameters; the dense layout is selected by a CLI flag |
| Warp | `WARP_THREAD_LIST`, `WARP_OBJ_SIZES`, PUT/GET durations | Object storage sweep parameters |
| Netbench | `NETBENCH_THREADS`, `NETBENCH_HOST_NIC_GBPS`, `NETBENCH_TARGET_RUNTIME` | Network test parameters |
| Slurm extras | `SLURM_JOB_NAME_PREFIX`, `SLURM_EXTRA_ARGS`, `SLURM_EXCLUSIVE_USER`, `SLURM_NODE_IGNORES`, `SLURM_NODE_INCLUDES`, `SLURM_JOB_POLL_INTERVAL_SECONDS` | Slurm job customization |
| Kubernetes | `KUBECTL_NAMESPACE`, `KUBECTL_NODE_SELECTOR`, `KUBECTL_ELBENCHO_IMAGE`, `KUBECTL_IMAGE_PULL_POLICY`, `KUBECTL_RUN_AS_USER`, `KUBECTL_RUN_AS_GROUP`, `KUBECTL_SEQUENCER_IMAGE`, `KUBECTL_SEQUENCER_PROBE_TIMEOUT_SECONDS` | Default namespace for `TEST_DIRS` claims (optional when every key names its namespace), eligible nodes, image (defaults to the pinned elbencho release) and pull policy, workload identity, an optional digest-pinned override (for a mirror) of the default sequencer image that batches spanning namespaces run, and how long `validate_env.sh` waits for its sequencer checks |

### 3.3 Defaults and Compatibility

`lib/env_base.sh` supplies defaults for configuration omitted from `env.sh`.
It also provides one limited variable-name compatibility rule:

- When `TEST_DIR` is set and `TEST_DIRS` is unset or empty, `TEST_DIR` becomes
  the sole `TEST_DIRS` entry with weight 1.
- Warp configuration uses the canonical `WARP_*` variables listed in Section
  3.2; no alternate variable names are mapped.

Current usage output is canonical for command-line forms.

### 3.4 Configuration Validation

`validate_env.sh` performs a live, accumulating validation of the entire
configuration before any benchmarks run. It is designed for an interactive
edit-validate loop:

1. **Accumulating errors.** Errors are appended to a temporary file (using
   `flock` where available for concurrency safety). The script does not
   stop at the first error — it reports all problems together at the end.

2. **What is validated:**

   | Check | Method |
   |-------|--------|
   | Output directories exist | `test -d` |
   | Slurm connectivity | `sinfo`, then one probe as an `sbatch` job (production options, waited on) and one as an `srun` step (minimal options) |
   | SSH connectivity | `ssh` command, string-scriptlet and file-scriptlet execution on one host |
   | Binary architecture match | `file` on binary vs. the probe's `uname -m` (srun's on Slurm, one SSH session's otherwise) |
   | Filesystem paths use storage distinct from `/` | The same probe compares `stat -c %d` device IDs for every root on one node per probe |
   | Filesystem paths are writable | `test -w` in the same probe |
   | Kubernetes prerequisites | Claim-qualified `TEST_DIRS` keys; `kubectl`, `flock`, and an active kubectl context; API access and Lease permission in the namespace of `env.sh`'s `TEST_DIRS`, which must carry the `kubernetes.io/metadata.name` label (Kubernetes 1.21+); per-claim identity (Bound, RWX, Filesystem volume mode; reports its bound PV); Ready nodes matching `KUBECTL_NODE_SELECTOR`; one short-lived Job that mounts all of its claims and checks the image, UID/GID, required tools, and read/write per root; sequencer server version (1.24+), RBAC, and image as warnings, and with `--sequencer` the full probe as errors (one namespace needs none of them) |
   | Existing toolset Kubernetes objects | Read-only listing of objects labeled `app.kubernetes.io/name=storage-scale-test`; informational (may warn), never fails validation |
   | S3 credentials and bucket access | `s3test` binary |
   | S3 bucket emptiness | Object count check (warning if non-empty) |
   | Elbencho parameters | Thread list integers, IO sizes valid, duration valid |

3. **Execution-mode-aware.** Validation uses Slurm, SSH, or kubectl to check
   remote nodes, matching the mode that benchmarks will actually use: one
   `sbatch` job and one `srun` step probe on Slurm, one probe session over SSH.

4. **Concise, deterministic output.** Without `--verbose`, passed checks print
   summary lines, and a failed Kubernetes check saves its full Pod and Job
   diagnostics under `LOGS_DIR`, printing the path. On Kubernetes the settings
   and claim identities are checked first, then the owned-object inventory runs
   alone (so it never lists validation's temporary Jobs), then the sequencer
   checks and the node and runtime-Job checks run concurrently; their output,
   errors, and warnings are replayed in a fixed order. The runtime Job stops
   early when its image cannot start or a claim's mount command fails, and
   otherwise within about 180 seconds. INT and TERM are forwarded to the
   concurrent checks, which delete their temporary Jobs before exiting.

**Rationale:** Storage benchmark failures are expensive — a bad configuration
discovered after a 2-hour run wastes the user's time and Slurm allocation.
Front-loading all validation into a fast, comprehensive check is the single
most effective ergonomic investment.

### 3.5 Target and Workload Override Files

Filesystem launchers split the override-allowed settings in two, on every
substrate: **what to test comes from `env.sh` or `--target`; how to test comes
from `env.sh` or `--env-override`.** Target settings are `TEST_DIRS`,
`STORAGE_TARGET_NAME`, `FS_MAX_AGG_THROUGHPUT`, `FS_MAX_NODE_THROUGHPUT_GBPS`,
and `FS_MAX_NODE_IOPS` (`filesystem_target_setting_names`); every other name in
`filesystem_env_override_names` is a workload setting. See
[Testing several filesystems](FILESYSTEM_TESTING.md#testing-several-filesystems)
for usage.

- **`--target FILE`** is repeatable on new submissions, `--batch`, and
  `--append`; N flags publish N groups in command-line order (§4.5). For each
  group the launcher clears `STORAGE_TARGET_NAME`, loads the target file
  (which must set `TEST_DIRS` and may set only target settings; `TEST_DIRS` is
  replaced whole, unset `FS_MAX_*` values keep `env.sh`'s), and then applies
  the override files. A plain run with more than one `--target` is rejected
  and the error prints the equivalent `--batch` and `--start` commands;
  lifecycle operations reject `--target`, and `--delete-only` accepts at most
  one, only to resolve `TEST_DIRS`.
- **`--env-override FILE`** may set only workload settings, and applies to
  every target of the submission. A workload setting in a target file, or a
  target setting in an override file, is an error naming the file, the
  variable, and the flag to use instead.

**Rationale:** Letting override files also set target settings gave two
overlapping ways to say what to test, with precedence rules to learn; disjoint
allowlists make each file's role obvious from the flag that passes it.

Override files are loaded as follows; target files use the same loader with
the target allowlist. After `env.sh`, `filesystem_env_override_declarations`
(`lib/env_functions.sh`) sources the file in an isolated child shell seeded
with the current allowed values and the exported environment, so relative edits
such as `LIST+=(x)` work. Only names listed by `filesystem_env_override_names`
may change; new lowercase scratch variables are discarded, and any other change
is an error. Values are type-checked (associative array, indexed array, or
scalar) and returned as declarations that the launcher `eval`s, followed by
`apply_filesystem_workload_defaults`. The launcher evaluates each file's
declarations before running the next file's loader, so later files build on
earlier ones; `resolve_env_override_chain` resolves the paths and rejects the
same file given twice.

- **Allowlists equal the snapshot.** Together, the target and workload names
  are exactly the settings that `env_used.sh` records. Slurm coordinators
  re-source `env.sh` and then only `env_used.sh`, so overriding anything else
  would silently revert.
- **`env_base.sh` is not re-sourced.** It is not idempotent (modules, `PATH`,
  Slurm queries); only the workload defaults are re-applied.
- **Evaluated once per group.** Batch preparation stages each override file as
  `.env-override-<n>.sh` (the operator's paths go in `.env-override-origins`)
  and reuses the launcher's concatenated, validated declarations instead of
  re-sourcing the files. Target files are staged the same way with their own
  provenance.
- **Provenance.**
  `STORAGE_SCALE_TEST_ENV_OVERRIDE_{FILES,SHA256S,FILE_VARIABLES}` arrays
  record each override file's path, SHA-256, and changed names in application
  order. The scalars `STORAGE_SCALE_TEST_ENV_OVERRIDE_{FILE,SHA256,VARIABLES}`
  keep the last file and the union of names. The target file is recorded
  separately as `STORAGE_SCALE_TEST_TARGET_FILE{,_SHA256,_VARIABLES}` (§8.1).

---

## 4. Execution Architecture

### 4.1 Execution Substrates

Filesystem IO supports three explicitly selected substrates from a single entry
point. `EXECUTION_SUBSTRATE` is required; there is no implicit default:

- `ssh` selects passwordless SSH and requires `SSH_HOST_LIST`.
- `slurm` submits through the configured scheduler.
- `kubectl` requires an already authorized `kubectl` context, existing
  namespaces, and pre-existing Bound RWX claims named by the
  `[namespace/]claim:path` keys of `TEST_DIRS` (§4.3).

The Kubernetes substrate does not provision storage or require host-networked
Pods. It selects Ready nodes with `KUBECTL_NODE_SELECTOR`, uses ordinary Pod
networking for elbencho's coordination port, and runs the workload as the
configured non-root UID/GID. Elbencho validation, worker, and coordinator Pods
request `seccompProfile.type: Unconfined` so Linux AIO is not rejected by a
runtime-default filter; administrative helper Pods retain `RuntimeDefault`.

### 4.2 Common Dispatch Layers

```
top-level orchestrator (storage-tests/*/nv-*.sh)
    │
    ├── Slurm: submit one or more sbatch dispatchers/coordinators
    │               │
    │               └── source shared lib functions and run benchmark phases
    │
    ├── SSH: select hosts and run an SSH dispatcher on the launch host
    │               │
    │               └── transmit a checked-in or generated scriptlet to a head host
    │                       └── source copied libraries and run benchmark phases
    │
    └── kubectl: reserve an attempt on the TEST_DIRS claims and create, per
                 namespace segment, owned
                    │
                    └── worker DaemonSet + coordinator Job (+ one sequencer
                        Job when segments > 1); query or collect the durable
                        asynchronous sweep later
```

The top-level scripts parse their benchmark-specific flags, validate the
requested sweep, create one datestamped result directory, and choose the
explicit substrate. The dispatcher establishes the selected node context.
Benchmark logic in
`lib/_elbencho_functions.sh`, `lib/_warp_functions.sh`, and
`lib/_netbench_functions.sh` is shared between substrates where their execution
models match.

The number of dispatches is deliberately benchmark-specific:

| Benchmark | Slurm dispatch boundary | SSH dispatch boundary |
|-----------|--------------------------|-----------------------|
| Filesystem IO | One coordinator job for the entire sweep, sized to the largest remaining node count | One local dispatcher loop for the entire sweep |
| Filesystem metadata | One coordinator job for the remaining sweep | One sequential dispatcher for the remaining sweep |
| Object storage | One job per node count | One invocation per node count |
| Network | One job per node count | One invocation per node count |

Kubernetes filesystem IO and metadata submit the complete reified sweep as one
asynchronous attempt: one coordinator Job per namespace segment (one, unless a
batch spans namespaces; §4.5), plus a sequencer Job when there are several.
`--status`, `--cancel`, and `--collect` address that attempt independently of
the submitting process lifetime. Object and network benchmarks do not use the
Kubernetes substrate.

### 4.3 Kubernetes Asynchronous Filesystem IO

The exact attempt, claim-run, and per-cell state machines; invariants;
linearization points; supported fault boundaries; and unsupported situations
are normative in
[KUBERNETES_ELBENCHO_LIFECYCLE.md](KUBERNETES_ELBENCHO_LIFECYCLE.md).

**Claim-qualified roots.** On Kubernetes every `TEST_DIRS` key is
`[namespace/]claim:path`, split at the first `:` (namespace and claim names
cannot contain `:`). The namespace defaults to `KUBECTL_NAMESPACE`, and `path`
is relative to the claim. All roots of one map must share a namespace, because
a Pod can mount claims only from its own namespace; a map spanning namespaces
is rejected with a pointer to separate targets (§4.5). Weights and modes keep
their meaning on every substrate: several roots form one aggregate target
with load split by weight and force completion mode, and the single-root
modes still need exactly one root. Each claim must be Bound, RWX, and in
Filesystem volume mode; there is no PV setting, and the claim's bound PV name
and the namespace, PV, and PVC UIDs are recorded in the attempt identity and
checked for drift. Unqualified keys, and the removed single-claim settings of
v1.x, fail before anything runs and print a replacement `TEST_DIRS` line, with
the real claim name when `KUBECTL_PVC` is still set (see
[Upgrading from v1.8.0](FILESYSTEM_TESTING.md#upgrading-from-v180)).

**Mount layout.** Every Pod (workers, coordinator, helpers, validation) mounts
each claim its namespace's groups use at `/mnt/storage-scale-test/<claim>`, and
`claim:path` maps to `/mnt/storage-scale-test/<claim>/<path>`; the
coordinator's path checks validate each root against its own claim's mount
root. Each root must be an existing directory writable by the workload identity, but a claim's mount
root need not be. The lexically first (bytewise) normalized root (`namespace/claim:path`)
of the namespace holds a reserved `.storage-scale-test` subtree for control
state, locks, completed-cell publications, and recovery metadata; no workload
path may overlap it.

**Submission.** The submitting host acquires one deterministic Lease per
claim, keyed by the claim's UIDs, in sorted (namespace, claim) order, and
releases them in reverse order. It creates attempt-scoped ownership metadata
and, per namespace, stages the control bundle and ledger on the control root
and starts one elbencho worker per selected Ready node in an owned DaemonSet
and a single coordinator Job. The coordinator has no Kubernetes API
credentials: it runs the copied control bundle, uses frozen Pod IPv4
endpoints, and writes active benchmark output to Job-local scratch. After each
cell reaches a terminal state, its result artifacts are copied from scratch to
the control root and an atomic publication manifest records the completed
cell. This bounds result loss if the submitting `kubectl` credentials expire or
the coordinator Pod is replaced.

The local lifecycle commands operate on the saved attempt identity (schema 4,
which lists the claims of each namespace segment) rather than today's
`env.sh`: `--status` reads durable state, `--cancel` stops the exact owned Job
and publishes cancellation, and `--collect` validates and retrieves the
published artifacts into the local result directory before releasing the
Leases and deleting owned Kubernetes resources. `--resume` for a Kubernetes
attempt is collection-gated: collect first imports partial results, then a new
sweep can resume the failed cells from the local execution ledger. Coordinator
loss, endpoint replacement, cancellation, and retry-safe collection are
treated as recoverable lifecycle events; ownership labels, annotations,
resource UIDs, and an attempt nonce prevent adopting unrelated objects.
Attempts started by v1.x use an older identity schema; v2.0.0 refuses them.

A batch whose groups use several namespaces runs one such segment per
namespace (§4.5).

**Rationale:** Naming the claim in every root makes an aggregate across
filesystems just several claims in one map, and makes "several roots but one
claim" impossible to misread. The v1.x model (one unqualified claim setting,
keys relative to it) could not span claims and was ambiguous for aggregates.

### 4.4 Filesystem IO Reification and Resume

Before a new filesystem IO sweep starts, the orchestrator expands the complete
Cartesian product `(nodes, IO size, threads, IO depth)`. Each cell becomes a
sourceable `executions/NNNN.sh` definition and an atomic `NNNN.status` sentinel
initially containing `PENDING`. A running execution transitions through
`RUNNING` to `SUCCESS` or `FAILED`; its log, exit code, and Slurm job ID (when
applicable) are stored beside it.

In Slurm mode, one coordinator allocation is sized to the maximum node count
among non-successful executions. Elbencho services start once across that
allocation. The coordinator then runs cells sequentially in their reified order,
using the first requested number of allocation hosts for each cell. In SSH mode,
services start once across the reachable host pool; the local dispatcher selects
a fresh host subset for each cell and runs all cells sequentially.

Both paths abort the remaining sequence after the first failure. The operator can
correct the problem and run `nv-elbencho-sweep.sh --resume <results_dir>`.
Resume sources the saved `env_used.sh`, converts stale `RUNNING` state back to
`PENDING`, skips every `SUCCESS` cell, and dispatches the rest in order. A dispatch
lock prevents concurrent Slurm coordinators or SSH resume loops from operating on
the same execution directory.

**Rationale:** Reification provides an auditable record of the intended sweep and
makes the smallest resumable unit one parameter cell, while a single maximum-sized
Slurm allocation avoids scheduler churn and repeated service startup.

### 4.5 Prepared Filesystem Batches

Both filesystem launchers share local `--batch`, `--append`, and `--start`
operations through `lib/_batch_functions.sh`. Preparation saves immutable IO or
metadata groups without dispatching. `batch-manifest.tsv` commits their ordered
membership, snapshot hashes, global execution IDs, and definition hashes by
atomic rename. One root ledger owns cell states; group directories own snapshots,
benchmark artifacts, completion evidence, and core dumps. Uncommitted staging
is not executable. The existing dispatch-lock ownership checks protect append
and seal operations.

The common execution environment and host/scheduler-list contents are frozen at
creation. Group target and workload settings may differ, through `env.sh` edits, a
`--target` file, or `--env-override` files (§3.5). Start performs non-mutating
preflight, checks that the manifest revision is unchanged, and permanently
seals it before external mutation. Submission failure never reopens
preparation. Every cell restores its own saved configuration in an isolated
context. Ordinary non-batch layouts and dispatch remain unchanged.

**Storage targets.** A target is one `TEST_DIRS` map, and separate targets
are separate groups on every substrate. `--target FILE` (§3.5) is the way to
submit several: N flags publish N groups in command-line order, and
`_elbencho_batch_publish_groups` commits all of a submission's groups under
one dispatch lock with one atomic manifest rename, so a crash never leaves a
partial target set. Each group's snapshot records a storage target name
(`STORAGE_TARGET_NAME`, else the sorted `TEST_DIRS` roots joined with `,`,
normalized to `namespace/claim:path` on Kubernetes).
`lib/storage_target.py` and `lib/env_functions.sh` share this identity rule,
and it is metadata only. `--status` reports each group's name as
`GROUP_<NNNN>_TARGET`. Batch reports are per group and so per target. Only a
single report whose inputs name different known targets (several results
directories, or a combined CSV) is refused, unless `--allow-mixed-targets` is
given. See
[Testing several filesystems](FILESYSTEM_TESTING.md#testing-several-filesystems).

**Kubernetes segments.** On Kubernetes, `KUBECTL_NAMESPACE` (the default
namespace for keys), the selector, image, pull policy, UID/GID, and
sequencer image (as resolved at preparation) are frozen common settings;
claims vary per group.
Batch preflight checks every group's roots and execution paths, and the
control root; for the namespaces of the cells the next attempt submits, it
checks claim identity and Lease permission, the 32-claim limit, the sequencer
settings when they span namespaces, and enough Ready nodes. An attempt has one
**segment** per namespace (at most 16), in the order each namespace first
appears in the batch ledger;
cells run in ledger order within a segment, so execution is namespace-major
(groups A, B, A, B with A and B in different namespaces run A, A, B, B). A
segment owns its claims' Leases, one worker DaemonSet and one coordinator Job
that mount all of the namespace's claims, its NetworkPolicies, and its control
root; each cell uses its own group's roots, so every workload mode is
unchanged.

- **One namespace** (the common case, including several targets in that
  namespace): one segment, a plain coordinator Job, and no sequencer,
  ServiceAccount, or RBAC.
- **Several namespaces:** submission creates every segment's Leases, run tree
  and workers, then each coordinator Job suspended, before any cell runs, so a
  claim that cannot mount fails the submission and rolls back every namespace.
  A sequencer Job (Kubernetes 1.24 or newer; a pinned default image or a
  digest-pinned `KUBECTL_SEQUENCER_IMAGE`) unsuspends each Job after its
  predecessor completes and stops at the first failure. It runs, with its
  ServiceAccount, in the first segment's namespace; its token is the only
  Pod-held API credential, scoped by a Role per namespace (`resourceNames`)
  and a UID precondition to `get` and `patch` on that attempt's Jobs. The
  sequencer re-derives progress from Job states, and `--status` performs the
  same idempotent advance with the user's credentials if the sequencer is
  lost. `--status` adds `SEGMENT_COUNT`, `SEGMENT_CURRENT`,
  `SEGMENT_<i>_NAMESPACE`, and `SEGMENT_<i>_STATE` (`i` from 0). Worker drift
  in any unfinished segment fails the whole attempt at once and marks later
  segments never started; cancellation stops the sequence, acting on the next
  segment when the running one already succeeded, and never overwrites a
  finished segment. Collection is refused until the attempt is terminal and
  publishes an aggregate `run.status` and `run-summary.tsv` at the results
  root beside per-namespace `run-<namespace>.status`,
  `run-summary-<namespace>.tsv`, `startup-error-<namespace>.txt`, and
  `coordinator-loss-<namespace>.tsv`.
  `validate_env.sh` warns when the image does not pull and provide its tools
  (a short-lived Job, no API call), the server is older than 1.24, or the
  RBAC is missing; `--sequencer` proves the image, token, and RBAC in its
  namespace by running the real sequencer in a probe Job against absent Jobs,
  reporting failures as errors.

The attempt identity lists only segments that own executions, so a resume
whose remaining cells use one namespace runs without a sequencer. The
lifecycle contract is normative for names, keys, and faults.

**Rationale:** Alternatives considered and rejected:

- *A Kubernetes-only list of claims expanded into one group each*: it could
  not express per-target sizing or layouts and duplicated what batch groups
  and `--target` already do on every substrate.
- *One segment per claim, chained in one Pod by init containers when the
  claims share a namespace*: unnecessary once one coordinator mounts every
  claim of its namespace, and it added a second execution mode with its own
  recovery rules.
- *Unqualified keys plus a single claim setting*: ambiguous for aggregates and
  unable to span claims (§4.3).
- *`--env-override` setting target settings*: two overlapping ways to say what
  to test (§3.5).

The sequencer remains only where Kubernetes forces it, because one Pod cannot
mount claims from two namespaces; keeping a batch in one namespace, or one
batch per namespace, avoids it and its RBAC.

SSH stays host-driven; Slurm acquires one maximum-sized allocation, and
Kubernetes selects enough workers for all pending cells in one attempt.
Kubernetes retains its existing attempt ownership, Lease, publication, and
collection/resume gates; each segment's control root comes from the sealed
union of its namespace's test roots. Control bundles retain the full
batch manifest and group provenance, including on partial resume.

`utils/extract-filesystem.py` delegates to the existing reporters independently
per group. It snapshots only authoritative successful evidence into temporary
inputs, writes disjoint group reports and an index, and never averages across
group boundaries or contacts the cluster. The specialized reporter entry points
share this batch routing while preserving legacy and cached-input behavior.
All three entry points share analysis option definitions. The unified reporter
routes common options to both kinds and type-specific options only to matching
selected groups, rejecting unused options. Filtered runs atomically rebuild the
whole-batch index from current cell states and retained group reports.

### 4.6 Remote Scriptlet and Result-Transfer Patterns

SSH-mode nodes may not share the repository or output filesystem with the launch
host. The launch host therefore copies the required benchmark binary, helper
libraries, and, for object tests, a mode-restricted copy of the object-auth file
to the SSH working directory.

Metadata, object, and network dispatchers transmit checked-in remote scriptlets
with their configuration as positional arguments. Filesystem IO instead generates
an inline scriptlet by concatenating the saved `NNNN.sh` execution definition with
an SSH-specific tail. The tail selects the saved cell, sources the copied
`_elbencho_functions.sh`, and runs that one iteration. These scriptlets do not
source the launch host's live `env.sh`.

Filesystem IO retrieves only the current cell's existing result artifacts through
a compressed `tar | tar` stream. The other SSH dispatchers retrieve their remote
result directory through the same streaming archive pattern. Binary and helper
deployment uses the shared SSH copy helpers; result retrieval is not based on
`scp` or `rsync`.

---

## 5. Benchmark Worker Lifecycle

### 5.1 Coordinator/Service Pattern

Multi-node benchmarks use the benchmark tool's distributed architecture:

1. A service or client process starts on each participating node and listens on
   a benchmark port.
2. A coordinator on one node drives the benchmark against those workers.
3. The coordinator writes results to shared storage in Slurm mode or to its SSH
   working directory for later retrieval.

Single-node cases can run the benchmark directly without a separate service
fleet. Multi-node Slurm workers are normally started by a background `srun`;
SSH workers are started with `spawn_N_ssh`, and the coordinator is invoked with
`run_ssh_single` on the selected head host.

### 5.2 Service Lifecycle by Benchmark

| Benchmark | Lifecycle |
|-----------|-----------|
| Filesystem IO | Slurm starts elbencho services once on the maximum-sized allocation; SSH starts them once on the usable host pool. Health checks can restart unhealthy services between phases. All services stop when the sweep dispatcher exits. Kubernetes uses one attempt-scoped worker DaemonSet per namespace segment (§4.3). |
| Filesystem metadata | Slurm and SSH reuse sweep-wide elbencho services across numbered `(nodes, tasks)` executions; Kubernetes uses an attempt-scoped worker fleet. |
| Object storage | Each node-count dispatch starts Warp clients, runs the object-size/thread work, then terminates the clients. |
| Network | Each node-count dispatch starts elbencho services and reuses them for the iteration/thread sweep, checking health between Slurm runs. |

Bidirectional netbench starts two service instances per node on adjacent ports
and runs two coordinators in parallel, one for each direction. Unidirectional
mode uses one service per node and runs both directions sequentially.

---

## 6. Sweep Loop Structure

### 6.1 Multi-Dimensional Parameter Sweeps

Each benchmark type sweeps across multiple dimensions, but their loop placement
differs:

| Benchmark | Sweep order and execution unit |
|-----------|--------------------------------|
| Filesystem IO | Reify `nodes → IO size → threads → IO depth`; each Cartesian cell is one sequential, resumable execution. |
| Filesystem metadata | Reify `nodes → tasks-per-node`; each sequential execution loops over `MDTEST_ITERATIONS` and can be retried. |
| Object storage | Dispatch each node count; inside it, loop over object sizes. PUT reaches the configured minimum object count at the last configured thread value, then GET sweeps all thread values before cleanup. |
| Network | Dispatch each node count; inside it, loop over iterations and then thread values. Each unidirectional cell runs A→B and B→A; bidirectional runs both concurrently. |

### 6.2 Node Count Specification

The `parse_range_specification()` function in `lib/env_functions.sh` parses
flexible node-count specifications into arrays:

| Input | Expansion |
|-------|-----------|
| `4` | `4` |
| `1,2,4,8` | `1 2 4 8` |
| `1-8+2` | `1 3 5 7 8` (always includes endpoints) |
| `1-4,8,16-32+8` | `1 2 3 4 8 16 24 32` |

This allows arbitrary orderings (including descending), sparse sequences, and
mixed specifications. Filesystem IO, filesystem metadata, and network entry
points require the explicit `--nodes` flag. The Warp entry point additionally
supports its legacy positional `max_node_count [increment_by]` form; it rejects
mixing positional arguments with `--nodes`.

### 6.3 Dispatch and Failure Boundaries

Object and network sweeps retain separate dispatches at the boundaries shown
in Section 4.2. Filesystem IO and metadata each use one Slurm coordinator
allocation or SSH dispatcher for the full remaining Cartesian product.
Scheduler walltime for each workload must cover every remaining cell, including
service checks, configured pauses, completion-based data volume, and cleanup.
Its first failed cell stops the sequence; `--resume` provides recovery at the
cell boundary.

---

## 7. Benchmark Tool Invocation

### 7.1 Filesystem IO (elbencho)

The IO entry point supports four related data models. All use the same reified
Cartesian sweep and result naming, but termination and cleanup semantics differ.

#### Worker-directory workload (default)

`ELBENCHO_FILE_LAYOUT=worker-directories` preserves the many-file workload.
Mkdir is separate. In this layout, a single `TEST_DIRS` root with weight 1
and direct IO uses timed writes and reads by default. Buffered IO, multiple
distinct roots, or `--run-to-completion` selects completion mode for both
phases; each requested
phase processes its finite dataset without benchmark time limits or repetition.
A sole `TEST_DIRS` root must have weight 1. Each thread visits every weighted
target.
`ELBENCHO_FILES_PER_NODE` budgets the total per node, rounded to the nearest
multiple of threads times summed weights (ties upward, minimum one file per
thread per target). Without an explicit count, FS budgets and duration derive
automatic counts. In completion mode, duration sizes the dataset rather than
limiting runtime. The effective mode is saved with execution coordinates; its
reason is printed during initial staging. Resume preserves the recorded
semantics rather than reinterpreting the request.

Unless `ELBENCHO_FILE_SIZE` is set, generated file size is the write block size
times `ELBENCHO_FILE_SIZE_MULTIPLIER` (default 1024). The CLI modes are:

- Default: mkdir → write → optional pause → read → cleanup.
- `--write-only`: mkdir → write, retain the uniquely suffixed dataset, and print
  `ELBENCHO_WRITE_ONLY_DATA_DIR`.
- `--write-no-read`: mkdir → write → cleanup.
- `--read-from <directory>`: scan or reuse a saved treefile for an existing
  dataset and run only the read phase. On Kubernetes the path is
  `[namespace/]claim:path` or the Pod path that `--write-only` printed.
- `--delete-only <directory>`: validate that the path is a strict descendant of
  the configured test root (`TEST_DIRS` from `env.sh` or one `--target`), then remove it on one compute node.

For directory `--read-from`, a successful initial scan can publish
`.storage-scale-test-elbencho-treefile.txt` in the dataset. Later sweeps reuse it;
the operator removes it after modifying the dataset. The per-execution workload
metadata records dataset totals and cache hit/miss behavior. Direct IO staged
reads are time-limited by default. Buffered IO or `--run-to-completion` reads
the scanned dataset to completion, regardless of `ELBENCHO_FILE_LAYOUT`.

#### Generated shared-directory workload

`ELBENCHO_FILE_LAYOUT=shared-directory` with `ELBENCHO_FILES_PER_NODE` generates
a bounded checkpoint-like workload in one shared flat directory. It requires one
`TEST_DIRS` root with weight 1. Each thread value must evenly divide the configured
files per node, giving `files_per_worker = files_per_node / threads`; aggregate
file count is `nodes × files_per_node`. `ELBENCHO_FILE_SIZE` fixes the per-file
size, or the write block size and multiplier derive it. Validation requires an
exact file-size/block-size division for direct or random phases; buffered
sequential IO may complete a final short block.

Generated shared-directory phases are exact-completion operations. Mkdir, write,
read, and distributed file deletion do not use `--timelimit` or `--infloop`.
The mkdir command must complete successfully, and write/read/delete JSON counters
must match their expected totals before the cell succeeds. The runner also records
workload metadata and write, delete, and lifecycle timings. A normal default run
uses a new, proven-empty, uniquely suffixed target and removes it after the read.
`--write-only` deliberately retains the target; `--write-no-read` performs the
verified distributed delete. Failure and signal handlers make a best-effort
attempt to remove a generated target and record whether cleanup succeeded.

#### Single shared large file

`ELBENCHO_SINGLE_BIG_FILE=1` selects regular-file path mode and permits only
sequential IO. A generated write/default run requires
`ELBENCHO_SINGLE_BIG_FILE_SIZE`; it writes and, unless suppressed, reads one exact
file extent before cleanup. By default elbencho partitions the file across
services. `ELBENCHO_ALL_NODES_ACCESS_ALL_DATA=1` adds `--nosvcshare`, making every
node access the whole file independently.

With `--read-from <file>`, the file's metadata supplies its extent and no treescan
or treefile is used. Direct IO repeats until the configured time limit.
Buffered IO or `--run-to-completion` reads the file extent without a time limit
or repetition.

#### IO pattern and cache controls

An IO-size entry encodes both sizes and access patterns:

- `4K` = sequential 4K write and read.
- `r4K` = random 4K write and read.
- `1M,r4K` = sequential 1M writes and random 4K reads.

For multi-node reads, the host list is rotated so readers do not retain the same
writer-to-file or writer-to-slice assignment. Reified filesystem IO executions
also advance the rotation between separate invocations. This reduces client-cache
reuse across phases and cells. Buffered IO runs to completion without
repetition to avoid repeatedly measuring the same warm page-cache data; this
does not guarantee cold caches. Direct IO remains the recommended baseline
when page-cache effects are not part of the workload being measured.

### 7.2 Filesystem Metadata (mdtest-elbencho)

Three separate elbencho invocations per iteration: **create → stat → delete**.

**Avoiding cache effects:** Between phases, the host assignment list is
rotated via `rotate_csv_list()`. This ensures stat and delete operations target
files created by different nodes, defeating client-side metadata caching. If
node A creates the files, node B stats them and node C deletes them, the
client dentry/inode cache provides no benefit.

**Standard directory structure:** The runner creates one
`mdtest-elbencho-target-N<suffix>` target per unit of `TEST_DIRS` weight, then
pre-creates `MDTEST_BRANCH_FACTOR` `b{i}` directories under each target. It
configures elbencho for `MDTEST_BRANCH_FACTOR²` directories per thread. The wide
tree increases metadata pressure and can spread work across filesystem metadata
servers.

**Dense directory structure:** `--single-dir-file-target <count>` requires one
node count, one task count, and one generated test target. It uses elbencho's
`-n 0` layout so all workers create uniquely named files directly in one shared
flat directory. Since elbencho accepts one uniform file count per worker, the
requested total is rounded to the nearest achievable whole-worker total; both
requested and actual values are recorded in `env_used.yaml`.

**Zero-byte files** (`-s 0`) isolate pure metadata operation rates from
any data transfer overhead.

### 7.3 Object Storage (warp)

**Bucket cleanup → PUT-until-minimum → GET thread sweep → DELETE cleanup** per
node-count/object-size configuration.

```
warp put --host <endpoint> --bucket <bucket> --obj.size <size> \
    --concurrent <threads> --duration <put_duration> --warp-client <nodes...>
warp get --host <endpoint> --bucket <bucket> --obj.size <size> \
    --concurrent <threads> --duration <get_duration> --warp-client <nodes...>
warp delete --host <endpoint> --bucket <bucket> --list-existing \
    --warp-client <nodes...>
```

The PUT uses the last value in `WARP_THREAD_LIST` and repeats until the aggregate
object count reaches `WARP_PUT_MIN_FILES_PER_CLIENT × node_count`. GET then runs
once for each configured concurrency. The thread list is not sorted, so the PUT
concurrency is not necessarily the numerically largest value. Cleanup before and
after the configuration prevents residual objects from affecting its PUT metrics;
the bucket is therefore destructive benchmark state and must be dedicated to the
run.

Optional flags include `--multipart` for multipart uploads, `--ranged` for
byte-range reads from larger objects, and `--s3-express` for the corresponding
S3 Express signing and endpoint behavior.

**RPS budgeting:** `WARP_RPS_BUDGET_PUT` and `WARP_RPS_BUDGET_GET` set aggregate
request-per-second budgets. The runner derives a per-node Warp limit, and Warp
apportions that limit across its concurrency, to respect object-storage rate
limits.

### 7.4 Network (elbencho netbench)

Nodes are split into two groups (A and B). The coordinator drives traffic
between the groups using elbencho's `--netbench` mode:

**Unidirectional (default):** Runs A→B, then B→A sequentially. Two benchmark
runs per iteration.

**Bidirectional (`--bidirectional`):** Runs A→B and B→A simultaneously using
two coordinators on different ports. Tests full-duplex capacity.

**Runtime normalization:** Per-thread transfer size is calculated as:

```
per_thread_size = (TARGET_RUNTIME × NIC_GBPS × 125MB) / threads
```

As thread count increases, per-thread work decreases, keeping wall-clock time
approximately constant when the NIC is saturated.

**Shuffling:** Group assignments are reshuffled between iterations to avoid
systematic bias from network topology.

---

## 8. Results & Output Structure

### 8.1 Datestamped Output Directories

Every sweep run creates a single output directory with a UTC datestamp:

```
$RESULTS_DIR/
├── elbencho-20250815Z143022/
│   ├── env_used.yaml
│   ├── env_used.sh
│   ├── executions/
│   │   ├── 0001.sh
│   │   ├── 0001.status
│   │   ├── 0001.log
│   │   └── ...
│   ├── elbencho-1M-c_001-s_032-d_001_20250815Z143022.csv
│   ├── elbencho-1M-c_001-s_032-d_001_20250815Z143022.out
│   ├── elbencho-1M-c_004-s_032-d_001_20250815Z143022.csv
│   └── ...
├── warp-20250816Z091500/
│   ├── warp-GET-16MiB-c_001-s_064_20250816Z091500.json.zst
│   └── ...
├── mdtest-elbencho-20250817Z120000/
│   └── ...
└── netbench-half-20250818Z080000/
    └── ...
```

**Rationale:**

- The datestamp answers "when was this run?" at a glance.
- Each directory is self-contained: all files from one campaign are together.
- Different runs never collide, even if parameters are identical.
- Analysis scripts take directories as input, not individual files — the
  directory *is* the unit of analysis.

Filesystem IO result directories intentionally preserve state between
invocations. `env_used.yaml` is the human/tool-readable configuration snapshot;
`env_used.sh` is the sourceable snapshot used by `--resume`. The `executions/`
directory is the execution ledger and may also contain exit codes, Slurm job IDs,
exact-completion JSON, workload TSV records, core files, and treefile-cache usage
records. Metadata sweeps write `env_used.yaml` and a sourceable `env_used.sh`
snapshot and use the same typed execution ledger. Both snapshot kinds record the
effective `STORAGE_TARGET_NAME` (§4.5), which the extractors read back. Filesystem `env_used.sh`
always records `STORAGE_SCALE_TEST_ENV_OVERRIDE_{FILE,SHA256,VARIABLES}` and
the arrays `STORAGE_SCALE_TEST_ENV_OVERRIDE_{FILES,SHA256S,FILE_VARIABLES}`
(empty without an override, so sourcing one group's snapshot after another's
cannot inherit provenance; snapshots with only the scalars are normalized to
one-entry arrays); `env_used.yaml` carries an `env_override` mapping (`file`,
`sha256`, `variables` for the last file and the union, plus `files`, a list of
`{file, sha256, variables}` in application order) or `null` (§3.5). The
`--target` file is recorded separately, always present and empty without one:
`STORAGE_SCALE_TEST_TARGET_FILE{,_SHA256,_VARIABLES}` in `env_used.sh` and
`target_file` (`null` or `{file, sha256, variables}`, with the operator's
original path for a batch) in `env_used.yaml`. Kubernetes snapshots record
the resolved `KUBECTL_NAMESPACE` and the Pod paths as
`KUBECTL_MAPPED_TEST_DIRS`; bound PVs and UIDs live in the attempt identity. Separately, staged
directory reads can persist their reusable treefile cache in the dataset,
outside the result directory.

### 8.2 File Naming Convention

Result files encode the configuration in the filename:

```
<tool>-<op>-<params>-c_<nodes>-<spec>_<datestamp>[_iter<N>][_<direction>].<ext>
```

Examples:
- `elbencho-1M-c_004-s_064-d_008_20250815Z143022.csv` — 1MiB IO, 4 nodes, 64 threads, 8 IO depth
- `warp-GET-16MiB-c_001-s_064_20250816Z091500.json.zst` — GET, 16MiB objects, 1 node, 64 threads
- `netbench-half-c_008-t_016_20250818Z080000_iter2_AtoB.csv` — 8 nodes, 16 threads, iteration 2, A→B

This makes it possible to identify results without opening files, and allows
glob-based filtering for partial re-analysis.

---

## 9. Reporting & Analysis

### 9.1 Self-Bootstrapping Python Analysis Tools

Each analysis tool is an executable Python entry point:

```
utils/extract-elbencho.py
utils/extract-warp.py
utils/extract-mdtest-elbencho.py
utils/extract-netbench.py
utils/extract-filesystem.py
utils/summarize-elbencho.py
```

The Python entry point handles its own runtime setup:

1. Parses help and version requests with the standard library before importing
   runtime dependencies.
2. Locates the repository root and uses the standard-library bootstrap in
   `lib/python_bootstrap.py` to create or reuse `.venv/` and install pinned
   `requirements.txt` when its hash changes.
3. Re-executes under that environment, then imports the reporting implementation.

The virtualenv is cached and bootstrap operations are locked, so concurrent
entry points safely share setup. Users can invoke the Python files directly;
they do not need a wrapper or a manually activated environment.

### 9.2 Analysis Workflow

```
Results directory → extract-*.py → Terminal tables + PNG plots [+ Markdown report]
```

Each analysis script:

1. **Parses** result files from the input directory (CSV, JSON, or text output).
2. **Aggregates** metrics across iterations/directions where applicable.
3. **Prints** summary tables to stdout, formatted for fixed-width terminal.
4. **Generates** PNG plots saved alongside the results.
5. **Optionally** produces `--markdown` output to stdout (with progress on
   stderr) suitable for pasting into Google Docs.

### 9.3 Markdown Report / Google Docs Workflow

The `--markdown` flag produces a complete report in Markdown on stdout. The
intended workflow:

1. `./utils/extract-elbencho.py --markdown results/elbencho-20250815Z143022/ > report.md`
2. Open Google Docs → Edit → Paste from Markdown
3. For each plot reference: Insert → Image → Upload from computer → select the
   corresponding PNG

This provides low-toil shareable reports without requiring dedicated reporting
infrastructure. The Markdown includes tables, section headers, and inline plot
references.

### 9.4 Filtering

All analysis scripts support filtering to reduce clutter:

```bash
./utils/extract-elbencho.py --only-sizes 4K --only-sizes 1M --only-threads 32,64 results/
./utils/extract-warp.py --only-sizes 16MiB --only-threads 64,128 results/
```

Malformed filters and filters that match neither aggregate nor live metrics
fail instead of silently producing an unfiltered or empty report.

Reports begin with the project versions that produced their results and the
reporter's version; see [VERSIONING.md](VERSIONING.md).

### 9.5 Plot Design Principles

- **Analyzer-specific accessible colors:** Filesystem IO and object plots use
  `tableau-colorblind10` for up to 10 series, `tab20` for 11–20, and `cividis`
  above 20. Metadata plots cycle `tableau-colorblind10`; network plots cycle a
  fixed seven-color palette.
- **Self-documenting titles:** Include operation, IO size, access pattern
  (Rand/Seq), IO mode (DirectIO/BufferedIO), and metric.
- **Consistent color mapping:** Pre-computed before plotting loops to avoid
  non-contiguous key bugs.
- **Single-node vs. multi-node:** SN plots use thread count on x-axis; MN plots
  use node count on x-axis.

---

## 10. Validation and Release

Changes are validated locally before committing. GitHub Actions runs the same
checks for pull requests and pushes to `main`:

| Check | Command |
|-------|---------|
| All local gates | `./utils/run_ci_checks.sh` |
| Concurrent static checks | `./utils/run_ci_checks.sh lint` |
| License compliance | `./utils/run_ci_checks.sh compliance` |
| Python unit tests | `./utils/run_ci_checks.sh pytest` |
| Shell static analysis | `./utils/run_ci_checks.sh shellcheck` |
| Python formatting | `./utils/run_ci_checks.sh black` |
| Python lint | `./utils/run_ci_checks.sh pylint` |

For pull requests and `main`, CI runs the static checks concurrently in one job
and runs `pytest-xdist` unit tests on the minimum supported Python version
(3.12) in another. Local full checks run those two phases concurrently and
buffer their output separately. A weekly and manually dispatchable workflow
tests Python 3.14 compatibility. CI does not publish benchmark binaries or
deployment tarballs; packaging is performed by users with
`utils/build_tarball.sh` after they have provided, helper-downloaded, or
helper-built the binaries needed for their tests.

### 10.1 Recommended Validation Stages

```
parallel static checks and unit tests ──► optional binary-helper scale tests ──► user packaging
```

| Stage | Purpose |
|-------|---------|
| shell/static analysis | Run ShellCheck for shell changes and any configured static analysis |
| Python tests | Run the repository's Python unit tests for parsing and reporting helpers |
| optional binary-helper scale tests | Exercise `utils/build/build_s3test_from_source.sh` and `utils/build/build_warp_from_source.sh` where compilers, Docker, and network access are available |
| user packaging | Run `utils/build_tarball.sh`, inspect warnings, and verify that the resulting deployment tarball contains the binaries required for the planned tests |

### 10.2 Release and Publishing

This project makes no design assumption that annotated tags publish deployment
tarballs, upload artifacts to external storage, create platform releases, or
publish static third-party binaries. If a project consuming this repository adds
such a pipeline, that pipeline should make its binary provenance,
license-compliance artifacts, and vulnerability-scanning responsibilities
explicit.

---

## 11. Security Considerations

### 11.1 Scope

NVIDIA Storage Scale Test is a benchmark tool, not infrastructure management
software. It operates on systems the user has already been granted access to.
**Securing the test bed is the user's responsibility.** The tool assumes:

- Slurm clusters are administered with appropriate access controls.
- SSH hosts have been configured with key-based authentication by the user.
- S3 credentials are managed and protected by the user.
- Kubernetes clusters, namespaces, RBAC, and claims are administered by the
  user (§11.7).

The tool is designed for an operator-controlled benchmark environment. It does
not establish an authorization boundary between mutually untrusted users. The
applicable organizational, contractual, regulatory, and data-handling obligations
depend on the environment and data selected by the operator; this design document
does not make compliance determinations for deployments.

### 11.2 Trusted Inputs and Persistent State

`env.sh`, the object-auth file, and `--target` and `--env-override` files are
sourced as Bash. They are trusted operator inputs and can execute arbitrary
commands with the invoking user's privileges.
Filesystem IO resume also sources the generated `env_used.sh` snapshot and each
reified `executions/NNNN.sh` definition. Result directories used with `--resume`
must therefore remain writable only by trusted users. Paths passed to
`--read-from` and `--delete-only` identify operator-controlled benchmark data;
the delete-only path is constrained to a strict descendant of the configured
test root.

This repository does not ingest arbitrary scriptlets from untrusted network
clients. Nevertheless, generated scriptlets and sourceable snapshots are code,
not passive data, and must be protected accordingly.

### 11.3 Credential Handling

- **S3 credentials** are stored in a file referenced by `OBJ_AUTH_FILE`. The
  README recommends mode `0400`. `lib/env_base.sh` sources it and exports the
  credential variables required by Warp. In SSH mode, the file is copied with
  a restrictive umask to `.obj_auth` in the remote working directory and sourced
  by the Warp scriptlet. Operators must secure and clean those working
  directories as credential-bearing locations.
- **SSH authentication** relies on the user's existing key-based SSH
  configuration (`~/.ssh/config`, `~/.ssh/authorized_keys`). No passwords are
  stored or transmitted by the tool.
- **Slurm authentication** uses the cluster's existing authentication
  mechanism (typically Munge). No additional credentials are needed.

### 11.4 Remote Execution

In SSH mode, the tool executes Bash on remote nodes through
`ssh host /bin/bash -s`. Checked-in scriptlets receive trusted configuration
values as arguments; filesystem IO scriptlets also contain the sourceable
reified cell definition. The remote shell sources copied project libraries and,
for object benchmarks, the copied auth file. Therefore repository contents,
configuration, reified state, result directories used for resume, and remote
working directories all belong to the trusted operator boundary.

### 11.5 Network Exposure

The intended deployment does not require inbound connections from outside the
cluster or trusted benchmark environment. Infrastructure administrators can
enforce that boundary with network policies, security groups, or firewalls.

Connections within that boundary are required. The launch or coordinator host
must reach SSH servers on SSH-mode clients. Elbencho and Warp workers listen on
benchmark ports while a run is active, and coordinators connect to them; netbench
can use two service ports plus elbencho's associated data ports. The exact ports
are configurable or tool-defined and must be permitted among participating
nodes. These benchmark services are not an authentication boundary, so their
ports must not be exposed to untrusted networks. Object tests also initiate
connections to the configured S3-compatible endpoint, and build helpers can
initiate internet connections when downloading source or upstream binaries.

### 11.6 Supply Chain

- NVIDIA does not publish prebuilt benchmark binaries or prepared deployment
  tarballs for this OSS project. Users decide which elbencho, Warp, and
  helper-built s3test binaries to include in their deployment tarball.
- `utils/build_tarball.sh` may download pinned upstream elbencho release
  binaries, build in-tree s3test binaries, and warn about missing Warp, but it
  does not make license, source-availability, SBOM, or vulnerability guarantees
  for the resulting binary set.
- `utils/build/build_warp_from_source.sh` enforces a hard-coded minimum Go
  version for CVE exposure control when it builds Warp from user-selected
  upstream source. `utils/build/build_s3test_from_source.sh` uses a current
  Alpine container (currently 3.24.x) for static OpenSSL/zlib builds and strips
  the resulting binaries.
- Users are responsible for binary provenance, vulnerability scanning, license
  compliance, and any required SBOM or source-offer artifacts for deployment
  tarballs they take into a test environment.
- Source-level static checks such as ShellCheck and Python tests reduce defects
  in the orchestration code, but they do not validate user-selected third-party
  binaries.

### 11.7 Kubernetes

- The operator owns the kubectl context credentials and the namespace RBAC
  that every lifecycle command uses; the tool deletes only objects it owns,
  verified by exact UID and ownership nonce.
- Anyone who can write a segment's control root (the `.storage-scale-test`
  subtree on its claim) can change what the coordinator runs, so the claims
  belong to the trusted operator boundary.
- The sequencer's ServiceAccount token, present only for batches spanning
  namespaces (and the temporary `validate_env.sh --sequencer` probe), is the
  only Pod-held API credential; its Roles allow `get` and `patch` on the
  attempt's named Jobs. Every other Pod sets
  `automountServiceAccountToken: false`.
- Attempt- and segment-scoped NetworkPolicies limit worker ingress and
  coordinator egress to the elbencho service port between the same segment's
  Pods, where the CNI enforces NetworkPolicy.
