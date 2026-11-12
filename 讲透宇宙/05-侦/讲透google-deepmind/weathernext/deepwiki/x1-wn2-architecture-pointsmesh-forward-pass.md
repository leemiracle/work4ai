<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/weathernext · page 2.2 WN2 Architecture: Points–Mesh Forward Pass · patched3 2026-10-26 -->

# WN2 Architecture: Points–Mesh Forward Pass
# WN2 Architecture: Points–Mesh Forward Pass

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [weathernext/utils/points_mesh_gnn.py](weathernext/utils/points_mesh_gnn.py)
- [weathernext/weathernext2/architecture.py](weathernext/weathernext2/architecture.py)
- [weathernext/weathernext2/architecture_utils.py](weathernext/weathernext2/architecture_utils.py)

</details>



## Purpose and Scope

This page documents the core neural network architecture of WeatherNext 2 (WN2), focusing on the implementation details found in `weathernext/weathernext2/architecture.py` and `weathernext/weathernext2/architecture_utils.py`. It covers the `ForwardPass` Haiku module, update block constructors for points-to-mesh, mesh, and mesh-to-grid transitions (`weathernext/utils/points_mesh_gnn.py`), latent and output dense configurations, spatial feature engineering, normalization conditioning, rematerialization (remat), and mesh splitting strategies.

---

## 1. The `ForwardPass` Module Architecture

The `ForwardPass` class is a Haiku module (`weathernext/weathernext2/architecture.py:49-117`) that acts as the primary orchestrator for the multi-modality deep learning predictor. It accepts input datasets and forcing fields, separates normalization conditioning variables, constructs spatial and graph features, passes them through an encoder-processor-decoder graph neural network pipeline, and maps them back to grid and global outputs.

```mermaid
graph TD
    sub5["weathernext/weathernext2/architecture.py"]
    sub6["weathernext/weathernext2/architecture_utils.py"]
    sub7["weathernext/utils/points_mesh_gnn.py"]

    Inputs[""xr.Dataset Inputs & Forcings""] --> Classify[""architecture_utils.classify_input_data""]
    Classify --> Split[""architecture_utils.split_norm_conditioning_features""]
    Split --> GridData[""grid_data & global_data""]
    GridData --> SpatialFeat[""feature_utils.get_spatial_features""]
    SpatialFeat --> P2M[""points_to_mesh_model_ctor (PointsMeshTypedGraphGNN)""]
    P2M --> Mesh[""mesh_model_ctor (Mesh GNN Backbone)""]
    Mesh --> M2G[""mesh_to_grid_model_ctor (PointsMeshTypedGraphGNN)""]
    M2G --> Output[""Predicted xr.Dataset""]

    sub6 -.-> Classify
    sub6 -.-> Split
    sub7 -.-> P2M
    sub7 -.-> M2G
```

Sources:
- `weathernext/weathernext2/architecture.py:49-117`
- `weathernext/weathernext2/architecture_utils.py:29-71`
- `weathernext/utils/points_mesh_gnn.py:70-175`

---

## 2. Input Classification and Normalization Conditioning

Before entering the GNN layers, raw inputs and forcing fields are classified and preprocessed by utility functions in `weathernext/weathernext2/architecture_utils.py`. 

The function `classify_input_data` (`weathernext/weathernext2/architecture_utils.py:29-71`) verifies that all required normalization conditioning features exist, splits them out via `split_norm_conditioning_features` (`weathernext/weathernext2/architecture_utils.py:111-125`), applies variable prefixes (`input_` and `forcing_`), and sorts variables into grid-based data and global data using `sort_by_grid_and_global` (`weathernext/weathernext2/architecture_utils.py:87-102`).

| Utility Function | File Path | Role |
| :--- | :--- | :--- |
| `classify_input_data` | `weathernext/weathernext2/architecture_utils.py:29-71` | Orchestrates input splitting, prefixing, and grid/global sorting. |
| `split_norm_conditioning_features` | `weathernext/weathernext2/architecture_utils.py:111-125` | Extracts conditioning features from datasets. |
| `sort_by_grid_and_global` | `weathernext/weathernext2/architecture_utils.py:87-102` | Separates variables with lat/lon dimensions from scalar global variables. |
| `merge_global_data` | `weathernext/weathernext2/architecture_utils.py:74-84` | Recombines global data dictionaries with modality-specific data. |

