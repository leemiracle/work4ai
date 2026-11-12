<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Shape Functions

Use this reference to implement element interpolation, containment, or a new shape.
`warp_simdata.shape_functions` defines canonical corners, interpolation weights,
and containment. Models that use these shapes map their native types and ordering
to these interfaces.

## Supported shapes

| Shape/module | Corners | Parametric domain |
| --- | ---: | --- |
| Hexahedron / `hexa_8` | 8 | r, s, t in [0, 1] |
| Axis-aligned voxel / `voxel_8` | 8 | r, s, t in [0, 1] |
| Tetrahedron / `tetra_4` | 4 | r, s, t >= 0; r+s+t <= 1 |
| Pyramid / `pyra_5` | 5 | r, s, t in [0, 1]; apex at t=1 |
| Wedge / `penta_6` | 6 | r, s >= 0; r+s <= 1; t in [0, 1] |
| Star-convex polyhedron / `star_convex_polyhedron` | Variable | World-space face/center geometry |

Module suffixes count nodes, not polynomial degree. Fixed-shape interpolation
uses corner nodes; higher-order nodes receive zero weight. Models may recognize
more source types than an operator accepts: `iso_surface` rejects higher-order
cells rather than linearizing them.

## Canonical node ordering

Fixed shapes use VTK canonical ordering:

| Shape | Corner diagram |
| --- | --- |
| Hexahedron | ![Hexahedron corner ordering](images/hexa_8.png) |
| Voxel | ![Voxel corner ordering](images/voxel_8.png) |
| Tetrahedron | ![Tetrahedron corner ordering](images/tetra_4.png) |
| Pyramid | ![Pyramid corner ordering](images/pyra_5.png) |
| Wedge | ![Wedge corner ordering](images/penta_6.png) |

Wedge corners 0–2 are (0,0,0), (1,0,0), (0,1,0); corners 3–5 repeat that
triangle at t=1. Linear CGNS `PENTA_6` and EnSight `penta6` share this order.

`UniformShapesLibraryAPI.get_vtk_corner_node_index(cell_type, native_idx)` maps
native to canonical corner order; `get_source_corner_node_index(cell_type,
canonical_idx)` is the inverse. Operators use
`ElementTopologyAPI.get_corner_node_id` to hide that mapping. Volume face loops
must wind outward by the right-hand rule. Corner order and face winding are
separate requirements; see [Kernel API](KernelAPI.md#optional-shape-and-topology-capabilities).

## Interpolation

Each fixed-shape module exposes device-callable functions:

| Function | Result |
| --- | --- |
| `compute_shape_functions(pcoords)` | One float32 weight per canonical corner |
| `compute_shape_derivatives(pcoords)` | N-by-3 float32 matrix of dNi/dr, dNi/ds, dNi/dt; see [numerical limits](#numerical-limits) |
| `weight_at(pcoords, canonical_idx)` | One corner weight |
| `is_inside(pcoords, tolerance=1.0e-6)` | Parametric-domain membership |

At a hexahedron's parametric center, all eight weights equal 1/8:

```python
import warp as wp
from warp_simdata.shape_functions import hexa_8

@wp.kernel
def center_weights(output: wp.array(dtype=wp.float32)):
    weights = hexa_8.compute_shape_functions(wp.vec3f(0.5))
    for i in range(8):
        output[i] = weights[i]

output = wp.empty(8, dtype=wp.float32, device="cpu")
wp.launch(center_weights, dim=1, outputs=[output], device="cpu")
assert output.numpy().tolist() == [0.125] * 8
```

[kernel_operator.py](examples/kernel_operator.py) combines this check with a
model-independent operator.

### Position evaluation and weight cursors

Position solvers are generated for a concrete model. A module's
`get_shape(data_model, shapes_library, WeightsCursor)` factory creates its
`ShapeAPI`; `ShapeDispatchAPI` dispatches native cell types and owns the weight
cursor. [shape_functions/typing.py](../warp_simdata/shape_functions/typing.py)
defines these interfaces.

For models supporting location and interpolation, build the dataset's locator
before launching a kernel. Interpolate a node-associated float32 field inside
the kernel:

```python
# Inside a kernel specialized on data_model and field_model; ds and field are handles.
elem = data_model.ElementLocatorAPI.find_elem_containing_position(
    ds, position, data_model.ElementAPI.empty(),
)
value = wp.float32(0.0)
if data_model.ElementAPI.is_valid(elem):
    weights = data_model.ElementLocatorAPI.evaluate_position(ds, elem, position)
    nodes = data_model.ElementAPI.get_nodes(ds, elem)
    for i in range(data_model.ElementAPI.get_num_nodes(nodes)):
        node_id = data_model.ElementAPI.get_node_id(ds, nodes, i)
        node_idx = data_model.DatasetAPI.get_node_idx_from_id(ds, node_id)
        value += data_model.ElementLocatorAPI.get_weight(ds, weights, i) * field_model.FieldAPI.get(field, node_idx)
```

A weight cursor stores per-position state, not a per-node array. Indices follow
the node cursor's native order. `evaluate_position` on a known element does not
establish containment; see the
[query workflow](KernelAPI.md#spatial-queries-and-lifetimes).

## Numerical limits

Tetrahedra use analytical inversion; voxels use direct axis-aligned mapping.
Hexahedra, pyramids, and wedges use Newton iteration: at most 10 iterations,
world-space residual tolerance `1.0e-5`, singular determinant threshold
`1.0e-20`. These are fixed constants. The solver returns its last coordinates
without a convergence flag, so parametric membership alone does not validate
cell quality or convergence.

For pyramids at `t >= 0.9999`, weights clamp to the apex. Derivatives use
a special approximation: `dN4/dt = 1`, all other entries zero.

Star-convex polyhedra use model-provided cell and face centers to form tetrahedra.
Interpolation distributes a containing tetrahedron's cell-center weight across
all nodes, its face-center weight across that face, and its edge weights to the
edge nodes. Cached face planes accelerate containment; unresolved cases search
the tetrahedral fan. Degenerate, severely distorted, or unsupported non-convex
geometry can invalidate these assumptions.

Polyhedron contouring uses outward face topology independently of this
interpolation scheme; see [Iso-Surface](IsoSurface.md).

## Adding a shape

1. Implement canonical corners, weights, derivatives, and the `get_shape` factory.
   Declare fixed-size vector/matrix types outside kernel bodies.
2. Add the neutral type and dispatch path; map native types and corner permutations
   in each supporting model's shape library.
3. Check corner weights, partition of unity, derivatives, interior/boundary/exterior
   positions, singular geometry, native ordering, and face winding on supported
   devices. Start from [test_shape_function_topology.py](../tests/test_shape_function_topology.py),
   [test_sids_shapes.py](../tests/test_sids_shapes.py), and
   [test_vtk_shapes.py](../tests/test_vtk_shapes.py).
4. State interpolation and contouring support separately. Adding a type identifier
   or corner permutation does not implement higher-order interpolation.
