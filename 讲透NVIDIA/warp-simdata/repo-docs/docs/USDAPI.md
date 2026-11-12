<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# OpenUSD Reference

Use `warp_simdata.usd` to load scientific USD prims into ordinary Warp SimData
datasets and fields. [CAE OpenUSD Plugins](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins)
provides schemas and native-file readers; Warp SimData provides compute.

## Runtime Requirements

Install Warp SimData as described in [INSTALL](../INSTALL.md). The verified
standalone recipe uses CPython 3.12 on x86-64 Linux (glibc >=2.35) or Windows x64:

```sh
python -m pip install "warp-simdata[usd]==0.2.0" "cae-openusd-plugins==0.1.2" "usd-core==26.8"
```

The plugins' 0.1.2 combined wheel supports PyPI `usd-core` **25.11, 26.3, 26.5,
and 26.8**, not every intervening version. Other OpenUSD builds require the
plugins' [source-build instructions](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins/blob/main/docs/installation.md).
Core Warp SimData does not require OpenUSD.

## Initialization

Register plugins before scientific-schema imports or opening/creating a stage
or layer. Importing base `pxr`/`Usd` first is allowed by the verified 0.1.2 wheel.
This complete example creates two sample points and loads their temperature:

```python
import cae_openusd_plugins

cae_openusd_plugins.register_usd_plugins()

from pxr import Gf, OmniSci, OmniSciCae, Sdf, Usd, Vt
import warp_simdata.usd as simusd

stage = Usd.Stage.CreateInMemory()
prim = OmniSci.Dataset.Define(stage, "/Cloud").GetPrim()
OmniSciCae.PointCloudAPI.Apply(prim)
OmniSci.ArrayAPI.Apply(prim, "points")
prim.CreateAttribute("omni:sci:array:points:value", Sdf.ValueTypeNames.Float3Array).Set(
    Vt.Vec3fArray([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0)])
)
metadata = OmniSci.FieldAPI.Apply(prim, "temperature")
metadata.CreateAssociationAttr("node")
OmniSci.ArrayAPI.Apply(prim, "temperature")
prim.CreateAttribute("omni:sci:array:temperature:value", Sdf.ValueTypeNames.FloatArray).Set(
    Vt.FloatArray([300, 325])
)

time_code = Usd.TimeCode.EarliestTime()
dataset = simusd.dataset_from_prim(prim, device="cpu", time_code=time_code)
field = simusd.field_from_prim(prim, "temperature", device="cpu", time_code=time_code)
dataset.add_field("temperature", field)
assert dataset.get_num_nodes() == 2
assert field.to_array().numpy().tolist() == [300, 325]
```

Use `device="cuda:0"` for CUDA loading. Fields and datasets must use the same
device, time sample and, where applicable, computational representation.

## Public API

| Entry point | Result / use |
| --- | --- |
| `dataset_from_prim(prim, *, device, time_code, **kwargs)` | `Dataset` or `DatasetCollection`; does not attach fields |
| `dataset_from_stage(stage, prim_path, *, device, time_code, **kwargs)` | Resolve a path, then convert |
| `list_fields(prim, *, time_code, **kwargs)` | `FieldInfo` records: `name`, display `label`, `association` |
| `field_from_prim(prim, field_names, *, device, time_code, **kwargs)` | Load one field; a list of scalar names produces a structure-of-arrays vector field |
| `find_supported_prims(stage)` | Prims matching an adapter; conversion may still fail |

`FieldInfo.name`, not its label, identifies a field. Vector components must have
matching associations, lengths and identical scalar dtypes.
Adapter-specific keywords are forwarded unchanged; unsupported keywords raise
the adapter's normal error. [API source](../warp_simdata/usd/api.py) owns full
signatures and defaults.

## Converting Datasets

Open a native asset through the registered plugins, discover candidates, then
load by path. The [upstream usage guide](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins/blob/main/docs/usage.md)
describes each file's stage layout.

```python
# Assumes registration above and valid asset_path / dataset_prim_path strings.
stage = Usd.Stage.Open(asset_path)
for supported in simusd.find_supported_prims(stage):
    print(supported.GetPath())
time_code = Usd.TimeCode.EarliestTime()
dataset = simusd.dataset_from_stage(stage, dataset_prim_path, device="cpu", time_code=time_code)
prim = stage.GetPrimAtPath(dataset_prim_path)
for info in simusd.list_fields(prim, time_code=time_code):
    print(info.name, info.label, info.association)
```

