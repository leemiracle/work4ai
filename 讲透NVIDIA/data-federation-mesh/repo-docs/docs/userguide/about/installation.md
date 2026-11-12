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

# Installation

DFM is distributed as a set of Python packages:

| Package | Description |
|---------|-------------|
| `nv-dfm-core` | Core framework — Pipeline API, execution engine, code generation, and CLI |
| `nv-dfm-lib-common` | Shared schemas and utilities used across adapter libraries |
| `nv-dfm-lib-weather` | Weather and climate data adapters (ECMWF, GFS, HRRR, SFNO, cBottle) |

`nv-dfm-core` is the only required package. The adapter libraries are optional and can be installed separately depending on your use case. See [Adapter Libraries](../../adapter_libraries/index.md) for more details.

## Install From PyPI

```bash
# Install core framework only
pip install nv-dfm-core

# Install weather adapters (includes core and common packages)
pip install nv-dfm-lib-weather
```

## Install From Source Code

DFM uses [uv](https://docs.astral.sh/uv/) to manage dependencies.

```{tip}
If you don't have `uv` installed, follow the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
```

```{admonition} Prerequisites
:class: warning

On Debian/Ubuntu systems, make sure the following system packages are installed:

    sudo apt update && sudo apt install -y curl gcc
```

Clone the repository:
```bash
git clone https://github.com/NVIDIA/data-federation-mesh.git
cd data-federation-mesh
```

Install all workspace packages:
```bash
uv sync --all-packages
```

Or install a single package:
```bash
uv sync --package nv-dfm-core
```

To run the tutorials, add the `tutorials` extra:
```bash
uv sync --all-packages --extra tutorials
```

```{note}
This is a multi-package workspace. Each `uv sync` invocation reconfigures the virtual environment to match exactly the requested set of packages — syncing for a single package will remove dependencies that are not required by that package. Use `--all-packages` when you need the full workspace available.
```

## Installing the Weather Data Library

The `nv-dfm-lib-weather` package contains adapters for loading and processing weather data from different sources.
This library relies on [Earth2Studio](https://nvidia.github.io/earth2studio/v/0.10.0/userguide/about/install.html) and its dependencies.

```{admonition} Experimental
:class: warning
`nv-dfm-lib-weather` is **experimental**. It is provided as a collection of examples and starting points for building your own adapters. Before any production use, review and extensively test all adapters in your target environment.
```

To install `nv-dfm-lib-weather` without AI models:
```bash
pip install nv-dfm-lib-weather
```

Or from source:
```bash
uv sync --package nv-dfm-lib-weather
```

```{note}
This package uses `earth2studio`, which may require additional setup depending on your environment. See the [AI Model Adapters](#ai-model-adapters-sfno-cbottle) section below for GPU prerequisites and instructions.
```

### AI Model Adapters (SFNO, cBottle)

The SFNO and cBottle adapters perform GPU-accelerated AI inference and require additional system-level prerequisites and Python packages beyond the base installation.

```{admonition} GPU Prerequisites
:class: warning

The following must be installed and configured **before** installing the AI model extras:

1. **NVIDIA GPU** — A CUDA-capable GPU with compute capability ≥ 8.9 and ≥ 40 GB of GPU memory is recommended. See [CUDA GPUs](https://developer.nvidia.com/cuda-gpus) for a list of supported hardware.

2. **NVIDIA GPU Drivers** — Install the appropriate driver for your GPU and OS. See the [NVIDIA Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/index.html).

3. **CUDA Toolkit** — CUDA 12.8 is the tested and recommended version. See [CUDA Toolkit Downloads](https://developer.nvidia.com/cuda-downloads).

4. **PyTorch** — Must be installed with CUDA support matching your CUDA toolkit version. See [pytorch.org](https://pytorch.org/) for platform-specific install commands. For example:
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    ```

5. **Earth2Studio model-specific dependencies** — The SFNO and cBottle models require packages that are not available on PyPI and must be installed manually. Follow the per-model installation instructions in the [Earth2Studio 0.10.0 Installation Guide](https://nvidia.github.io/earth2studio/v/0.10.0/userguide/about/install.html#optional-dependencies):
    - **SFNO**: requires `makani` (installed from git). See the [SFNO section](https://nvidia.github.io/earth2studio/v/0.10.0/userguide/about/install.html#sfno).
    - **cBottle**: requires `earth2grid` and `cbottle` (installed from git with `--no-build-isolation`). See the [CBottle section](https://nvidia.github.io/earth2studio/v/0.10.0/userguide/about/install.html#cbottle).

6. **Earth2Studio 0.10.0** — Installed automatically as a dependency of `nv-dfm-lib-weather`. The AI model extras (`cbottle`, `sfno`) pull in the corresponding Earth2Studio optional dependencies.
```

Install the AI model extras:

```bash
pip install nv-dfm-lib-weather[cbottle]   # cBottle (Climate in a Bottle) model adapters
pip install nv-dfm-lib-weather[sfno]      # SFNO (Spherical Fourier Neural Operator) adapters
pip install nv-dfm-lib-weather[all]       # all optional AI model dependencies
```

Or from source:
```bash
uv sync --package nv-dfm-lib-weather --extra cbottle
uv sync --package nv-dfm-lib-weather --extra sfno
uv sync --package nv-dfm-lib-weather --extra all
```

```{note}
When installing from source with `uv`, the non-PyPI dependencies (`cbottle`, `earth2grid`, `makani`) are resolved automatically via git sources configured in the workspace — no manual installation of step 5 is needed. The manual step 5 is only required when installing the published wheel via `pip`.
```

