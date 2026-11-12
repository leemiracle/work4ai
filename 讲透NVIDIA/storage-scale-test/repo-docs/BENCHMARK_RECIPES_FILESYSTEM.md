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

# Filesystem Benchmark Recipes

Suggested `env.sh` settings for common benchmark use-cases. These recipes
target the **elbencho filesystem IO sweep**
(`storage-tests/fs/nv-elbencho-sweep.sh`).

For full documentation on the variables, IO size syntax (the `r` prefix for
random IO, comma-separated write/read sizes), and the test workflow, see
[filesystem guide](docs/FILESYSTEM_TESTING.md) and the comments in
[env.sh.template](env.sh.template).

Each settings block below also works unchanged as an override file, so you
can run recipes without editing `env.sh`:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh \
    --env-override overrides/r2-requirements.env --nodes 8,16
```

Queue several with `--batch`/`--append`; each group keeps its own overrides.
`--env-override` may repeat within one command: the files apply in order, each
on top of the previous one, so recipes stack. Override files hold workload
settings only. The filesystem to test (`TEST_DIRS`, `STORAGE_TARGET_NAME`,
`FS_MAX_*`) comes from `env.sh` or from a target file passed with `--target`:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh \
    --target targets/vendor-a.env \
    --env-override overrides/r2-requirements.env --nodes 8,16
```

