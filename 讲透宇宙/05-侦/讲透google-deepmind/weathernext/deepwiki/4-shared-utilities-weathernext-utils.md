<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/weathernext · page 4 Shared Utilities (weathernext/utils) · fetched 2026-10-26 -->

# Shared Utilities (weathernext/utils)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [weathernext/utils/__init__.py](weathernext/utils/__init__.py)
- [weathernext/utils/predictor_base.py](weathernext/utils/predictor_base.py)
- [weathernext/utils/variables.py](weathernext/utils/variables.py)

</details>



The `weathernext/utils` package provides the foundational infrastructure used across all WeatherNext models, including WeatherNext 2 (FGN), WeatherNext Cyclones, and legacy architectures (GraphCast and GenCast). This shared layer handles data ingestion, pipeline slicing, forcing computations, xarray-to-JAX translations, predictor wrapper patterns, multi-step autoregressive rollouts, loss formulations, checkpoint serialization, and distributed sharding.

Because this is a parent overview page, each section below introduces a core subsystem and links to its dedicated child page for deep technical details.

---

## 4.1. Data Utilities: Inputs, Targets, and Forcings

The data pipeline infrastructure manages how raw meteorological datasets (such as ERA5 or HRES) are sliced, parsed, and converted into structured JAX inputs, targets, and external forcings. Variables are grouped into standard categories such as pressure-level atmospheric fields, surface parameters, and time-dependent indicators as defined in `variables.py` [weathernext/utils/variables.py:17-82]().

For details, see [Data Utilities: Inputs, Targets, and Forcings](#4.1).

Sources:
- `weathernext/utils/variables.py`

---

## 4.2. Solar Radiation Forcing

Top-of-Atmosphere (TOA) Incident Solar Radiation serves as an essential external physical forcing that dictates diurnal and seasonal heating cycles. The utility module computes these irradiance values geometrically based on latitude, longitude, and timestamps, integrating them seamlessly into the forcing pipeline.

For details, see [Solar Radiation Forcing](#4.2).

---

## 4.3. xarray–JAX Integration Layer

WeatherNext models interface with `xarray.Dataset` and `xarray.DataArray` structures for labeled meteorological axes, while underlying JAX neural networks operate on dense arrays and PyTrees. The xarray-JAX integration layer bridges this gap using specialized PyTree registrations (`xarray_tree.py`) and dataset-level dense application utilities (`xarray_dense.py`).

For details, see [xarray–JAX Integration Layer](#4.3).

---

## 4.4. Predictor Wrappers: Normalization, Casting, and NaN Cleaning

Predictors implement the abstract base class `Predictor` [weathernext/utils/predictor_base.py:27-41](), establishing a standard interface for `__call__` inference [weathernext/utils/predictor_base.py:43-84]() and `.loss(...)` training [weathernext/utils/predictor_base.py:86-130](). WeatherNext uses a layered wrapper pattern over base predictors to inject capabilities like bfloat16 casting (`Bfloat16Cast`), input normalization and residual target handling (`InputsAndResiduals`), cleaning invalid numerical values (`NaNCleaner`), and handling ensemble dimensions.

```mermaid
title "PredictorWrapperStack"
graph TD
    Client["ClientCode"] --> Wrapper["PredictorWrapper"]
    Wrapper --> NaN["NaNCleaner"]
    NaN --> Cast["Bfloat16Cast"]
    Cast --> Norm["InputsAndResiduals"]
    Norm --> Base["PredictorBasePredictor"]

    style Client fill:none,stroke:#000,stroke-width:1px
    style Wrapper fill:none,stroke:#000,stroke-width:1px
    style NaN fill:none,stroke:#000,stroke-width:1px
    style Cast fill:none,stroke:#000,stroke-width:1px
    style Norm fill:none,stroke:#000,stroke-width:1px
    style Base fill:none,stroke:#000,stroke-width:1px
```
*Figure 1: Layered composition of predictor wrappers executing preprocessing tasks before reaching the core predictor implementation.*

Sources:
- `weathernext/utils/predictor_base.py`

For details, see [Predictor Wrappers: Normalization, Casting, and NaN Cleaning](#4.4).

---

## 4.5. Autoregressive Predictor Wrapper

To scale single-step atmospheric models into multi-day weather forecasts, the autoregressive wrapper (`autoregressive.py`) chains single-step predictions across multiple lead times. It manages sliding window input histories, gradient checkpointing configurations, stochastic noise injection for generative trajectories, and separates static geographic features from time-dependent prognostic variables.

For details, see [Autoregressive Predictor Wrapper](#4.5).

---

## 4.6. Chunked Prediction and Ensemble Rollout

Long-horizon rollouts and large-scale ensemble forecasts require memory-efficient execution strategies. The rollout infrastructure (`rollout.py`) handles chunked prediction generators, target template extensions, coordinate alignment across forecast steps, device-parallel distribution via `pmap`, and deterministic PRNG key splitting across ensemble members.

For details, see [Chunked Prediction and Ensemble Rollout](#4.6).

---

## 4.7. Loss Functions

Model optimization relies on specialized loss definitions (`losses.py`) that respect the geometry and physical scale of meteorological data. This includes weighted Mean Squared Error (MSE) per pressure level, latitude-dependent cosine weighting to account for grid cell area convergence at the poles, pressure-level weighting factors, per-variable loss aggregations, and diagnostics logging protocols conforming to the `LossFunction` specification.

For details, see [Loss Functions](#4.7).

---

## 4.8. Checkpoint Serialization

Model parameters, optimizer states, and configuration metadata are serialized and restored using `checkpoint.py`. This utility handles flattening and unflattening of nested JAX PyTrees, dataclasses, and dictionaries, while supporting direct read/write operations against local storage and Google Cloud Storage (GCS) buckets.

For details, see [Checkpoint Serialization](#4.8).

---

## 4.9. Sharding, Padding and Performance Utilities

High-performance execution on distributed TPU/GPU hardware relies on lower-level infrastructure modules. These include device mesh configuration (`sharding.py`), array padding utilities to fit tensor dimensions cleanly across mesh splits (`padding_utils.py`), optimized gather and scatter indexing (`gather_scatter_ops.py`), activation layers (`activations.py`), and dense transformation primitives (`dense.py`).

```mermaid
title "SharedUtilityCodebaseMapping"
graph TB
    subgraph "ShardingAndPerformance"
        Mesh["sharding.py"]
        Padding["padding_utils.py"]
        Gather["gather_scatter_ops.py"]
    end
    subgraph "CoreInfrastructure"
        BasePred["predictor_base.py"]
        Vars["variables.py"]
        Check["checkpoint.py"]
    end
    
    Mesh --> Padding
    Padding --> Gather
    BasePred --> Vars

    style Mesh fill:none,stroke:#000,stroke-width:1px
    style Padding fill:none,stroke:#000,stroke-width:1px
    style Gather fill:none,stroke:#000,stroke-width:1px
    style BasePred fill:none,stroke:#000,stroke-width:1px
    style Vars fill:none,stroke:#000,stroke-width:1px
    style Check fill:none,stroke:#000,stroke-width:1px
```
*Figure 2: Relationships among core utility modules and performance-oriented sharding primitives.*

Sources:
- `weathernext/utils/predictor_base.py`
- `weathernext/utils/variables.py`

For details, see [Sharding, Padding and Performance Utilities](#4.9).

---

