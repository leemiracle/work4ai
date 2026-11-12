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

# Site Customization

This guide explains how to customize DFM Sites with custom properties and methods.

## Overview

DFM Sites can be customized by:
1. Creating a custom Site subclass
2. Referencing it via `impl:` in the federation configuration
3. Accessing custom properties/methods from adapters

## Example: SiteWithLocalStorage

The following example adds local storage support via environment variables. This file should live alongside your other federation code — for example, `myfed/lib/site_with_local_storage.py`:

```python
# myfed/lib/site_with_local_storage.py

import nv_dfm_core.exec
import logging
import os
from pathlib import Path


class SiteWithLocalStorage(nv_dfm_core.exec.Site):
    """Extended DFM Site with a local storage path configured via environment variable."""

    def __init__(self, *args, **kwargs) -> None:
        self._env_var_name = kwargs.pop("dfm_local_storage_env_var", "DFM_LOCAL_STORAGE")
        super().__init__(*args, **kwargs)
        self._logger: logging.Logger = logging.getLogger(__name__)

    def dfm_local_storage(self) -> Path:
        """
        Returns the local storage path, creating it if necessary.
        
        Reads from environment variable (default: DFM_LOCAL_STORAGE).
        Falls back to Path.home() / "dfm-local-storage" if not set.
        """
        env_path = os.environ.get(self._env_var_name)
        if env_path:
            path = Path(env_path)
        else:
            self._logger.warning(
                f"Environment variable {self._env_var_name} not set. "
                f"Using user home folder for site {self.dfm_context.this_site}."
            )
            path = Path.home() / "dfm-local-storage"

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if not path.is_dir():
            raise FileExistsError(f"Local storage directory {path} is not a directory")

        return path
```

## Usage

### In Adapters

Since `dfm_local_storage()` is a method, access it directly in your adapter for example `myfed/lib/my_adapter.py`):

```python
# myfed/lib/my_adapter.py

from nv_dfm_core.exec import Site, Provider

class MyAdapter:
    def __init__(self, site: Site, provider: Provider | None):
        self._site = site

    async def body(self, input_data: str) -> str:
        storage_path = self._site.dfm_local_storage()
        output_file = storage_path / "result.txt"
        output_file.write_text(f"Processed: {input_data}")
        return str(output_file)
```

### Configuration

Reference your custom site class and adapter in the federation configuration (`federation.dfm.yaml`):

```yaml
sites:
  local_worker:
    impl:
      path: myfed.lib.site_with_local_storage.SiteWithLocalStorage
      args:
        # Optional: custom environment variable name
        dfm_local_storage_env_var: "CUSTOM_STORAGE_PATH"
    interface:
      "#/operations/data.ProcessData":
        adapter: myfed.lib.my_adapter.MyAdapter
        is-async: true
```

### Environment Variables

Set the storage path using the environment variable:

```bash
export DFM_LOCAL_STORAGE="/data/my_federation/storage"
```

Or in deployment configs (Kubernetes/Docker):

```yaml
env:
  - name: DFM_LOCAL_STORAGE
    value: "/data/my_federation/storage"
```

## Key Points

```{note}

- **Custom Site must extend `nv_dfm_core.exec.Site`** — Call `super().__init__()` with required parameters
- **Methods vs Properties** — Methods (like `dfm_local_storage()`) are called directly in adapters. Properties can be used with `from-site:` in YAML configuration
- **Environment variables** — Useful for deployment-specific configuration without code changes

```