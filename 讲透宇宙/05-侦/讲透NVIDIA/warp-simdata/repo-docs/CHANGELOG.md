<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Changelog

All notable changes to Warp SimData are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Python package versions follow [PEP 440](https://peps.python.org/pep-0440).

Add changes to `Unreleased` under `Added`, `Changed`, `Deprecated`, `Removed`,
`Fixed`, or `Security`. At release time, move those entries into a dated version
section. Release branches carry only dated sections.

## [0.2.0] - 2026-10-06

This release contains compatibility changes; entries marked **Breaking**
describe the migration. Patch releases on the 0.2 line stay backward
compatible.

### Added

- Added `probe.compute_many()` to sample several fields with shared temporary
  point locations and an optional validity mask. Reuse is scoped to the call;
  `compute()` remains a single-field adapter with no location storage.
- Added `to_vtk_data_model()` to canonicalize any built-in dataset as the closest
  VTK-shaped Warp data model without importing VTK. Point, curve, and surface
  models become polydata; fixed and polyhedral volumes become unstructured grids;
  image and structured grids retain their native structure; collections preserve
  their pieces. Implicit geometry and topology are materialized on the source
  device when needed, while attached fields retain their storage when ordering is
  unchanged. Higher-order volume cells are linearized to canonical corners.

- Added the optional `warp_simdata.vtk` adapter and `vtk` dependency extra.
  `to_vtk()` deep-copies canonical geometry, topology, polyhedron faces, and fields
  into VTK-owned CPU arrays and returns pipeline-ready `vtkImageData`,
  `vtkStructuredGrid`, `vtkPolyData`, `vtkUnstructuredGrid`, or
  `vtkPartitionedDataSet`. The module also re-exports `vtk_to_dataset()` for the
  reverse conversion.

- Added `to_common_vtk_data_model()` to canonicalize several datasets under one
  unstructured-grid data model (the union of their cell types) so they can form a
  `DatasetCollection`. The CGNS zone adapter uses it when a zone's sections have
  different element types (say `HEXA_8` next to `TETRA_4`, or fixed shapes next
  to `NFACE_n`), which previously failed with "All datasets must use the same
  data model".

### Changed

- ParaView extensions now load together through one `WarpSimData.py` plugin,
  replacing the individual filter entry points, and cache converted Warp SimData
  inputs by VTK `MTime` and device. Re-executing a filter after changing only
  operator properties reuses uploaded arrays and acceleration structures.
  Streamlines now use ParaView's native proxy-selected Line and Point Cloud seed
  sources and their interactive widgets while exposing integration controls. A
  separate Streamlines With Custom Source filter accepts any point-set pipeline
  input as its seeds. New Slice, Element Faces, Probe, Mesh Analysis, Point Data
  to Cell Data, Cell Data to Point Data, and Warp Calculator filters cover the
  useful geometry, sampling, association, topology, selection, and scalar
  expression operations. Iso Surface accepts point or cell scalars, averaging
  cell values onto points internally. Voxelize and Voronoi Voxelize now expose
  point/cell output association and validity masks.
- ParaView filters now use `warp_simdata.scoped_timer()` for consistent
  synchronized preparation, execution, output, and total timing printed to the
  terminal without modifying filter outputs. Process-wide NVTX ranges can be
  enabled through Warp SimData configuration in ParaView's Python shell.
- ParaView filters now share converted inputs and device data until the last
  filter using an input is deleted or switches inputs. Element Faces and Iso
  Surface can also pass supported input fields to their generated surfaces.
  Leaf-local Calculator, field-association, Mesh Analysis, Slice, Iso Surface,
  and Element Faces filters now preserve multiblock and partitioned-dataset
  hierarchies while caching every converted leaf across executions.

- Batched iso-surface selection now reuses per-cell scalar extrema across
  groups of four or more iso-values, reducing repeated comparisons without
  retaining a field-dependent cache between calls.

- `element_in_box` now rejects elements immediately when their first vertex is
  outside the box in `all` mode, reducing vertex traversal for small regions of
  interest. Mask values and compacted index ordering are unchanged.

- Large CUDA field-range queries now combine samples per thread before updating
  shared extrema, reducing atomic contention. Component and magnitude ranges
  retain float64 storage and the existing field-level cache.

- Added `get_per_element_bounds()` on datasets and collections to explicitly
  prepare shared conservative per-element bounds (24 bytes per element).
  Slicing reuses these bounds when available and otherwise classifies vertices
  directly; it no longer creates a private persistent bounds cache. Exact
  selection, non-finite diagnostics, and output provenance are preserved.

- Small CUDA advection batches (up to 1,024 seed/direction pairs) now launch one
  trace per block to reduce divergent control flow and spread tracing across
  the GPU. Integration and output ordering are unchanged; larger batches keep
  the existing launch. AOT builds include both launch variants.

- Refreshed the Python, kernel, shape-function, installation, testing, and
  interoperability documentation against current APIs. Added a datasets-and-
  fields guide and runnable CPU pipeline/kernel examples; corrected voxelization
  arguments, cursor interfaces, ownership/cache semantics, USD support boundaries,
  and AOT recording/compilation instructions.

- CGNS `PENTA_6` and EnSight `penta6` corners are no longer permuted to
  `[1, 3, 2, 4, 6, 5]` before reaching the wedge shape functions and the VTK
  conversion. CGNS, EnSight Gold and VTK share the same linear wedge order
  (`vtkCGNSReader` passes `PENTA_6` connectivity through unchanged and VTK's cell
  validator accepts it); the permutation produced mirror-image wedges, which
  `to_vtk()` exposed as inverted cells with negative volume. Interpolation and
  point location on wedges are unchanged (a relabelled linear prism interpolates
  the same values); iso-surface triangles on SIDS and EnSight wedges now wind the
  same way as on VTK wedges. `ElementTopologyAPI.get_corner_node_id` returns the
  source corners in order for these types.

- `to_vtk_data_model()` keeps shared polyhedron faces for models that store them:
  CGNS `NFACE_n` polyhedra reuse the `NGON_n` face table and OpenFOAM `polyMesh`
  reuses its face, owner-cell and cell-point arrays, sharing the coordinate array
  instead of copying it. Other polyhedral models still get one face loop per cell.
  On a 277M-cell polyhedral case this halves the face memory of the VTK object.

- `to_vtk_data_model()` on a `DatasetCollection` attaches fields that live only on
  the collection to the converted pieces: per-piece collection fields are split
  back up and node fields covering every piece's nodes are shared, so `to_vtk()`
  no longer drops zone-level fields on multi-section CGNS zones.

- Updated the ParaView extension filters to use the shared `warp_simdata.vtk`
  adapters for generic VTK input and SimData output conversion, while retaining
  filter-specific input policies and benchmark instrumentation.

- **Breaking:** Reworked the kernel-scope data-model protocols around explicit
  cursors. `ElementAPI.get_nodes(ds, elem)` returns a `NodeCursor`,
  `get_face(ds, elem, face_idx)` returns a `FaceCursor`,
  `NodeElementLinksAPI.get_elems(ds, node_id)` returns a `NodeElementsCursor`,
  and `ElementLocatorAPI.evaluate_position(ds, elem, position)` returns a
  `WeightsCursor` read through `get_weight(ds, weights, local_idx)`. Counts and
  per-item lookups take the cursor instead of re-resolving the element. Methods
  that read dataset memory take the dataset handle first; queries that use only
  a cursor or handle omit it. Each model defines the cursor types its APIs use.
  `DatasetAPI.get_elem` is now `get_elem_from_id`, with a new `get_elem_from_idx`,
  and `ElementAPI.get_face_slot` gives each cell face a dense index. Face-heavy
  operators on polyhedral models
  resolve each face once instead of per node (2.4x on CGNS `NFACE_n`, 1.7x on
  EnSight `nfaced` face loops); point location no longer materializes a
  64-wide weight vector (3x on hexahedra, 8x on polyhedra). EnSight Gold
  uniform elements now report all their nodes, including higher-order ones,
  like the VTK and CGNS models do, instead of only the corners.

- Packed the shape-library face-corner tables into compile-time integer
  constants selected by an unrolled loop, instead of runtime-indexed Warp
  vectors that the compiler materializes in local memory. The external-face
  hash build on a 120M-cell mixed VTK mesh drops from 386 to 315 ms.

- Added `config.element_locator_bvh_constructor` and
  `config.element_locator_bvh_leaf_size` (environment variables
  `WARP_SIMDATA_BVH_CONSTRUCTOR`, `WARP_SIMDATA_BVH_LEAF_SIZE`) to select the
  Warp BVH construction algorithm (`"cubql"`, `"sah"`, `"median"`, `"lbvh"`) and
  leaf size for element locators, including the per-piece locators of dataset
  collections, and made cuBQL the default on CUDA devices (the CPU keeps
  Warp's default, SAH). Warp 1.17's GPU LBVH builds a 48.8M-element tree in
  0.4 s against 3.7 s for cuBQL and matches it on random far-field queries,
  but its traversal degrades by about two orders of magnitude for points in
  the finely graded region of a large CFD mesh, which is where streamlines are
  seeded: a 64-seed, 500-step trace next to the vehicle of that mesh takes
  9.1 s with the LBVH, 0.10 s with cuBQL and 0.075 s with SAH (27 s host
  build). Hint-less location of the same near-body points is likewise ~100x
  faster with cuBQL.

- Made polyhedral point location exact and fast by default. `build_element_locator()`
  now also caches one plane per cell face (unit outward normal and offset,
  keyed by `ElementAPI.get_face_slot`), a planarity band and a convexity flag
  per element on the dataset handle of every polyhedral data model (CGNS
  `NFACE_n`, OpenFOAM polyMesh, EnSight Gold `nfaced`, VTK polyhedra), 16 bytes
  per cell face plus 5 per element. For a convex cell the planes decide
  containment outside the planarity band; points within the band and every
  point of a non-convex cell fall back to the fan-tetrahedron search that also
  produces the interpolation weights, so "inside" means exactly "has weights".
  The ray-parity shell test is gone.

- Raised the minimum supported `warp-lang` version from 1.12.0 to 1.17.0.

- Cleaned up idioms that predate the Warp 1.17 and VTK 9.6 baselines: host code
  uses the total returned by `simdata.utils.array_scan` instead of reading the
  trailing offset back separately (one fewer device sync per scan); the
  trailing-sum kernel indexes from the end; the remaining bare `@wp.kernel`
  definitions use `simdata.kernel`; scalar `wp.constant` wrappers are plain
  Python constants; `Union`/`Optional` annotations use `X | Y`; VTK
  unstructured-grid cell types are read with `GetCellTypes()` (falling back to
  the deprecated getter on older VTK) and polydata verts, lines and polys come
  from the cell array's offsets and connectivity arrays instead of parsing the
  legacy count-prefixed stream in Python; tests use the NumPy `Generator` API.

- Kept streamline output compaction on the source device by replacing NumPy
  staging with Warp kernels and prefix scans, copying one output point per
  thread. The same path serves CPU and CUDA devices.

- Read prefix-scan totals in the OpenFOAM and EnSight Gold connectivity
  builders with a single-element slice instead of copying the whole offsets
  array to the host.

- Counted unique polyhedron nodes during EnSight Gold `nfaced`, CGNS `NFACE_n`,
  and OpenFOAM polyMesh dataset creation by scanning each face node against
  the element's earlier faces instead of keeping a per-thread scratch vector
  (a runtime-indexed Warp vector lives in local memory). The count kernel is
  faster without changing results.

- Derived and validated `surface_mesh` face offsets and counts on the device
  in `surface_mesh.create_handle`, reading back three integers instead of
  copying the whole per-face array to the host and checking it with NumPy.
  Extracting all faces of 2M hexahedra with `element_faces.compute` drops
  from 40 to 5 ms; error checks and messages are unchanged.

- Validated CGNS/SIDS element connectivity on the device when a dataset handle
  is created: element offsets must be non-decreasing and within the
  connectivity array, and node ids within the grid. A malformed section now
  raises a `ValueError` naming the element and value instead of surfacing later
  as an illegal-memory-access CUDA error.

- Extended those device-side bounds checks to every data model with index
  arrays, through a shared `data_models.bounds_checks` module: VTK
  unstructured grid cell offsets, point ids, and polyhedron face tables; VTK
  polydata verts, lines, and polys; OpenFOAM polyMesh face offsets, point ids,
  owner and neighbour cell ids, and boundary-mesh face offsets and point ids;
  EnSight Gold `nsided`/`nfaced` counts and 1-based node ids; CGNS `NFACE_n`
  face ids resolved against the `NGON_n` element ranges (and the block element
  types), including separate validation of inline `MIXED` element-type tags;
  `surface_mesh` vertex ids; and `element_subset` parent element indices. Each
  check runs on the device and reads back only a few integers. The checks are
  on by default and can be skipped with `config.validate_datasets = False`
  (environment variable `WARP_SIMDATA_VALIDATE_DATASETS=0`).

- Resolved each fixed-cell corner once in the iso-surface classification
  kernel and reused the cached node indices for topology validation and case
  classification, replacing per-pair corner re-derivation. The kernel is
  2-4.5x faster on CUDA and `iso_surface.compute` is up to 3.7x faster on
  large hexahedral inputs; output is unchanged.

- Rebuilt the shape-functions library lookups (`build_shape_functions_library`)
  around per-shape constant tables behind statically unrolled cell-type
  dispatch instead of one flat table indexed by a runtime shape offset.
  Indexing a `wp.constant` vector with a runtime index costs time
  proportional to the vector length on the device, so every topology query
  (corner and face node indices, node and face counts) was several times
  slower than necessary and degraded further with each additional element
  type in a dataset. The public `ShapesLibrary` API and results are
  unchanged; iso-surface classification is a further 2-9x faster on mixed
  hexahedron/tetrahedron/wedge meshes, and other operators that query
  element topology benefit as well.

- Checked polyhedral iso-surface segment and triangle count totals for int32
  overflow on the device, reading back two integers instead of copying the
  full per-element count arrays to the host twice per call. Polyhedral
  `iso_surface.compute` is about 2.2x faster on 2M-cell VTK polyhedron and
  OpenFOAM polyMesh inputs.

- Skipped the face walk in the polyhedral iso-surface segment count for cells
  whose node samples all lie on one side of the contour value, reusing the
  existing finite-sample pass to classify them. A further 1.1-2.4x on 2M-cell
  polyhedral inputs depending on how many cells the contour crosses.

- Ran the polyhedral segment-emission, loop-triangulation, and triangle-emission
  kernels over a compacted list of the cells the contour actually crosses
  instead of over every element, reducing work when few cells cross the contour.

- Keyed external-face classification in `element_faces` with an
  order-independent face hash (a non-linear integer mix of each node index,
  summed) instead of insertion-sorting the face's nodes in a per-thread scratch
  vector, and recorded each face's hash-table slot while building the table so
  the classification pass reads one occurrence count per face instead of
  re-hashing and re-matching it. Candidate matches are still exact-verified.
  `element_faces.compute(external_only=True)` is 2-7x faster on CUDA (2M
  hexahedra: 123 -> 21 ms; 2M polyhedra: 45 -> 6 ms); output is unchanged.

- Matched candidate faces in `element_faces` from register-resident node
  lists (faces with up to 8 nodes) instead of re-reading each node through the
  element API for every comparison, and reused the fetched nodes for the
  face key. Exact verification is unchanged; `external_only=True` is a
  further 1.1-1.7x faster (2M hexahedra: 20.4 -> 12.1 ms). Known limitation:
  this kernel produces an illegal memory access on faces of mixed node counts
  when Warp is configured to emit sm_90 PTX for a Blackwell GPU
  (`wp.config.cuda_output="ptx"`, `ptx_target_arch=90`) and the driver
  JIT-compiles it; compile natively for the device instead.

### Removed

- Removed the in-repository benchmark suite, packaging, and source-
  publication references.

- **Breaking:** Dropped the `warp_simdata.io` module (including
  `warp_simdata.io.cgns`) and the `io` optional-dependency extra from the
  public package. It was a thin convenience wrapper used only by the test
  suite; the CGNS/HDF5 loader now lives at `tests/support/io/cgns.py` as
  test-only support code with no API stability guarantee. For production
  code, load data with a library of your choice (`cae-openusd-plugins` via
  `warp_simdata.usd` for OpenUSD-staged CAE data, or VTK/PyVista)
  and construct a dataset explicitly; see
  [Datasets and fields](docs/DatasetsAndFields.md).

### Fixed

- Streamline output packing reuses validated scan totals, eliminating two
  redundant scalar GPU-to-CPU transfers and their synchronizations.
- External-face extraction and OpenFOAM, SIDS, and EnSight connectivity
  construction reuse scan totals instead of fetching trailing offsets again.
  Surface meshes built from counts avoid redundant offset validation, and
  iso-surfaces retain scan totals without copying them through a status buffer.
- OpenUSD VTK PolyData conversion now treats canonical empty split and packed
  triangle-strip topology arrays as zero cells, matching VTK and ParaView,
  while continuing to reject non-empty triangle strips.

- Fixed a CUDA illegal-memory-access error in batched iso-surfaces of collection
  subsets with Warp 1.17 / CUDA 12.9 targeting `sm_89` (including NVIDIA L40).
  Triangle emission now shares the edge-key helper used during classification.

- `to_vtk()` now exports polyhedron face connectivity exceeding the signed
  32-bit offset range by expanding faces in bounded batches into VTK-owned host
  arrays. Point IDs stay `int32` while large face offsets use `int64`.
  `polyhedron_storage="int64"` optionally uses VTK's specialized 64-bit face
  storage, trading additional memory for its optimized access path. Source
  and canonical Warp data-model limits are unchanged.

- Preserved canonical polyhedron face orientations when `to_vtk()` creates a
  native `vtkUnstructuredGrid`. Shared faces are now expanded into cell-local
  outward-wound loops at the VTK export boundary, preventing fragmented or
  incorrect `vtkContourFilter` output from CGNS `NFACE_n` and OpenFOAM
  `polyMesh` datasets.

- Detected int32 overflow of prefix-sum totals instead of silently wrapping
  offsets. `simdata.utils.array_scan(..., add_trailing_sum=True)` now computes
  the total in 64 bits on the device, returns it, and raises `OverflowError`
  when it exceeds the int32 range; every offsets table built through it (face,
  node and cell-face offsets in the data models and operators) is covered.
  `element_faces` now raises `OverflowError` naming the face and vertex counts
  and suggesting `external_only=True` or an element subset, instead of risking
  an illegal memory access or corrupt offsets.

- Stopped dropping a point from combined streamlines when a seed's backward
  trace recorded no steps, which previously raised a `ValueError` during
  output assembly.

- Corrected the `VTK_VOXEL` face table in `vtk_shapes`, whose six loops were
  wound inward; `element_faces` on voxel cells (including image data and
  structured grids) now emits outward-facing quads like every other cell type.
  A test checks every fixed VTK 3D cell table for outward winding.

## [0.1.0] - 2026-08-03

### Added

- Initial public release of Warp SimData.
- Warp-native datasets, fields, data-model protocols, and CPU/CUDA simulation
  data operators.
- Data-model support for VTK, CGNS/SIDS, OpenFOAM, EnSight Gold, FLASH,
  reservoir corner-point grids, and custom mesh and point-cloud types.
- Optional OpenUSD adapters backed by CAE OpenUSD Plugins.
- Optional ParaView filters for iso-surfaces, streamlines, and voxelization.

### Fixed

- Corrected NanoVDB tile allocation for negative, non-tile-aligned voxel bounds.
