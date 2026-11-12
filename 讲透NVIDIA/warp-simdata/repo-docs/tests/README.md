<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Testing

Run from the repository root of a source checkout. Install test dependencies and fetch the [Git LFS fixtures](data/README.md):

```bash
python -m pip install -e ".[test]"
git lfs install
git lfs pull
python -m pytest tests/ -m "not usd"
```

The `test` extra includes pytest plugins, HDF5, and VTK. For USD tests, also install the [compatible OpenUSD runtime and plugins](../INSTALL.md#standalone-openusd), then run `python -m pytest tests/`. The `cae_openusd_plugins` fixture checks compatibility and registers schemas. Missing dependencies can cause skips or collection/setup errors; inspect the summary.

Kernel compilation can dominate the first run. To choose a writable cache:

```bash
export WARP_CACHE_PATH=/tmp/warp-simdata-test-cache
```

## Select tests

```bash
python -m pytest tests/test_bounds.py::test_sids_hex
python -m pytest tests/test_element_faces.py
python -m pytest tests/ -m "not slow and not usd"
python -m pytest tests/ --cov=warp_simdata --cov-report=html
python -m pytest tests/ -n 2 -m "not usd"
python -m pytest tests/ --collect-only -q
```

Parallel workers allocate their own GPU resources; choose a count that fits memory. [pytest.ini](../pytest.ini) registers `slow`, `usd`, `vtk`, `cgns`, `sids`, `operator`, `datamodel`, and `collection`. There is no `gpu` marker. Markers select tests after modules are imported, so they do not isolate all optional dependencies.

### Devices

The `device` fixture and several dataset fixtures use CPU and `cuda:0` when available. `cpu_device` selects CPU; `gpu_device` skips without CUDA.

```bash
python -m pytest tests/ -m "not usd" -k "cpu and not cuda"
python -m pytest tests/ -m "not usd" -k cuda
```

These are **name filters**, not global device switches. They omit cases without a matching ID, and selected tests may create other devices. Use `--collect-only` with the same selector to inspect coverage.

## Find or add coverage

| Area | Location |
| --- | --- |
| Datasets and fields | `test_datasets.py`, `test_field_api.py`, `test_field_range.py` |
| Operators | Operator-named modules such as `test_probe.py` and `test_element_faces.py` |
| Shapes and ordering | `test_shape_function_topology.py`, `test_sids_shapes.py`, `test_vtk_shapes.py` |
| USD adapters | `test_usd_*.py`, `test_warp_simdata_usd_namespace.py` |
| Shared fixtures | `conftest.py`, `test_utils/` |
| Source data and readers | `data/`, `support/io/` |

`tests/support/io/` is test support, not an installed file-loading API. File-backed tests use `tests/data`; override it with `--data-dir /path/to/fixtures`. LFS pointers must be replaced with payloads before testing.

Reuse a dataset fixture's device. For example, save this as `tests/test_bounds_example.py`:

```python
import numpy as np
import pytest

from warp_simdata.operators import bounds


@pytest.mark.operator
def test_bounds_example(sids_hex_dataset):
    result = bounds.compute(sids_hex_dataset)
    assert result.device == sids_hex_dataset.device
    np.testing.assert_allclose(result.get_field("bounds_min").to_array().numpy(), [[-1.0, -1.0, -0.5]])
    np.testing.assert_allclose(result.get_field("bounds_max").to_array().numpy(), [[1.0, 1.0, 0.5]])
```

```bash
python -m pytest tests/test_bounds_example.py
```

`Field.to_array()` reads logical values without assuming a storage layout. A surrounding `wp.ScopedDevice` does not move a fixture. For newly constructed datasets, accept the `device` fixture and allocate all inputs there. Inspect tuple-valued fixtures before use; `any_dataset` covers selected models, not every model.

Also check associations, topology, provenance, and empty/invalid behavior where relevant.

## Documentation and integration checks

The core-only examples check their results and accept `--device cpu` or `--device cuda:0`:

```bash
python docs/examples/basic_pipeline.py --device cpu
python docs/examples/kernel_operator.py --device cpu
python docs/examples/custom_model.py --device cpu
```

Validate core CPU, core CUDA, optional OpenUSD, VTK, and AOT paths separately. One group does not establish another's coverage. The [ParaView tests](../extras/paraview/README.md#tests) require ParaView's matching `pvpython` runtime.
