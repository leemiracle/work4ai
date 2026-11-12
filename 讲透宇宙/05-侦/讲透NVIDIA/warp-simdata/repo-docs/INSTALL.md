<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Installation

Install the core package to process arrays from Python. Add extras for custom integrations or development.

## Core package

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install "warp-simdata==0.2.0"
```

Requirements:

- Python >=3.10
- `warp-lang>=1.17.0`
- `numpy>=1.20.0`
- For CUDA execution, a compatible NVIDIA GPU and driver; see [Warp's runtime requirements](https://nvidia.github.io/warp/stable/user_guide/installation.html#cuda-requirements).

CPU execution is supported, including the [quickstart](README.md#quick-start).
**As of Warp 1.17, CPU kernels run on a single thread.**

Verify the installed version and available devices:

```bash
python -c "import warp as wp, warp_simdata as sd; wp.init(); print(sd.__version__, wp.get_devices())"
```

To install a downloaded [release wheel](https://github.com/NVIDIA/warp-simdata/releases), run from its directory:

```bash
python -m pip install ./warp_simdata-0.2.0-py3-none-any.whl
```

## Optional dependencies

Add an extra when installing, for example:

```bash
python -m pip install "warp-simdata[vtk]==0.2.0"
```

| Extra | Adds | Notes |
| --- | --- | --- |
| `usd` | CAE OpenUSD Plugins >=0.1.0 | Scientific schemas, native-format plugins, and a matching OpenUSD runtime; see the verified setup below. |
| `vtk` | VTK >=9.6 | [VTK object adapters](docs/VTK.md). Warp-native VTK layouts need no VTK installation. |
| `paraview` | NVTX | [ParaView plugin](extras/paraview/README.md) from a source checkout. ParaView supplies VTK; match its Python minor version. |
| `test` | pytest, HDF5, VTK, test plugins | [Test suite](tests/README.md), excluding the optional USD runtime. |
| `dev` | `test`, linting and formatting tools | Source development; does not include `usd`. |

### Standalone OpenUSD

Requirements for the verified CAE OpenUSD Plugins 0.1.2 combined wheel:

- CPython 3.12
- x86-64 Linux (glibc >=2.35) or Windows x64
- PyPI `usd-core` version 25.11, 26.3, 26.5, or 26.8

For example, in a Python 3.12 environment:

```bash
python -m pip install "warp-simdata[usd]==0.2.0" "cae-openusd-plugins==0.1.2" "usd-core==26.8"
```

Follow [plugin registration and loading](docs/USDAPI.md) before using scientific schemas. These wheel constraints are narrower than core Python support. Other OpenUSD builds require a compatible plugin build; see [upstream installation](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins/blob/main/docs/installation.md).

## From source

In an activated virtual environment, clone and install the release:

```bash
git clone --branch v0.2.0 https://github.com/NVIDIA/warp-simdata.git
cd warp-simdata
python -m pip install .
```

For development, use an editable install, then format and lint:

```bash
python -m pip install -e ".[dev]"
ruff format warp_simdata/ tests/
ruff check warp_simdata/ tests/
```

This editable install adds development tools and uses your checkout, so Python source edits take effect without reinstalling.

Optional extras use the same names, such as `".[usd]"` or `".[vtk]"`; see [optional dependencies](#optional-dependencies) for runtime requirements.

Run the [basic pipeline](docs/examples/basic_pipeline.py) with `python docs/examples/basic_pipeline.py --device cpu`.

Git LFS is needed for test fixture payloads. See [test setup and commands](tests/README.md).

Build a wheel and source archive in `dist/`:

```bash
python -m pip install build
python -m build
```

See [versioning](docs/versioning.md) for artifact identity and compatibility.
