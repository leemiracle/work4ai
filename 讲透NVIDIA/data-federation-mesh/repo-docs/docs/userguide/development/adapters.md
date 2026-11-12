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

# Adapters and Operations

Adapters are concrete implementations of DFM functionality. They are classes initialized with `site` and `provider`, with a single `body()` method that accepts input arguments and returns output.

## Adapter Structure

```python
from dfm.exec import Site, Provider

class MyNewAdapter:
    def __init__(self, site: Site, provider: Provider | None):
        self._site = site
        self._provider = provider

    async def body(self, param_1: Any, local_param: str) -> Any:
        # body implementation
        return output
```

## Adapters versus Operations

- **Adapters** — created by adapter developers; maintained and tested separately. DFM users do not interact with adapters directly.
- **Operations** — the public API. Users call operations in their pipelines and apps. Operations define how adapters are exposed (or not) to federation or site users.

Adapters implement functionality; operations define the interface users see.

## Defining Operations

All public operations are listed in the `operations` section of the [configuration file](./federation_configuration.md) (`.dfm.yaml`) and defined by the federation administrator:

```yaml
operations:
  operation_package.UsersExposedOperation:
    description: "This is operations exposed to DFM users"
    parameters:
      param_1:
        description: "First parameter"
        type: _type_
    required:
      - param_1
    returns: _type_
```

## Mapping Operations to Adapters

The site administrator maps public operations to adapters per site. When creating site configuration, they decide which:

- Public operations are available at the site
- Local adapter implements each operation

This mapping is defined in the `sites` section of the [configuration file](./federation_configuration.md):

```yaml
sites:
  my_site:
    interface:
      "#/operations/operation_package.UsersExposedOperation":
      adapter: adapters_dir.lib.my_adapter.MyAdapter
      args:
        param_1:
          from-param: param_1
        local_param:
          const: "Some site-specific param"
```

**Parameter overloading:** When mapping operations to adapters, the operation interface can be overloaded. In the example above, the public operation exposes only `param_1`, but the adapter's `body()` requires two arguments. The extra parameter (`local_param`) is supplied using a constant. This gives site administrators flexibility in how operations are managed.

## Standard Library

DFM includes [adapter libraries](../../adapter_libraries/index.md) with reusable schemas and example adapters as a starting point. Users are expected to write their own adapters tailored to their federation's needs.