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

# nv-dfm-core

Core framework for [NVIDIA Data Federation Mesh (DFM)](https://github.com/NVIDIA/data-federation-mesh).

## What is DFM?

Data Federation Mesh (DFM) is a Python-based framework for creating and orchestrating complex workflows that process data from various distributed sources and stream results into applications. DFM determines where to run each operation of a data processing pipeline and handles data movement between sites automatically.

DFM is built on top of [NVIDIA Flare](https://developer.nvidia.com/flare), which provides distributed messaging, job management, security, deployment, and a simulation framework.

## Overview

`nv-dfm-core` is the core package of the DFM framework. It provides:

| Component | Description |
|-----------|-------------|
| **Pipeline API** | Declarative Python API for defining pipelines (`Pipeline`, `Yield`, `PlaceParam`, `ForEach`, etc.) |
| **Compilation** | IRGen and ModGen convert pipelines to executable Petri nets |
| **Execution** | NetRunner, JobController, and Router for distributed execution |
| **CLI** | `dfm` command for development, federation management, and deployment |
| **Targets** | Flare (distributed) and Local (multiprocessing) execution backends |

Additional DFM packages provide domain-specific adapters:

| Package | Description |
|---------|-------------|
| [`nv-dfm-lib-common`](https://pypi.org/project/nv-dfm-lib-common/) | Shared schemas and utilities used across adapter libraries |
| [`nv-dfm-lib-weather`](https://pypi.org/project/nv-dfm-lib-weather/) | Experimental weather and climate data adapters (GFS, ECMWF, HRRR, SFNO, cBottle) |

## Installation

```bash
pip install nv-dfm-core
```

Or from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/NVIDIA/data-federation-mesh.git
cd data-federation-mesh
uv sync --package nv-dfm-core
```

## Quick Start

```python
from nv_dfm_core.api import Pipeline, Yield, PlaceParam
from nv_dfm_core.session import Session

# Define a pipeline
with Pipeline() as p:
    result = SomeOperation(...)
    Yield(value=result)

# Execute with a session (see tutorials for federation setup)
with Session(federation="my_federation") as session:
    job = session.execute(p)
    for result in job.results():
        print(result)
```

## Documentation

- [DFM Documentation](https://nvidia.github.io/data-federation-mesh/index.html)
- [Installation Guide](https://nvidia.github.io/data-federation-mesh/userguide/about/installation.html)
- [CLI Reference](https://nvidia.github.io/data-federation-mesh/userguide/cli/index.html)
- [Tutorials](https://github.com/NVIDIA/data-federation-mesh/tree/main/tutorials)

## License

Apache License 2.0. See the [LICENSE](https://github.com/NVIDIA/data-federation-mesh/blob/main/LICENSE) file for details.
