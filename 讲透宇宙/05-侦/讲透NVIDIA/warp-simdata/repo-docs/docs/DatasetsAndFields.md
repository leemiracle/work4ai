<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Datasets and Fields

A `Dataset` combines a data model, its handle, a device, and named fields.
Models expose geometry and topology through shared APIs without requiring
conversion to a common mesh. Point location and interpolation support vary by
model. Fields associate values with nodes (`NODE`) or elements (`ELEMENT`),
or leave the association unspecified (`NOT_SPECIFIED`). See
[Python API](PythonAPI.md) for workflows and [Kernel API](KernelAPI.md) for
extension.

## Construction and devices

Use a model's `create_dataset()` factory to construct its handle and retain
required resources. Array-based models normally use their arrays' device;
implicit grids accept one explicitly. This uniform-grid example needs only
the core package. Later examples reuse its `dataset` and `pressure`.

```python
import warp as wp
import warp_simdata as simdata
from warp_simdata.data_models.vtk import image_data

# Node extents are inclusive: 27 nodes, eight elements.
dataset = image_data.create_dataset(
    origin=wp.vec3f(0.0), spacing=wp.vec3f(1.0),
    extent_min=wp.vec3i(0), extent_max=wp.vec3i(2), device="cpu",
)
pressure = simdata.Field.from_array(
    wp.full(27, 1.0, dtype=wp.float32, device=dataset.device),
    simdata.AssociationType.NODE,
)
dataset.add_field("pressure", pressure)
assert dataset.get_num_nodes() == 27
assert dataset.get_num_elems() == 8
```

Construct NumPy-backed inputs with `wp.array(..., dtype=..., device=...)`.
Coordinates, connectivity, fields, and secondary inputs must share a device.
Supplying `Dataset(device=...)` does not move backing arrays. Use canonical
aliases such as `"cpu"`, `"cuda:0"`, or `wp.get_device(device).alias`: a supplied
`"cuda"` label can fail comparison with fields reporting `"cuda:0"`.

## Data model capabilities

Operator support depends on the model, element types, and fields. This table
summarizes model capabilities. Contours/slices require `ElementShapeAPI`;
fixed cells also need canonical `ElementTopologyAPI`. Located sampling covers
probe sources and voxelization. Face extraction uses actual `ElementAPI` face
traversal. Method presence alone is insufficient: some are stubs.

| Model under `warp_simdata.data_models` | Contour/slice topology | Located sampling | Face extraction |
| --- | --- | --- | --- |
| `vtk.image_data`, `vtk.structured_grid` | Linear volumes | Yes | Yes |
| `vtk.unstructured_grid` | Supported volumes¹ | Yes¹ | Yes¹ |
| `sids.unstructured`, `sids.nface_n` | Supported volumes¹ | Yes¹ | Yes¹ |
| `ensight_gold.unstructured_part` | Supported volumes¹ | Yes¹ | Yes¹ |
| `openfoam.polymesh` | Polyhedra | Yes¹ | Yes |
| `flash.axisymmetric` (primal) | No | Yes | Yes |
| `flash.axisymmetric_dual` | Linear wedges/hexes | No | Yes |
| `reservoir.corner_point_grid` | No | Yes² | Yes² |
| `vtk.polydata`, `custom.surface_mesh`, `openfoam.boundary_mesh` | No | No | Existing polygons |
| `custom.point_cloud`, `custom.curves` | No | No | No |
| `custom.gaussian_point_cloud` | No | Gaussian blending | No |
| `custom.voronoi_point_cloud` | No | Nearest seed | No |

