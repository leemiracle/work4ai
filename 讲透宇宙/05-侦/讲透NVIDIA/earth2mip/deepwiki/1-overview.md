<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2mip · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [earth2mip/ensemble_utils.py](earth2mip/ensemble_utils.py)
- [earth2mip/inference_ensemble.py](earth2mip/inference_ensemble.py)
- [earth2mip/netcdf.py](earth2mip/netcdf.py)
- [earth2mip/schema.py](earth2mip/schema.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



Earth-2 Model Intercomparison Project (MIP) is a Python-based AI framework that enables climate researchers and scientists to explore and experiment with AI models for weather and climate forecasting. The framework provides a unified interface for running inference with pre-trained model checkpoints, scoring model performance using standard meteorological metrics, and facilitating intercomparison between different AI weather models.

This document provides a high-level architectural overview of the Earth-2 MIP codebase and its major systems. For detailed installation instructions, see [Installation](#2.1). For specific model usage examples, see [Quick Start Examples](#2.2). For in-depth information about individual systems, see the relevant sections on [Model Management](#4), [Data Systems](#5), [Inference and Forecasting](#6), and [Model Evaluation](#7).

## System Architecture

Earth-2 MIP follows a layered architecture that separates concerns between model management, data handling, orchestration, and evaluation. The framework is designed around several key abstractions that enable different AI weather models to work together through common interfaces.

### Core Abstraction Layers

```mermaid
graph TB
    subgraph "CLI & API Layer"
        CLI["CLI Tools<br/>ensemble forecasting"]
        PythonAPI["Python API<br/>get_model(), run_basic_inference()"]
        Notebooks["Jupyter Notebooks<br/>Examples & Tutorials"]
    end
    
    subgraph "Orchestration Layer" 
        EnsembleEngine["Ensemble Engine<br/>run_inference()"]
        TimeCollection["Time Collection<br/>run_over_initial_times()"]
        ScoringEngine["Scoring Engine<br/>score_deterministic()"]
    end
    
    subgraph "Model Interface Layer"
        ModelRegistry["Model Registry<br/>get_model()"]
        TimeLoop["TimeLoop Interface<br/>TimeLoop.__call__()"]
        NetworksModule["networks Module<br/>earth2mip.networks.*"]
    end
    
    subgraph "Data Abstraction Layer"
        InitialConditions["Initial Conditions<br/>get_initial_condition_for_model()"]
        DataSources["Data Sources<br/>CDS, GFS, IFS, HDF5"]
        GridSystem["Grid System<br/>LatLonGrid, regridding"]
    end
    
    subgraph "AI Models"
        Pangu["Pangu Weather<br/>ONNX Runtime"]
        GraphCast["GraphCast<br/>JAX/Haiku"]
        FCN["FourCastNet<br/>PyTorch"]
        DLWP["DLWP<br/>PyTorch"]
    end
    
    CLI --> EnsembleEngine
    PythonAPI --> ModelRegistry
    Notebooks --> PythonAPI
    
    EnsembleEngine --> TimeLoop
    TimeCollection --> EnsembleEngine
    ScoringEngine --> TimeLoop
    
    ModelRegistry --> NetworksModule
    TimeLoop --> NetworksModule
    
    NetworksModule --> Pangu
    NetworksModule --> GraphCast  
    NetworksModule --> FCN
    NetworksModule --> DLWP
    
    EnsembleEngine --> InitialConditions
    ScoringEngine --> InitialConditions
    
    InitialConditions --> DataSources
    TimeLoop --> GridSystem
```

The architecture enables users to interact with AI weather models through multiple interfaces while maintaining consistency in data handling and model execution. The `TimeLoop` interface serves as the central abstraction that standardizes how different AI models are called and integrated into workflows.

**Sources:** [earth2mip/inference_ensemble.py:35-51](), [README.md:13-25](), [pyproject.toml:91-101]()

### Configuration and Schema System

Earth-2 MIP uses a structured configuration system based on Pydantic models to manage complex forecasting workflows:

```mermaid
graph LR
    subgraph "Configuration Schema"
        EnsembleRun["EnsembleRun<br/>Pydantic Model"]
        WeatherEvent["WeatherEvent<br/>Weather Configuration"]
        PerturbStrategy["PerturbationStrategy<br/>Enum: gaussian, correlated, etc."]
    end
    
    subgraph "Runtime Components"
        Perturb["get_initializer()<br/>Perturbation Function"]
        NoiseGen["Noise Generation<br/>generate_noise_*()"]
        ModelExec["Model Execution<br/>TimeLoop.__call__()"]
    end
    
    EnsembleRun --> WeatherEvent
    EnsembleRun --> PerturbStrategy
    PerturbStrategy --> Perturb
    Perturb --> NoiseGen
    WeatherEvent --> ModelExec
```

The `EnsembleRun` schema defines ensemble forecasting parameters including model selection, perturbation strategies, simulation length, and output configuration. This configuration-driven approach enables reproducible experiments and flexible workflow customization.

**Sources:** [earth2mip/schema.py:81-136](), [earth2mip/inference_ensemble.py:208-271]()

## Model Integration Framework  

The framework's plugin architecture allows seamless integration of diverse AI weather models through standardized interfaces:

### Model Registry and Loading System

```mermaid
graph TB
    subgraph "Model Discovery"
        EntryPoints["setuptools entry_points<br/>earth2mip.networks"]
        ModelIds["Model IDs<br/>fcn, dlwp, pangu, graphcast"]
        NGC["NVIDIA NGC Catalog<br/>Pre-trained Checkpoints"]
    end
    
    subgraph "Loading Pipeline" 
        GetModel["get_model()<br/>earth2mip.networks"]
        LoadFunctions["Model-specific loaders<br/>fcn.load(), pangu.load()"]
        TimeLoopWrapper["TimeLoop Wrapper<br/>Standardized Interface"]
    end
    
    subgraph "Model Implementations"
        ONNX["ONNX Runtime Models<br/>Pangu Weather"]
        PyTorch["PyTorch Models<br/>FCN, DLWP"]
        JAX["JAX/Haiku Models<br/>GraphCast"]
    end
    
    EntryPoints --> GetModel
    ModelIds --> GetModel
    NGC --> LoadFunctions
    
    GetModel --> LoadFunctions
    LoadFunctions --> TimeLoopWrapper
    
    TimeLoopWrapper --> ONNX
    TimeLoopWrapper --> PyTorch  
    TimeLoopWrapper --> JAX
```

The `get_model()` function serves as the central entry point for model loading, using setuptools entry points to discover available models and their loading functions. Each model type implements a loader function that returns a `TimeLoop`-compatible interface.

**Sources:** [earth2mip/networks/__init__.py](), [pyproject.toml:91-101](), [earth2mip/inference_ensemble.py:48]()

### TimeLoop Interface Standardization

```mermaid
graph LR  
    subgraph "TimeLoop Protocol"
        Interface["TimeLoop Interface"]
        Properties["Properties<br/>grid, in_channel_names, out_channel_names"]
        CallMethod["__call__(time, x)<br/>Iterator[time, data, restart]"]
    end
    
    subgraph "Model Adaptations"
        PanguWrapper["PanguTimeLoop<br/>ONNX Runtime Integration"]
        GraphCastWrapper["GraphCastTimeLoop<br/>JAX Integration"] 
        FCNWrapper["FCNTimeLoop<br/>PyTorch Integration"]
    end
    
    Interface --> Properties
    Interface --> CallMethod
    
    Properties --> PanguWrapper
    CallMethod --> PanguWrapper
    Properties --> GraphCastWrapper
    CallMethod --> GraphCastWrapper  
    Properties --> FCNWrapper
    CallMethod --> FCNWrapper
```

The `TimeLoop` interface provides a standardized way to interact with AI weather models regardless of their underlying implementation framework. Models expose grid information, channel names, and a callable interface that yields time-stepped forecasts.

**Sources:** [earth2mip/time_loop.py](), [earth2mip/inference_ensemble.py:120-156]()

## Data Flow and Processing Pipeline

Earth-2 MIP implements a flexible data pipeline that can access meteorological data from multiple sources and transform it for model consumption:

### Data Source Architecture

```mermaid
graph TB
    subgraph "External Data Sources"
        CDS["Climate Data Store<br/>ERA5 Reanalysis"]
        GFS["NOAA GFS<br/>GRIB Format"]
        IFS["ECMWF IFS<br/>S3 Storage"] 
        HDF5Files["Local HDF5<br/>Custom Datasets"]
    end
    
    subgraph "Data Source Abstraction"
        DataSourceFactory["get_data_source()<br/>Factory Function"]
        CDSSource["cds.DataSource<br/>CDS API Integration"]
        GFSSource["gfs.DataSource<br/>GRIB Processing"]
        IFSSource["ifs.DataSource<br/>S3 Access"]
        HDF5Source["hdf5.DataSource<br/>Local File Access"]
    end
    
    subgraph "Processing Pipeline"
        GetInitialCondition["get_initial_condition_for_model()<br/>Model-specific Extraction"]
        Regridding["Regridding System<br/>TempestRegridder, RegridLatLon"]
        Cache["Local Cache<br/>~/.cache/earth2mip"]
    end
    
    CDS --> CDSSource
    GFS --> GFSSource
    IFS --> IFSSource
    HDF5Files --> HDF5Source
    
    DataSourceFactory --> CDSSource
    DataSourceFactory --> GFSSource  
    DataSourceFactory --> IFSSource
    DataSourceFactory --> HDF5Source
    
    CDSSource --> GetInitialCondition
    GFSSource --> GetInitialCondition
    IFSSource --> GetInitialCondition
    HDF5Source --> GetInitialCondition
    
    GetInitialCondition --> Regridding
    Regridding --> Cache
```

The data source abstraction enables consistent access to heterogeneous meteorological data providers. The `get_initial_condition_for_model()` function handles model-specific data requirements including channel selection, temporal alignment, and spatial regridding.

**Sources:** [earth2mip/initial_conditions.py](), [earth2mip/inference_ensemble.py:327-334]()

## Ensemble Forecasting Workflow

The ensemble forecasting system represents the framework's most sophisticated orchestration capability, supporting distributed computation and multiple perturbation strategies:

### Ensemble Execution Pipeline

```mermaid
graph TB
    subgraph "Configuration & Setup"
        Config["EnsembleRun Configuration<br/>JSON/Pydantic"]
        WeatherEventConfig["WeatherEvent<br/>start_time, domains, initial_condition_source"]
        PerturbConfig["Perturbation Configuration<br/>strategy, amplitude, channels"]
    end
    
    subgraph "Distributed Execution"
        DistManager["DistributedManager<br/>torch.distributed"]
        BatchProcessing["Ensemble Batching<br/>ensemble_batch_size"]
        NoiseGeneration["Noise Generation<br/>generate_noise_*()"]
    end
    
    subgraph "Model Integration"
        ModelLoad["Model Loading<br/>get_model()"]
        InitialConditions["Initial Condition Loading<br/>get_initial_condition_for_model()"]
        TimeLoop["Time Integration<br/>TimeLoop.__call__()"]
    end
    
    subgraph "Output Generation"
        NetCDFWriter["NetCDF Output<br/>ensemble_out_*.nc"]
        RegridOutput["Output Regridding<br/>Optional Grid Transformation"]
        MetadataWrite["Metadata & Config<br/>Global Attributes"]
    end
    
    Config --> WeatherEventConfig
    Config --> PerturbConfig
    WeatherEventConfig --> InitialConditions
    PerturbConfig --> NoiseGeneration
    
    DistManager --> BatchProcessing
    BatchProcessing --> NoiseGeneration
    NoiseGeneration --> TimeLoop
    
    ModelLoad --> TimeLoop
    InitialConditions --> TimeLoop
    
    TimeLoop --> RegridOutput
    RegridOutput --> NetCDFWriter
    Config --> MetadataWrite
    MetadataWrite --> NetCDFWriter
```

The `run_inference()` function orchestrates the complete ensemble workflow, from configuration parsing through distributed execution to output generation. It supports multiple perturbation strategies including Gaussian noise, correlated noise, bred vectors, and spherical Gaussian random fields.

**Sources:** [earth2mip/inference_ensemble.py:301-408](), [earth2mip/ensemble_utils.py:186-232]()

Earth-2 MIP's architecture enables climate researchers to focus on scientific questions rather than implementation details, providing a robust foundation for AI weather model experimentation and evaluation.

---

