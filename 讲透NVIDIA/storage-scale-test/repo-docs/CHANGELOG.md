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

# Changelog

Notable changes in each release. Versions follow [Semantic Versioning](https://semver.org/);
see [docs/VERSIONING.md](docs/VERSIONING.md). Each release's notes are its
section below.

## Unreleased

### Breaking

- The report caches are removed: `--to-csv`/`--from-csv` (filesystem and
  netbench) and `--to-json`/`--from-json` (Warp). Reports read raw results.
- Live-client analysis compares clients with the fleet median over a steady
  window instead of z-scores. `--client-shortfall-percent` and
  `--client-min-slow-windows` replace `--client-outlier-threshold` and
  `--client-min-underperform-segments`; the heatmap is now
  `client-ratio-heatmap.png`, and the client summary and `results.json`
  z-score fields are replaced.

### Added

- `--to-json` writes a versioned, schema-validated results document for a
  filesystem batch or result directory, with optional live-client detail. See
  [docs/MACHINE_READABLE_RESULTS.md](docs/MACHINE_READABLE_RESULTS.md).
- Live CSV reports add a fairness plot, a fleet latency panel, and "Live
  fairness" lines in `report.txt`; `results.json` adds `steady`, `fairness`,
  and `latency`. See
  [docs/FILESYSTEM_TESTING.md](docs/FILESYSTEM_TESTING.md#live-client-and-latency-reports).

## [2.0.0] - 2026-10-19

### Breaking

- On Kubernetes, every `TEST_DIRS` key and `--read-from` path names its claim:
  `[namespace/]claim:path`. `KUBECTL_PVC` and `KUBECTL_PV` are removed.
- `--env-override` may no longer set `TEST_DIRS` or `FS_MAX_*`; put them in a
  `--target` file.
- One filesystem report no longer combines results from different storage
  targets, such as sweep directories with different `TEST_DIRS` passed
  together; `--allow-mixed-targets` combines them anyway. Batch reports are
  unaffected: each group is reported separately.

See [Upgrading from v1.8.0](docs/FILESYSTEM_TESTING.md#upgrading-from-v180).

### Added

- Spread load across several filesystems with weighted `TEST_DIRS` roots, now
  also across Kubernetes claims
  ([#16](https://github.com/NVIDIA/storage-scale-test/issues/16)). See
  [Testing several filesystems](docs/FILESYSTEM_TESTING.md#testing-several-filesystems).
- Compare filesystems in one batch with one `--target` file each, then report
  the batch directory as usual: each target gets its own report. A Kubernetes
  batch can span namespaces. See
  [Storage target reference](docs/FILESYSTEM_TESTING.md#storage-target-reference)
  and [Several Kubernetes namespaces](docs/FILESYSTEM_TESTING.md#several-kubernetes-namespaces).
- `STORAGE_TARGET_NAME` names a storage target (derived from `TEST_DIRS` when
  unset); results and reports record it. See
  [Reporting per target](docs/FILESYSTEM_TESTING.md#reporting-per-target).
- Repeat `--env-override` to stack workload files. See
  [Workload override files](docs/FILESYSTEM_TESTING.md#workload-override-files).
- After a failure, `--status` (and `--collect` on Kubernetes) names the failed
  cell and its group, plus `FAILED_LOG`: the console output holding the
  benchmark's error. Kubernetes now saves the failed coordinator's log (up to
  its last 16 MiB), not just its last 200 lines. See
  [Resume after failure](docs/FILESYSTEM_TESTING.md#resume-after-failure).

### Changed

- Buffered random writes now visit every block of each file once, in random
  order, so files reach full size. They used unaligned offsets that could
  repeat and leave files short, failing a later random read; buffered
  random-write results differ from v1.8.0.
- `validate_env.sh` is faster, especially on busy Slurm clusters, and prints a
  short summary unless `--verbose`. Errors name the node and the likely cause
  (such as a filesystem that cannot mount or is not writable).
- `KUBECTL_ELBENCHO_IMAGE` defaults to the pinned elbencho image when unset.
- CSV exports gain a `storage_target_name` column; older CSVs still load.

## [1.8.0] - 2026-10-09

### Added

- Kubernetes (`EXECUTION_SUBSTRATE=kubectl`) runs filesystem IO and
  metadata sweeps alongside SSH and Slurm. Sweeps run in the cluster; use
  `--status`, `--collect`, `--cancel`, and `--resume` to follow them. See
  [Kubernetes](README.md#kubernetes).
- Prepared filesystem batches: build a set of IO and metadata sweeps with
  `--batch` and `--append`, run them together with `--start`, and report
  them with `utils/extract-filesystem.py`, which also saves one combined
  `reports.txt`. See
  [Prepared filesystem batches](docs/FILESYSTEM_TESTING.md#prepared-filesystem-batches).
- Workload override files: `--env-override FILE` changes selected workload
  settings for one run or batch group without editing `env.sh`. See
  [Workload override files](docs/FILESYSTEM_TESTING.md#workload-override-files).
- Metadata sweeps can be resumed with `--resume`, like IO sweeps. See
  [Metadata sweeps](docs/FILESYSTEM_TESTING.md#metadata-sweeps).
- Completion-based IO sweeps: buffered IO, multiple `TEST_DIRS` roots, or
  `--run-to-completion` process a finite dataset once instead of running
  for a fixed time. See [First IO sweep](docs/FILESYSTEM_TESTING.md#first-io-sweep).
- Project versions: commands accept `--version`, results record the
  version that produced them, and reports list it. See
  [docs/VERSIONING.md](docs/VERSIONING.md).
- Deployment tarballs and release source archives carry their version
  and detect later edits.

### Changed

- Result tools are executable Python (`utils/extract-*.py`,
  `utils/summarize-elbencho.py`) that set up `.venv` on first use; the
  `.sh` wrappers are gone, so update scripts that call them.
- elbencho v3.2-1 is the pinned download and default Kubernetes image.
- Deployment tarballs leave out object storage credentials. See
  [Prepare the tools](docs/OBJECT_STORAGE_TESTING.md#prepare-the-tools).
