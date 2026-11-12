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

# Weather Federation

Jupyter notebooks that demonstrate DFM applied to a real-world use case: distributed weather data loading and processing using the `nv-dfm-lib-weather` adapter library.

These tutorials are designed to be run interactively. The notebooks contain inline output and visualizations that are best experienced in JupyterLab rather than read as static text.

## Tutorials

| # | Notebook | Description |
|---|----------|-------------|
| 1 | [Basic Pipeline](01-basic-pipeline.ipynb) | Set up a weather federation and run your first pipeline |
| 2 | [Loaders and Transforms](02-weather-loaders-and-transforms.ipynb) | Work with weather data loaders and transform operations |

## Prerequisites

1. Clone the [DFM repository](https://github.com/NVIDIA/data-federation-mesh).
2. Make sure you are comfortable with the basics covered in the [Zero to Thirty](../zero-to-thirty/) tutorials.

## Running the Notebooks

From the repository root, install DFM and the tutorial dependencies:

```bash
uv sync --all-packages --extra tutorials
```

Then launch JupyterLab:

```bash
uv run jupyter lab
```

Open the notebooks in order and follow along.

## Documentation

A static rendering of these notebooks is available in the [DFM documentation](https://nvidia.github.io/data-federation-mesh/tutorials.html), but running them locally is strongly recommended.
