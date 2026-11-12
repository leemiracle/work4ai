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

# Adapter Libraries

```{admonition} Experimental
:class: warning
The adapter libraries (`nv-dfm-lib-common` and `nv-dfm-lib-weather`) are **experimental**.
They are provided as examples and starting points for building your own adapters.
Before any production use, review and extensively test all adapters in your target environment.
```

In addition to the core `nv-dfm-core` package, DFM ships optional adapter library packages that provide reusable schemas and ready-made adapters for common data processing tasks. These libraries are intended to accelerate development by offering working examples that can be used directly or adapted to your needs.

## Package Overview

| Package | Purpose | Install |
|---------|---------|---------|
| `nv-dfm-lib-common` | Shared schemas and validation utilities used across adapter libraries | `pip install nv-dfm-lib-common` |
| `nv-dfm-lib-weather` | Weather and climate data adapters (data loaders, processing, AI models) | `pip install nv-dfm-lib-weather` |

Both packages depend on `nv-dfm-core`. The weather library also depends on `nv-dfm-lib-common` for shared output schemas.

```
nv-dfm-core           (core framework, no lib dependencies)
  └── nv-dfm-lib-common    (shared schemas: XArraySchema, GeoJsonFile, TextureFile)
        └── nv-dfm-lib-weather  (weather adapters, data loaders, AI models)
```

## Using Library Adapters in Your Federation

To use an adapter from a library package in your federation:

1. **Install the library** alongside `nv-dfm-core`.
2. **Reference the adapter** in your site's interface section of `.dfm.yaml`, mapping the operation to the adapter class.
3. **Run code generation** (`dfm gen`) to produce the operations API.

See [Adapters & Operations](../userguide/development/adapters.md) for the full details on how adapters are bound to operations and exposed to pipeline users, and [Federation Configuration](../userguide/development/federation_configuration.md) for `.dfm.yaml` syntax.

## Writing Your Own Adapter Library

The `nv-dfm-lib-*` packages in this repository serve as examples. In practice, you should build your own adapters and federations in separate repositories, using these packages as reference for structure and conventions. A new adapter library should:

1. Live in its own repository alongside your federation configuration.
2. Depend on `nv-dfm-core` and optionally `nv-dfm-lib-common` for shared schemas.
3. Include YAML config files declaring each adapter's operation signature.
4. Include tests — see `tests/unit/nv_dfm_lib_weather/` in this repository for examples of adapter unit tests.

```{toctree}
:maxdepth: 1
:hidden:

common
weather
```
