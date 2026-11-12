<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Warp SimData

GPU-accelerated simulation-data processing across common scientific data models, built on [NVIDIA Warp](https://nvidia.github.io/warp/).

As solvers and AI physics accelerate, processing large simulation outputs becomes the bottleneck to scientific and engineering decisions. Warp SimData provides slicing, iso-surfaces, probing, streamlines, external-face extraction, voxelization, and field transformations for analysis, visualization, and simulation-data preparation.

Developers and their agents can reuse performance tuned and tested algorithms for supported scientific representations, and extend model interfaces for custom layouts. Use it directly from Python or through existing (optional) OpenUSD and VTK integrations.

## Performance

Warp SimData can substantially reduce processing time for common operations on large structured, unstructured, and polyhedral datasets. Its algorithms are tuned for GPU execution to make interactive visualization and high-throughput simulation data processing practical.

Initial benchmarks on unstructured meshes of varying sizes showed average speedups of roughly 14–40× over CPU implementations and 5–25× over GPU implementations for slicing, iso-surface extraction, and field averaging. Average speedups reached 90×+ over CPU implementations for element-center computation, streamlines on structured grids, and iso-surface extraction on polyhedral meshes.

Performance varies with the operator, data layout, hardware, and reuse of prepared data. See [performance guidance](docs/PythonAPI.md#performance) for data reuse and timing.

## Installation

```bash
python -m pip install "warp-simdata==0.2.0"
```

### Requires 
* Python 3.10+
* Warp 1.17+
* NumPy 1.20+
* An NVIDIA CUDA-capable GPU and compatible driver for CUDA execution; CPU
  execution is also supported
* Git LFS when cloning the full source tree and its test data

See [installation][install] for optional dependencies and wheels, or [install from source](INSTALL.md#from-source).

## Quick start

Create a scalar field on a grid, extract a spherical iso-surface, and slice the grid. This example needs only the core package.

```python
import numpy as np
import warp as wp

import warp_simdata as simdata
from warp_simdata.data_models.vtk import image_data
from warp_simdata.operators import iso_surface, slice

device = "cuda:0" if wp.is_cuda_available() else "cpu"

# A 101^3-node grid on [-1, 1]^3, with distance from the center at each node.
n = 101
grid = image_data.create_dataset(
    origin=wp.vec3f(-1.0), spacing=wp.vec3f(2.0 / (n - 1)),
    extent_min=wp.vec3i(0), extent_max=wp.vec3i(n - 1), device=device,
)
x = np.linspace(-1.0, 1.0, n, dtype=np.float32)
z, y, x = np.meshgrid(x, x, x, indexing="ij")  # x varies fastest
radius = np.sqrt(x**2 + y**2 + z**2).ravel()
grid.add_field("radius", simdata.Field.from_array(wp.array(radius, device=device), simdata.AssociationType.NODE))

sphere = iso_surface.compute(grid, "radius", 0.5)
plane = slice.compute(grid, origin=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), field_names=["radius"])
print(sphere.get_num_elems(), plane.get_num_elems())  # 22808 20000
```

The outputs are triangular surface datasets. `plane` also carries the sampled `radius` field. The first call compiles kernels. For a broader workflow, see [basic_pipeline.py][pipeline].

## What's included

- **Operators:** geometry/topology queries, field averaging, sampling, surface extraction, streamlines, and voxelization. See the [operator reference][python].
- **Data models:** VTK layouts, CGNS/SIDS, EnSight Gold, OpenFOAM, FLASH, reservoir corner-point grids, and custom point/curve/surface models. [Capabilities vary by model][datasets]; adapters may convert or materialize arrays. VTK-shaped Warp models work without VTK installed.
- **Extension interfaces:** specialize operators on an existing representation or supply a new model through [kernel interfaces][kernel].

| Optional integration | Purpose |
| --- | --- |
| [OpenUSD][usd] | Load scientific prims through [CAE OpenUSD Plugins](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins), which provides native-format access and composition. |
| [VTK][vtk] | Adapt existing objects and return VTK-owned results. |
| [ParaView][paraview] | Use operators as filters through the source-checkout plugin. |

Construct datasets from arrays or use these adapters. Warp SimData handles in-memory compute and analysis; its sampling and extraction can feed AI-data preparation.

## Documentation

| Task | Start here |
| --- | --- |
| Install or develop | [Installation][install] |
| Choose inputs, fields, and devices | [Datasets and fields][datasets] |
| Run operators or understand performance | [Python API][python] |
| Add a model or operator | [Kernel API][kernel], [shape functions][shapes] |
| Upgrade | [Changelog][changelog], [versioning][versioning] |
| Run tests | [Test guide][tests] |

## Project

Warp SimData is a pre-1.0 library maintained by NVIDIA. Minor releases may change APIs; operator-specific experimental features are identified in the reference. It is a Warp ecosystem library, separate from `warp-lang` and the Warp core team's maintenance. Issues and releases are managed here.

- [Support](SUPPORT.md): best-effort assistance through GitHub Issues.
- [Contributing](CONTRIBUTING.md): the project currently does not accept contributions.
- [Security](SECURITY.md): use the private disclosure process.
- [Governance](GOVERNANCE.md) and [maintainers](MAINTAINERS.md).
- [Apache-2.0 license](LICENSE.md) and [third-party notices](NOTICE.md).

[install]: INSTALL.md
[python]: docs/PythonAPI.md
[datasets]: docs/DatasetsAndFields.md
[kernel]: docs/KernelAPI.md
[shapes]: docs/ShapeFunctions.md
[usd]: docs/USDAPI.md
[vtk]: docs/VTK.md
[paraview]: extras/paraview/README.md
[pipeline]: docs/examples/basic_pipeline.py
[changelog]: CHANGELOG.md
[versioning]: docs/versioning.md
[tests]: tests/README.md
