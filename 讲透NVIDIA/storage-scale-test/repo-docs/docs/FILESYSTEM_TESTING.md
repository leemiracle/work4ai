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

# Filesystem testing

Configure and validate your launcher first using the
[getting-started workflow](../README.md#getting-started). Commands below run
from the repository root or unpacked deployment directory. Use dedicated test
paths: these tests create, overwrite, and delete data.

Start with [IO](#first-io-sweep) or [metadata](#metadata-sweeps), or assemble a
[mixed batch](#prepared-filesystem-batches); vary workloads without editing
`env.sh` using [override files](#workload-override-files), and measure several
filesystems or compare them in [testing several filesystems](#testing-several-filesystems).
Kubernetes users should also read the
[asynchronous workflow](#kubernetes-run-inspect-and-collect). Finish with
[reporting](#filesystem-reporting); tuned settings live in the
[benchmark recipes](../BENCHMARK_RECIPES_FILESYSTEM.md).

SSH and Slurm require an elbencho binary for each client architecture under
`utils/` and filesystems mounted at the same paths on every client. Kubernetes
uses an elbencho image (default `docker.io/breuner/elbencho:v3.2-1`) and
claim-qualified test roots instead; see [Kubernetes setup](#kubernetes-setup).
For SSH or Slurm, configure one test root:

```bash
declare -A TEST_DIRS=(["/mnt/fs1/scaletest"]=1)
```

To spread load across several roots or compare filesystems, see
[testing several filesystems](#testing-several-filesystems). Tune
`FS_MAX_AGG_THROUGHPUT`, `FS_MAX_NODE_THROUGHPUT_GBPS`, and `FS_MAX_NODE_IOPS`
for your filesystem; they determine generated file counts.

## First IO sweep

Set `TEST_DIRS` and the elbencho variables in `env.sh`, then run
`validate_env.sh`; to vary a workload without editing `env.sh`, use an
[override file](#workload-override-files). `ELBENCHO_SCALE_IO_SIZES`,
`ELBENCHO_SCALE_THREAD_LIST`, and `ELBENCHO_IODEPTH_LIST` form a Cartesian
product for every requested node count. An IO-size entry may be `4K`, `r4K`,
or a write/read pair such as `1M,r4K`; see `env.sh.template`. For a short
smoke test, use a small product:

```bash
export ELBENCHO_SCALE_IO_SIZES=("r4K" "1M")
export ELBENCHO_SCALE_THREAD_LIST=("1")
export ELBENCHO_IODEPTH_LIST=("1")
export ELBENCHO_SCALE_READ_WRITE_DURATION=10
```

Ten seconds checks operation, not sustained performance. For timed direct IO,
60 seconds suits exploration; 300 seconds or more is a typical starting point
for publishable runs.

Start with one node, analyze it, then retain only useful thread, size, and I/O
depth values for the scale sweep:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1
# Set RUN to the complete result-directory path printed by the sweep.
# Kubernetes: collect terminal results before reporting (see below).
./utils/extract-filesystem.py "$RUN"
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1,2,4,8
```

All sweep scripts accept comma-separated positive integers and ascending
inclusive ranges: `X`, `X-Y`, or `X-Y+Z`; order is preserved. The endpoint is
always included: `3-10+2` expands to `3,5,7,9,10`. Run a script with `--help`
for its full mode and argument contract.

The default lifecycle is mkdir, write, read, and cleanup.
`--write-no-read` skips the read and still cleans up; the
[retained-dataset modes](#retained-datasets) keep, reread, or delete a dataset.
Slurm uses one coordinator allocation sized to the largest node count; Slurm
and SSH run cells sequentially. Size Slurm `run_time` for the complete product
and all phases, startup, pauses, and cleanup.

Ordinary sweeps default to direct IO; `-b/--bio` selects buffered IO.
`-r/--rand` makes write and read access random; `r`-prefixed IO-size entries
can instead select random access per phase. Random writes visit every block of
each file once in random order, so files always reach full size; buffered
random reads use unaligned offsets. Random IO is incompatible with
single-shared-file mode. A sole `TEST_DIRS` root with weight other than 1 is
rejected.

Worker-directory phases are timed or run to completion as shown below.
Generated shared-directory and single-file datasets always run to completion.

| Configuration | Phase behavior |
|---|---|
| One weight-1 root, direct IO | Timed by default |
| Buffered IO, any root count | Complete writes and reads |
| Multiple distinct roots, direct IO | Complete writes and reads |
| `--run-to-completion` | Complete writes and reads |

Completion mode processes each requested phase's finite dataset once, without
a benchmark time limit. Buffered IO completes to avoid repeatedly measuring
the same warm page-cache data; this does not guarantee cold caches. Only staged
`--read-from` reads can still be time limited (direct IO without
`--run-to-completion`). Write-only modes still skip reads.

### Finite dataset sizing

For a sized finite workload, prefer an explicit per-node file-count budget and
file size:

```bash
TEST_DIRS=(["/path/to/test"]=1)
export ELBENCHO_FILES_PER_NODE=8
export ELBENCHO_FILE_SIZE=1G
export ELBENCHO_SCALE_THREAD_LIST=("1" "4")
# Worker-directory layout; each cell writes and reads nodes * 8 GiB.
./storage-tests/fs/nv-elbencho-sweep.sh --run-to-completion --nodes 1,2
```

In worker-directory mode, each thread visits every weighted target. With
`G = threads * sum(TEST_DIRS weights)`, the per-node count is the requested
budget rounded to the nearest multiple of G (ties up, minimum G); for example,
budget 1,000, 16 threads, and weights 2:1 produce 1,008 files per node, split
672:336. Each cell prints requested and effective counts, which can vary with
the thread count.

Explicit counts in worker-directory mode require completion mode. Generated
shared-directory mode is always completion-based and keeps exact counts: one
root with weight 1, with the count at least and divisible by every thread
count. Neither setting redefines a staged read dataset. `ELBENCHO_FILE_SIZE`
fixes each generated file's size; otherwise, size is the write block size
times `ELBENCHO_FILE_SIZE_MULTIPLIER`.

With the count unset, the file count is sized from `FS_MAX_AGG_THROUGHPUT`,
`FS_MAX_NODE_THROUGHPUT_GBPS`, `FS_MAX_NODE_IOPS`, file/block sizes, topology,
and `ELBENCHO_SCALE_READ_WRITE_DURATION`, with at least one file per thread per
target. In completion mode that duration sizes the dataset but sets no
deadline, so a large dataset can take a long time; in timed direct IO mode,
reads retain the time limit.

## Kubernetes: run, inspect, and collect

`TEST_DIRS` keys are `[namespace/]claim:path`, with the path relative to
the claim (see [claims and test roots](#claims-and-test-roots)); path
components accept letters, digits, `.`, `_`, and `-`. Durable state and
completed-cell data live in `.storage-scale-test` under the lexically first
root (bytewise, as `namespace/claim:path`), so do not use that name as a
component. Each claim is locked with a Kubernetes Lease object, so concurrent
sweeps on the same claim are blocked even with different test roots.

A Kubernetes invocation submits one asynchronous Job for the whole sweep and
prints commands to query, cancel, and collect it:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1,2,4
# Set RUN to the complete printed result-directory path.
./storage-tests/fs/nv-elbencho-sweep.sh --status "$RUN"
# Collect when --status prints NEXT_ACTION=COLLECT.
./storage-tests/fs/nv-elbencho-sweep.sh --collect "$RUN"
```

`--status` prints the same `KEY=value` lines for plain runs and batches; see the
[key table](#prepared-filesystem-batches).

The metadata launcher offers the same lifecycle commands. The Job runs without
your credentials, but lifecycle commands need current `kubectl` access.

- `--status` exits 0 whatever the benchmark outcome.
- `--cancel "$RUN"` stops an active attempt; collect it afterward. On
  `STATE=CANCEL_REQUESTED`, retry `--cancel`.
- On `STATE=SUBMISSION_FAILED` (rolled back), fix the cause, then `--resume`
  a batch or submit a plain run again.
- `--collect` is required after every terminal attempt: it copies results and
  diagnostics locally and cleans up. For a failed or cancelled attempt it
  publishes partial results, then exits nonzero.
- `--resume "$RUN"` requires collection first and, with the same Kubernetes
  configuration, reruns only unfinished cells.
- A failure mid-cell can lose that cell's partial output, but never records it
  as successful.

The [Kubernetes lifecycle contract](KUBERNETES_ELBENCHO_LIFECYCLE.md) covers
the details.

## Resume after failure

The sweep records each cell separately and stops at the first failure. To
find the cause, start with `FAILED_LOG` from `--status` (on Kubernetes,
`--collect` prints it too); `FAILED_EXECUTION` and `FAILED_GROUP` name the
cell (see the [key table](#prepared-filesystem-batches)). On SSH and Slurm,
every cell's output is in `executions/<id>.log` of its result directory.
After correcting the cause, continue it with:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --resume "$RUN"
```

`--resume` must be the only argument. It restores the original environment and
CLI modes from the result directory, skips successful cells, resets stale
running cells, and dispatches the remainder in their original order; on
Kubernetes, [collect first](#kubernetes-run-inspect-and-collect). Do not run
concurrent resumes. A Slurm resume also refuses to reset work while its prior
coordinator may still be active. Resume sources shell files in the result
directory, so use only a trusted, unmodified result directory.

## Retained datasets

Use `--write-only`, `--read-from`, and `--delete-only` to create a dataset once,
run repeated read sweeps, and remove it without rewriting it for each read.

1. Configure one value in each sweep dimension (each cell retains its own
   dataset) and run `--write-only`. Each successful cell prints its directory,
   `ELBENCHO_WRITE_ONLY_DATA_DIR=<root>/elbencho-sweep-target-1-<DS>-e<NNNN>`;
   on Kubernetes this is a Pod path below `/mnt/storage-scale-test/<claim>/`.
2. Run `--read-from <dir> --nodes <spec>` with that printed value, as often as
   needed; for a [single shared file](#single-shared-file), append the file
   name (`elbencho-bigfile` by default). On Kubernetes,
   `[namespace/]claim:path` also works. A many-file read caches its scan in
   `<dir>/.storage-scale-test-elbencho-treefile.txt`; remove that file after
   changing the dataset.
3. Run `--delete-only <dir>` (SSH and Slurm only). The path must be below the
   one `TEST_DIRS` root, from `env.sh` or one `--target FILE`. On Kubernetes,
   delete the dataset from a Pod that mounts the claim.

To build a mixed-size tree, move retained directories below one common
directory under the test root, read that parent, then delete it once. Do not
read a test root itself or a directory containing its `.storage-scale-test`
control directory.

## Shared-directory checkpoint files

This layout models ranks writing distinct checkpoint files into one flat shared
directory. Configure one `TEST_DIRS` entry with weight `1`:

```bash
export ELBENCHO_SINGLE_BIG_FILE=0
export ELBENCHO_FILE_LAYOUT=shared-directory
export ELBENCHO_FILES_PER_NODE=1
export ELBENCHO_FILE_SIZE=64G
export ELBENCHO_SCALE_THREAD_LIST=("1")
export ELBENCHO_IODEPTH_LIST=("1")
```

For `N` nodes, `F` files per node, and `T` threads per node:

```text
total_files = N * F
files_per_worker = F / T
```

`F` must be at least and evenly divisible by every `T`; the harness does not
round. Each worker owns complete files. I/O depth controls outstanding block
I/O per worker, not the number of writers. To model one file per single-threaded
saving rank, set both `F` and `T` to the rank count per node and use I/O depth
`1`.

Generated shared-directory phases are completion-based. They make one pass,
ignore duration and verify exact file and byte counts. Normal and
`--write-no-read` runs delete with distributed elbencho workers;
`--write-only` retains the dataset. `ELBENCHO_FILE_SIZE` is optional; otherwise
the write block size and `ELBENCHO_FILE_SIZE_MULTIPLIER` determine it. Direct or
random I/O requires the file size to be divisible by the effective block size.

With `--read-from <directory>`, the scanned tree defines aggregate file and
byte counts; the configured layout and file count do not repartition it. Direct
IO staged reads are time-limited by default; buffered IO or
`--run-to-completion` reads the scanned dataset to completion.

See Recipe 5 in [BENCHMARK_RECIPES_FILESYSTEM.md](../BENCHMARK_RECIPES_FILESYSTEM.md).

## Single shared file

This mode benchmarks sequential I/O to one regular file. It requires one
`TEST_DIRS` entry, `ELBENCHO_SINGLE_BIG_FILE=1`, and
`ELBENCHO_SINGLE_BIG_FILE_SIZE` for generated data. Random I/O is rejected.

By default, elbencho partitions the file into non-overlapping host ranges.
`ELBENCHO_ALL_NODES_ACCESS_ALL_DATA=1` makes every host process the complete
file, transferring `nodes * file_size` bytes. The default is direct I/O; pass
`-b` for buffered I/O.

With `--read-from`, pass a file, not a directory. Its metadata supplies the
extent, so `ELBENCHO_SINGLE_BIG_FILE_SIZE` is optional. Direct reads repeat
until the time limit; buffered IO or `--run-to-completion` reads the file once,
to completion (see the [IO policy](#first-io-sweep)). Host assignment rotates
between read cells to reduce cross-run client-cache reuse.

`utils/extract-elbencho.py` handles these results normally. See Recipe 4 in
[BENCHMARK_RECIPES_FILESYSTEM.md](../BENCHMARK_RECIPES_FILESYSTEM.md).

## Metadata sweeps

This is the recommended metadata test. It runs create, stat, and delete phases
without MPI and rotates host assignment between phases to reduce client-cache
reuse. Configure `MDTEST_BRANCH_FACTOR`, `MDTEST_ITEMS_PER_DIR`, and
`MDTEST_ITERATIONS`, then run:

```bash
./storage-tests/fs/nv-mdtest-elbencho.sh --nodes 1,2,4,8 --tasks 64,128
# Set RUN to this sweep's complete printed result-directory path.
# Kubernetes: collect terminal results before reporting.
./utils/extract-filesystem.py "$RUN"
```

Each `(nodes, tasks)` pair is saved as a numbered execution. SSH and Slurm
run these executions in order and can continue after interruption:

```bash
./storage-tests/fs/nv-mdtest-elbencho.sh --resume "$RUN"
```

With `EXECUTION_SUBSTRATE=kubectl`, submission returns while a coordinator Job
runs the sweep. Use `--status`, `--cancel`, and `--collect` with the same result
directory. Collect a terminal attempt before using `--resume`.

### Dense single-directory runs

The default layout creates a branched tree. To measure contention in one flat
directory, pass `--single-dir-file-target <count>`:

```bash
./storage-tests/fs/nv-mdtest-elbencho.sh --nodes 2 --tasks 64 --single-dir-file-target 1000000
```

Dense mode requires one node count, one task count, and one generated target.
Every worker creates, stats, and deletes uniquely named zero-byte files in that
directory. The actual total is `workers * max(1, round(target / workers))`,
where `workers = nodes * tasks` and ties round up: target 1 with two nodes and
64 tasks creates 128 files. Requested and actual counts are recorded.

## Prepared filesystem batches

Assemble IO and metadata sweeps before running them. Each `--batch` or
`--append` adds one **group** per `--target` (one group without `--target`),
including its workload settings and CLI flags:

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --batch --nodes 1,2
# Set BATCH to the printed STORAGE_SCALE_TEST_BATCH_RESULTS path.
# Vary each group's workload with an override file (see the next section).
./storage-tests/fs/nv-mdtest-elbencho.sh --append "$BATCH" \
    --env-override overrides/md-deep-tree.env --nodes 2,4 --tasks 4,8
./storage-tests/fs/nv-elbencho-sweep.sh --status "$BATCH"
./storage-tests/fs/nv-mdtest-elbencho.sh --start "$BATCH"
# Kubernetes: wait for terminal status, then collect before reporting.
# After a failure, collect first on Kubernetes, then resume:
# ./storage-tests/fs/nv-elbencho-sweep.sh --resume "$BATCH"
# Once results are local:
./utils/extract-filesystem.py "$BATCH"
```

Either launcher can start or resume the complete batch on SSH, Slurm, or
Kubernetes. `--resume` also starts a draft batch. First start permanently seals
the execution set: append is rejected thereafter, even if submission fails.
Existing ordinary runs cannot be converted to batches. Execution stops at the
first failure; resume skips successful cells and sizes resources for the
remaining work. Initial start acquires capacity for the entire batch's maximum
node requirement. `--batch` creates a new directory and takes no directory
argument; only `--append` adds work to an existing draft.

`--status` prints `KEY=value` lines; on Kubernetes, wait for
`NEXT_ACTION=COLLECT` before collecting.

| Key | Meaning |
| --- | --- |
| `BATCH` | `DRAFT` until first start, then `SEALED` |
| `ATTEMPT` | Kubernetes only: current attempt ID |
| `STATE` | For people (`RUNNING`, `SUCCESS`, `FAILED`, ...; `UNKNOWN` is not success); scripts act on `NEXT_ACTION` |
| `EXECUTION_SCOPE` | `BATCH`: full SSH/Slurm or draft ledger; `CURRENT_ATTEMPT`: current Kubernetes attempt, excluding cells completed before resume |
| `PROGRESS_SOURCE` | Ledger read: `LOCAL` or `PVC` |
| `EXECUTIONS_{TOTAL,PENDING,RUNNING,SUCCEEDED,FAILED}` | Cell counts within that scope |
| `RESULT_COLLECTION` | `PENDING` (results remote), `CLEANUP_PENDING` (published, cleanup needed), `COMPLETE`; SSH/Slurm: `NOT_REQUIRED` |
| `NEXT_ACTION` | `START`, `WAIT`, `COLLECT`, `RESUME`, `INSPECT`, or `NONE` |
| `FAILED_EXECUTION` | After a failure: the first failed cell's ID; `executions/<id>.sh` holds its settings |
| `FAILED_GROUP` | Batches only: that cell's group (results under `groups/<gid>/`) |
| `FAILED_LOG` | Console output with the benchmark's error, shell-quoted: SSH/Slurm `executions/<id>.log`, or the saved Kubernetes coordinator log |
| `SEGMENT_COUNT` | Kubernetes, [several namespaces](#appendix-one-batch-across-several-kubernetes-namespaces) only: namespaces in this attempt (a resume leaves out finished ones) |
| `SEGMENT_CURRENT` | Several namespaces only: index `i` (from 0, in run order) of the running or last-run namespace |
| `SEGMENT_<i>_NAMESPACE` | Several namespaces only: that namespace's name |
| `SEGMENT_<i>_STATE` | Several namespaces only: `SUCCESS`, `FAILED`, `CANCELLED`, `RUNNING`, `PENDING` (Job not yet started), or `NOT_STARTED` |
| `GROUP_<NNNN>_KIND` | Batches only, one pair per committed group: `io` or `mdtest` |
| `GROUP_<NNNN>_TARGET` | Batches only: the group's recorded storage target name, shell-quoted (`unknown` when none) |

`--batch` and `--append` print these keys:

| Key | Meaning |
| --- | --- |
| `STORAGE_SCALE_TEST_BATCH_RESULTS` | The batch directory |
| `STORAGE_SCALE_TEST_BATCH_GROUP` | The new group's ID (the first new group's when there are several) |
| `STORAGE_SCALE_TEST_BATCH_GROUPS` | Several new groups only (one per `--target`): every new group ID, comma-separated, in command-line order |
| `STORAGE_SCALE_TEST_BATCH_GROUP_<gid>_TARGET` | Every new group: its storage target name, shell-quoted |
| `STORAGE_SCALE_TEST_BATCH_EXECUTIONS` | The new execution IDs, `<first>-<last>`, across every new group |

If these keys are printed, the groups were added, even if a warning follows;
do not repeat the `--append`.

Groups may differ in target, IO mode, sizes, durations, and metadata layout; to
compare filesystems in one batch, see
[testing several filesystems](#testing-several-filesystems). Everything else
about how the batch connects and allocates is frozen for the whole batch, and
`--append` names mismatched fields: substrate, executable identity,
architecture, ordering, host pool, and connection/allocation settings (on
Kubernetes, `KUBECTL_NAMESPACE`, `KUBECTL_NODE_SELECTOR`, the images, pull
policy, and UID/GID). The claims and namespaces in each target's keys may
still differ. Start and resume use saved settings, not the current
`env.sh`; Kubernetes credentials remain the current client's. The durable
control directory is chosen from the group test roots (on Kubernetes, the
lexically first root of each namespace across its groups).

## Workload override files

`--env-override <file>` varies a workload without editing `env.sh`; it changes
how to test, never what to test (that is
[`--target`](#testing-several-filesystems)). Either launcher, IO or metadata,
accepts the flag on a new run, `--batch`, or `--append`, on any substrate. Each
appended group keeps its own override list, so a directory of small numbered
files and a short script can build a mixed batch:

```bash
# overrides/10-small-random.env
ELBENCHO_SCALE_IO_SIZES=("r4K" "r16K")
ELBENCHO_IODEPTH_LIST=(1 16)
ELBENCHO_SCALE_THREAD_LIST+=(512)   # extends the list from env.sh
```

```bash
#!/usr/bin/env bash
set -euo pipefail
IO=./storage-tests/fs/nv-elbencho-sweep.sh
MD=./storage-tests/fs/nv-mdtest-elbencho.sh
BATCH=$("$IO" --batch --env-override overrides/10-small-random.env \
    --nodes 1,2,4,8 | sed -n 's/^STORAGE_SCALE_TEST_BATCH_RESULTS=//p')
test -n "$BATCH"
"$IO" --append "$BATCH" --env-override overrides/20-large-seq.env --nodes 1,8
"$MD" --append "$BATCH" --env-override overrides/30-deep-tree.env \
    --nodes 2,4 --tasks 64,128
"$IO" --start "$BATCH"
```

The flag may repeat. The first file builds on `env.sh`; each later file builds
on the one before, so a later `ELBENCHO_SCALE_THREAD_LIST+=(4)` extends a list
an earlier file set, and a later assignment to the same scalar wins. Each
group's list is independent of the others. Giving the same file twice, even
through a symlink or a different spelling of its path, is an error: it would
repeat every relative edit.

Each file is trusted Bash, sourced after `env.sh` in an isolated shell. It sees
the exported environment and the current values of the allowed settings, so
`+=` and `$((MDTEST_ITERATIONS + 1))` build on `env.sh`; unexported `env.sh`
helper variables are not visible. `unset NAME` gives a setting its usual
default. A relative file path resolves from the current directory. The file
must finish with status 0 and must not call `exit`.

Both launchers accept every allowed setting, so IO and metadata groups can
share a file:

- Indexed arrays, one value per element (no whitespace):
  `ELBENCHO_SCALE_THREAD_LIST`, `ELBENCHO_SCALE_IO_SIZES`,
  `ELBENCHO_IODEPTH_LIST`.
- Scalars: `MDTEST_{BRANCH_FACTOR,ITEMS_PER_DIR,ITERATIONS}`,
  `ELBENCHO_{FILE_SIZE_MULTIPLIER,FILE_LAYOUT,FILES_PER_NODE,FILE_SIZE}`,
  `ELBENCHO_{SCALE_READ_WRITE_DURATION,READ_AFTER_WRITE_PAUSE}`,
  `ELBENCHO_{LIVE_CSV_EXTENDED,LIVEINT,ALL_NODES_ACCESS_ALL_DATA}`,
  `ELBENCHO_SINGLE_BIG_FILE{,_BASENAME,_SIZE}`.

Setting `TEST_DIRS`, `STORAGE_TARGET_NAME`, or `FS_MAX_*` is an error that names
the file and the variable and says to pass the file with `--target` (it works
there as-is if it sets only those). Changing any other variable (a typo, a new
uppercase name, or a lowercase name that `env.sh` or the launcher already
defines) is an error, and the message lists every allowed name. A value of the
wrong type is also an error. Either fails before a results directory is created
or a group is appended. New lowercase variables, such as loop counters, are
discarded.

Each run records the override files it used (path and SHA-256) in its saved
settings (`env_used.yaml`), and each submission prints them with the variables
they changed. `--start`, `--resume`, `--status`, `--cancel`, `--collect`, and
`--delete-only` reject the flag; lifecycle commands use the saved values, so
later edits to the files have no effect.

## Testing several filesystems

**What to test comes from `env.sh` or `--target`; how to test comes from
`env.sh` or `--env-override`.**

Terms: a **root** is one `TEST_DIRS` key; a **target** is one `TEST_DIRS` map;
a **target file** sets one target and is passed with `--target`; a **group** is
one target's work in a batch.

| You want to | Configure | You get |
|---|---|---|
| Test one filesystem | `TEST_DIRS` with one root | one group |
| Spread load across several filesystems | `TEST_DIRS` with several weighted roots | one group, load split by weight |
| Compare several filesystems | one target file each, passed with `--target` | one group per target |

### Example: spread load 2:1 across lustre-a and lustre-b

In `env.sh` (size `FS_MAX_*` for both filesystems combined):

```bash
# SSH or Slurm: paths mounted on every client
TEST_DIRS=(["/mnt/lustre-a/scale-test"]=2 ["/mnt/lustre-b/scale-test"]=1)

# Kubernetes, instead: claim:path, both claims in KUBECTL_NAMESPACE
KUBECTL_NAMESPACE=validation
TEST_DIRS=(["lustre-a:scale-test"]=2 ["lustre-b:scale-test"]=1)
```

```bash
./storage-tests/fs/nv-elbencho-sweep.sh --nodes 1,2,4
```

You get:

```text
one run, one target: 2/3 of each cell's files on lustre-a, 1/3 on lustre-b
one report, target "/mnt/lustre-a/scale-test,/mnt/lustre-b/scale-test"
  (Kubernetes: "validation/lustre-a:scale-test,validation/lustre-b:scale-test")
```

### Example: compare vendor-a and vendor-b

One target file per filesystem, plus one workload file for both:

```bash
# targets/vendor-a.env  (targets/vendor-b.env: the same with vendor-b)
STORAGE_TARGET_NAME=vendor-a
TEST_DIRS=(["/mnt/vendor-a/scale-test"]=1)   # SSH or Slurm
#TEST_DIRS=(["vendor-a:scale-test"]=1)       # Kubernetes: claim in KUBECTL_NAMESPACE

# recipes/rand-4k.env
ELBENCHO_SCALE_IO_SIZES=("r4K")
ELBENCHO_IODEPTH_LIST=(1 16)
```

```bash
IO=./storage-tests/fs/nv-elbencho-sweep.sh
"$IO" --batch --target targets/vendor-a.env --target targets/vendor-b.env \
    --env-override recipes/rand-4k.env --nodes 1,2,4
# Set BATCH to the printed STORAGE_SCALE_TEST_BATCH_RESULTS path.
"$IO" --start "$BATCH"
# Kubernetes only: repeat until it prints NEXT_ACTION=COLLECT, then collect.
# "$IO" --status "$BATCH"
# "$IO" --collect "$BATCH"
./utils/extract-filesystem.py "$BATCH"
```

The `--batch` command prints, among its keys:

```text
STORAGE_SCALE_TEST_BATCH_GROUPS=0001,0002
STORAGE_SCALE_TEST_BATCH_GROUP_0001_TARGET=vendor-a
STORAGE_SCALE_TEST_BATCH_GROUP_0002_TARGET=vendor-b
```

The report step writes `reports/groups/0001/report.txt` and
`reports/groups/0002/report.txt`, `reports/index.md` (with a Target column),
and the combined `reports.txt`, all under `$BATCH`.

### Rules

- A target file sets only `TEST_DIRS` (required), `STORAGE_TARGET_NAME`, and
  `FS_MAX_*`; an override file sets only the
  [supported workload settings](#workload-override-files). Substrate,
  connection, and allocation settings stay in `env.sh`. A setting in the wrong
  file is an error that names the flag to use.
- A target file replaces `env.sh`'s `TEST_DIRS`; any `FS_MAX_*` it leaves
  unset comes from `env.sh`. The target's name comes from its own file or
  roots, never `env.sh`.
- Override files apply to every target in the submission. For a different
  workload per target, `--append` another submission.
- Report the batch as usual with `./utils/extract-filesystem.py <batch-dir>`;
  each target gets its own report (see
  [Reporting per target](#reporting-per-target)).
- Several `--target` flags need `--batch` or `--append`. Groups run one at a
  time in the order added (on Kubernetes,
  [grouped by namespace](#several-kubernetes-namespaces)), and a failure stops
  the batch, so use one batch per target when one target's failure must not
  stop the others.

> **Kubernetes notes**
>
> - Roots are `[namespace/]claim:path`; the namespace defaults to
>   `KUBECTL_NAMESPACE`. See [claims and test roots](#claims-and-test-roots).
> - All roots of one target are in one namespace; claims in two namespaces are
>   two targets.
> - Keep a batch's targets in one namespace, or prepare one batch per
>   namespace; a batch spanning namespaces needs
>   [extra setup](#several-kubernetes-namespaces).

Reference: [target files](#target-files), [naming](#naming-a-target),
[several namespaces](#several-kubernetes-namespaces),
[reporting per target](#reporting-per-target), and the batch
[status and output keys](#prepared-filesystem-batches).

## Storage target reference

### Target files

- **Settings.** `TEST_DIRS` (associative array, required),
  `STORAGE_TARGET_NAME`, `FS_MAX_AGG_THROUGHPUT`,
  `FS_MAX_NODE_THROUGHPUT_GBPS`, and `FS_MAX_NODE_IOPS`. Setting a workload
  variable is an error that says to use `--env-override`; any other variable
  belongs in `env.sh`. The file is trusted Bash, loaded like an
  [override file](#workload-override-files).
- **Order, per group.** `env.sh`'s `STORAGE_TARGET_NAME` is cleared, the target
  file is applied over `env.sh`, then the `--env-override` files apply in
  order. A target is therefore named by its own file or its roots, never by
  `env.sh`'s name.
- **Where.** Both launchers accept `--target`:
  - Plain run: at most one (more is rejected, and the error prints the
    equivalent `--batch` and `--start` commands).
  - `--batch` and `--append`: any number; N flags add N groups, one each, in
    command-line order, committed together. The same file twice is an error.
  - `--start`, `--resume`, `--status`, `--cancel`, and `--collect` reject it;
    the IO launcher's `--delete-only` takes at most one, to locate `TEST_DIRS`.
  - Without `--target`, the one target comes from `env.sh`; keep a valid
    `TEST_DIRS` there for `validate_env.sh`.
- **Mounts.** On SSH and Slurm, a batch uses one host pool, so every target's
  roots must be mounted on every client. On Kubernetes, each target's keys
  are checked when it is submitted and its claims when the batch starts.
- **Provenance.** Each run records its target file (path and SHA-256) in
  its saved settings (`env_used.yaml`), and each submission prints it.

### Naming a target

Each run saves the name of its storage target with its settings. Set
`STORAGE_TARGET_NAME` in `env.sh` or a target file to choose it. When it is
empty, the name is derived when the sweep starts: the `TEST_DIRS` roots,
sorted and joined with `,`.

| Substrate | Each root as |
| --- | --- |
| SSH, Slurm | The path, trailing `/` removed |
| Kubernetes | `namespace/claim:path`, with the namespace filled in |

An explicit name is 1-128 characters from letters, digits, and `._:@+/-`,
starting with a letter or digit; `unknown` is reserved for results whose
target cannot be identified. An invalid name is rejected before any results
directory is created.

The name is metadata only. It never changes a path, directory, or group name;
it appears in report headers, the batch index, `--status`, and the CSV
exports (see [reporting per target](#reporting-per-target)).

### Several Kubernetes namespaces

Keep a batch's claims in one namespace, or run one batch per namespace; that
needs no sequencer and no extra RBAC. One batch can span namespaces with extra
setup; see the
[appendix](#appendix-one-batch-across-several-kubernetes-namespaces).

### Reporting per target

Report a multi-target batch like any other batch: run
`./utils/extract-filesystem.py <batch-dir>` (after `--collect` on Kubernetes).
Each group is one target and gets its own report; there is no combined
cross-target report.

- **Batches.** Groups are single-target, so batch reports never mix targets. `reports/index.md` has a `Target` column, and the
  combined `reports.txt` heads every group `Group 0001 (io) target: "<name>"`.
  Current snapshots always record the effective name, so `(derived)` appears
  only beside results saved before this feature, which never recorded one.
  Index cells are escaped, so odd characters in a name show literally.
- **Report headers.** IO and metadata reports print a `Storage target:` line
  after the version lines, and the IO settings summary leads its Targets row
  with `name=` (a long row is shortened with an ellipsis or `(+K more)`).
- **Combining separate results.** One report given results from different
  targets (several results directories on one command line) exits 1 before
  writing anything, because IO tables would merge and metadata results would
  be averaged. Sweeps of different `TEST_DIRS`
  roots are different targets unless they share a `STORAGE_TARGET_NAME`; this
  includes results saved before v2.0.0, whose name is derived from their roots.
  Inputs without a saved `env_used.yaml` are unknown and only warn.
  `--allow-mixed-targets` combines them anyway, with a warning and a
  `Storage target: mixed: "a", "b"` header; aggregate tables then average
  across targets.

## Filesystem reporting

Use `./utils/extract-filesystem.py "$RUN"` as the unified front door for
ordinary IO or metadata runs and mixed batches. It dispatches each kind to
its analyzer without combining unlike metrics.

Each group has separate artifacts and reports, so repeated coordinates never
overwrite or average across groups. All tables for one group are saved in
`reports/groups/<group-id>/report.txt`; individual tables do not have separate
text files. `reports/index.md` links the group reports and lists cell states.
Report only selected groups with `--groups 0001,0003`, choose
`--kind io|mdtest|all`, or redirect reports with `--output-dir PATH`.
Reports include successful cells only; Kubernetes results must first be
collected. Both existing specialized reporters accept batches and select their
own workload kind.

When at least two groups have valid reports, the reporter also writes
`reports.txt` at the batch root and links it from `reports/index.md`. This file
collects the groups' tables in manifest order without combining their metrics.
Each IO group begins with one compact summary of its effective saved settings,
targeting about six lines. It covers the runner, targets, configured sweep,
file layout and sizing, lifecycle, and a `Setting files:` row naming the
target and override files; inactive optional settings are omitted. The summary
abbreviates: long names and lines are shortened and long lists end in
`(+N more)`. To check that groups used equivalent settings, compare their
complete `env_used.yaml` snapshots, which the `Saved settings` path and
`reports/index.md` link.
Table titles remain adjacent to their tables. Metadata reports include the raw
saved YAML once before the entire workload group report, keeping configuration,
rates, elapsed times, latency tables, and commands together. Individual group
`report.txt` files remain unchanged. Both plain-text and `--markdown` reports
are supported. With `--output-dir PATH`,
the combined file is `PATH/reports.txt`, alongside `PATH/index.md` and
`PATH/groups/`.

The unified reporter also accepts the established analysis options. Common
options such as `--only-nodes` and `--markdown` apply to both kinds;
`--normalize-to` applies only to metadata and `--per-client-plots` only to IO.
An option with no matching selected group is an error. Filtered runs update
selected reports and rebuild the index and combined file, retaining valid
reports from other groups in the same batch. Failed, stale, or unowned reports
are excluded; when fewer than two valid group reports remain, `reports.txt`
is removed:

```bash
./utils/extract-filesystem.py --normalize-to 1 --only-nodes 2,4 "$BATCH"
./utils/extract-filesystem.py --kind io --per-client-plots "$BATCH"
```

Results from different storage targets are never combined silently; see
[reporting per target](#reporting-per-target).

Use `--help` for all options. Single-file parsing requires `--kind io|mdtest`
and is not a batch-reporting mode. For scripts and gates, see
[MACHINE_READABLE_RESULTS.md](MACHINE_READABLE_RESULTS.md).

| Scope | Option | Purpose |
| --- | --- | --- |
| Both | `--only-nodes LIST`, `--only-threads LIST` | Select counts with comma lists or ranges |
| Both | `--markdown` | Markdown on stdout; progress on stderr |
| Both | `--test-parse FILE` | Inspect one raw result without reporting |
| Both | `--to-json` | Also write `<output-dir>/results.json`, the [machine-readable results document](MACHINE_READABLE_RESULTS.md) |
| Both | `--allow-mixed-targets` | Combine results from different [storage targets](#reporting-per-target) in one report (a batch never needs it) |
| IO | `--only-sizes SIZE` | Repeat or separate with `;`; preserve compound-size commas |
| IO | `--only-iodepths LIST` | Select depths with comma lists or ranges |
| IO | `--no-dual-y-axis` | Separate throughput and latency axes |
| IO | `--per-client-plots` | Write per-client live summaries and plots |
| IO | `--client-shortfall-percent PCT` | Slow-client shortfall below the fleet median, percent (default 5) |
| IO | `--client-min-slow-windows N` | Minimum 5 s windows at twice the shortfall for a transient client (default 3) |
| IO | `--client-max-timeseries-lines N` | Limit client lines per plot (default 10) |
| IO | `--client-max-heatmap-rows N` | Limit clients per heatmap (default 50) |
| Metadata | `--normalize-to N` | Scale rates/stddev to N nodes, not latency |

For several result directories at once, use `extract-elbencho.py` or
`extract-mdtest-elbencho.py`, which accept the same filters
and `--markdown`. IO reports show IOPS or throughput and
latency by operation, size, thread count, node count, and I/O depth. Metadata
reports show create/stat/delete rates, elapsed times, latency distributions,
variance, and scaling efficiency.

### Live client and latency reports

Set `ELBENCHO_LIVE_CSV_EXTENDED=1` before the run, then report as usual.
Extended capture grows large at scale; choose `ELBENCHO_LIVEINT` deliberately.

Each phase is judged over a **steady window**: from the first interval where
every client has progressed and aggregate MiB/s reaches 75% of its steady
median, to elbencho's `time ms [first]` (the first client finishing). Ramp-up
and the straggler tail are excluded. Without a window (`no_first_time`,
`too_short` under 10 s, or `no_steady_state`), summaries give the reason.

**Sliding windows** of one interval, 5 s, and 30 s compare each client's bytes
in the window with the fleet median. Each window gives Jain's index (1.0 is
even), the slowest client's ratio to the median, and an expected Jain floor,
`k / (k + 1)` for `k` blocks per client, which counting noise alone allows.

**Slow clients**, with S = `--client-shortfall-percent`:

| Class | Rule |
| --- | --- |
| `persistent` | Below `1 - S` of the median over the steady window, or in at least half of the 30 s windows |
| `transient` | Otherwise, below `1 - 2S` in at least twice the median client's share of 5 s windows, and in at least `--client-min-slow-windows` of them |
| `ok` | Neither |

Clients take turns dipping, so `transient` means dipping more often than the
fleet, not dipping at all. Missing and invalid samples are counted separately
and do not affect the class.
In multi-node runs each client is a host, so imbalance between threads inside
a host is invisible.

Outputs, named `<stem>-<phase slug>-*` in the report directory:

| Output | When | Content |
| --- | --- | --- |
| "Live fairness" lines | always | Per phase: steady span, Jain p50/min per window, 5 s slowest/median p10, slow-client counts, latency p50, p90, and max/p50. In `report.txt` and stdout (stdout only with `--markdown`) |
| `aggregate-timeseries.png` | always | Total MiB/s and IOPS, plus a fleet IO latency panel; warmup and tail shaded, `[first]`/`[last]` marked |
| `fairness-timeseries.png` | always | Jain per window with the 5 s floor; below, the 5 s slowest/median ratio against `1 - S` and `1 - 2S` |
| `client-summary.csv` / `.txt` | `--per-client-plots` | Per client: class, steady MiB/s and ratio, worst 5 s and 30 s ratios and times, percent of 5 s windows short, whole-run mean and median, sample counts |
| `client-timeseries.png` | `--per-client-plots` | 5 s client rates against the fleet p10-p90 band; slow clients first |
| `client-ratio-heatmap.png` | `--per-client-plots` | Clients by 5 s windows, percent of the fleet median on a 50-150% scale; slow clients, then representatives |

Fleet latency is the Total rows' `Lat IO us`, an op-weighted mean per
interval; captures without that column have no latency panel.

## Advanced node selection and Slurm options

Use tuned clients with enough aggregate bandwidth to saturate the target.
A starting node count is `1.1 * 8 * FS_MAX_AGG_THROUGHPUT / measured_per_client_Gbps`
(`FS_MAX_AGG_THROUGHPUT` is in GB/s; the 8 converts it to Gbps).

Random subsets from mixed-throughput clients can make adjacent sweep points
incomparable. `ORDER_NODES` and `utils/slurm/group_into_bins.py` create an
ordered host list with balanced cumulative throughput.

Create an input CSV:

```csv
InstanceName,Gbps
node-01,100
node-02,50
node-03,100
node-04,50
```

Generate the ordered list on stdout and a suggested descending `--nodes` list
on stderr:

```bash
python3 utils/slurm/group_into_bins.py --bin-size 25 nodes.csv \
    > ordered_nodes
```

Use `ordered_nodes` as `SSH_HOST_LIST` or `SLURM_NODE_INCLUDES`, set
`ORDER_NODES=1`, and pass the suggested `--nodes` list from stderr to a sweep. SSH then takes the
first `N` hosts; Slurm with an include list requests exactly its first `N`
expanded nodes.

Smaller bins add sweep points; larger bins provide more balancing freedom.

`SLURM_JOB_NAME_PREFIX` prefixes job names. `SLURM_EXTRA_ARGS` is a Bash array
appended after generated sbatch/srun options, so later duplicate options can
override earlier ones while arguments with spaces remain intact:

```bash
SLURM_EXTRA_ARGS=("--constraint=ib" "--comment=storage validation run")
```

`SLURM_EXCLUSIVE_USER=1` uses `--exclusive=user` and derives
`--cpus-per-task` when the target CPU count is available; the default uses
`--exclusive`.

## Kubernetes setup

The tool provisions no cluster, namespace, PV, or PVC. Set the
[README Kubernetes configuration](../README.md#kubernetes), then check the
claims and the cluster below.

### Claims and test roots

Each `TEST_DIRS` key names its claim: `[namespace/]claim:path`.

```bash
KUBECTL_NAMESPACE=validation
# Use one of:
TEST_DIRS=(["scale-test:data"]=1)                # claim scale-test
TEST_DIRS=(["lustre-a:scale-test"]=2 ["lustre-b:scale-test"]=1)  # two, 2:1
TEST_DIRS=(["vendor-b/data:scale-test"]=1)       # claim data in vendor-b
```

- `claim` is a PersistentVolumeClaim; `path` is a directory below the
  claim's root. A key without `namespace/` uses `KUBECTL_NAMESPACE`; leave
  that empty only if every key names its namespace.
- All roots of one target share one namespace; a map that spans namespaces is
  rejected. Compare namespaces with [`--target`](#testing-several-filesystems).
- Every Pod mounts each claim at `/mnt/storage-scale-test/<claim>`, so
  `claim:path` is `/mnt/storage-scale-test/<claim>/<path>` inside the Pod. Do
  not write that prefix in `TEST_DIRS`.

### Cluster prerequisites

- Each claim exists in its namespace and is Bound, ReadWriteMany, and
  Filesystem mode. The tool records the PV it is bound to and fails if that
  changes during an attempt.
- Each namespace carries the `kubernetes.io/metadata.name` label (automatic
  since Kubernetes 1.21); `validate_env.sh` fails without it.
- The selector matches enough Ready, schedulable nodes of the intended
  architecture for your largest node count. Inspect labels with
  `kubectl get nodes --show-labels`; comma-separated equality labels are ANDed,
  for example `storage-scale-test/worker=true,storage-tier=lustre`.
- Every selected node can mount every claim. Each `TEST_DIRS` path already
  exists and is writable by the configured positive UID/GID; `2000:2000` is an
  example, not a required identity. The claim's root need not be writable.
- The CNI provides cross-node Pod IPv4 connectivity on TCP 1611 and enforces
  NetworkPolicies.
- Admission policy allows `Unconfined` seccomp for elbencho validation, worker,
  and coordinator Pods; Linux AIO needs it. These Pods still run as the
  configured non-root UID/GID, disable privilege escalation, drop all
  capabilities, and mount no API token. Helper Pods keep more restrictive
  settings. The one exception is the sequencer Pod used across
  [several namespaces](#appendix-one-batch-across-several-kubernetes-namespaces).
- The submitting identity can:
  - get Nodes, PersistentVolumes, and Namespaces (cluster-scoped, so a
    ClusterRole);
  - get PVCs, workload resources, and events in the namespace;
  - create, get, and delete Jobs, Pods, DaemonSets, NetworkPolicies, and
    Leases;
  - read Pod logs and exec into Pods.

  The coordinator itself has no Kubernetes API credentials.
- The elbencho image supports your nodes and is usable under the pull policy
  with any required registry credentials. `KUBECTL_ELBENCHO_IMAGE` defaults to
  `docker.io/breuner/elbencho:v3.2-1`; set it only for another image or a
  mirror. `Never` requires preloading; `Always` requires a digest-pinned
  image, so not the default tag.

`validate_env.sh` then checks each claim and runs a temporary Job that mounts
them all, to check the image, workload identity, write access to each root,
and seccomp mode.

## Kubernetes access and troubleshooting

`validate_env.sh` also lists, informationally, any Jobs, DaemonSets, Pods,
NetworkPolicies and Leases labeled `app.kubernetes.io/name=storage-scale-test`
(all namespaces, falling back to the namespace of the `TEST_DIRS` roots if
cluster-wide listing is forbidden); with none, it prints nothing for this
unless `--verbose`.
Existing objects never fail validation, and the label does not prove
ownership: they may belong to an active or uncollected attempt. Find the
result directory whose `kubernetes/attempts/<run-id>/` matches the listed RUN
and use `--status`, `--collect`, or `--cancel`. Delete manually only after the
object's ownership annotation matches the nonce recorded in that attempt.

On failure, read the diagnostic bundle path and safe next action printed by
validation or the sweep. A failed cell's error is in `FAILED_LOG` (see
[Resume after failure](#resume-after-failure)); the bundle adds Pod
descriptions, events, and recent worker logs. Common causes are:

| Evidence | Check |
| --- | --- |
| Image inspect/pull failure | Fully qualified image, architecture, pull policy, registry credentials |
| Claim permission failure | Test-root ownership and configured workload UID/GID |
| `FailedMount` | Node-side CSI/storage setup; changing the benchmark image cannot fix a pre-container mount failure |
| Admission rejection | Namespace policy and requested resource/security settings |
| Service readiness failure | Direct Pod IPv4 connectivity on TCP 1611, CNI policy and service logs |
| Interrupted collection | Retry `--collect` to complete exact cleanup |

Keep the saved local state and remote resources while investigating. Do not
bypass ownership checks by deleting the Lease or editing the ledger.
The [Kubernetes lifecycle contract](KUBERNETES_ELBENCHO_LIFECYCLE.md)
defines supported recovery, diagnostics, and remaining acceptance gates.

## Upgrading from v1.8.0

- Kubernetes `TEST_DIRS` keys are `[namespace/]claim:path`, and `KUBECTL_PVC`
  and `KUBECTL_PV` are removed: `KUBECTL_PVC=scale-test` with
  `TEST_DIRS=(["data"]=1)` becomes `TEST_DIRS=(["scale-test:data"]=1)`.
  `validate_env.sh` and new submissions stop with a message showing the
  replacement line.
- On Kubernetes, `--read-from` takes `[namespace/]claim:path` or the Pod path
  that `--write-only` printed.
- An `--env-override` file can no longer set `TEST_DIRS` or `FS_MAX_*`; pass
  that file with [`--target`](#target-files) instead.
- One report no longer combines results from different storage targets, such
  as v1.8.0 sweeps of different `TEST_DIRS` given together; add
  `--allow-mixed-targets` to combine them. Batch reports are unaffected.

## Appendix: one batch across several Kubernetes namespaces

Targets in one namespace share one set of workers and one coordinator that
mount all of their claims. A batch spanning namespaces runs one namespace at a
time, in the order each first appears in the batch (on resume, among the
remaining cells), and each namespace's groups in the order added: groups
`0001` (ns-a), `0002` (ns-b), and `0003` (ns-a) run as `0001`, `0003`, `0002`.

- **How.** `--start` checks every claim, prepares every namespace's workers and
  a suspended coordinator Job, and rolls everything back if a claim cannot
  mount on a selected node. A **sequencer** Job in the first namespace then
  starts each coordinator when the previous one finishes. Its ServiceAccount
  can only get and patch that attempt's coordinator Jobs, and its Pod is the
  only one in a sweep that mounts an API token. If it is lost, `--status`
  starts the next coordinator with your credentials.
- **Prerequisites.** Kubernetes 1.24 or newer; permission to create, get, and
  delete a ServiceAccount in the first namespace and Roles and RoleBindings in
  every namespace, and to patch Jobs; and the sequencer image, by default a
  pinned `docker.io/alpine/kubectl`. Set `KUBECTL_SEQUENCER_IMAGE` only for a
  mirror: any digest-pinned image providing `sh`, `kubectl`, `grep`, `mkdir`,
  and `sleep` (a private mirror needs node-level pull credentials). A set value
  must be digest-pinned even when unused.
- **Limits.** `--start` rejects an attempt spanning more than 16 namespaces or
  32 claims before creating anything.
- **Validation.** `validate_env.sh` checks the RBAC, the server version, and
  that the sequencer image pulls and provides its tools, in the namespace of
  `env.sh`'s `TEST_DIRS`, as warnings only. `validate_env.sh --sequencer` runs
  the real sequencer and treats problems as errors (raise
  `KUBECTL_SEQUENCER_PROBE_TIMEOUT_SECONDS`, default 120, for a slow pull).
- **Progress.** `--status` adds `SEGMENT_*` keys per namespace (see
  [prepared batches](#prepared-filesystem-batches)); `EXECUTIONS_*` counts
  span every namespace.
- **Failures.** A failed cell stops the batch: later namespaces show
  `NOT_STARTED` and `NEXT_ACTION` becomes `COLLECT`. `--cancel` stops the
  sequencer and the running namespace.
- **Results.** One `--collect` gathers every namespace and cleans up.
  `run.status` is `SUCCESS` only when every namespace succeeded; each
  namespace also gets its own `run-<namespace>.status`.
- **Resume.** `--resume` skips successful cells and uses only the namespaces
  that still have cells (no sequencer when one is left).

The [Kubernetes lifecycle contract](KUBERNETES_ELBENCHO_LIFECYCLE.md) has the
details.
