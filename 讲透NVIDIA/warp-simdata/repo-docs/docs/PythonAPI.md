<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Python API

Use this guide to compose operators in Python. Start with the
[quick start](../README.md#quick-start); see [Datasets and Fields](DatasetsAndFields.md)
for construction, devices, ownership, and capabilities. The
[pipeline example](examples/basic_pipeline.py) shows a broader workflow.

## Available operators

Import modules from `warp_simdata.operators` and call their `compute()` functions.
Inputs must satisfy both the model capability and field requirements below.
Exact parameters and defaults live in the linked source docstrings.

| Operator | Needs | Result and main limit |
| --- | --- | --- |
| [bounds](../warp_simdata/operators/bounds.py) | Node coordinates | Dataset copy with unassociated `bounds_min`, `bounds_max` |
| [element_bounds](../warp_simdata/operators/element_bounds.py) | Element nodes | Copy with `element_bounds_min`, `element_bounds_max` |
| [centroid](../warp_simdata/operators/centroid.py) | Element nodes | Copy with `element_centers`; averages vertices, not volume |
| [element_center](../warp_simdata/operators/element_center.py) | Element faces and nodes | Experimental centers; bounded face/iteration support |
| [element_sizes](../warp_simdata/operators/element_sizes.py) | Element nodes | Copy with `element_sizes`; bounding-box diagonals |
| [element_node_counts](../warp_simdata/operators/element_node_counts.py) | Element nodes | Copy with `element_node_counts` |
| [node_element_counts](../warp_simdata/operators/node_element_counts.py) | Node-to-element links | Copy with `node_element_counts` |
| [element_field](../warp_simdata/operators/element_field.py) | Named node/element field and element nodes | Copy with `element_field`; arithmetic averaging |
| [node_field](../warp_simdata/operators/node_field.py) | Named element/node field and element nodes | Copy with `node_field`; averages incident elements |
| [element_in_box](../warp_simdata/operators/element_in_box.py) | Element nodes | Copy with `element_in_box`, or indices via `compute_indices()`; vertex predicates |
| [element_faces](ElementFaces.md) | Faces exposed by `ElementAPI` | Polygon surface; all faces by default, boundary with `external_only=True` |
| [iso_surface](IsoSurface.md) | Supported volume topology; scalar `NODE` float32 field | Merged triangular surface; `compute_many()` returns a list |
| [slice](Slice.md) | Supported volume topology | Merged triangular plane cut; node/element field transfer |
| [probe](../warp_simdata/operators/probe.py) | Source location/interpolation; target node coordinates | Copy of target with `NODE` samples; misses read zero |
| [voxelization](../warp_simdata/operators/voxelization.py) | Source location/interpolation and a named field | Image dataset with `Volume`; array or NanoVDB storage |
| [node_splats](../warp_simdata/operators/node_splats.py) | Node coordinates | Point/Gaussian cloud; attach fields explicitly |
| [advection](../warp_simdata/operators/advection.py) | Located vector field, valid element indices and nonzero element sizes; seed nodes | `(forward, backward)` trajectory buffers; unrequested direction is `None` |
| [streamlines](../warp_simdata/operators/streamlines.py) | Same as advection | Curves, or `None` when no curves survive |

Generated property names are configurable except the provenance names on surfaces
(`element_idx`, and `node_idx` for faces) and the streamline fields (`times`,
`element_idx`). Field conversions retain an already matching association without
averaging. Averaging has no conservation guarantee or special AMR reconstruction.

## Using operators

This complete example creates eight hexahedra with pressure equal to x, converts
the field to element values, and extracts a contour. It needs only the core package.
Later operator examples reuse its `dataset`, `result`, `device`, and imports.

```python
import numpy as np
import warp as wp
import warp_simdata as simdata
from warp_simdata.data_models.vtk import image_data
from warp_simdata.operators import centroid, element_field, iso_surface

device = "cuda:0" if wp.is_cuda_available() else "cpu"
dataset = image_data.create_dataset(
    origin=wp.vec3f(0.0), spacing=wp.vec3f(1.0),
    extent_min=wp.vec3i(0), extent_max=wp.vec3i(2), device=device,
)
pressure = simdata.Field.from_array(
    wp.array(np.tile(np.arange(3, dtype=np.float32), 9), device=device),
    simdata.AssociationType.NODE,
)
dataset.add_field("pressure", pressure)
result = element_field.compute(dataset, "pressure", output_field_name="cell_pressure")
result = centroid.compute(result)
surface = iso_surface.compute(result, "pressure", 0.5)
assert result.get_field("cell_pressure").size == 8
assert surface.get_num_elems() == 8
assert not dataset.has_field("cell_pressure")
```

Operators that add fields usually return a shallow copy with a separate field
dictionary. Geometry, existing fields, and caches remain shared; this is not
deep immutability. Operators can build caches on the input. Geometry-producing
operators create their own output. See [ownership](DatasetsAndFields.md#ownership-and-caches).

Field inputs are names; check them before calling an operator when inputs vary:

```python
if not dataset.has_field("pressure"):
    raise KeyError(f"pressure is missing; available fields: {dataset.get_field_names()}")
```

### Geometry properties

```python
from warp_simdata.operators import bounds, element_sizes

properties = bounds.compute(dataset, min_field_name="lower", max_field_name="upper")
print(properties.get_field("lower").to_array().numpy()[0])  # [0. 0. 0.]
properties = element_sizes.compute(properties, field_name="sizes")
properties = centroid.compute(properties, field_name="centers")
assert properties.get_field("centers").size == dataset.get_num_elems()
```

Sizes are bounding-box diagonals; centers are vertex averages. For surface
geometry, see the examples for [faces](ElementFaces.md),
[contours](IsoSurface.md), and [slices](Slice.md).

### Probing fields

```python
# Assumes dataset and imports from the example above.
from warp_simdata.data_models.custom import point_cloud
from warp_simdata.operators import probe

positions = point_cloud.create_dataset(wp.array(
    [[0.5, 0.5, 0.5], [3.0, 3.0, 3.0]], dtype=wp.vec3f, device=dataset.device,
))
sampled = probe.compute(dataset, "pressure", positions, output_mask_field_name="valid")
assert sampled.get_field("probed_values").to_array().numpy().tolist() == [0.5, 0.0]
assert sampled.get_field("valid").to_array().numpy().tolist() == [1, 0]
```

Sample several fields in one call:

```python
# result above contains pressure (NODE) and cell_pressure (ELEMENT).
sampled_many = probe.compute_many(
    result, ["pressure", "cell_pressure"], positions, output_mask_field_name="valid",
)
assert sampled_many.has_field("pressure")
assert sampled_many.has_field("cell_pressure")
```

Batch output names default to input names; `output_field_names` can rename them.
With explicit locators, the batch reuses locations across fields; implicit
locators such as image grids repeat lookup per field.
Samples and the optional shared `uint32` mask are node-associated. Mask 1 means
a location was found; 0 means a miss. Use it to distinguish misses from real zeros.
Existing target fields remain; source fields are sampled only when requested.

Plain `point_cloud` and `surface_mesh` are useful targets or seeds but their
locators always miss, so they cannot supply located source samples. Other
point-cloud models have different [capabilities](DatasetsAndFields.md#data-model-capabilities).

### Voxelization

```python
# Assumes dataset and imports from the example above.
from warp_simdata.operators import voxelization

volume = voxelization.compute(
    dataset, "pressure", min_ijk=wp.vec3i(0), max_ijk=wp.vec3i(1),
    voxel_size=wp.vec3f(1.0), use_nanovdb=False, output_mask_field_name="valid",
)
assert volume.get_field("Volume").size == 8
```

IJK limits are inclusive. Default element samples lie at
`voxel_size * (ijk + 0.5)`; `output_association="node"` samples at
`voxel_size * ijk`. The first index varies fastest. Misses receive `bg_value`.
The validity mask is 0/1: `uint32` with arrays, float32 with NanoVDB. NanoVDB is
the default storage path and supports fewer value types; integer values can
convert to floating point. Choose arrays explicitly to retain dtype.

### Streamlines and advection

```python
# Assumes dataset, positions, and imports from the examples above.
from warp_simdata.operators import streamlines

dataset.add_field("velocity", simdata.Field.from_array(
    wp.array(np.tile([1.0, 0.0, 0.0], (dataset.get_num_nodes(), 1)),
             dtype=wp.vec3f, device=dataset.device),
    simdata.AssociationType.NODE,
))
curves = streamlines.compute(dataset, "velocity", positions, direction="forward", max_steps=20)
assert curves is not None
assert curves.get_num_elems() == 1  # The outside seed produces no curve.
times = curves.get_field("times").to_array()
source_elements = curves.get_field("element_idx").to_array()
```

Both interfaces use adaptive RK4(5), normalized velocity, and step sizes scaled
by element size. `direction` accepts `"forward"`, `"backward"`, or `"both"`.
`streamlines.compute()` packs trajectories into curves. `times` contains the
accumulated propagation parameter; it is neither physical elapsed time nor
guaranteed arc length. This traces a supplied vector field, not time-varying paths.

For trajectory buffers with explicit step limits:

```python
from warp_simdata.operators import advection

forward, backward = advection.compute(
    dataset, "velocity", positions, initial_dt=0.2, min_dt=0.01,
    max_dt=0.5, max_steps=20, direction="forward",
)
assert backward is None
length = int(forward.lengths.numpy()[0])
first_path = forward.positions.numpy()[0, :length]
first_times = forward.times.numpy()[0, :length]
```

Each buffer also has `elem_idx`. Only each seed's prefix indicated by `lengths`
is valid. For custom termination, see `tc_model` and `tc_handle` in the
[advection docstring](../warp_simdata/operators/advection.py).

## Loading data

Load files with a format reader, then construct the appropriate Warp model.
The core package performs in-memory processing.

### Using OpenUSD

After [registering the plugins](USDAPI.md#initialization), open a scientific
asset and select its dataset prim:

```python
from pxr import Usd
import warp_simdata.usd as simusd

stage = Usd.Stage.Open("case.usd")  # Replace with your asset and prim path.
prim = stage.GetPrimAtPath("/World/Zone")
time_code = Usd.TimeCode.EarliestTime()
usd_dataset = simusd.dataset_from_prim(prim, device=device, time_code=time_code)
```

Load and attach fields separately. [OpenUSD integration](USDAPI.md) covers
discovery, native formats, and matching geometry and fields by time/representation.

### Using VTK

With the [VTK extra](VTK.md#loading-from-vtk) installed:

```python
from vtkmodules.vtkIOLegacy import vtkDataSetReader
from warp_simdata.vtk import vtk_to_dataset

reader = vtkDataSetReader()
reader.SetFileName("dataset.vtk")  # Replace with your legacy VTK file.
reader.ReadAllScalarsOn()
reader.ReadAllVectorsOn()
reader.Update()
vtk_dataset = vtk_to_dataset(reader.GetOutput(), device=device)["dataset"]
```

[VTK interoperability](VTK.md) covers composite mappings, export, copies, and
fidelity limits. File-reader support does not imply model support.

### Reservoir corner-point grids

Construct native COORD/ZCORN storage directly from a reader's flat arrays:

```python
# Assumes nx, ny, nz and arrays coord_values, zcorn_values, actnum_values, porosity.
from warp_simdata.data_models.reservoir import corner_point_grid

reservoir = corner_point_grid.create_dataset(
    wp.vec3i(nx, ny, nz),
    coord=wp.array(coord_values, dtype=wp.float32, device=device),  # 6*(nx+1)*(ny+1)
    zcorn=wp.array(zcorn_values, dtype=wp.float32, device=device),  # 8*nx*ny*nz
    actnum=wp.array(actnum_values, dtype=wp.int32, device=device),  # nx*ny*nz
    depth_direction="zDown",
)
reservoir.add_field("porosity", simdata.Field.from_array(
    wp.array(porosity, dtype=wp.float32, device=device), simdata.AssociationType.ELEMENT,
))
```

Fields need `nx * ny * nz` logical values, including inactive slots; expand
active-cell-packed arrays first. ACTNUM is optional. See the
[model source](../warp_simdata/data_models/reservoir/corner_point_grid.py)
for coordinate transforms and location limits.

### Axisymmetric FLASH AMR

This core-only example revolves one two-cell block into 16 elements:

```python
from warp_simdata.data_models.flash import axisymmetric, axisymmetric_dual

flash_inputs = dict(
    block_bounds=wp.array([[0.0, 1.0, -1.0, 1.0]], dtype=wp.vec4f, device=device),
    gid=wp.array([[-2] * 9], dtype=wp.int32, device=device),
    node_types=wp.array([1], dtype=wp.int32, device=device),
    leaf_block_indices=wp.array([0], dtype=wp.int32, device=device),
    cell_dims=wp.vec2i(2, 1), angular_cells=8,
)
primal = axisymmetric.create_dataset(**flash_inputs)
source_density = simdata.Field.from_array(
    wp.array([1.0, 3.0], dtype=wp.float32, device=device), simdata.AssociationType.ELEMENT,
)
primal.add_field("density", axisymmetric.create_element_field(primal, source_density))
assert primal.get_num_elems() == 16
```

The source field uses block-major order, including non-leaf blocks, with radius
varying fastest inside each block. The field view repeats values over angular
sectors without allocating expanded storage. The primal supports located sampling.

### Cell-Centered Axisymmetric Dual

For contouring, expose the same cell-centered values on implicit dual nodes:

```python
dual = axisymmetric_dual.create_dataset(**flash_inputs)
dual.add_field("density", axisymmetric_dual.create_node_field(dual, source_density))
density_surface = iso_surface.compute(dual, "density", 2.0)
assert density_surface.get_num_elems() > 0
```

The dual supports contours and slices but not point location. When loading
through OpenUSD, use the same representation and time for geometry and fields;
see the [USD recipe](USDAPI.md#cell-centered-dual).

## Configuration

Warp initializes lazily; an explicit `wp.init()` is optional. Importing SimData
sets process-wide Warp options `enable_vector_component_overwrites=True` and
`enable_backward=False`, and installs a pre-compilation hook. Account for this
when embedding it in an application with its own Warp configuration.

```python
wp.init()  # Optional eager initialization.
wp.config.log_level = wp.LOG_WARNING  # Optional quieter Warp logging.
simdata.config.validate_datasets = True  # Default; False skips construction checks.
```

Construction checks catch malformed index arrays, not all geometric defects.
Disable them only for already validated inputs; their readbacks can synchronize
the device.

Configuration and environment variables live in [core/config.py](../warp_simdata/core/config.py).
Environment defaults are read at import. Set locator options before building
locators; changing them does not rebuild existing locators.
BVH defaults select cuBQL on CUDA and Warp's CPU default; changing the constructor
or leaf size trades preparation cost, memory, and query performance.

## Performance

Keep geometry and fields on the device and reuse the source dataset for repeated
queries. Locator construction, lazy geometry caches, and specialization/compilation
can make the first call slower. Warp's kernel cache can avoid recompilation on
later runs. Cached geometry and field ranges require stable backing data.
Prepare per-element bounds only when repeated slices justify their retained
storage; see [caches](DatasetsAndFields.md#ownership-and-caches).

[Recording and AOT](KernelAPI.md) support known deployment specializations.
Recorded masked probe/voxelization specializations cannot be replayed by
the AOT compiler; their ordinary JIT calls work.

For printed, synchronized timings:

```python
simdata.config.enable_timing = True
with simdata.scoped_timer("geometry"):
    timed_result = centroid.compute(dataset)
simdata.config.enable_timing = False  # Restore the default.
```

For NVTX ranges, first install `nvtx` (`python -m pip install nvtx`):

```python
simdata.config.enable_timing = True
simdata.config.enable_nvtx = True
profiled_result = centroid.compute(dataset)
simdata.config.enable_nvtx = False
simdata.config.enable_timing = False
```

NVTX avoids timer-boundary synchronization by default. When timing a CUDA
operation yourself, synchronize before and after it.

See [Available operators](#available-operators) for supported operations,
required inputs, and results.
