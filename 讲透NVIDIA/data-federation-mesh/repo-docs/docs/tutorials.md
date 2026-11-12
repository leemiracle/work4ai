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

# Tutorials

These tutorials give you hands-on experience building and running DFM federations, from first steps to real-world data pipelines. They are designed to be followed in order — each series builds on concepts from the previous one.

```{tip}
Recommended reading order:
1. [Zero to Thirty](#zero-to-thirty)
2. [Weather Federation](#weather-federation)
```

## Running Tutorials Locally

Clone the repository and install DFM with the tutorial dependencies:

```bash
git clone https://github.com/NVIDIA/data-federation-mesh.git
cd data-federation-mesh
uv sync --all-packages --extra tutorials
```

```{tip}
See the [README](https://github.com/NVIDIA/data-federation-mesh/blob/main/README.md#development-setup) for detailed setup instructions, including how to install `uv`.
```

The Zero to Thirty tutorials are step-by-step written guides — all commands can be run directly in your terminal. The Weather Federation tutorials are Jupyter notebooks — launch JupyterLab and open them in order:

```bash
uv run jupyter lab
```

### Zero to Thirty

The fastest path to a working federation. In two short tutorials you will create a federation from scratch, write an adapter, and run a pipeline — first locally using Python multiprocessing, then over NVIDIA Flare's POC infrastructure on the same machine. No prior DFM experience required.

```{toctree}
:caption: Zero to Thirty
:maxdepth: 1

Introduction <tutorials-zero-to-thirty/00-introduction>
Part 1 – Local Federation <tutorials-zero-to-thirty/01-local-federation>
Part 2 – Flare POC Mode <tutorials-zero-to-thirty/02-flare-poc-mode>
```

### Weather Federation

Jupyter notebooks that show DFM applied to a real-world use case: distributed weather data loading and processing. Assumes you are comfortable with the basics covered in Zero to Thirty.

```{note}
These tutorials are designed to be run interactively as Jupyter notebooks. The pages below are a static reference. To run them yourself, follow the [Running Tutorials Locally](#running-tutorials-locally) instructions.
```

```{toctree}
:caption: Weather Federation
:maxdepth: 1

Part 1 – Basic Pipeline <tutorials-weather-fed/01-basic-pipeline>
Part 2 – Loaders and Transforms <tutorials-weather-fed/02-weather-loaders-and-transforms>
```