Recipes that edit a list with `+=` build on the earlier file's list, so make
each recipe set the lists it depends on outright when it must not depend on
what came before. See
[Workload override files](docs/FILESYSTEM_TESTING.md#workload-override-files)
and, for several filesystems,
[section 10](#10-testing-several-filesystems).

---

## Table of Contents

1. [General Principles](#1-general-principles)
2. [Recipe 1 — Find Peak Filesystem Scaling](#2-recipe-1--find-peak-filesystem-scaling)
3. [Recipe 2 — Confirm Minimum Performance Requirements](#3-recipe-2--confirm-minimum-performance-requirements)
4. [Recipe 3 — Quick Post-Maintenance Validation](#4-recipe-3--quick-post-maintenance-validation)
5. [Recipe 4 — Single Large File Testing](#5-recipe-4--single-large-file-testing)
6. [Recipe 5 — Shared-Directory Checkpoint Testing](#6-recipe-5--shared-directory-checkpoint-testing)
7. [Sequential IO Size Tuning](#7-sequential-io-size-tuning)
8. [Choosing Node Counts](#8-choosing-node-counts)
9. [Thread Count Sizing by CPU Count](#9-thread-count-sizing-by-cpu-count)
10. [Testing Several Filesystems](#10-testing-several-filesystems)

---

## 1. General Principles

### Sequential IO Size Should Match the Filesystem's RPC / Stripe Size

To find maximum sequential throughput, match the block size to the
filesystem's RPC or transfer size.

| Starting Point | When to Use |
|----------------|-------------|
| **1M** | Default when the optimal size is unknown; a common baseline for sequential throughput |
| **4M, 8M, 16M** | Try when documentation indicates a larger RPC, stripe, or transfer size, or when 1M underperforms in single-node sweeps |

If time allows, testing multiple sequential sizes (e.g., 1M and 16M) is
worthwhile — you may discover the sweet spot differs from these starting
points, especially on filesystems with non-default tuning. See
[§7](#7-sequential-io-size-tuning) for a sweep-based approach when the
optimal size is unknown.

### Random IO Uses Small Block Sizes

Random IOPS testing should use 4K blocks. This is the standard across all
filesystems and matches the common page size. The `r` prefix in
`ELBENCHO_SCALE_IO_SIZES` forces random IO (e.g., `"r4K"`).

**Note:** On kernels configured with 64K page size (common on aarch64 /
Grace platforms), DirectIO requires the IO size to be a multiple of the page
size. In this case the smallest usable IO size is 64K, not 4K. Use `"r64K"`
instead of `"r4K"` on these systems.

### Duration vs. Accuracy Trade-Off

Longer durations produce more stable, trustworthy results but increase total
wall time. Short durations risk measuring transient warm-up or cache effects
rather than sustained performance.

| Purpose | Recommended Duration |
|---------|---------------------|
| Exploratory / iteration on settings | 30–60 seconds |
| Production single- or multi-node sweep | 120–300 seconds |
| Quick post-maintenance check | 30–60 seconds |

Duration limits runtime only for timed runs, the default for direct IO to one
`TEST_DIRS` root. Buffered IO, multiple roots, `--run-to-completion`, and
generated shared-directory or single-file layouts instead run a fixed dataset
to completion; there, duration at most sizes an automatic dataset. See
[Finite dataset sizing](docs/FILESYSTEM_TESTING.md#finite-dataset-sizing).

### IO Depth

IO depth (`ELBENCHO_IODEPTH_LIST`) controls the number of outstanding
asynchronous IO operations per thread. Higher values help saturate
high-latency links (e.g., networked storage) but add complexity to the sweep
matrix. A good default starting point is `("1" "8" "32")`.

For initial exploration, leaving `ELBENCHO_IODEPTH_LIST` empty (which
defaults to IO depth 1 only) reduces the parameter space and speeds up runs.
Once you've narrowed down IO sizes and thread counts, add IO depth to the
sweep for finer characterization.

---

## 2. Recipe 1 — Find Peak Filesystem Scaling

**Goal:** Discover the maximum achievable throughput (GB/s) and IOPS for the
filesystem under test, and determine the node count at which performance
stops scaling (the "knee" of the curve).

This is the most thorough recipe. It uses wide parameter sweeps in the
single-node phase to find optimal per-node settings, then a multi-node
sweep to find the filesystem's aggregate limits.

### Phase 1: Single-Node Characterization

Run a broad single-node sweep to identify which thread counts saturate a
single node's NIC for each IO pattern. Use `r64K` instead of `r4K` on
64K-page kernels (see §1), and replace `1M` with your filesystem's sequential
size (see §7).

```bash
# env.sh or --env-override file: single-node peak-finding
export ELBENCHO_SCALE_THREAD_LIST=("1" "32" "64" "128" "256")
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")
export ELBENCHO_IODEPTH_LIST=("1" "8" "32")
export ELBENCHO_SCALE_READ_WRITE_DURATION=60           # 60s is fine for exploration
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1
```

Review the single-node report (`utils/extract-filesystem.py`) and identify:

1. The **first thread count** that saturates (or nearly saturates) the
   node's storage-facing NIC line rate for sequential IO.
2. The **thread count** that maximizes IOPS for random IO (`r4K` or `r64K`
   per §1).
3. The **best sequential IO size** for your filesystem (replace the default
   `1M` if the sweep shows a better size).

Use the random and sequential IO sizes chosen here in all later phases; their
examples show `("r4K" "1M")` as placeholders (substitute e.g. `("r64K" "8M")`).

### Phase 2: Multi-Node Scaling Sweep

Pare down the thread list to the 1–2 values chosen from single-node
results. Extend duration for trustworthy numbers.

```bash
# env.sh or --env-override file: multi-node peak-finding
export ELBENCHO_SCALE_THREAD_LIST=("64" "128")         # chosen from Phase 1
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")           # chosen from Phase 1
export ELBENCHO_IODEPTH_LIST=("1" "8" "32")
export ELBENCHO_SCALE_READ_WRITE_DURATION=300          # 5 min for publishable results
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
# Sweep one step past the storage server count (see §8).
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1,8,16,24,32
```

**What to look for:** The point where adding nodes stops increasing
aggregate throughput / IOPS. That's the filesystem's peak under the current
configuration.

### Phase 3: Max-Node Sustained Test

After identifying peak settings in Phases 1–2, run a single sustained test
at the highest available client node count. This validates that the
filesystem can maintain peak throughput over an extended period without
degradation (e.g., from thermal throttling, cache exhaustion, or write
amplification).

Use one thread count and one IO depth value — the combination that
produced the best results in Phase 2 — and two IO sizes covering both
ends of the spectrum (small random and large sequential).

```bash
# env.sh or --env-override file: max-node sustained test
export ELBENCHO_SCALE_THREAD_LIST=("128")              # best value from Phase 2
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")           # chosen from phase 1
export ELBENCHO_IODEPTH_LIST=("32")                    # best value from Phase 2
export ELBENCHO_SCALE_READ_WRITE_DURATION=1800         # 30 min sustained
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
# Run at the highest available client node count.
# Example: 32 client nodes available → test at 32.
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 32
```

**What to look for:** Compare the 30-minute sustained results against the
5-minute results from Phase 2 at the same node count. A significant drop
(>10%) indicates performance that isn't sustainable over time and warrants
investigation into caching behavior, storage tiering, or thermal limits.

### When Peak-Finding Is Hard

- **Not enough client nodes.** If the filesystem keeps scaling past your
  available client count, you can't find the true peak. Document the
  highest result and note that the filesystem was not saturated.
- **Multi-tenant filesystem.** Running at full scale may impact other
  tenants. Be cautious and coordinate with the storage administrators.
- **Filesystem limits at high node counts.** Some filesystems or
  deployments may become unstable or unresponsive at very high client
  counts. Scale node counts up gradually; if this occurs, cap node count and
  increase per-node concurrency (threads, IO depth) instead. See
  [§7](#7-sequential-io-size-tuning) for IO size and deployment tuning.

---

## 3. Recipe 2 — Confirm Minimum Performance Requirements

**Goal:** Verify that the filesystem meets a known performance target (e.g.,
contractual SLA, sizing-model expectation) without necessarily finding the
absolute peak.

This recipe is appropriate when:

- Users are already on the system and you can't monopolize enough nodes for
  peak-finding.
- You have a specific throughput or IOPS target to validate against.
- Time is limited but you need defensible numbers.

Use the same IO sizes and thread counts you would for peak-finding, but run
fewer node counts — just enough to confirm the target is met.

```bash
# env.sh or --env-override file: requirements confirmation
export ELBENCHO_SCALE_THREAD_LIST=("64" "128")         # known-good from prior peak-finding
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")           # chosen from Recipe 1 peak-finding
export ELBENCHO_IODEPTH_LIST=("1" "8" "32")
export ELBENCHO_SCALE_READ_WRITE_DURATION=300          # 5 min for defensible results
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
# Run at the node count your target expects, plus one smaller for comparison.
# Example: target is 200 GB/s at 16 nodes → test 8 and 16.
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 8,16
```

**Interpreting results:** If you meet or exceed your target at the expected
node count, the requirement is confirmed. If you fall short, you have two
data points to help diagnose whether the gap is per-node or aggregate.

### Relationship to Peak-Finding

If Recipe 2 falls short, use Recipe 1 to determine whether the filesystem
*can* meet the target at a different scale or configuration.

---

## 4. Recipe 3 — Quick Post-Maintenance Validation

**Goal:** After a maintenance event (firmware upgrade, configuration change,
node replacement), quickly verify that storage performance hasn't regressed.

This recipe prioritizes speed over thoroughness. Run a compact test, compare
against a known-good baseline from a prior Recipe 1 or Recipe 2 run.

```bash
# env.sh or --env-override file: quick validation
export ELBENCHO_SCALE_THREAD_LIST=("64" "128")    # same as your baseline run
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")       # from baseline run
export ELBENCHO_IODEPTH_LIST=("1" "8")            # 8 sometimes needed to get full IOPS
export ELBENCHO_SCALE_READ_WRITE_DURATION=60      # 60s is sufficient for comparison
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
# Match your baseline's node count(s).
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 8,16
```

**What to compare:** Generate a report with `utils/extract-filesystem.py` and
compare key metrics (sequential read/write GB/s, random 4K IOPS) against
the baseline. A regression of more than ~10% warrants investigation.

### Establishing the Baseline

The first time you run on a known-good system, save the results directory
and report in a durable location (both on the filesystem under test and
backed up elsewhere). This becomes the reference point for all future
Recipe 3 runs.

---

## 5. Recipe 4 — Single Large File Testing

**Goal:** Measure multi-host sequential throughput when all nodes cooperate
on a single shared file — the access pattern of checkpoint writes, container
image pulls, and packed-dataset reads.

This recipe uses `ELBENCHO_SINGLE_BIG_FILE=1` mode.  For background on the
env vars and access modes, see
[Single shared file](docs/FILESYSTEM_TESTING.md#single-shared-file).

### Choosing File Size

Set `ELBENCHO_SINGLE_BIG_FILE_SIZE` based on your workload:

* **Workload-driven (preferred):** Use the actual file size from your use
  case.  Examples: "Our checkpoint is 50G and must write in under 10
  seconds" or "Our container image is 12G and 64 nodes pull it
  simultaneously."  The benchmark validates whether the filesystem meets
  that requirement at the target node count — even if the total I/O time
  is short.
* **General exploration:** When there is no specific workload size, choose
  a file large enough that I/O lasts at least a few minutes at the expected
  aggregate throughput, so the measurement reflects sustained behavior
  rather than burst or cache effects.  A rough formula:
  `file_size ≈ aggregate_throughput_GiB/s × desired_seconds`.  For example,
  at 10 GiB/s aggregate write throughput, a 600G file gives ~60 seconds of
  sustained write time.

### DirectIO vs BufferedIO

This choice matters more for single-file testing than for the many-files
sweep, because page-cache effects are concentrated on one inode.

* **DirectIO** (the sweep default, no `-b` flag): bypasses OS page cache.
  Write throughput measures raw storage ingest speed.  Read throughput
  measures data fetched from storage, not local memory.  This is the right
  choice for measuring storage subsystem capability and for workloads that
  use O_DIRECT (some checkpoint libraries, NVIDIA Magnum IO GPUDirect
  Storage).
* **BufferedIO** (`-b` flag): reads and writes go through the OS page
  cache.  For writes, data may appear "written" faster if the kernel
  hasn’t flushed to storage yet (the sweep uses sync, but write-back
  caching on the storage side can still inflate numbers).  For reads, if a
  host reads a range it recently wrote (or that is still cached), throughput
  may be artificially high.  The sweep rotates the host list between write
  and read phases (when node count ≥ 2) to reduce this effect, but cannot
  eliminate it entirely.  BIO is the right choice when the workload itself
  uses buffered I/O and you want to measure application-observed throughput
  including cache effects.
* **Recommendation:** run DirectIO first to establish a storage baseline,
  then optionally BufferedIO if the workload uses buffered I/O.

### Phase 1: Write + Read at Target Node Count

Run a single-file write then read at the node count that matches your
workload (or a representative count from your many-files Recipe 1 results).

```bash
# env.sh or --env-override file: single-file testing
export ELBENCHO_SINGLE_BIG_FILE=1
export ELBENCHO_SINGLE_BIG_FILE_SIZE=50G          # set to your workload's file size
export ELBENCHO_SCALE_THREAD_LIST=("64" "128")    # from prior single-node characterization
export ELBENCHO_SCALE_IO_SIZES=("1M")             # use the value from Recipe 1 Phase 1
export ELBENCHO_IODEPTH_LIST=("1")
export ELBENCHO_READ_AFTER_WRITE_PAUSE=0
```

```bash
# Full pipeline: write then read (DirectIO, the default)
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 4,8,16

# Or staged: write-only (one thread value), then read separately
./storage-tests/fs/nv-elbencho-sweep.sh --write-only --nodes 8
# Prints ELBENCHO_WRITE_ONLY_DATA_DIR=/mnt/fs/elbencho-sweep-target-1-<DS>-e0001
./storage-tests/fs/nv-elbencho-sweep.sh \
    --read-from /mnt/fs/elbencho-sweep-target-1-<DS>-e0001/elbencho-bigfile --nodes 8
```

`--write-only` retains one dataset per cell, so use one thread value for the
staged write (the two values above would retain two files). With
`ELBENCHO_SINGLE_BIG_FILE=1`, `--read-from` must name the file itself: the
printed directory plus `elbencho-bigfile` (`ELBENCHO_SINGLE_BIG_FILE_BASENAME`).
Its size comes from the file, so `ELBENCHO_SINGLE_BIG_FILE_SIZE` may be unset.
On Kubernetes the printed directory is a Pod path, which `--read-from` accepts
as is; collect the `--write-only` run before a dependent `--read-from` or
report.

### Phase 2: Partitioned vs Full-File Read

Compare the two access modes at a representative node count:

* **Default** (`ELBENCHO_ALL_NODES_ACCESS_ALL_DATA` unset or `0`): each
  host reads a non-overlapping slice.  Total data read equals file size.
  Models cooperative parallel ingest (e.g. distributed data loading where
  each rank reads its shard).
* **`ELBENCHO_ALL_NODES_ACCESS_ALL_DATA=1`**: every host reads the entire
  file independently.  Total data read is N × file size.  Models the
  "N nodes all pulling the same container image or model weights" pattern.
  Stresses inode and file-level locking more heavily.

To run both modes in one batch, put the Recipe 4 settings in
`overrides/single-file.env`, and in `overrides/full-file-read.env` repeat
them plus `ELBENCHO_ALL_NODES_ACCESS_ALL_DATA=1`:

```bash
set -euo pipefail
IO=./storage-tests/fs/nv-elbencho-sweep.sh
BATCH=$("$IO" --batch --env-override overrides/single-file.env --nodes 8 |
    sed -n 's/^STORAGE_SCALE_TEST_BATCH_RESULTS=//p'); test -n "$BATCH"
"$IO" --append "$BATCH" --env-override overrides/full-file-read.env --nodes 8
"$IO" --start "$BATCH"
```

Compare per-host throughput between the two modes — full-file mode should
show roughly the same per-host throughput if the storage can serve the
parallel reads, but aggregate traffic is N× higher.

### Phase 3: Node-Count Scaling

Sweep node counts to find the single-file scaling curve:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1,2,4,8,16
```

Compare against many-files throughput at the same node counts (from
Recipe 1) to quantify the single-file overhead.  Single-file throughput
typically peaks at a lower node count than many-files due to inode and
lock contention.

### What to Look For

* **Single-file vs many-files:** How much throughput is lost by
  concentrating all I/O on one file?  This gap may reflect metadata and
  locking overhead, or a network/storage bottleneck in the subset of the
  storage system backing that file (e.g. a subset of storage servers or
  stripes).
* **Scaling plateau:** The node count where adding more nodes stops
  increasing single-file throughput.
* **Full-file read scaling:** With `ELBENCHO_ALL_NODES_ACCESS_ALL_DATA=1`,
  does per-host throughput remain roughly constant as nodes increase?
  If it drops, the filesystem may be bottlenecked on per-file metadata
  or locking.
* **DIO vs BIO gap:** If BufferedIO results are significantly higher than
  DirectIO for reads, page-cache hits are inflating the measurement.

### Cleanup

On SSH or Slurm, delete the retained directory (on Kubernetes, delete it from
a Pod that mounts the claim):

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --delete-only /mnt/fs/elbencho-sweep-target-1-<DS>-e0001
```

---

## 6. Recipe 5 — Shared-Directory Checkpoint Testing

**Goal:** Generate a bounded set of independently written files in one shared
directory. With one worker and one file per saving rank, this approximates a
checkpoint layout. It differs from Recipe 4's one shared file and from the
default many-file layout's per-worker directory tree.

### Map the Application Topology

Generated shared-directory mode gives each elbencho worker complete files; it
never puts multiple workers on one file. To model one file per single-threaded
saving rank, set both the `ELBENCHO_SCALE_THREAD_LIST` value and
`ELBENCHO_FILES_PER_NODE` to the saving ranks per node, and the
`ELBENCHO_IODEPTH_LIST` value to `1`. Do not multiply either count by writer
threads per rank: this mode cannot reproduce several writer threads sharing
one rank's file.

* `--nodes`: participating node count.
* `ELBENCHO_SCALE_THREAD_LIST` value: concurrent workers per node, and so the
  maximum active files per node. Each worker owns
  `ELBENCHO_FILES_PER_NODE / threads` complete files.
* `ELBENCHO_FILES_PER_NODE`: total files per node. It must be at least, and
  evenly divisible by, every thread value; the harness never rounds it.
* `ELBENCHO_FILE_SIZE`: exact size of each file.
* `ELBENCHO_IODEPTH_LIST` value: outstanding block I/Os per worker. It does
  not add writers to a file.

Total files are nodes × `ELBENCHO_FILES_PER_NODE`, total bytes are total files
× `ELBENCHO_FILE_SIZE`, and outstanding block I/Os per node peak at threads ×
I/O depth.

### Baseline Distributed Checkpoint Run

This models a distributed checkpoint (DCP): the write pattern produced when a
distributed training job saves model state, with each rank writing its own shard
in parallel. The example approximates eight saving ranks per node, one writer
thread per rank, and one 64 GiB checkpoint file per rank:

```bash
# env.sh or --env-override file; TEST_DIRS must have one root with weight 1
export ELBENCHO_FILE_LAYOUT=shared-directory
export ELBENCHO_FILES_PER_NODE=8
export ELBENCHO_FILE_SIZE=64G
export ELBENCHO_SCALE_THREAD_LIST=("8")
export ELBENCHO_SCALE_IO_SIZES=("1M")
export ELBENCHO_IODEPTH_LIST=("1")
export ELBENCHO_SINGLE_BIG_FILE=0
```

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 2,4,8
```

For each node-count execution, all files are placed directly in its one
generated `...-<DS>-e<NNNN>` target. Elbencho's service-worker ranks provide
unique flat filenames across nodes.

The mkdir, write, and read phases run to completion with no time limit or
repetition, and `ELBENCHO_SCALE_READ_WRITE_DURATION` is inactive. Size Slurm
walltime from the node count, `ELBENCHO_FILES_PER_NODE`, `ELBENCHO_FILE_SIZE`,
filesystem throughput, read-after-write pause, and cleanup.

For a checkpoint written by 12,000 single-threaded saving ranks, one per GPU,
with four GPUs per node, 3,000 nodes, one approximately 2.5 GiB file per rank,
buffered I/O, and no readback:

```bash
export ELBENCHO_FILE_LAYOUT=shared-directory
export ELBENCHO_SINGLE_BIG_FILE=0
export ELBENCHO_FILES_PER_NODE=4
export ELBENCHO_FILE_SIZE=2560M
export ELBENCHO_SCALE_THREAD_LIST=("4")
export ELBENCHO_SCALE_IO_SIZES=("512M") # replace with the observed write size
export ELBENCHO_IODEPTH_LIST=("1")
```

```bash
./storage-tests/fs/nv-elbencho-sweep.sh -b --write-no-read --nodes 3000
```

This creates exactly 12,000 files. Confirm the application's exact byte size:
`2560M` means 2.5 GiB, not 2.5 decimal GB. Elbencho's phase-level `--sync` is
only an approximation of each rank calling `fsync` on its own completed file.
The cleanup phase unlinks the just-written generated checkpoint rather than a
separate older checkpoint. It matches the configured file count, write
barrier, and distributed unlink work, but not age- or placement-dependent
metadata effects.

### Concurrency Variants

| `ELBENCHO_SCALE_THREAD_LIST` value | `ELBENCHO_FILES_PER_NODE` | `ELBENCHO_IODEPTH_LIST` value | Workload |
|---:|---:|---:|---|
| 1 | 1 | 1 | One file per node with one outstanding block I/O |
| 8 | 8 | 1 | Eight worker-owned checkpoint files per node, all active |
| 1 | 8 | 1 | One worker owns eight checkpoint files per node |
| 1 | 1 | 8 | One active file per node with eight queued I/Os |

The last row is a storage-stress variant. Increasing I/O depth changes
outstanding I/O within each active file; it does not add writer threads or
increase the file count.

### File and Block Sizes

`ELBENCHO_FILE_SIZE` supplies the exact generated many-file size. If it is
unset, file size remains the write block size multiplied by
`ELBENCHO_FILE_SIZE_MULTIPLIER`. The explicit value uses the same uppercase
`K`, `M`, or `G` size grammar as the other elbencho settings.

For direct or random I/O, the file size must be divisible by the effective
block size. This rule is checked independently for write and read components
of a compound size such as `"1M,4M"`.
Buffered sequential I/O does not require this divisibility. Choose compatible
values rather than relying on elbencho to reduce the requested file size,
because the checkpoint workload's byte total is exact.

### Retention, Cleanup, and Resume

Use the normal modes according to the desired dataset lifecycle:

```bash
# Retain the completed generated dataset and print its path.
./storage-tests/fs/nv-elbencho-sweep.sh --write-only --nodes 8

# Verify the write, then unlink the files through the same distributed workers.
./storage-tests/fs/nv-elbencho-sweep.sh --write-no-read --nodes 8

# Verify write and read, then remove the generated dataset.
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 8
```

Each phase must verify its exact file (and, for write and read, byte) counts
before the execution counts as complete; results record write, read, delete,
and end-to-end lifecycle times. `--resume <results_dir>` retries failed or
interrupted executions with the saved configuration.

### Reading a Staged Dataset

A staged read covers the scanned tree regardless of reader count: eight files
written by two nodes read as eight files and the same bytes on one or three
nodes. `ELBENCHO_FILES_PER_NODE` and `ELBENCHO_FILE_SIZE` are ignored.

```bash
./storage-tests/fs/nv-elbencho-sweep.sh \
    --read-from /mnt/fs/checkpoints/example --nodes 1,3
```

On Kubernetes, collect the `--write-only` run before reading or reporting it.

Direct IO staged reads are time-limited by default; buffered IO or
`--run-to-completion` reads the scanned dataset to completion. The first read
caches its scan in `<read-from>/.storage-scale-test-elbencho-treefile.txt`;
delete that file after changing the dataset.

---

## 7. Sequential IO Size Tuning

The recipes above use `"1M"` as a default sequential IO size. Replace it
with a value that matches your filesystem's documented RPC, stripe, or
internal transfer size.

### Choosing a Sequential IO Size

1. **Check documentation.** Consult your filesystem or storage administrator
   for the recommended client IO size. Match the filesystem's RPC or
   transfer size when known.
2. **Sweep when unsure.** If the optimal size is unknown, run a single-node
   sweep across several candidates (use `r64K` on 64K-page kernels; see §1):

```bash
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M" "4M" "8M" "16M")
```

Use the single-node results to identify which size maximizes throughput,
then narrow down for multi-node runs. Filter the report afterward with
`utils/extract-elbencho.py --only-sizes ...`.

3. **Compare nearby sizes.** When documentation suggests a size (e.g., 1M
   or 16M), testing both that value and one step larger or smaller can
   confirm whether the filesystem benefits from a different transfer size.

### Deployment Tuning Notes

- Thread counts up to 256 are common on high-core client nodes; see
  [§9](#9-thread-count-sizing-by-cpu-count) for CPU-relative sizing.
- An IO depth sweep (§1) helps find the IOPS peak for random IO.
- For node counts and scaling limits, see [§8](#8-choosing-node-counts) and
  [When Peak-Finding Is Hard](#when-peak-finding-is-hard).
- **Use longer durations.** 120–300s durations help ensure measurements
  reflect steady-state behavior, especially on tiered or buffered storage.
- **Read-after-write pause.** Storage with asynchronous data placement may
  need time between write and read phases for reads to reflect full
  capability. Set `ELBENCHO_READ_AFTER_WRITE_PAUSE` to **300–600 seconds**
  (5–10 minutes) when write-then-read results look inconsistent.
- **Burst vs. sustained write throughput.** Compare results at 60s vs.
  300s durations to quantify buffering or tiering effects on write
  performance.
- **Mount options.** For NFS mounts, options such as `nconnect` (TCP
  connections per mount) and `rsize`/`wsize` can significantly affect
  throughput. Document mount options (`mount` output) when reporting
  results.
- **Metadata-heavy workloads.** For create/stat/delete characterization,
  consider also running mdtest-elbencho (see
  [Metadata sweeps](docs/FILESYSTEM_TESTING.md#metadata-sweeps)).

---

## 8. Choosing Node Counts

### For Peak-Finding (Recipe 1)

The goal is to find where the scaling curve flattens. Ideal coverage:

1. **Start at 1 node** — establishes per-node baseline.
2. **Go one step past the storage server count** (e.g. 24 servers → 32
   clients) — if clients and servers have similar NIC bandwidth, the
   filesystem should saturate near a 1:1 ratio; the extra step confirms the
   plateau.
3. **Use enough intermediate points** to see the curve shape.

**Rule of thumb for node count list:**

| Storage Server Count | Suggested Client Node Counts |
|---------------------|------------------------------|
| 8 | `1,4,8,12` |
| 16 | `1,4,8,12,16,20` |
| 24 | `1,8,16,24,32` |
| 48 | `1,8,16,24,32,48,56` |

Adjust based on client node availability. If you can't get enough nodes,
test what you can and note that the filesystem wasn't fully saturated.

### For Requirements Confirmation (Recipe 2)

Run at the node count specified in the requirement, plus at least one
smaller count for comparison.

### For Post-Maintenance (Recipe 3)

Match the node count(s) used in the baseline run.

---

## 9. Thread Count Sizing by CPU Count

If your client nodes have significantly different CPU core counts than
the examples above, scale the thread list proportionally. A useful pattern
based on total CPU core count N (from `nproc`):

| Entry | Value | Rationale |
|-------|-------|-----------|
| 1 | 1 | Baseline single-thread (not expected to saturate) |
| 2 | N/4 | Quarter saturation |
| 3 | N/2 | Half saturation |
| 4 | N | Full core count |
| 5 | 2N | Oversubscription (tests IO depth via thread count) |

**Example for a 96-core node:**

```bash
export ELBENCHO_SCALE_THREAD_LIST=("1" "24" "48" "96" "192")
```

**Example for a 128-core node:**

```bash
export ELBENCHO_SCALE_THREAD_LIST=("1" "32" "64" "128" "256")
```

This CPU-relative approach produces reasonable sweep ranges regardless of
hardware, and the oversubscribed value (2N) often helps find the IOPS
ceiling for random IO workloads.

For multi-node sweeps, pare this down to the 1–2 values that saturated the
single node's NIC. There's no need to re-sweep the full thread range at
every node count.

---

## 10. Testing Several Filesystems

What to test comes from `env.sh` or `--target`; how to test comes from
`env.sh` or `--env-override`. A target file may set only `TEST_DIRS` (required),
`STORAGE_TARGET_NAME` and the `FS_MAX_*` estimates; an override file may set
only the
[supported workload settings](docs/FILESYSTEM_TESTING.md#workload-override-files).
Substrate, connection, and allocation settings stay in `env.sh`. The full
explanation is in
[Testing several filesystems](docs/FILESYSTEM_TESTING.md#testing-several-filesystems).

### Spread Load Across Several Filesystems (One Aggregate Target)

Several weighted roots in one `TEST_DIRS` form one target, and the load is split
by weight. Here `lustre-a` gets twice the load of `lustre-b`. On SSH or Slurm
the keys are paths that exist on every worker:

```bash
# env.sh or a target file
TEST_DIRS=(["/mnt/lustre-a/scale-test"]=2 ["/mnt/lustre-b/scale-test"]=1)
```

On Kubernetes the keys are `[namespace/]claim:path`. A key without a namespace
uses `KUBECTL_NAMESPACE`; all roots of one target must be in one namespace:

```bash
KUBECTL_NAMESPACE=validation   # in env.sh; a target file cannot set it
TEST_DIRS=(["lustre-a:scale-test"]=2 ["lustre-b:scale-test"]=1)
```

Recipes 1-3 run as usual, except that with more than one root, writes and
reads run to completion rather than for the configured duration. Recipes 4 and
5 and the staged `--write-only`, `--read-from`, and `--delete-only` modes need
one root with weight 1. Set `FS_MAX_AGG_THROUGHPUT`,
`FS_MAX_NODE_THROUGHPUT_GBPS` and `FS_MAX_NODE_IOPS` for the filesystems
combined; they size the generated dataset.

### Compare Several Filesystems (Separate Targets)

Give each filesystem its own target file and run one recipe against both as a
batch. `--target` is repeatable and creates one group per file, in
command-line order:

```bash
# targets/vendor-a.env (targets/vendor-b.env is the same for the second one)
STORAGE_TARGET_NAME=vendor-a
TEST_DIRS=(["/mnt/vendor-a/scale-test"]=1)   # Kubernetes: ["vendor-a:scale-test"]=1
                                             # (namespace from env.sh's KUBECTL_NAMESPACE)
```

```bash
IO=./storage-tests/fs/nv-elbencho-sweep.sh
BATCH=$("$IO" --batch --target targets/vendor-a.env \
    --target targets/vendor-b.env \
    --env-override overrides/r2-requirements.env --nodes 8,16 \
    | sed -n 's/^STORAGE_SCALE_TEST_BATCH_RESULTS=//p'); test -n "$BATCH"
"$IO" --start "$BATCH"
# Kubernetes only: wait for --status to print NEXT_ACTION=COLLECT, then collect.
# "$IO" --status "$BATCH"
# "$IO" --collect "$BATCH"
./utils/extract-filesystem.py "$BATCH"
```

You get group `0001` for `vendor-a` and `0002` for `vendor-b`, each reported
separately. Notes:

- The override applies to every target in the submission.
- A failed target stops the batch, so later groups do not run. Use one batch per
  target when the comparison must survive a failure.
- Only combining separately run results from different targets in one report
  needs `--allow-mixed-targets`; a batch never does.
- A plain run (without `--batch`) accepts only one `--target`; given more, it
  is rejected with the equivalent `--batch` and `--start` commands.
- On Kubernetes, targets in one namespace need nothing extra. Targets in several
  namespaces need the in-cluster sequencer and its RBAC; check them with
  `validate_env.sh --sequencer`.

---

## Quick Reference

| | Recipe 1 Ph 1–2 (Peak) | Recipe 1 Ph 3 (Sustained) | Recipe 2 (Requirements) | Recipe 3 (Validation) | Recipe 4 (Single File) | Recipe 5 (Checkpoint) |
|---|---|---|---|---|---|---|
| **Goal** | Find max throughput/IOPS | Verify sustained at peak | Confirm target met | Check for regression | Single-file multi-host throughput | Exact flat checkpoint files |
| **Thread list** | Wide (5+ values) then narrow | 1 best value | 1–2 known-good values | Same as baseline | 1–2 known-good values | Saving ranks (one writer each) |
| **IO sizes** | `r4K` / `r64K` + FS-specific seq size | `r4K` / `r64K` + FS-specific seq size | Same as Recipe 1 | Same as baseline | FS-specific seq size only | Workload block size |
| **IO depth** | `1 8 32` | 1 best value | `1 8 32` | `1 8` (fast) | `1` | `1` for checkpoint I/O |
| **Duration** | 60s explore → 300s publish | 1800s (30 min) | 300s | 60s | Workload file size driven | Inactive; exact completion |
| **Node counts** | 1 to past server count | Max available | Target count + 1 smaller | Same as baseline | Workload target count | Workload saving nodes |
| **Wall time** | Hours | 1–2 hours | 1–2 hours | 15–30 minutes | Minutes–hours | Requested bytes/throughput |
