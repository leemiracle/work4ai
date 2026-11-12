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

# nv-dfm-lib-weather

Weather and climate data adapters for [NVIDIA Data Federation Mesh (DFM)](https://github.com/NVIDIA/data-federation-mesh).

## What is DFM?

Data Federation Mesh (DFM) is a Python-based framework for creating and orchestrating complex workflows that process data from various distributed sources and stream results into applications. DFM determines where to run each operation of a data processing pipeline and handles data movement between sites automatically.

> **Experimental:** This library is provided as a collection of examples and starting points for building your own adapters. Before any production use, review and extensively test all adapters in your target environment.

## Overview

`nv-dfm-lib-weather` provides pre-built adapters for weather and climate data sources, AI models, and xarray processing:

| Category | Adapters |
|----------|----------|
| **Data Loaders** | GFS, ECMWF ERA5, HRRR, CMIP6 |
| **Xarray** | VariableNorm, ConvertToUint8, RenderUint8ToImages, caching |
| **AI Models** | SFNO (Spherical Fourier Neural Operator), cBottle (Climate in a Bottle) |

## Installation

```bash
pip install nv-dfm-lib-weather
```

Or with `uv` in the monorepo:

```bash
uv sync --package nv-dfm-lib-weather
```

> **Note:** This package depends on `earth2studio`, which may require additional dependencies depending on your environment. See the [Weather Data Library](https://nvidia.github.io/data-federation-mesh/userguide/about/installation.html#installing-the-weather-data-library) section of the installation guide for details.

### Optional Extras

| Extra | Description |
|-------|-------------|
| `cbottle` | cBottle (Climate in a Bottle) model adapters (video, TC guidance, super-resolution, infilling, data gen) |
| `sfno` | Spherical Fourier Neural Operator for weather prediction |
| `all` | All optional AI model dependencies |

```bash
uv sync --package nv-dfm-lib-weather --extra sfno
uv sync --package nv-dfm-lib-weather --extra cbottle
```

### GPU Prerequisites for AI Model Adapters

The SFNO and cBottle adapters perform GPU-accelerated AI inference. Before installing these extras, ensure you have:

- **NVIDIA GPU** with compute capability ≥ 8.9 and ≥ 40 GB GPU memory. See [CUDA GPUs](https://developer.nvidia.com/cuda-gpus).
- **NVIDIA GPU Drivers** — see the [Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/index.html).
- **CUDA Toolkit 12.8** (tested) — see [CUDA Downloads](https://developer.nvidia.com/cuda-downloads).
- **PyTorch with CUDA support** matching your toolkit version — see [pytorch.org](https://pytorch.org/). Example:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
  ```
- **[Earth2Studio 0.10.0](https://nvidia.github.io/earth2studio/v/0.10.0/userguide/about/install.html)** — installed automatically as a dependency. See the Earth2Studio docs for model-specific setup details.

> **Note:** The `cbottle` and `sfno` extras depend on packages (`cbottle`, `earth2grid`, `makani`) that are not published on PyPI. When installing from source with `uv`, these resolve automatically via workspace git sources. When installing the published wheel via `pip`, users must install them manually — a clear error message with instructions is shown at runtime if they are missing.

## Adapters

### Data Loaders

| Adapter | Description |
|---------|-------------|
| `LoadGfsEra5Data` | GFS data via Earth2Studio (AWS backend) |
| `LoadEcmwfEra5Data` | ECMWF ERA5 reanalysis data |
| `LoadHrrrEra5Data` | HRRR high-resolution data |
| `LoadCmip6Data` | CMIP6 climate model data |

### Xarray Processing

| Adapter | Description |
|---------|-------------|
| `VariableNorm` | Normalize xarray variables |
| `ConvertToUint8` | Convert to uint8 for visualization |
| `RenderUint8ToImages` | Render datasets to PNG textures |

### AI Models (optional extras)

| Adapter | Description |
|---------|-------------|
| `SfnoPrognostic` | Spherical Fourier Neural Operator for weather prediction |
| `CbottleVideo` | video prognostic Climate in a Bottle |
| `CbottleInfilling` | Climate in a bottle infill diagnostic |
| `CbottleSuperResolution` | cBottle super-resolution |
| `CBottleTropicalCycloneGuidance` | cBottle tropical cyclone guidance diagnostic |
| `CbottleDataGen` | CBottle3D synthetic climate data generator|

## DFM Ecosystem

| Package | Description |
|---------|-------------|
| [`nv-dfm-core`](https://pypi.org/project/nv-dfm-core/) | Core framework — Pipeline API, execution engine, code generation, and CLI |
| [`nv-dfm-lib-common`](https://pypi.org/project/nv-dfm-lib-common/) | Shared schemas and utilities used across adapter libraries |

## Dependencies

- `nv-dfm-core` – Core DFM framework
- `nv-dfm-lib-common` – Shared schemas (GeoJsonFile, TextureFile, etc.)
- `earth2studio[data]` – Data loaders (GFS, ECMWF, HRRR, CMIP6)
- `xarray`, `netCDF4`, `rioxarray` – Data handling

## Documentation

- [DFM Documentation](https://nvidia.github.io/data-federation-mesh/index.html)
- [Weather Tutorial](https://github.com/NVIDIA/data-federation-mesh/tree/main/tutorials/weather-fed) – pipelines and adapters for weather data
- [Tutorials](https://github.com/NVIDIA/data-federation-mesh/tree/main/tutorials)

## License

Apache License 2.0. See the [LICENSE](https://github.com/NVIDIA/data-federation-mesh/blob/main/LICENSE) file for details.
