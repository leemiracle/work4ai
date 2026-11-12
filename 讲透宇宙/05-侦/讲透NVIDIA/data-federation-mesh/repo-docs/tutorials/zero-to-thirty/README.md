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

# Zero to Thirty

The fastest path to a working DFM federation. In two short tutorials you will create a federation from scratch, write an adapter, and run a pipeline — first locally using Python multiprocessing, then over NVIDIA Flare's POC infrastructure on the same machine. No prior DFM experience required.

## Tutorials

| # | Tutorial | Description |
|---|----------|-------------|
| 0 | [Introduction](00-introduction.md) | Overview of the scenario and what you will build |
| 1 | [Local Federation](01-local-federation.md) | Create a federation, write adapters, and run a pipeline locally |
| 2 | [Flare POC Mode](02-flare-poc-mode.md) | Run the same federation over NVIDIA Flare's simulated distributed infrastructure |

## Prerequisites

1. Clone the [DFM repository](https://github.com/NVIDIA/data-federation-mesh).
2. From the repository root, install DFM and the tutorial dependencies:
   ```bash
   uv sync --all-packages --extra tutorials
   ```
3. All commands in these tutorials can be run directly in your terminal.

## Documentation

The rendered version of these tutorials is available in the [DFM documentation](https://nvidia.github.io/data-federation-mesh/tutorials.html).
