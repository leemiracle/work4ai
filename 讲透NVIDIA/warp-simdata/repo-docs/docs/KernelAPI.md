<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Kernel Scope Reference

Use this guide to connect a custom layout or algorithm to Warp SimData.
For Python containers, ownership, and fields, see [Datasets and Fields](DatasetsAndFields.md).

## Choose an extension path

1. **Reuse a shipped model.** Choose a model that matches your representation from
   the [capability table](DatasetsAndFields.md#data-model-capabilities), then pass
   arrays or grid parameters to its `create_dataset()` factory.
   [basic_pipeline.py](examples/basic_pipeline.py) constructs a uniform grid and checks
   field conversion, probing, voxelization, streamlines, contours, and subsets.
2. **Implement a model.** Define the access APIs required by your operators.
   [custom_model.py](examples/custom_model.py) stores disconnected segments in separate
   start/end arrays, with one-based IDs. It checks bounds, centers `[[1, 0, 0], [0, 2, 2]]`,
   sizes `[2, 4]`, and node-to-element averages `[1, 4]`. It deliberately omits faces,
   locators, interpolation, reverse links, and volume topology. For a volume model,
   choose a reference that matches your storage, such as
   [sectioned elements](../warp_simdata/data_models/sids/unstructured.py) or
   [polyhedra with shared faces](../warp_simdata/data_models/openfoam/polymesh.py).
3. **Write an operator.** Specialize a kernel factory on the data-model namespace.
   [kernel_operator.py](examples/kernel_operator.py) computes each element's average
   node x coordinate. It checks `[0.5, 1.5] * 4` on eight image-grid elements, reads a
   field view, and verifies hexahedron center weights.

After [installation](../INSTALL.md), run these from the repository root:

```bash
python docs/examples/basic_pipeline.py --device cpu
python docs/examples/custom_model.py --device cpu
python docs/examples/kernel_operator.py --device cpu
```

Use `--device cuda:0` to check a CUDA device. Each script asserts its results and
prints a success message. Save custom kernels in a Python file so Warp can inspect
their source.

## Data-model contract

Use `Dataset` and `Field` objects in Python. Kernels access data through their
`.handle` values and the model's API classes, without depending on the storage layout.

The [DataModel protocol](../warp_simdata/data_models/typing.py) describes the types
and APIs below. Each operator uses a subset of this contract.

| Attributes | Purpose |
| --- | --- |
| `DatasetHandle`, `ElementHandle` | Opaque Warp structs or scalar handles |
| `NodeIdHandle`, `ElementIdHandle` | Model-specific Warp ID types |
| `DatasetAPI` | Counts, ID/index conversion, coordinates, host builders |
| `ElementAPI` | Validity, node cursors, face cursors |
| `ElementLocatorAPI` | Position lookup and interpolation weights |
| `NodeElementLinksAPI` | Elements incident to a node |

A narrow model may implement only the APIs its operators use, as the segment
example does; it does not then satisfy the full protocol. Method presence alone
does not establish support: shipped `point_cloud` and `surface_mesh` locators always
miss, so those models are probe targets, not sources. See the
[capability table](DatasetsAndFields.md#data-model-capabilities).

An **ID** belongs to the model: it may be one-based, sparse, or a struct.
An **index** is a zero-based `wp.int32` position. Use `get_node_idx_from_id` or
`get_elem_idx_from_id` before indexing logical field arrays. A node cursor's
`local_idx` is an index within that element's node list.

Cursors resolve a range once and then expose its count and items:

```python
# Inside a kernel specialized on data_model; ds is its dataset handle.
elem = data_model.DatasetAPI.get_elem_from_idx(ds, wp.tid())
if data_model.ElementAPI.is_valid(elem):
    nodes = data_model.ElementAPI.get_nodes(ds, elem)
    for local_idx in range(data_model.ElementAPI.get_num_nodes(nodes)):
        node_id = data_model.ElementAPI.get_node_id(ds, nodes, local_idx)
        position = data_model.DatasetAPI.get_node_coords(ds, node_id)
```

Keep cursors paired with the dataset handle that produced them. They are small
struct values containing scalar state, not arrays. The `DataModel` protocol does
not require cursor classes as namespace attributes; individual helper factories
may require them. Functions reading dataset memory take `ds` first. Functions
reading only a cursor or handle, such as `get_num_nodes(nodes)` and `is_valid(elem)`,
do not.

## Optional shape and topology capabilities

`ElementShapeAPI.get_shape_type(ds, elem)` returns a neutral
`shape_functions.ELEMENT_TYPE_*` value. Contouring requires this capability.
Fixed cells also need `ElementTopologyAPI.is_linear(ds, elem)` and
`get_corner_node_id(ds, nodes, canonical_corner_idx)`. These map native connectivity
to the [canonical corner order](ShapeFunctions.md#canonical-node-ordering).

Generate both capabilities from a uniform shape library:

```python
from warp_simdata import shape_functions

# Your model supplies DataModel, ShapesLibrary, and these typed Warp functions.
DataModel.ElementTopologyAPI = shape_functions.get_element_topology_api(
    DataModel, ShapesLibrary, get_cell_type, get_nodes_cell_type,
)
DataModel.ElementShapeAPI = DataModel.ElementTopologyAPI
```

`get_cell_type(ds, elem)` and `get_nodes_cell_type(ds, nodes)` return native
type codes understood by `ShapesLibrary`. This helper also requires
`DataModel.NodeCursor`.

Polyhedral models return `ELEMENT_TYPE_POLYHEDRON` and expose face loops through
`ElementAPI`. For a pure-polyhedron model, use this classifier instead:

```python
DataModel.ElementShapeAPI = shape_functions.get_polyhedron_shape_api(DataModel)
```

Resolve a face with `get_face(ds, elem, face_idx)`, then read its count and node IDs.
Volume face loops must wind outward by the right-hand rule. Adapters establish
that orientation; operators do not repair the complete shell.

`get_face_slot(face)` identifies a unique `(element, face)` occurrence, dense in
element order. A shared interior face has one slot per incident element.
Face matching uses node identity, not equal coordinates. See
[Element Faces](ElementFaces.md) for extraction behavior.

## Operator and field kernels

Use `@simdata.cached` on the Python factory and `@simdata.kernel` / `@simdata.func`
on device code. Capture the model in the factory; annotate its kernel argument
with `data_model.DatasetHandle`. This kernel computes each element's vertex-average x:

```python
import warp as wp
import warp_simdata as simdata

@simdata.cached
def get_kernel(data_model):
    @simdata.kernel(module="unique")
    def mean_x(ds: data_model.DatasetHandle, output: wp.array(dtype=wp.float32)):
        elem_idx = wp.tid()
        elem = data_model.DatasetAPI.get_elem_from_idx(ds, elem_idx)
        value = wp.float32(0.0)
        if data_model.ElementAPI.is_valid(elem):
            nodes = data_model.ElementAPI.get_nodes(ds, elem)
            count = data_model.ElementAPI.get_num_nodes(nodes)
            for i in range(count):
                node_id = data_model.ElementAPI.get_node_id(ds, nodes, i)
                value += data_model.DatasetAPI.get_node_coords(ds, node_id).x
            if count > 0:
                value /= wp.float32(count)
        output[elem_idx] = value
    return mean_x
```

Launch it in Python and attach the output to a shallow copy:

```python
# Assumes a dataset, such as the grid in Datasets and Fields.
output = wp.empty(dataset.get_num_elems(), dtype=wp.float32, device=dataset.device)
wp.launch(get_kernel(dataset.data_model), dim=output.size,
          inputs=[dataset.handle], outputs=[output], device=dataset.device)
result = dataset.shallow_copy()
result.add_field("mean_x", simdata.Field.from_array(output, simdata.AssociationType.ELEMENT))
```

The complete [kernel_operator.py](examples/kernel_operator.py) also demonstrates
field-view reads and checks the results.

Specialize field-reading kernels on `field.field_model`. Read through
`FieldAPI.get(handle, idx)`, obtain the logical count with `get_count(handle)`,
and obtain a correctly typed zero with `zero()`. This supports different storage
layouts and derived views. **Selection and reduction views silently ignore
`FieldAPI.set()` calls.** Allocate an array-backed output field for writes.
The [field protocol](../warp_simdata/fields/typing.py) defines the signatures.

## Spatial queries and lifetimes

For models supporting point location, prepare acceleration and a field
interpolator in Python:

```python
# Assumes field is attached to dataset.
dataset.build_element_locator()
interpolator = field.get_interpolated_field_api(dataset.data_model)
```

The builder retains resources on the dataset and may fail for unsupported
models. Built-in sampling operators build their locators. Call
`dataset.build_node_element_links()` separately if the algorithm needs adjacency.

Capture `data_model`, `field_model`, and `interpolator` in the kernel factory,
then locate a point before sampling:

```python
# Inside the kernel; ds and field_handle are the dataset and field handles.
elem = data_model.ElementLocatorAPI.find_elem_containing_position(
    ds, position, data_model.ElementAPI.empty(),
)
value = field_model.FieldAPI.zero()
if data_model.ElementAPI.is_valid(elem):
    value = interpolator.get(ds, field_handle, elem, position)
```

The interpolator handles node/element associations and model-specific rules.
For direct weight access, see [Shape Functions](ShapeFunctions.md#position-evaluation-and-weight-cursors).
Evaluating a known element alone does not check containment.

Keep datasets, fields, backing arrays, and acceleration owners alive until all
launches using them have completed. A handle or cursor is not an ownership transfer.
Do not modify geometry behind cached locators; rebuild the dataset and its
acceleration resources when geometry changes.

## Validate an extension

Unpack the structure check's result:

```python
# Assumes data_model is the namespace to inspect.
from warp_simdata.data_models.validation import validate_data_model

ok, errors = validate_data_model(data_model, verbose=False)
assert ok, errors
```

The `(ok, errors)` tuple itself is always truthy. This validator checks selected
types, required method names, and `staticmethod` declarations; it does not check
signatures, locator behavior, or numerical correctness. It rejects scalar
`ElementHandle` types, including the shipped `point_cloud` model. Use it as a
structural aid, not an operator-support test.

Check ID/index round trips, invalid handles, empty ranges, field order, and known
operator results on CPU and available CUDA devices. Volume models also need tests
for canonical corners, face winding, containment, and interpolation; see the
[model tests](../tests/README.md).

## Compilation and recording

JIT specialization is the default. Record representative calls before their
factory cache entries exist:

```python
# Assumes dataset is a shipped model supported by centroid.
import warp_simdata as simdata
from warp_simdata.operators import centroid

with simdata.recorder.Recorder() as recording:
    result = centroid.compute(dataset)
recording.save("aot_config.json")
```

Recording observes cache misses, not every launch. To include existing cached
specializations, use `simdata.recorder.save_config_from_cache("aot_config.json")`.
Setting `simdata.config.aot_record_path` saves that configuration after each new
recordable specialization. Compile in a separate process with a writable
`WARP_CACHE_PATH`:

```bash
WARP_SIMDATA_COMPILE_KERNELS_AOT=1 python -m warp_simdata.aot_compile --config aot_config.json --devices cpu
```

Factories opt into recording with `@simdata.cached(aot="operators.<name>")`.
`aot_roles={"data_model": "dataset", "positions_data_model": "positions"}` assigns
distinct roles when an operator consumes multiple models. Recording is not
automatic AOT support: reconstruction requires supported model factories and
operator compilation paths. The custom examples are JIT-only; arbitrary custom
models and nested collections/subsets are not covered.

Recorded `probe` or `voxelization` calls using `output_mask_field_name`
cannot be AOT-compiled because the generated configuration refers to an unavailable
`probe_masked` or `voxelization_masked` module. Use JIT for those calls. CUDA advection AOT builds include
both 1-thread and 256-thread block sizes; Warp caches them separately. See
[`aot_compile.py`](../warp_simdata/aot_compile.py) and its `--help` for controls.
