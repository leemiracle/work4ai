<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# VTK Integration

Use these adapters to exchange in-memory datasets with VTK. Load files with
VTK's readers before conversion. Warp SimData provides two layers:

| Entry point | Storage / dependency |
| --- | --- |
| `data_models.vtk.to_vtk_data_model(dataset)` | VTK-shaped Warp arrays on the dataset's device; no VTK dependency |
| `vtk.to_vtk(dataset, *, polyhedron_storage="auto")` | VTK object with deep-copied, VTK-owned host arrays |
| `vtk.vtk_to_dataset(vtk_data, device=...)` | Dictionary of Warp datasets/collections loaded on the requested device |

## Loading From VTK

Install the optional object adapters with `python -m pip install "warp-simdata[vtk]==0.2.0"`
(VTK >=9.6). This complete example imports an eight-cell image and exports it:

```python
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonDataModel import vtkImageData

from warp_simdata.vtk import to_vtk, vtk_to_dataset

vtk_input = vtkImageData()
vtk_input.SetDimensions(3, 3, 3)
values = numpy_to_vtk(np.arange(27, dtype=np.float32), deep=True)
values.SetName("value")
vtk_input.GetPointData().AddArray(values)

dataset = vtk_to_dataset(vtk_input, device="cpu")["dataset"]
assert dataset.get_num_elems() == 8
vtk_output = to_vtk(dataset)
assert vtk_output.GetNumberOfCells() == 8
assert vtk_output.GetPointData().GetArray("value").GetNumberOfTuples() == 27
```

Choose `device="cuda:0"` to upload input arrays to CUDA. The loader accepts
`vtkImageData`, `vtkStructuredGrid`, `vtkUnstructuredGrid` and `vtkPolyData`.
Volume cells must be supported linear types or polyhedra; quadratic cells raise.
Polydata supports vertices, lines and polygons, including mixed families.

| Composite input | Dictionary result |
| --- | --- |
| Single dataset | `{"dataset": Dataset}` |
| `vtkPartitionedDataSet` | `{"dataset": DatasetCollection}` |
| `vtkPartitionedDataSetCollection` | Name-to-collection mapping; unnamed entries use `Block_<index>` |
| `vtkMultiBlockDataSet` | Converted to a partitioned collection, then the mapping above |

Collection pieces must have compatible data models. Unsupported/null partitions
can be skipped with warnings; inspect the returned mapping and warnings before
assuming full coverage. Collected fields must be compatible across pieces; see
[Datasets and Fields](DatasetsAndFields.md).

### Import Fidelity

| Input detail | Import behavior |
| --- | --- |
| Scalar / 3-component arrays | Imported as float32 / vec3f; int64 and float64 can lose precision |
| Other component counts | Skipped with a warning |
| Same name in point and cell data | Cell data replaces point data |
| VTK field data | Not imported |
| Image direction matrix | Ignored; use axis-aligned data or convert to structured points before loading |
| Ghost/blanking state | Not applied as a visibility mask; cells are processed normally |
| Rectilinear grids, uniform-grid AMR, triangle strips | Raise; strips must first become triangles |
| Topology indices / connectivity | int32 limits; export's wider face offsets do not widen import |

These adapters do not guarantee lossless round trips. Supported conversion also
does not imply support by every operator.

## Warp-Native Conversion

```python
# Assumes dataset is a Warp SimData dataset, as constructed above.
from warp_simdata.data_models.vtk import to_vtk_data_model

vtk_model_dataset = to_vtk_data_model(dataset)
```

| Source semantics | Warp target |
| --- | --- |
| Image / curvilinear structured | `vtk.image_data` / `vtk.structured_grid` |
| Points / curves / surfaces | `vtk.polydata` vertices / lines / polygons |
| Fixed-cell / polyhedral volumes, including reservoir grids | `vtk.unstructured_grid` |
| Collection | Collection of converted pieces |

Existing VTK-shaped models are shallow-copied. Other conversions can materialize
coordinates/connectivity and canonical corner ordering on the source device.
Fields are retained when node/element ordering is unchanged. Higher-order
volumes become linear corner cells; Voronoi/Gaussian point-cloud interpolation
becomes explicit vertices and loses its implicit influence semantics.

CGNS `NFACE_n` and OpenFOAM polyMesh conversions reuse shared faces and
coordinates; export respects signed CGNS references and reverses OpenFOAM
neighbour-side loops. Other polyhedral models may create cell-local face loops.
For unlike collection pieces, `to_common_vtk_data_model()` creates one model
covering their combined cell types and distributes compatible collection fields.
See [conversion source](../warp_simdata/data_models/vtk/conversion.py).

## VTK Objects

`to_vtk(dataset)` performs native conversion itself and returns `vtkImageData`,
`vtkStructuredGrid`, `vtkPolyData`, `vtkUnstructuredGrid`, or
`vtkPartitionedDataSet`. Node fields become point data, element fields become
cell data, and unassociated fields become field data.

All exported arrays are deep-copied to host memory. CUDA export includes transfer
and synchronization. The returned object can outlive its Warp dataset and enter
a VTK pipeline:

```python
# Assumes dataset from the complete example above.
from warp_simdata.vtk import to_vtk
from vtkmodules.vtkFiltersCore import vtkElevationFilter

vtk_output = to_vtk(dataset)
elevation = vtkElevationFilter()
elevation.SetInputData(vtk_output)
elevation.Update()
```

### Large Polyhedron Connectivity

Cell-local face expansion can exceed `2**31 - 1` entries despite int32 point,
cell and face IDs. Export builds face tables in bounded batches directly into
VTK-owned arrays. Default `polyhedron_storage="auto"` keeps point IDs int32 and
promotes face offsets to int64 as needed. For VTK's specialized 64-bit storage:

```python
# Assumes dataset contains polyhedra and to_vtk is imported.
vtk_output = to_vtk(dataset, polyhedron_storage="int64")
```

This doubles face-connectivity memory and applies to all collection pieces' face arrays. Other arrays retain
their types. Batching limits temporary storage; the complete VTK object still
needs host memory, and source/canonical Warp index limits remain unchanged.
