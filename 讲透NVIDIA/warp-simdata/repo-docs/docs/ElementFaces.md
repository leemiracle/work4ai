<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Element Faces Operator

Use `warp_simdata.operators.element_faces` to extract element-local faces or
only topological boundary faces on the input CPU/CUDA device.

Dedicated guides like this one expand on the API reference for more complex
operators, explaining the algorithms and tradeoffs behind their behavior and
performance. See the [full operator list](PythonAPI.md#available-operators) for all
available operations.

```python
# Assumes dataset from the image-grid example in PythonAPI.md.
from warp_simdata.operators import element_faces

all_faces = element_faces.compute(dataset)
boundary = element_faces.compute(dataset, external_only=True)
assert all_faces.get_num_elems() == 48
assert boundary.get_num_elems() == 24
```

## Input contract

Elements must expose faces through `ElementAPI.get_num_faces`, `get_face`,
`get_face_num_nodes`, and `get_face_node_id`. Node IDs must resolve to dataset
node indices. Face loops must contain distinct nodes. Polygons can expose themselves
as one face; clouds and curves do not supply volume faces.

Shared faces require shared node identity. Geometrically coincident faces with
different node indices remain distinct, including boundaries between separately
indexed collection pieces. The operator does not weld nodes or use a coordinate
tolerance. Reservoir corners are element-local, so coincident cell faces do not
cancel as shared boundaries.

## Output contract

The result is a `custom.surface_mesh` on the input device:

- each selected source face becomes one polygon with its original loop order/winding;
- nodes are compacted to those referenced by output faces;
- element-associated `element_idx` maps faces to local input element indices;
- node-associated `node_idx` maps compact nodes to local input node indices;
- other input fields are not copied or interpolated.

The default emits all faces: a face shared by two elements appears twice.
`external_only=True` emits faces with exactly one topological occurrence.
Empty inputs, inputs with no faces, and boundary requests with no external faces
raise `ValueError` rather than return an empty mesh.

## Topological classification

Face keys hash the node count and node indices independently of loop order.
Candidates with matching keys are compared against source topology exactly;
hash collisions do not equate unrelated faces.

| Exact occurrences | Classification | Boundary output |
| --- | --- | --- |
| One | External | Included |
| Two on different elements | Internal | Excluded |
| Other duplicate patterns | Non-manifold | Excluded |

Repeated faces within one element and faces shared by more than two elements
are excluded. The operator does not repair them or return separate non-manifold
diagnostics. Outward output winding depends on the source model's face convention.

## Shared extraction pipeline

Both device paths use the same output pipeline:

1. Count the faces exposed by every source element.
2. Exclusive-scan those counts to assign global candidate-face indices.
3. For `external_only=True`, classify candidates and scan selected counts to
   allocate output face storage. Otherwise, keep all candidates.
4. Count vertices for selected faces and scan those counts to allocate exact
   polygon connectivity.
5. Emit source node indices in original face-loop order.
6. Mark referenced nodes, scan the usage mask, and compact output coordinates.
7. Remap face connectivity and attach `element_idx` and `node_idx` provenance.

Boundary classification precedes output connectivity allocation, so omitted
faces do not consume polygon connectivity.

## CPU implementation

The CPU path uses radix sorting:

1. Generate one `wp.int64` face hash and global face ID per candidate.
2. Sort the hash/ID pairs with `warp.utils.radix_sort_pairs`.
3. Inspect equal-hash runs and exact-compare their source faces.
4. Store one `wp.int32` classification flag per candidate.

The sort uses the second half of both key and value arrays as alternate storage.
Together with element indices, local-face indices, and classification flags,
these arrays occupy approximately 36 bytes per candidate occurrence before output
and additional sort workspace. This path is also the CUDA fallback when
occurrence-table construction fails.

## CUDA implementation

CUDA normally uses an open-addressed occurrence table. Each occupied slot stores
an `int64` owner descriptor packing the source element index and local face index,
and an `int32` occurrence count.

Each candidate hashes to an initial slot. A 64-bit atomic compare-and-swap claims
an empty slot. Occupied slots are compared exactly against their owner face;
a match atomically increments the count, while a collision continues linear probing.

The first allocation uses roughly 0.8 slots per candidate occurrence, targeting
conforming volume meshes where most unique faces occur twice. Insertions exceeding
128 probes trigger a retry at 1.5 slots per occurrence, then radix fallback if
necessary. Failed table construction does not return incomplete topology.

The classifier records each candidate's table slot in `face_slots`. A query pass
uses those slots to write a `uint8` boundary mask and per-element external counts.
After those counts are scanned, the table is released; connectivity passes use
the compact mask without probing the table again.

Initial classification storage is about 14.6 bytes per candidate occurrence,
including `face_slots` and the boundary mask. Per-element counts/offsets, node
compaction, and output add storage; retry/fallback paths cost more. This is not
an overall peak-memory guarantee. Mostly disconnected topology can trigger retries.

## Limitations and diagnostics

Counts, connectivity, scans, and provenance use int32. Overflow checks reject
excessive face or connectivity totals; reduce the input with an element subset
or request boundary faces when appropriate. Allocation limits can be reached sooner.
Topology-based boundaries can differ from another application's surface policy;
validate results on representative inputs.

On Blackwell GPUs, forcing `wp.config.cuda_output="ptx"` with
`wp.config.ptx_target_arch=90` can cause an illegal memory access for mixed face
sizes. Use native device compilation instead of that PTX configuration.