### Component Fields

Load a scalar by name, as in the initialization example, or combine components:

```python
# Assumes prim has matching scalar velocityX/Y/Z fields, plus dataset and time_code above.
velocity = simusd.field_from_prim(
    prim, ["velocityX", "velocityY", "velocityZ"], device="cpu", time_code=time_code,
)
dataset.add_field("velocity", velocity)
```

### Time-Sampled Data

Loader defaults are `Usd.TimeCode.Default()`. Tested native-file inputs have
time-sampled arrays; request `EarliestTime()` or a numbered sample. Reload
geometry and fields together:

```python
# Assumes prim provides a temperature field and dataset arrays at sample 1.
time_code = Usd.TimeCode(1.0)
dataset = simusd.dataset_from_prim(prim, device="cpu", time_code=time_code)
dataset.add_field("temperature", simusd.field_from_prim(
    prim, "temperature", device="cpu", time_code=time_code,
))
```

Authored USD may instead provide default values. FLASH maps `Default()` to its
earliest `nodeType` sample.

## Supported Schema Patterns

The default registry checks adapters in this order. Schema details belong to
the upstream [schema reference](https://github.com/NVIDIA-Omniverse/cae-openusd-plugins/tree/main/docs/schemas).

| Input prim | Representation / important limit |
| --- | --- |
| FLASH AMR | Axisymmetric primal or dual; see below |
| CGNS zone / unstructured section (`OmniSciCgns*`) | SIDS fixed cells or `NFACE_n`; multiple unlike sections are canonicalized before collection. `MIXED` sections raise; a lone GridCoordinates prim is not an input dataset. |
| EnSight unstructured part | Native part with piece connectivity, including `nsided` / `nfaced` |
| OpenFOAM polyMesh | Native volume with owner/neighbour face topology |
| OpenFOAM boundary patch | Surface geometry only; no fields |
| VTK scientific schemas | Image, structured, unstructured or polydata; rectilinear grids, triangle strips and legacy inline polyhedron face streams raise. Split and XML packed face arrays are supported. |
| Reservoir corner-point grid | Native COORD/ZCORN, optional ACTNUM; evaluated Z-up/MAPAXES coordinates. `lengthUnit` must be `m` or unauthored; `indexOrder` must be `eclipse`. |
| Reservoir property prim | Fields only, in authored logical/active-cell order; cannot become a dataset |
| CAE point cloud | Points and fields; no volume locator |
| CAE mesh | Surface polygons and fields; no volume locator |
| Plain `UsdGeomMesh` | World-space points and polygons; no fields |

For reservoir grids, `get_num_elems()` includes all logical element slots.
`ACTNUM=0` slots return invalid element handles. COORD/ZCORN remain unchanged on
the handle. Evaluation applies `depthDirection` and MAPAXES orientation without
adding the absolute MAPAXES origin.

### Axisymmetric FLASH AMR

Packed 2D fields of shape `[1, nyb, nxb]` are revolved around output Y, with source
X as radius. The default `AxisymmetricRepresentation` uses 64 angular cells
over `2*pi`, implicit leaf-block geometry, and element-associated scalar fields.
The primal supports located sampling; block boundaries remain separate for
external-face extraction, including coarse/fine interfaces. Node fields, vector
basis conversion, node-element links and 3D FLASH are unsupported.
For a quarter revolution with finer angular resolution:

```python
# Assumes registered plugins, simusd, Usd, and a convertible flash_prim with dens.
import math

representation = simusd.AxisymmetricRepresentation(angular_cells=128, angle_range=(0.0, 0.5 * math.pi))
time_code = Usd.TimeCode.EarliestTime()
dataset = simusd.dataset_from_prim(
    flash_prim, device="cpu", time_code=time_code, representation=representation,
)
dataset.add_field("dens", simusd.field_from_prim(
    flash_prim, "dens", device="cpu", time_code=time_code, representation=representation,
))
```

Pass the same representation to both loaders; see the
[representation types](../warp_simdata/usd/types.py) for options.

#### Cell-Centered Dual

`AxisymmetricDualRepresentation` exposes cell-centered scalars as nodal values
for contours/slices:

```python
# Assumes registered plugins, simusd, Usd, and a convertible flash_prim with dens.
from warp_simdata.operators import iso_surface

representation = simusd.AxisymmetricDualRepresentation(angular_cells=64)
time_code = Usd.TimeCode.EarliestTime()
dual = simusd.dataset_from_prim(
    flash_prim, device="cpu", time_code=time_code, representation=representation,
)
dual.add_field("dens", simusd.field_from_prim(
    flash_prim, "dens", device="cpu", time_code=time_code, representation=representation,
))
surface = iso_surface.compute(dual, "dens", 15.0)
```

The dual requires consistent `gid` hierarchy, uniform block shape and a covered
rectangular domain; shell coverage is not fully validated. Boundary values use
zero-order extrapolation. Hierarchy lookup allows 32 transitions. Located
sampling, node-element links and ghost semantics are unsupported. See
[data-model capabilities](DatasetsAndFields.md) before selecting an operator.

## Virtual Scientific Array Values

`scoped_sci_array_value_resolver(resolver)` supplies derived arrays without
authoring payloads. Declare typed array and field metadata, then resolve values
on the requested device. Save kernel code in a Python file:

```python
# Assumes the /Cloud prim, imports, and time_code from Initialization.
import warp as wp

OmniSci.FieldAPI.Apply(prim, "temperature_celsius").CreateAssociationAttr("node")
OmniSci.ArrayAPI.Apply(prim, "temperature_celsius")
prim.CreateAttribute("omni:sci:array:temperature_celsius:value", Sdf.ValueTypeNames.FloatArray)

@wp.kernel
def to_celsius(kelvin: wp.array(dtype=wp.float32), celsius: wp.array(dtype=wp.float32)):
    i = wp.tid()
    celsius[i] = kelvin[i] - 273.15

def resolve_array(request):
    if request.instance_name == "temperature_celsius":
        kelvin = request.resolve("temperature")
        celsius = wp.empty_like(kelvin)
        wp.launch(to_celsius, dim=kelvin.size, inputs=[kelvin], outputs=[celsius], device=request.device)
        return celsius
    return None  # Read the authored value for other arrays.

with simusd.scoped_sci_array_value_resolver(resolve_array):
    field = simusd.field_from_prim(prim, "temperature_celsius", device="cpu", time_code=time_code)
assert abs(float(field.to_array().numpy()[0]) - 26.85) < 1e-4
```

The request also exposes `prim` and `time_code`. Returned arrays must match the
declared dtype/layout. Dependencies re-enter the resolver; cycles raise
`USDAdapterError`. Virtual results are memoized by stage/prim/name/time/device
until the scope exits. Keep one scope around one logical loading request.
See [resolver source and contract](../warp_simdata/usd/array_values.py).

## Registry and Extensibility

Implement [PrimAdapter](../warp_simdata/usd/adapters/base.py): `can_handle`,
`to_dataset`, `list_fields`, `get_field`. Reuse
[array/field/relationship helpers](../warp_simdata/usd/utils.py) and the existing
[adapters](../warp_simdata/usd/adapters). `registry.register(adapter)` appends;
the first match wins, so it cannot override an earlier built-in match. A separate
`AdapterRegistry([...])` can choose another order. Use [KernelAPI](KernelAPI.md)
for extending the computational representation itself.

## Current Limitations

- Missing schema imports can interrupt registry search, even for unrelated
  prims. Earlier matches and FLASH's guarded import are exceptions.
- Geometry commonly narrows to float32. NumPy index conversions can wrap values
  outside int32; validate the source range before loading. On CUDA, custom
  resolver arrays must already match the adapter's target dtype; a requested
  different dtype can reinterpret their bytes instead of converting values.
- Reservoir active-cell fields on a grid require `logicalCellToActiveCell`;
  missing lookup raises. Inactive entries read zero. COORD/ZCORN are float32;
  recenter large map coordinates upstream if precision matters. Shared topology,
  local refinement, NNC/fault/transmissibility, schedules and wells are not
  interpreted. Native INIT/UNRST parsing belongs to the plugins.
- `USDAdapterError` reports adapter/runtime failures; `UnsupportedPrimError`
  reports no matching adapter. Matching a schema does not establish valid data
  or per-operator support. Model factories can also propagate `ValueError` or
  `TypeError` for invalid inputs.
