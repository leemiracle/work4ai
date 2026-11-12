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

Shared schemas and validation utilities used across DFM adapter libraries.

## Installation

This package is typically installed as a dependency of other `nv-dfm-lib-*` packages:

```bash
pip install nv-dfm-lib-common
```

## Schemas

| Schema | Description |
|--------|-------------|
| `GeoJsonFile` | Pydantic model for GeoJSON file output |
| `TextureFile` | Pydantic model for texture file output |
| `TextureFileList` | Pydantic model for texture file list output |

### XArray Schemas

Schema definitions and validation for xarray Datasets:

| Component | Description |
|-----------|-------------|
| `XArraySchema` | Main schema class for defining and validating xarray Dataset structure |
| `DataVariable`, `Coordinate`, `Attribute` | Schema building blocks for variables, coordinates, and attributes |
| `check_dims`, `check_dtype`, `check_range`, ... | Validation functions for dataset dimensions, types, ranges, and CF conventions |

## Usage

```python
from nv_dfm_lib_common.schemas import GeoJsonFile, TextureFile, TextureFileList
from nv_dfm_lib_common.schemas.xarray import XArraySchema, check_dims, check_dtype
```

When building your own adapter library, use `nv-dfm-lib-common` schemas to keep return types consistent with the rest of the ecosystem.
