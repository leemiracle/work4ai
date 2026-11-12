<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Plane Slice Operator

Use `warp_simdata.operators.slice` to cut supported volume elements with a plane
on the input CPU/CUDA device. Plane distance is evaluated without storing a value
at every source node.

Dedicated guides like this one expand on the API reference for more complex
operators, explaining the algorithms and tradeoffs behind their behavior and
performance. See the [full operator list](PythonAPI.md#available-operators) for all
available operations.

```python
# Assumes dataset with "pressure" from PythonAPI.md.
from warp_simdata.operators import slice as plane_slice

surface = plane_slice.compute(
    dataset, origin=(0.5, 0.0, 0.0), normal=(1.0, 0.0, 0.0),
    field_names=["pressure"],
)
assert surface.get_num_elems() == 8
```

## Input contract

The dataset must satisfy the [contour topology contract](IsoSurface.md#supported-topology).
`origin` and `normal` have three finite components; the normal must be nonzero.
Normals are normalized internally, and the resulting plane offset must fit float32.
Optional `field_names` transfers floating-point node fields and element fields;
`element_idx` is reserved for provenance.

## Output contract

The output is a triangular `custom.surface_mesh` on the source device. Intersections
on shared source edges are merged. Points lie on the plane within float32 arithmetic.
Requested node fields are interpolated; element fields are copied from their parent
onto each triangle. `element_idx` records the original input's local element index,
including collection/subset index spaces. No private distance field is retained.

Empty inputs and non-intersecting planes return typed empty surfaces with requested
fields. The input field dictionary is unchanged; existing acceleration caches can
be reused. Selected cells follow contour validation and
[degeneracy rules](IsoSurface.md#degeneracy-and-diagnostics), including warnings
for skipped polyhedral intersections and potential holes.

## Multiple planes

`compute_many(dataset, origins, normals, field_names=None)` returns independent
surfaces in input order. Both arrays have shape `(N, 3)` and equal length; an empty
pair returns `[]`.

```python
# Assumes dataset and plane_slice from above.
surfaces = plane_slice.compute_many(
    dataset, origins=[(0.5, 0.0, 0.0), (1.5, 0.0, 0.0)],
    normals=[(1.0, 0.0, 0.0), (1.0, 0.0, 0.0)], field_names=["pressure"],
)
assert len(surfaces) == 2
```

## Implementation

The operator uses a candidate pass on the input device:

1. Evaluate signed plane distance at each element's nodes.
2. Select elements containing at least one value below zero and one value at or
   above zero. Retain invalid elements and elements with non-finite distances
   for diagnostics.
3. Scan and compact the selected parent element indices.
4. Create a zero-copy `element_subset` that shares parent coordinates,
   connectivity, and fields.
5. Run `iso_surface` at zero over the procedural plane-distance field on that subset.
6. Remap output provenance from subset-local indices to parent indices.
7. Gather requested element fields using the remapped parent indices.

Plane distance varies linearly, so vertex signs determine whether an element
crosses the plane. Zero belongs to the nonnegative side; touching the plane alone
does not guarantee output triangles. Subset construction does not copy point or
topology buffers.

### Prepared bounds

For repeated slices, prepare the shared conservative boxes explicitly:

```python
# Assumes dataset from the usage example above.
lower, upper = dataset.get_per_element_bounds()
assert lower.size == upper.size == dataset.get_num_elems()
```

The arrays retain 24 bytes per element. Treat them as read-only and recreate the
dataset after geometry changes; see [ownership and invalidation](DatasetsAndFields.md#ownership-and-caches).
Without prepared bounds, selection reads vertices directly.

Prepared boxes conservatively reject cells away from all planes in a batch.
Remaining cells still undergo vertex classification for every plane. Invalid,
empty, or non-finite cells have unbounded boxes so the box test does not hide
them from classification and diagnostics.

### Batched selection

Candidate classification is processed in groups of at most 32 planes. One
`wp.uint32` word per source element records which planes cross it. The operator
reads element topology and coordinates once per group without allocating a dense
`num_elements * num_planes` mask. Elements selected by each bit are stably compacted
into a zero-copy subset and passed through the same extraction, provenance, and
field-transfer pipeline. A single-plane `compute()` call uses this path with one request.

Input indices and scans must fit int32, as must the selected contour output.
