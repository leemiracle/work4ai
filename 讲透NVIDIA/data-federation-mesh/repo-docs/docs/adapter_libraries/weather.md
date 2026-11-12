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

Pre-built adapters for weather and climate data workflows.

## Installation

```bash
pip install nv-dfm-lib-weather
```

AI model adapters require GPU hardware and are installed via extras:

```bash
pip install nv-dfm-lib-weather[sfno]     # SFNO model
pip install nv-dfm-lib-weather[cbottle]  # cBottle (Climate in a Bottle) models
pip install nv-dfm-lib-weather[all]      # all optional dependencies
```

## Data Loaders

| Adapter | Description |
|---------|-------------|
| `LoadGfsEra5Data` | GFS data via Earth2Studio (AWS backend) |
| `LoadEcmwfEra5Data` | ECMWF ERA5 reanalysis data |
| `LoadHrrrEra5Data` | HRRR high-resolution data |
| `LoadCmip6Data` | CMIP6 climate model data |

## XArray Processing

| Adapter | Description |
|---------|-------------|
| `VariableNorm` | Normalize xarray variables |
| `ConvertToUint8` | Convert to uint8 for visualization |
| `RenderUint8ToImages` | Render datasets to PNG textures |

## AI Models (optional extras)

| Adapter | Extra | Description |
|---------|-------|-------------|
| `SfnoPrognostic` | `sfno` | Spherical Fourier Neural Operator for weather prediction |
| `CbottleVideo` | `cbottle` | video prognostic Climate in a Bottle
| `CbottleInfilling` | `cbottle` | Climate in a bottle infill diagnostic |
| `CbottleSuperResolution` | `cbottle` | cBottle super-resolution |
| `CBottleTropicalCycloneGuidance` | `cbottle` | cBottle tropical cyclone guidance diagnostic |
| `CbottleDataGen` | `cbottle` | CBottle3D synthetic climate data generator |

## Adapter Configurations

Each adapter includes a YAML configuration file (under `nv_dfm_lib_weather/configs/`) that declares its operation signature — parameters, types, and return values. These configs can be referenced directly from your federation's `.dfm.yaml` to expose adapters as operations.
