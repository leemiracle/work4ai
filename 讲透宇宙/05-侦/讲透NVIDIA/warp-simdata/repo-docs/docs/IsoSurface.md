<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Iso-Surface Operator

Use `warp_simdata.operators.iso_surface` to extract a merged triangular surface
from a node scalar field on [supported volume elements](#supported-topology).
The operation runs on the input CPU/CUDA device.

Dedicated guides like this one expand on the API reference for more complex
operators, explaining the algorithms and tradeoffs behind their behavior and
performance. See the [full operator list](PythonAPI.md#available-operators) for all
available operations.

```python
# Assumes dataset, wp, and simdata from PythonAPI.md.
from warp_simdata.operators import iso_surface

dataset.add_field("temperature", simdata.Field.from_array(
    wp.full(dataset.get_num_nodes(), 300.0, dtype=wp.float32, device=dataset.device),
    simdata.AssociationType.NODE,
))
surface = iso_surface.compute(dataset, "pressure", 0.5, field_names=["temperature"])
assert surface.has_field("temperature")

surfaces = iso_surface.compute_many(
    dataset, "pressure", [0.5, 1.0, 1.5], field_names=["temperature"],
)
assert len(surfaces) == 3  # Same order as the requested values.
```

## Input contract

`dataset` must expose the topology below. `field_name` selects a scalar,
`NODE`-associated `wp.float32` field with one value per node. Iso-values must be
finite and representable as float32.

Optional `field_names` selects additional floating-point node fields (scalar or
vector, float32/float64 components). Duplicate names are ignored. `element_idx`
is reserved for output provenance; element-associated fields cannot be transferred.
Convert them to nodes explicitly if that reconstruction is appropriate.

## Supported topology

| Cells | Required model capability |
| --- | --- |
| Linear tetrahedra, voxels, hexahedra, wedges, pyramids | `ElementShapeAPI` and canonical corners from `ElementTopologyAPI` |
| Polyhedra | `ElementShapeAPI` and outward-wound face loops from `ElementAPI` |

Collections, subsets, mixed supported cells, and implicit connectivity use this
same contract. Native IDs and node order remain model concerns. See
[model capabilities](DatasetsAndFields.md#data-model-capabilities) and
[shape conventions](ShapeFunctions.md). FLASH cell-centered fields can use the
[axisymmetric dual](PythonAPI.md#cell-centered-axisymmetric-dual).

Higher-order and lower-dimensional unstructured cells are unsupported and raise
`ValueError`; higher-order nodes are not silently discarded. Incorrect fixed-cell
corner counts, duplicate corners, and out-of-range node references also fail.

## Output contract

The result is a `custom.surface_mesh` on the source device:

- triangles share intersections on the same canonical source edge;
- the contour field is always present on nodes, filled with the float32 iso-value;
- requested node fields are linearly interpolated along source edges;
- element field `element_idx` maps each triangle to the input's local element index;
- normals and unrequested fields are absent.

Collection/subset provenance refers to that wrapper's index space, not native
IDs. Empty inputs and non-intersecting contours return typed empty surfaces with
requested fields. Degenerate image/structured extents also return empty surfaces.
`compute_many()` returns one independent surface per value; an empty sequence
returns `[]`.

## Implementation

Data models own native element-type classification, canonical corner ordering,
and outward face winding. Contour case tables, source-edge keys, point merging,
and polyhedron triangulation remain private to the operator. Warp specializes
these model interfaces for CPU and CUDA without converting the input to a common
host-side mesh.

### Fixed cells

The fixed-cell path uses one table family per supported linear shape:

1. Classify every corner as high when `value >= iso_value` and encode the case bits.
2. Read source-edge triples from the case tables and count triangles with three
   distinct intersection keys.
3. Exclusive-scan per-element counts to allocate exact triangle output.
4. Emit canonical 64-bit source-edge keys and source-element provenance.
5. Radix-sort the keys, identify unique keys, then scatter merged points and
   triangle connectivity.
6. Interpolate additional fields from the two source nodes recorded for each
   merged point.

Keys use dataset-local node indices. Intersections exactly on a source vertex
use `(node, node)` as their key so incident cells share that vertex.

### Polyhedra

Polyhedra use a separate private path and then join the common source-edge merge:

1. Traverse each outward-wound face and pair every low-to-high crossing with
   the next high-to-low crossing in face order.
2. Express those directed contour segments as canonical source-edge keys.
3. Require exactly one incoming and one outgoing segment at every active key,
   then trace every closed cycle in the element.
4. Project each cycle to 2D along the dominant axis of its Newell normal.
   Reject degenerate or self-intersecting projections.
5. Ear-clip each remaining simple convex or non-convex loop, pruning collinear
   points only when they lie between their neighbors. The lowest canonical key
   breaks ear-selection ties for deterministic output.
6. Feed the emitted edge keys and triangle provenance into the same merge path
   used by fixed cells.

The algorithm does not tetrahedralize through an element or face center and
therefore introduces no synthetic scalar samples.

### Batched extraction

The first value in `compute_many()` uses the complete single-surface path so
unsupported or malformed topology cannot be hidden by candidate selection.
Remaining values share a candidate pass in groups of at most 32:

1. Read each element's topology and scalar node values once per group.
2. Store crossing decisions as one `wp.uint32` bitmask per element.
3. Extract one bit at a time and stably compact parent element indices.
4. Run the existing extractor on a zero-copy `element_subset`.
5. Remap triangle provenance to the original dataset.

This bounds selection storage independently of the number of requested values,
preserves subset order, and avoids a dense `num_elements * num_values` mask.

## Degeneracy and diagnostics

Samples equal to the iso-value are on the high side. Intersections at a source
vertex merge by node ID, and triangles with repeated intersection keys are removed.
Exact-valued plateaus can still produce coincident, oppositely wound triangles;
there is no global triangle deduplication.

Cells with non-finite scalar samples are skipped with an aggregate `RuntimeWarning`.
Invalid polyhedral contour graphs or projected loops that cannot be triangulated
are also skipped with an aggregate warning; partial output can contain holes.
Polyhedron loops must have valid outward winding. The operator does not validate
or repair the complete shell, so incorrect winding has undefined output.

Classic cube case tables resolve ambiguous cases; another contour algorithm can
produce different topology. Polyhedral contouring follows face-edge intersections,
without synthetic center samples. Non-planar, self-intersecting, or very small
loops remain numerical limits; see [Shape Functions](ShapeFunctions.md).

Indices, scans, and provenance use int32. Checked limits include `INT32_MAX / 5`
input elements and `INT32_MAX / 3` polyhedral segments or output triangles.
Split inputs before these limits; bounds checks do not remove the indexing ceiling.

Use the [ParaView guide](../extras/paraview/README.md) for the filter integration,
and [Python performance guidance](PythonAPI.md#performance) for preparation and timing.
