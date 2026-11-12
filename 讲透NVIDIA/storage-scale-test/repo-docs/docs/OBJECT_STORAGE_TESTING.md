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

# Object storage testing

Configure and validate your [SSH or Slurm launcher](../README.md#getting-started)
first. Kubernetes and prepared filesystem batches do not support object tests.
Commands below run from the deployment directory.

## Prepare the tools

Supply Warp binaries for every client architecture as `utils/warp` and/or
`utils/warp.aarch64`. The tarball builder includes existing Warp binaries; it
does not download them. Build them before creating the deployment archive:

```bash
./utils/build/build_warp_from_source.sh
./utils/build_tarball.sh
```

The build helper defaults to [NVIDIA/warp-minio](https://github.com/NVIDIA/warp-minio)
and accepts another GitHub/GitLab URL with a tag, branch, or commit. Review its
help and third-party licenses before use. The tarball builder also builds
`s3test` for validation; check warnings for missing tools or architectures.

The tarball never includes `.obj_auth` or links to it. To exclude other
credential files, pass `--obj-auth-file PATH` (repeatable) or export
`OBJ_AUTH_FILE`; relative paths are from the checkout. An exported path that
does not exist is ignored. The builder never reads `env.sh`; create the
credentials file on the launcher.

```bash
./utils/build_tarball.sh --obj-auth-file credentials/object.auth
```

## Configure the target and run a sweep

Set `OBJ_BUCKET`, `OBJ_REGION`, `OBJ_HOST`, `OBJ_HOST_PORT`, and an absolute
`OBJ_AUTH_FILE` path in `env.sh`. The bucket must already exist and must contain
no valuable objects: the test cleans it and deletes its benchmark objects.
Store credentials in a mode-`0400` file:

```bash
export WARP_ACCESS_KEY="..."
export WARP_SECRET_KEY="..."
```

Configure `WARP_OBJ_SIZES`, `WARP_THREAD_LIST`, `WARP_PUT_DURATION`,
`WARP_GET_DURATION`, and `WARP_PUT_MIN_FILES_PER_CLIENT` in `env.sh`.
GET sweeps each thread-list value; the last value also sets PUT and DELETE
concurrency per client (it need not be the largest). Run `validate_env.sh`,
then establish a single-node baseline before scaling:

```bash
./storage-tests/object/nv-warp-sweep.sh --nodes 1
# Set RUN to the complete result-directory path printed by the sweep.
./utils/extract-warp.py "$RUN"
./storage-tests/object/nv-warp-sweep.sh --nodes 1,2,4,8
```

For each node count and object size, the test cleans the bucket, PUTs until at
least `nodes * WARP_PUT_MIN_FILES_PER_CLIENT` objects exist, sweeps GET thread
counts, and performs final DELETE cleanup. Each node count is a separate Slurm
job or SSH invocation.

Optional modes are `--multipart`, `--ranged`, and `--s3-express`. Ranged reads
run 30-second PUT stages until at least `nodes` objects exist in total, using
`WARP_RANGE_OBJ_SIZE` for object size and `WARP_OBJ_SIZES` for read range sizes.
This is a minimum, not an exact count; stages can create substantially more
objects, so budget storage accordingly.

Aggregate PUT and GET request-rate budgets are available through
`WARP_RPS_BUDGET_PUT` and `WARP_RPS_BUDGET_GET`. `WARP_PREFIXES` selects static
prefixes and requires [NVIDIA/warp-minio](https://github.com/NVIDIA/warp-minio).

## Reporting

`extract-warp.py` generates terminal tables and PNG plots for throughput, TTFB
latency, and scaling efficiency. Markdown output is not implemented.

| Option | Purpose |
| --- | --- |
| `--only-sizes SIZE` | Select object sizes; repeat or separate with `;`, not commas |
| `--only-threads LIST` | Select comma-separated thread counts |
| `--output-dir DIR` | Choose the report/plot directory |
| `--per-client-plots` | Compare clients and flag underperformance |
| `--client-outlier-threshold Z` | Underperformance z-score magnitude (default 2.0) |
| `--client-min-underperform-segments N` | Require N underperforming segments (default 1) |

Use `--help` for defaults.
