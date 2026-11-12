# NVIDIA Storage Scale Test

Shell and Python tools for running distributed storage benchmarks and turning
their results into tables and plots.

- [Filesystem testing](docs/FILESYSTEM_TESTING.md): data IO and metadata with elbencho.
- [Object storage testing](docs/OBJECT_STORAGE_TESTING.md): S3-compatible storage with Warp.
- [Network testing](docs/NETWORK_TESTING.md): peer throughput and latency with elbencho (beta).

Each release has a version, such as `v1.2.3`, and commands print theirs with
`--version`. Results record the version that produced them, and reports show
it. See [versions](docs/VERSIONING.md) and the [changelog](CHANGELOG.md).

## Warning: these tests destroy data

Tests **create, overwrite, and delete files and objects**. Use dedicated test
directories and empty, disposable buckets. Root access is neither required nor
recommended.

## Getting started

The workflow is **configure → validate → run → report**. Run commands from the
repository root or an unpacked deployment directory.

1. Prepare a host that can reach your workers: a Slurm login host, a
   passwordless-SSH launcher, or a workstation authorized for your Kubernetes
   cluster. See [prerequisites and deployment](#prerequisites-and-deployment).
2. Create the configuration:

   ```bash
   cp env.sh.template env.sh
   ```

3. Edit `env.sh`: [select an execution substrate](#configure-the-execution-substrate),
   configure connection settings, and choose workload targets.
   `RESULTS_DIR` sets the parent directory for local results.
4. [Validate](#validate-and-correct-the-configuration), fix reported problems,
   and repeat until it passes:

   ```bash
   ./validate_env.sh
   ```

5. Follow the [filesystem](docs/FILESYSTEM_TESTING.md#first-io-sweep),
   [object](docs/OBJECT_STORAGE_TESTING.md#configure-the-target-and-run-a-sweep),
   or [network](docs/NETWORK_TESTING.md#configure-and-run) guide to run and report.

Each run creates its own directory below `RESULTS_DIR`. Use that complete
printed directory, not its parent, for reporting and lifecycle commands.
Filesystem launchers can also vary workload settings per run with
[`--env-override <file>`](docs/FILESYSTEM_TESTING.md#workload-override-files)
instead of edits to `env.sh`.

To test several filesystems, either spread one workload across them (several
weighted `TEST_DIRS` roots) or compare them (one `--target <file>` per
filesystem in one batch; `./utils/extract-filesystem.py <batch-dir>` reports
each one separately). What to test comes from `env.sh` or `--target`; how to
test comes from `env.sh` or `--env-override`. See
[Testing several filesystems](docs/FILESYSTEM_TESTING.md#testing-several-filesystems).
Kubernetes runs asynchronously: collect terminal results before reporting.

## Prerequisites and deployment

- Benchmarks and Slurm orchestration require Linux. macOS can launch SSH and
  kubectl filesystem sweeps with Homebrew's Bash first on `PATH`
  (`brew install bash coreutils`; kubectl also needs `gnu-tar flock`).
- Reporting requires Python 3.12+. The extraction wrappers set up their Python
  dependencies.
- SSH/Slurm workers need benchmark binaries under `utils/` for each client
  architecture; see the archive builder below. Kubernetes uses the configured
  workload image instead.

Use a prepared checkout or create a deployment archive:

```bash
./utils/build_tarball.sh
```

It downloads pinned elbencho binaries into `utils/` (keeping existing or
custom builds unless `--force-download` is given), includes Warp binaries if
present ([Warp preparation](docs/OBJECT_STORAGE_TESTING.md#prepare-the-tools)),
builds `s3test`, and writes `storage-scale-test.tar.gz` (without `docs/`;
read guides in the checkout or repository browser). Unpack it on your launcher
and configure its `env.sh`. A failed download only warns, so confirm the tools
for every client architecture. Neither the repository nor NVIDIA distributes
these binaries; see [NOTICE](NOTICE) for provenance and licenses (elbencho
GPL-3.0, Warp AGPL-3.0).

## Configure the execution substrate

Set `EXECUTION_SUBSTRATE` explicitly in `env.sh`; there is no default.
`SSH_HOST_LIST` configures SSH but does not select it.

| Substrate | Filesystem | Object storage | Network |
| --- | --- | --- | --- |
| `ssh` | Supported | Supported | Beta |
| `slurm` | Supported | Supported | Beta |
| `kubectl` | Supported | Not supported | Not supported |

### Passwordless SSH

```bash
export EXECUTION_SUBSTRATE=ssh
export SSH_HOST_LIST=/absolute/path/to/host_list
# export SSH_USER=ubuntu       # otherwise your user/SSH configuration applies
# export SSH_HOMEDIR_SHARED=1  # set only if workers share a home directory
```

The host list accepts comma- or whitespace-separated hosts across multiple
lines and ignores comment lines. Authentication must be non-interactive.
Filesystem paths must exist on every selected worker:

```bash
declare -A TEST_DIRS=(["/mnt/fs/scaletest"]=1)
```

### Slurm

```bash
export EXECUTION_SUBSTRATE=slurm
account="your-account"
partition="your-partition"
reservation=""                 # set if your site requires one
```

Configure site modules, `client_type`, and `client_arch` in `env.sh`.
Filesystem `TEST_DIRS` use worker-side paths as above. Set `run_time` for
the complete filesystem sweep or batch, including startup and cleanup.
See [advanced node selection and Slurm options](docs/FILESYSTEM_TESTING.md#advanced-node-selection-and-slurm-options).

### Kubernetes

Authorize `kubectl` for the intended context first:

```bash
export EXECUTION_SUBSTRATE=kubectl
export KUBECTL_NAMESPACE=storage-scale-test
export KUBECTL_NODE_SELECTOR='storage-scale-test/worker=true'
export KUBECTL_IMAGE_PULL_POLICY=IfNotPresent
export KUBECTL_RUN_AS_USER=2000
export KUBECTL_RUN_AS_GROUP=2000
declare -A TEST_DIRS=(["scale-test-pvc:scale-test"]=1)
```

Each `TEST_DIRS` key is `[namespace/]claim:path`: here the directory
`scale-test` inside the claim (PVC) `scale-test-pvc` in `KUBECTL_NAMESPACE`.
The tool provisions no cluster, namespace, PV, or PVC; complete the
[Kubernetes setup](docs/FILESYSTEM_TESTING.md#kubernetes-setup) before
validating. For lifecycle commands, durable storage layout, and
troubleshooting, see the
[filesystem guide](docs/FILESYSTEM_TESTING.md#kubernetes-run-inspect-and-collect).

## Validate and correct the configuration

Run `./validate_env.sh` after configuration changes and repeat until it prints
`All validation checks passed successfully`. A passing run prints a few
summary lines; errors, warnings, and notes are always printed, and `--verbose`
(`-v`) adds a detail line for every check that passed.

- It probes the selected substrate and enabled workloads (filesystem: nonempty
  `TEST_DIRS`; object: `OBJ_BUCKET`): writable paths, bucket access and, on
  Kubernetes, each claim plus one temporary validation Job. It checks only
  `env.sh`'s target; `--target` files are checked when a run is prepared or
  started.
- On Kubernetes, `./validate_env.sh` warns (never fails) when the in-cluster
  sequencer that batches spanning several namespaces need lacks its image or
  RBAC; `./validate_env.sh --sequencer` runs its full probe and makes problems
  errors.
- Read the errors above the final summary. Fix configuration errors in
  `env.sh`; take mount, admission, registry, or CNI problems to your
  cluster/storage administrator. Disabled-test notes and the
  [Kubernetes object inventory](docs/FILESYSTEM_TESTING.md#kubernetes-access-and-troubleshooting)
  are informational. Validation cannot prove every workload or performance
  limit; start with a small run before scaling.

## Further reading

- [Filesystem benchmark recipes](BENCHMARK_RECIPES_FILESYSTEM.md): tuned settings by use case.
- [Testing several filesystems](docs/FILESYSTEM_TESTING.md#testing-several-filesystems): spread load across filesystems, or compare them with `--target`.
- [Design](docs/DESIGN.md), [requirements](docs/REQUIREMENTS.md), and [architecture diagrams](docs/ARCHITECTURE_DIAGRAMS.md).
- [Kubernetes lifecycle contract](docs/KUBERNETES_ELBENCHO_LIFECYCLE.md): authoritative recovery and fault boundaries.
- [Roadmap](ROADMAP.md), [security policy](SECURITY.md), [LICENSE](LICENSE), and [NOTICE](NOTICE).

External code contributions are not currently accepted. Bug reports,
documentation corrections, and suggestions are welcome; see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Copyright

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

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.
