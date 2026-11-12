<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2mip · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [earth2mip/ensemble_utils.py](earth2mip/ensemble_utils.py)
- [earth2mip/inference_ensemble.py](earth2mip/inference_ensemble.py)
- [earth2mip/netcdf.py](earth2mip/netcdf.py)
- [earth2mip/networks/__init__.py](earth2mip/networks/__init__.py)
- [earth2mip/networks/pangu.py](earth2mip/networks/pangu.py)
- [earth2mip/schema.py](earth2mip/schema.py)

</details>



This page describes the fundamental design patterns, abstractions, and architectural components that form the foundation of Earth-2 MIP. It covers the core interfaces that enable unified access to diverse AI weather models, the orchestration systems for running ensemble forecasts, and the data flow patterns that connect external data sources to model execution.

For detailed information about specific model implementations, see [Supported AI Models](#4.3). For ensemble forecasting workflows, see [Ensemble Forecasting](#6.1). For data source configuration, see [Data Sources](#5.2).

## System Overview

Earth-2 MIP is built around a layered architecture that separates concerns between model management, data handling, and forecast orchestration. The core design enables different AI weather models (ONNX, JAX, PyTorch-based) to work seamlessly together through standardized interfaces.

### Core Architecture Diagram

```mermaid
graph TB
    subgraph "Orchestration Layer"
        RunInference["run_inference()"]
        RunEnsembles["run_ensembles()"]
        EnsembleRun["EnsembleRun Schema"]
    end
    
    subgraph "Model Interface Layer"
        GetModel["get_model()"]
        TimeLoop["TimeLoop Interface"]
        Inference["Inference Class"]
        ModelRegistry["ModelRegistry"]
    end
    
    subgraph "Data Interface Layer"
        InitialConditions["initial_conditions"]
        DataSource["DataSource Factory"]
        Regridder["regrid.get_regridder()"]
        LatLonGrid["LatLonGrid"]
    end
    
    subgraph "AI Model Implementations"
        PanguInference["PanguInference"]
        FCNInference["FCN Models"]
        GraphCastInference["GraphCast Models"]
        DLWPInference["DLWP Models"]
    end
    
    RunInference --> GetModel
    RunInference --> InitialConditions
    RunEnsembles --> TimeLoop
    
    GetModel --> ModelRegistry
    GetModel --> Inference
    Inference --> TimeLoop
    
    TimeLoop --> PanguInference
    TimeLoop --> FCNInference
    TimeLoop --> GraphCastInference
    TimeLoop --> DLWPInference
    
    InitialConditions --> DataSource
    DataSource --> Regridder
    Regridder --> LatLonGrid
    
    EnsembleRun --> RunInference
```

Sources: [earth2mip/inference_ensemble.py:35](), [earth2mip/networks/__init__.py:44](), [earth2mip/schema.py:81]()

## Core Design Patterns

### Plugin Architecture

Earth-2 MIP uses a plugin-based architecture where AI weather models are loaded dynamically through entry points and model registries. The `get_model` function serves as the central factory that can instantiate any registered model type.

```mermaid
sequenceDiagram
    participant Client
    participant GetModel as "get_model()"
    participant Registry as "ModelRegistry"
    participant Loader as "Model Loader"
    participant TimeLoop as "TimeLoop"
    
    Client->>GetModel: "get_model('e2mip://pangu')"
    GetModel->>Registry: "get_model()"
    Registry->>Loader: "load model package"
    Loader->>TimeLoop: "create TimeLoop instance"
    TimeLoop-->>GetModel: "return unified interface"
    GetModel-->>Client: "return TimeLoop"
```

The model loading process abstracts away the differences between model architectures (ONNX, JAX, PyTorch) and provides a unified `TimeLoop` interface for time integration.

Sources: [earth2mip/networks/__init__.py:312-351]()

### TimeLoop Abstraction

The `TimeLoop` interface is the cornerstone abstraction that provides a unified way to run time integration for any AI weather model. All models, regardless of their underlying framework, implement this interface.

```mermaid
classDiagram
    class TimeLoop {
        <<interface>>
        +grid: LatLonGrid
        +in_channel_names: List[str]
        +out_channel_names: List[str]
        +device: torch.device
        +__call__(time, x, restart) Iterator
    }
    
    class Inference {
        +model: torch.nn.Module
        +center: torch.Tensor
        +scale: torch.Tensor
        +time_step: timedelta
        +__call__(time, x, restart) Iterator
        +_iterate(x, normalize, time) Iterator
    }
    
    class PanguInference {
        +model_6: PanguStacked
        +model_24: PanguStacked
        +grid: LatLonGrid
        +__call__(time, x, normalize, restart) Iterator
    }
    
    TimeLoop <|-- Inference
    TimeLoop <|-- PanguInference
```

The `TimeLoop` interface standardizes model execution by requiring all implementations to:
- Accept initial conditions as tensors with shape `(batch, history, channel, lat, lon)`
- Yield `(time, output, restart)` tuples for each forecast step
- Provide metadata about grids and channel names

Sources: [earth2mip/time_loop.py](), [earth2mip/networks/__init__.py:121-251](), [earth2mip/networks/pangu.py:168-258]()

### Configuration-Driven Execution

Earth-2 MIP uses Pydantic schemas to define type-safe configurations for ensemble runs. The `EnsembleRun` schema encapsulates all parameters needed for a forecast.

| Configuration Aspect | Schema Class | Key Fields |
|----------------------|--------------|------------|
| Ensemble Parameters | `EnsembleRun` | `ensemble_members`, `perturbation_strategy`, `noise_amplitude` |
| Model Metadata | `Model` | `grid`, `in_channels_names`, `time_step`, `entrypoint` |
| Weather Events | `WeatherEvent` | `start_time`, `initial_condition_source`, `domains` |
| Perturbation Strategy | `PerturbationStrategy` | `gaussian`, `correlated`, `bred_vector`, `spherical_grf` |

Sources: [earth2mip/schema.py:81-136](), [earth2mip/schema.py:54-71]()

## Data Flow Architecture

### Initial Conditions Pipeline

The data flow for initial conditions follows a standardized pipeline that transforms external meteorological data into model-ready tensors.

```mermaid
graph LR
    subgraph "External Sources"
        CDS["Climate Data Store"]
        GFS["NOAA GFS"]
        IFS["ECMWF IFS"]
        HDF5["Local Files"]
    end
    
    subgraph "Data Source Layer"
        GetDataSource["get_data_source()"]
        CDSSource["CDS DataSource"]
        GFSSource["GFS DataSource"]
        IFSSource["IFS DataSource"]
    end
    
    subgraph "Processing Pipeline"
        GetInitialCondition["get_initial_condition_for_model()"]
        Regridder["get_regridder()"]
        TensorPrep["Tensor Preparation"]
    end
    
    subgraph "Model Input"
        ModelTensor["(B,H,C,Y,X) Tensor"]
    end
    
    CDS --> CDSSource
    GFS --> GFSSource
    IFS --> IFSSource
    HDF5 --> IFSSource
    
    GetDataSource --> CDSSource
    GetDataSource --> GFSSource
    GetDataSource --> IFSSource
    
    CDSSource --> GetInitialCondition
    GFSSource --> GetInitialCondition
    IFSSource --> GetInitialCondition
    
    GetInitialCondition --> Regridder
    Regridder --> TensorPrep
    TensorPrep --> ModelTensor
```

The `get_initial_condition_for_model` function handles the complexity of:
- Selecting appropriate channels for the target model
- Regridding data to match model grid requirements  
- Normalizing and formatting data as PyTorch tensors
- Managing time history for models that require it

Sources: [earth2mip/initial_conditions.py](), [earth2mip/inference_ensemble.py:282](), [earth2mip/inference_ensemble.py:334]()

### Ensemble Orchestration Flow

The ensemble forecasting system coordinates model execution across multiple ensemble members with perturbations.

```mermaid
graph TD
    subgraph "Ensemble Setup"
        Config["EnsembleRun Config"]
        WeatherEvent["WeatherEvent"]
        GetInitializer["get_initializer()"]
    end
    
    subgraph "Perturbation Generation"
        PerturbStrategy["PerturbationStrategy"]
        NoiseGeneration["Noise Generation"]
        PerturbFunction["perturb(x, rank, batch_id)"]
    end
    
    subgraph "Distributed Execution"
        RunEnsembles["run_ensembles()"]
        BatchProcessing["Batch Processing"]
        ModelIteration["Model Time Integration"]
    end
    
    subgraph "Output Processing"
        NetCDFOutput["NetCDF Output"]
        Regridding["Output Regridding"]
        UpdateNetCDF["update_netcdf()"]
    end
    
    Config --> GetInitializer
    WeatherEvent --> RunEnsembles
    GetInitializer --> PerturbStrategy
    PerturbStrategy --> NoiseGeneration
    NoiseGeneration --> PerturbFunction
    
    RunEnsembles --> BatchProcessing
    PerturbFunction --> BatchProcessing
    BatchProcessing --> ModelIteration
    
    ModelIteration --> Regridding
    Regridding --> UpdateNetCDF
    UpdateNetCDF --> NetCDFOutput
```

The `run_ensembles` function manages:
- Distributed processing across multiple GPU ranks
- Batching of ensemble members for memory efficiency
- Perturbation application through the `perturb` function
- Time integration using the model's `TimeLoop` interface
- Output regridding and NetCDF file writing

Sources: [earth2mip/inference_ensemble.py:68-164](), [earth2mip/inference_ensemble.py:208-271]()

## Integration Points

### Model Registry System

The model registry provides a unified interface for discovering and loading models from various sources including NGC (NVIDIA GPU Cloud), local files, and S3 storage.

```mermaid
graph LR
    subgraph "Model Sources"
        NGC["NGC Catalog"]
        S3["S3 Storage"]
        Local["Local Files"]
        HTTP["HTTP URLs"]
    end
    
    subgraph "Registry Layer"
        ModelRegistry["ModelRegistry"]
        Package["Package"]
        Metadata["metadata.json"]
    end
    
    subgraph "Loading System"
        GetModel["get_model()"]
        EntryPoint["Entry Points"]
        DefaultInference["_default_inference()"]
        LoadPackage["_load_package()"]
    end
    
    NGC --> Package
    S3 --> Package
    Local --> Package
    HTTP --> Package
    
    Package --> Metadata
    ModelRegistry --> Package
    
    GetModel --> EntryPoint
    GetModel --> LoadPackage
    LoadPackage --> DefaultInference
```

Model URIs are resolved through different schemes:
- `e2mip://model_name` - Built-in models with entry points
- `ngc://org/model:version` - NGC catalog models  
- `s3://bucket/path` - S3-hosted models
- `file:///local/path` - Local filesystem models

Sources: [earth2mip/networks/__init__.py:341-351](), [earth2mip/model_registry.py]()

### Normalization and Scaling

The `Inference` class handles data normalization and denormalization automatically using pre-computed statistics stored with each model.

```mermaid
graph TB
    subgraph "Input Processing"
        RawInput["Raw Input (x)"]
        Center["center (μ)"]
        Scale["scale (σ)"]
        Normalize["(x - μ) / σ"]
    end
    
    subgraph "Model Processing"
        NormalizedInput["Normalized Input"]
        ModelForward["model.forward()"]
        NormalizedOutput["Normalized Output"]
    end
    
    subgraph "Output Processing"
        Denormalize["y * σ + μ"]
        PhysicalOutput["Physical Units Output"]
    end
    
    RawInput --> Normalize
    Center --> Normalize
    Scale --> Normalize
    Normalize --> NormalizedInput
    
    NormalizedInput --> ModelForward
    ModelForward --> NormalizedOutput
    
    NormalizedOutput --> Denormalize
    Scale --> Denormalize
    Center --> Denormalize
    Denormalize --> PhysicalOutput
```

The normalization parameters are loaded from `global_means.npy` and `global_stds.npy` files stored in the model package and registered as PyTorch buffers for automatic device management.

Sources: [earth2mip/networks/__init__.py:170-179](), [earth2mip/networks/__init__.py:232-250](), [earth2mip/networks/__init__.py:264-266]()

---

