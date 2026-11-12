<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# ParaView Extensions

Use Warp SimData through ParaView filters with the source-checkout plugin
`WarpSimData.py`. It is the single entry point; installed wheels do not include
these source-checkout extras. The integration suite targets ParaView 6.0.1 with
Python 3.12.

## Setup

Use a Python interpreter whose minor version matches ParaView. From the
repository root:

```sh
python -m venv .venv-paraview
.venv-paraview/bin/python -m pip install -e '.[paraview]' pytest
paraview --venv "$(pwd)/.venv-paraview"
```

Load `extras/paraview/WarpSimData.py` through ParaView's **Plugin Manager**.
`[paraview]` adds NVTX; ParaView supplies VTK. Do not substitute a separately
installed PyPI VTK for that runtime. See [INSTALL](../../INSTALL.md) for core
requirements and [VTK fidelity limits](../../docs/VTK.md#import-fidelity).

## Filters

Names below omit the common **Warp SimData** prefix. Image links show the UI;
[PythonAPI](../../docs/PythonAPI.md) and the operator pages own compute contracts.

| Filter | Result and decisive controls |
| --- | --- |
| [Streamlines](images/warp-simdata-streamlines.png) | Curves from a selected vector array; Line or Point Cloud seed proxy, direction, adaptive step lengths, maximum steps/error, Pass Input Fields |
| [Streamlines With Custom Source](images/warp-simdata-streamlines-custom-source.png) | Same integration with a second `vtkPointSet` Seed Source; every point is a seed |
| [Slice](images/warp-simdata-slice.png) | Triangular plane intersection; Origin, Normal, Pass Input Fields. See [Slice](../../docs/Slice.md). |
| [Iso Surface](images/warp-simdata-iso-surface.png) | One merged triangular contour; scalar Contour By, Iso Value, Pass Input Fields. Cell scalars are averaged to nodes each execution. See [IsoSurface](../../docs/IsoSurface.md). |
| [Element Faces](images/warp-simdata-element-faces.png) | Faces with `element_idx`/`node_idx` provenance; External Faces Only defaults on, Pass Input Fields. See [ElementFaces](../../docs/ElementFaces.md). |
| [Probe](images/warp-simdata-probe.png) | Sample one Field or Probe All Fields at a second Probe Points input; Generate Valid Mask adds point array `valid` (1 hit, 0 miss) |
| [Mesh Analysis](images/warp-simdata-mesh-analysis.png) | Experimental element centers (automatic/Chebyshev), sizes, bounds, element-node/node-element counts, or selection in a box |
| [Point Data to Cell Data](images/warp-simdata-point-to-cell.png) | Vertex average; selected array, optional Output Array Name (default `<input>_cell`) |
| [Cell Data to Point Data](images/warp-simdata-cell-to-point.png) | Incident-cell average; selected array, optional Output Array Name (default `<input>_point`) |
| [Calculator](images/warp-simdata-calculator.png) | Scalar expression over point or cell arrays; association, expression and output name |
| [Voxelize](images/warp-simdata-voxelize.png) | All supported fields on regular `vtkImageData`; bounds, maximum resolution, point/cell association, Generate Valid Mask |
| [Voronoi Voxelize](images/warp-simdata-voronoi-voxelize.png) | Nearest-seed resampling of point fields, with the same grid/mask controls |

Streamline Line **Resolution** counts segments, yielding one more seed. Point
Cloud exposes Center, Radius and Number of Points. Step lengths multiply the
containing cell's bounding-box diagonal and must satisfy
`0 < Minimum <= Initial <= Maximum`; Maximum Error is positive. Velocity is
normalized; the result's `times` is a propagation parameter, not physical time.

Calculator array names must be Python identifiers, with scalar values and the
chosen association. If point and cell arrays share a name, only the cell array
is available to the expression. Syntax includes arithmetic, comparisons and
`abs`, `sqrt`, `exp`, `log`, `sin`, `cos`, `floor`, `ceil`, `min`, `max`, `pow`,
`clamp`, `where`; expressions are AST-validated, not evaluated as Python code.

Voxel filters output ordinary VTK arrays. NanoVDB storage is a Python operator
option, not a ParaView output option.

## Shared Execution Controls

Every filter exposes **Device** (default `cuda:0`, or `cpu`) and advanced
**Enable Timing**. Converted inputs are shared by object identity, `MTime`,
device and conversion context. Changing operator properties reuses uploaded
arrays and locators; changing the input, its modification time or device
invalidates the conversion. Update VTK modification times after editing arrays.
Two-input filters cache inputs independently; entries are released when their
last filter releases them. Derived fields and outputs can still be rebuilt.

### Composite Inputs

| Filters | Execution domain |
| --- | --- |
| Calculator, field conversion, Mesh Analysis, Slice, Iso Surface, Element Faces | One dataset leaf at a time; multiblock/partitioned hierarchy, names and null blocks are preserved |
| Probe, both Streamlines filters | One homogeneous `vtkPartitionedDataSet` is a domain; searches/curves can cross partitions. A partitioned collection runs once per domain. Multiblock is rejected; convert it to a partitioned collection first. Points/seeds must be non-composite `vtkPointSet`. |
| Both voxel filters | Single dataset only; no composites |

Leaf-local averaging and external-face extraction do not cross partition
boundaries. Most filters rebuild output through `to_vtk`, copying arrays to
host memory. Calculator instead shallow-copies the VTK input and appends a
deep-copied host result array.

Ghosts, hidden cells and blanking are not applied as visibility controls; those
cells are processed normally. Iso Surface rejects oriented images; the general
importer ignores image direction, so use axis-aligned images or structured
points. Field/component/type limits are inherited from VTK import.

### Terminal Timing

**Enable Timing** prints synchronized phase times when NVTX is off:
`input_prepare` (or `source_prepare`, `points_prepare`, `seed_prepare`),
`execute`, `output`, and `total`, with
additional field-sampling phases where applicable. First execution may include
JIT and locator construction. Compare warm runs; short preparation indicates a
cache hit. Output timing includes host transfer and VTK rebuilding.

### NVTX Profiling

Launch a profiled process, then enable ranges in its **View > Python Shell**:

```sh
# Assumes the matching .venv-paraview above and NVIDIA Nsight Systems (nsys).
nsys profile --trace=cuda,nvtx,osrt paraview --venv "$(pwd)/.venv-paraview"
```

```python
import warp_simdata as simdata

simdata.config.enable_timing = True
simdata.config.enable_nvtx = True
```

NVTX emits plugin/operator ranges instead of terminal timing and omits its
phase-boundary synchronization. Set both values to `False` to disable global
profiling. There is no separate NVTX filter property.

## Operator Coverage

The tables cover direct filters and Mesh Analysis. `advection` is the streamline
engine; `centroid` and `bounds` remain Python operations. `node_splats` has no
filter because exporting points does not preserve its Gaussian interpolation.

## Tests

Run from the repository root with the configured environment and ParaView's
`pvpython`, so tests use ParaView's VTK:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  pvpython --venv "$(pwd)/.venv-paraview" \
  -m pytest -c extras/paraview/tests/pytest.ini extras/paraview/tests -v
```