Sources:
- `weathernext/weathernext2/architecture_utils.py:29-125`

---

## 3. Update Block Constructors and Points–Mesh GNNs

The architecture relies on composable update constructors that transform features across geometric domains (grid points, icosahedral mesh nodes, and global contexts). These are implemented via `PointsMeshTypedGraphGNN` in `weathernext/utils/points_mesh_gnn.py`.

```mermaid
graph TD
    sub1["weathernext/utils/points_mesh_gnn.py"]

    PointData[""LatLonPointsData""] --> P2M_Block[""PointsMeshTypedGraphGNN (is_points_to_mesh=True)""]
    MeshNodes[""TriangularMeshData""] --> P2M_Block
    P2M_Block --> MeshUpdate[""MeshUpdateConstructor (DeepGNN Backbone)""]
    MeshUpdate --> M2G_Block[""PointsMeshTypedGraphGNN (is_mesh_to_points=True)""]
    M2G_Block --> PointOutput[""Updated LatLonPointsData""]

    sub1 -.-> P2M_Block
    sub1 -.-> M2G_Block
```

### Connectivity Types
`PointsMeshTypedGraphGNN` supports three distinct spatial connectivity strategies defined in `ConnectivityType` (`weathernext/utils/points_mesh_gnn.py:59-68`):
1. `CLOSEST` (`1`): Connects each point to its closest neighbor in the mesh.
2. `IN_TRIANGLE` (`2`): Connects each point to the three vertices of the enclosing triangular mesh face.
3. `BALL_QUERY` (`3`): Connects mesh points to all points within a scaled radius fraction (`ball_query_radius_fraction`) (`weathernext/utils/points_mesh_gnn.py:98-124`).

Sources:
- `weathernext/utils/points_mesh_gnn.py:59-175`
- `weathernext/weathernext2/architecture.py:60-62`

---

## 4. Latent and Output Dense Configurations

Neural network layers throughout `ForwardPass` utilize flexible configuration dictionaries (`dense_kwargs`) to define dense transformations:
- **`latent_dense_kwargs`**: Dictionary of parameters passed to internal dense blocks used for message passing and feature projection across the encoder-processor-decoder (`weathernext/weathernext2/architecture.py:56`).
- **`output_dense_kwargs`**: Dictionary of parameters for output MLPs excluding the terminal output size (`weathernext/weathernext2/architecture.py:57`), ensuring compatibility with variable-specific output dimensions.
- **`norm_conditioning_latent_dense_kwargs`**: Optional specific dense kwargs assigned to encode normalization conditioning features when `norm_conditioning_features` is non-empty (`weathernext/weathernext2/architecture.py:65-66`).

Sources:
- `weathernext/weathernext2/architecture.py:49-117`

---

## 5. Spatial Features and Conditioning

Spatial awareness is injected into the model through coordinate transformations and feature generation. The configuration dictionary `spatial_features_kwargs` is forwarded directly to `feature_utils.get_spatial_features` (`weathernext/weathernext2/architecture.py:58`), generating Cartesian conversions, local coordinate frames, and Fourier features from latitude and longitude coordinates.

Normalization conditioning features are processed independently and fused into the network backbone to modulate layer representations dynamically based on global metadata or lead-time parameters.

Sources:
- `weathernext/weathernext2/architecture.py:58-66`
- `weathernext/weathernext2/architecture_utils.py:29-71`

---

## 6. Rematerialization (Remat) and Mesh Splitting

To manage memory consumption during backward passes on large-scale weather grids, `ForwardPass` exposes explicit rematerialization toggles (`weathernext/weathernext2/architecture.py:71-73`):
- `remat_grid_to_mesh_gnn`: Wraps the input grid-to-mesh GNN stage in JAX remat (gradient checkpointing).
- `remat_mesh_gnn`: Wraps the core mesh processor backbone in remat.
- `remat_mesh_to_grid_gnn`: Wraps the mesh-to-grid decoding GNN stage in remat.

Additionally, `mesh_num_splits` (`weathernext/weathernext2/architecture.py:59`) specifies the refinement depth of the icosahedral mesh hierarchy, controlling resolution steps across spatial sharding domains.

Sources:
- `weathernext/weathernext2/architecture.py:49-156`

---

