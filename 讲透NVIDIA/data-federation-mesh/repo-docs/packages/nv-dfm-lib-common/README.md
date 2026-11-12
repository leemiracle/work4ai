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

# nv-dfm-lib-common

Shared schemas and utilities for [NVIDIA Data Federation Mesh (DFM)](https://github.com/NVIDIA/data-federation-mesh) adapter libraries.

## What is DFM?

Data Federation Mesh (DFM) is a Python-based framework for creating and orchestrating complex workflows that process data from various distributed sources and stream results into applications. DFM determines where to run each operation of a data processing pipeline and handles data movement between sites automatically.

## Overview

`nv-dfm-lib-common` provides common building blocks used across DFM adapter libraries such as `nv-dfm-lib-weather`:

| Component | Description |
|-----------|-------------|
| **Output Schemas** | Pydantic models for adapter return types: `GeoJsonFile`, `TextureFile`, `TextureFileList` |
| **XArray Schemas** | Schema definitions and validation for xarray Datasets (`XArraySchema`, coordinate/variable checks) |

This package is part of the DFM ecosystem:

| Package | Description |
|---------|-------------|
| [`nv-dfm-core`](https://pypi.org/project/nv-dfm-core/) | Core framework — Pipeline API, execution engine, code generation, and CLI |
| [`nv-dfm-lib-weather`](https://pypi.org/project/nv-dfm-lib-weather/) | Experimental weather and climate data adapters (GFS, ECMWF, HRRR, SFNO, cBottle) |

## Installation

This package is typically installed as a dependency of other `nv-dfm-lib-*` packages:

```bash
pip install nv-dfm-lib-common
```

Or from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/NVIDIA/data-federation-mesh.git
cd data-federation-mesh
uv sync --package nv-dfm-lib-common
```

## Usage

```python
from nv_dfm_lib_common.schemas import GeoJsonFile, TextureFile, TextureFileList
from nv_dfm_lib_common.schemas.xarray import XArraySchema, check_dims, check_dtype
```

## Documentation

- [DFM Documentation](https://nvidia.github.io/data-federation-mesh/index.html)
- [Installation Guide](https://nvidia.github.io/data-federation-mesh/userguide/about/installation.html)
- [Tutorials](https://github.com/NVIDIA/data-federation-mesh/tree/main/tutorials)

## License

Apache License 2.0. See the [LICENSE](https://github.com/NVIDIA/data-federation-mesh/blob/main/LICENSE) file for details.