¹ [Contour topology](IsoSurface.md#supported-topology) and
[shape interpolation limits](ShapeFunctions.md) apply per cell. Lower-dimensional
and higher-order cells cannot be contoured. Polyhedral sampling has geometric
limits. Surface-only inputs can still supply sample positions or seeds.

² Reservoir fields use `NX * NY * NZ` logical element slots, including inactive
cells; packed active-cell fields must be expanded. ACTNUM-masked cells are skipped.
Float32 coordinates and degenerate/non-convex hexes limit location accuracy.
Corners are element-local, so coincident faces across cells are not shared topology.

Streamlines and advection also require valid element indices and nonzero element
sizes. Gaussian and Voronoi point clouds cannot serve as their source datasets.

Collections and element subsets wrap a base model; they do not add missing
capabilities. See the [operator table](PythonAPI.md#available-operators) for field
association/type requirements and [USD](USDAPI.md) for format-to-model mappings.

## Field access and storage

`add_field()` checks devices and warns on name replacement. Callers must match
association and logical size: one value per node for `NODE`, or per element for
`ELEMENT`. `NOT_SPECIFIED` fields need not match either count.

```python
assert dataset.has_field("pressure")
print(dataset.get_field_names())
field = dataset.get_field("pressure")
print(field.size, field.dtype, field.association, field.device)
minimum, maximum = field.get_range()
values = field.to_array().numpy()
assert dataset.get_field("missing") is None
```

| Constructor | Storage |
| --- | --- |
| `Field.from_array(array, association)` | Scalar/vector Warp array (AoS) |
| `Field.from_arrays([x, y, z], association)` | Scalar components (SoA); same dtype, length, device |
| `Field.from_volume(volume, dims, association, origin=wp.vec3i(0))` | NanoVDB; explicit logical dimensions and integer origin, first index fastest |
| `Field.from_fields(fields)` | Concatenated pieces with matching field model, dtype, association, and device |

`get_data()` exposes storage, which may include backing objects. `to_array()`
returns logical AoS values: the original array for AoS, a materialized array for
other layouts/views. `.numpy()` reads host values and can transfer or synchronize.
`get_range()` caches `(min, max)`; vectors use magnitude unless `component` is set.

## Read-only views

```python
velocity = simdata.Field.from_arrays([
    wp.full(pressure.size, 1.0, dtype=wp.float32, device=dataset.device),
    wp.zeros(pressure.size, dtype=wp.float32, device=dataset.device),
    wp.zeros(pressure.size, dtype=wp.float32, device=dataset.device),
], simdata.AssociationType.NODE)
vx = simdata.Field.from_field(velocity, component=0)
speed = simdata.Field.from_field(velocity, magnitude=True)

window = pressure.subrange(start=2, count=4)
sampled = pressure.subset([10, 3, 10])  # Preserves order and duplicates.
logical = pressure.indexed_lookup([0, -1, 1])  # Negative entries read as zero.
assert sampled.size == 3
assert logical.to_array().numpy().tolist() == [1.0, 0.0, 1.0]

writable = simdata.Field.from_array(window.to_array(), window.association)
```

Views retain their sources. Their kernel `FieldAPI.set()` silently does nothing.
The last line materializes independent, writable storage. `select(start=..., count=...)`
and `select(indices=...)` provide the same window/index variants.
A shortened view can only attach where its logical association/index space matches.

## Collections

```python
pieces = [dataset, dataset.shallow_copy()]
collection = simdata.DatasetCollection.from_datasets(pieces)
assert collection.get_num_elems() == 2 * dataset.get_num_elems()
```

`pieces` must be a nonempty list with matching models and devices.
Indices concatenate piece index spaces; coincident nodes are not welded.
Only names on piece 0 are considered for collection fields, and each
must be present with compatible model, dtype, and association in every piece.
Missing/incompatible fields are excluded from the collection, not removed from pieces.
Process pieces with unlike models separately, or convert them to a shared model
before collecting them.
`warp_simdata.data_models.vtk.conversion.to_common_vtk_data_model()` is one option
for supported inputs; see [VTK conversion](VTK.md) for costs.

## Element selection

```python
# Assumes dataset and pressure from the construction example above.
from warp_simdata.data_models.custom import element_subset
from warp_simdata.operators import element_in_box

indices = element_in_box.compute_indices(
    dataset, box_min=(0.0, 0.0, 0.0), box_max=(1.0, 1.0, 1.0), mode="all",
)
selected = element_subset.create_dataset(dataset, indices)
selected.add_field("pressure", pressure)  # All parent nodes remain addressable.
assert selected.get_num_elems() == 1
```

A subset retains its parent, shares nodes/topology, and starts with no fields.
Share node fields and select element fields with `field.subset(indices)`.
Element indices are subset-local; `indices` maps to parent indices.
Box selection uses `all`, `any`, or vertex-average `centroid` predicates,
not general geometric intersection. You can also supply your own `wp.int32` indices.

## Ownership and caches

`shallow_copy()` shares the handle, existing fields, cached geometry, and locators,
with its own field dictionary. `pass_fields=False` starts that dictionary empty.
Replacing/removing a name affects one copy; mutating shared storage can affect both.

`get_bounds()`, `get_cached_field("element_centers")`, and
`get_cached_field("element_sizes")` compute and cache geometry on first use.
Locators are also built lazily.

`get_per_element_bounds()` retains two `vec3f` arrays (24 bytes per element), shared
by copies; slice reuses them when present. Empty/invalid/non-finite cells receive
unbounded boxes to remain conservative candidates. Treat cached arrays as read-only.
`get_element_bounds()` returns a single bounding box for the elements.

Backing mutations do not invalidate geometry caches, locators, or field ranges.
Keep inputs stable while caches are used; construct fresh handles/datasets and
fields after changes. Probe keeps no point-location cache between `compute_many()`
calls. Positions and values can change between queries while source geometry stays stable.
