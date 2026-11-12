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

# Network testing (beta)

Configure and validate your [SSH or Slurm launcher](../README.md#getting-started)
first. Kubernetes and filesystem batch mode are not supported here. Commands
below run from the deployment directory.

## Configure and run

Network testing is **beta** and needs more work before it is ready for
at-scale usage. The available netbench test still provides useful TCP
throughput and latency measurements between small sets of clients.

It requires elbencho and at least two nodes. Permit peer traffic on
`NETBENCH_PORT` and that port plus 1000; `--bidirectional` also uses both ports
plus 1. Configure NIC speed, target runtime, block/response sizes, threads, and
iterations in `env.sh`, then run:

```bash
./storage-tests/network/nv-netbench.sh --nodes 2,4,8
./storage-tests/network/nv-netbench.sh --nodes 2,4,8 --bidirectional
```

Both modes split nodes into groups A and B without localhost traffic. The
default runs A→B and B→A sequentially; `--bidirectional` runs them
concurrently. Transfer size is scaled by thread count so a saturated NIC runs
for approximately `NETBENCH_TARGET_RUNTIME`.

Analyze `$RESULTS_DIR/netbench-{half|bidir}-<datestamp>/` with:

```bash
# Set RUN to the complete result-directory path printed by netbench.
./utils/extract-netbench.py "$RUN"
```

The analyzer reports throughput, latency distributions, variance, and scaling
efficiency in terminal tables and plots. It also supports Markdown
output and scale filters; see `--help`.
