<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2studio · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document provides a comprehensive overview of earth2studio, an open-source deep-learning framework for exploring, building and deploying AI weather and climate workflows. It covers the core architecture, key components, and how the major subsystems interact to enable scientific computing workflows.

For detailed installation instructions, see [Installation and Setup](#2). For specific component documentation, see [Core Architecture](#3) and its subsections covering [Data Sources](#3.1), [Models](#3.2), [I/O Systems](#3.3), and [Statistics and Metrics](#3.4).

## Purpose and Scope

earth2studio is designed as a modular framework that enables researchers and practitioners to:

- Access diverse weather and climate datasets from multiple sources
- Run state-of-the-art AI models for weather prediction and climate analysis  
- Perform statistical analysis and ensemble forecasting
- Deploy workflows with efficient I/O and distributed computing support
- Standardize variables and coordinates across different data sources and models

The framework supports both **prognostic models** (for time-stepping forecasts) and **diagnostic models** (for analysis and post-processing), with a unified interface for model loading, data handling, and workflow execution.

Sources: [pyproject.toml:6-10](), [CHANGELOG.md:1-354]()

## Core Architecture

### System Overview

```mermaid
graph TB
    subgraph "Core Framework"
        CoreAPI["earth2studio Core API<br/>torch, xarray, zarr"]
        Lexicon["Lexicon System<br/>E2STUDIO_VOCAB<br/>Variable Standardization"]
        CoordSys["CoordSystem<br/>OrderedDict Management"]
    end
    
    subgraph "Model Ecosystem"
        AutoModel["AutoModelMixin<br/>load_default_package<br/>load_model"]
        PXModels["Prognostic Models<br/>AIFS, Aurora, GraphCast<br/>SFNO, FuXi, Pangu"]
        DXModels["Diagnostic Models<br/>CorrDiff, CBottle<br/>ClimateNet, AFNO"]
    end
    
    subgraph "Data Layer"
        DataSources["Data Sources<br/>GFS, HRRR, ARCO<br/>WB2ERA5, CDS"]
        IOBackends["I/O Backends<br/>AsyncZarrBackend<br/>NetCDF4Backend"]
    end
    
    subgraph "Analysis Tools"
        Statistics["Statistics<br/>Mean, Variance"]
        Metrics["Metrics<br/>RMSE, CRPS, ACC"]
        Perturbations["Perturbations<br/>SphericalGaussian<br/>BreedVector"]
    end
    
    CoreAPI --> Lexicon
    CoreAPI --> CoordSys
    AutoModel --> PXModels
    AutoModel --> DXModels
    DataSources --> Lexicon
    DataSources --> IOBackends
    PXModels --> Statistics
    DXModels --> Metrics
    Statistics --> IOBackends
```

The architecture consists of four main layers that work together to provide a complete weather and climate modeling platform.

Sources: [pyproject.toml:14-33](), [CHANGELOG.md:42-51](), [CHANGELOG.md:94-102]()

### Component Interaction Flow

```mermaid
graph LR
    subgraph "Data Acquisition"
        AWS_S3["AWS S3<br/>GFS, HRRR, GEFS"]
        GCS["Google Cloud<br/>ARCO, WB2ERA5"] 
        NGC["NVIDIA NGC<br/>Model Registry"]
        CDS["Copernicus CDS"]
    end
    
    subgraph "Data Processing"
        GFS_Source["GFS DataSource<br/>grib parsing"]
        ARCO_Source["ARCO DataSource<br/>zarr access"]
        fetch_data["fetch_data<br/>utility function"]
        prep_data_array["prep_data_array<br/>coordinate prep"]
    end
    
    subgraph "Model Execution"
        load_model["AutoModelMixin.load_model<br/>Package system"]
        px_forward["Prognostic.forward<br/>time integration"]
        dx_forward["Diagnostic.forward<br/>analysis"]
    end
    
    subgraph "Output & Analysis"
        AsyncZarr["AsyncZarrBackend<br/>non-blocking writes"]
        NetCDF4["NetCDF4Backend<br/>scientific data"]
        statistics["Statistics.run<br/>ensemble analysis"]
        metrics["Metrics.run<br/>verification"]
    end
    
    AWS_S3 --> GFS_Source
    GCS --> ARCO_Source
    NGC --> load_model
    CDS --> fetch_data
    
    GFS_Source --> prep_data_array
    ARCO_Source --> prep_data_array
    fetch_data --> prep_data_array
    
    prep_data_array --> px_forward
    prep_data_array --> dx_forward
    load_model --> px_forward
    load_model --> dx_forward
    
    px_forward --> AsyncZarr
    dx_forward --> NetCDF4
    px_forward --> statistics
    dx_forward --> metrics
```

This flow shows how data moves from external sources through the processing pipeline to model execution and analysis output.

Sources: [CHANGELOG.md:42-43](), [CHANGELOG.md:306-307](), [CHANGELOG.md:332-334]()

## Key Components

### Model System

The framework supports two primary model categories:

| Model Type | Purpose | Examples | Key Features |
|------------|---------|----------|--------------|
| **Prognostic** | Time-stepping forecasts | `AIFS`, `Aurora`, `GraphCast`, `SFNO`, `FuXi`, `Pangu` | Auto-regressive, ensemble support |
| **Diagnostic** | Analysis & enhancement | `CorrDiff`, `CBottle`, `ClimateNet`, `AFNO` | Post-processing, super-resolution |

All models implement the `AutoModelMixin` interface with methods:
- `load_default_package()` - Downloads model from registry
- `load_model()` - Instantiates model from package
- `input_coords()` - Returns expected input coordinates
- `output_coords()` - Returns output coordinate mapping

Sources: [CHANGELOG.md:94-102](), [CHANGELOG.md:124-128](), [CHANGELOG.md:332-334]()

### Data Sources

```mermaid
graph TB
    subgraph "Real-time Sources"
        GFS["GFS<br/>NCEP/AWS GRIB"]
        HRRR["HRRR<br/>AWS Zarr"]
        GEFS["GEFS<br/>Ensemble forecasts"]
    end
    
    subgraph "Reanalysis Sources"
        ARCO["ARCO<br/>Google Cloud ERA5"]
        WB2["WB2ERA5<br/>Weather Bench 2"]
        NCAR["NCAR<br/>ERA5 NetCDF"]
    end
    
    subgraph "Climate Sources"
        CDS["CDS<br/>Copernicus Data Store"]
        CMIP6["CMIP6<br/>Climate projections"]
        CBottle_Data["CBottle<br/>Mixture of experts"]
    end
    
    subgraph "Standardization"
        Lexicon_Vocab["E2STUDIO_VOCAB<br/>Variable mapping"]
        CoordSystem["CoordSystem<br/>OrderedDict"]
    end
    
    GFS --> Lexicon_Vocab
    HRRR --> Lexicon_Vocab
    ARCO --> Lexicon_Vocab
    WB2 --> Lexicon_Vocab
    CDS --> Lexicon_Vocab
    
    Lexicon_Vocab --> CoordSystem
```

Each data source implements async fetching with built-in caching and automatic coordinate standardization through the lexicon system.

Sources: [CHANGELOG.md:13-18](), [CHANGELOG.md:241-248](), [CHANGELOG.md:265-270]()

### Storage and I/O

The framework provides multiple I/O backends optimized for different use cases:

| Backend | Use Case | Key Features |
|---------|----------|--------------|
| `AsyncZarrBackend` | Large-scale parallel writes | Non-blocking, thread-safe |
| `ZarrBackend` | Chunked storage | Compression codecs, Zarr 3.0 |
| `NetCDF4Backend` | Scientific data exchange | CF conventions, metadata |

All backends support:
- Coordinate-aware writing with automatic chunking
- Configurable compression and encoding
- Batch and ensemble dimension handling

Sources: [CHANGELOG.md:43-44](), [CHANGELOG.md:54-55](), [CHANGELOG.md:275-278]()

### Package and Model Loading

```mermaid
graph LR
    subgraph "Model Registries"
        NGC_Registry["NGC ModelFileSystem<br/>NVIDIA registry"]
        HuggingFace["HuggingFace Hub<br/>Community models"]
        S3_Storage["S3 Storage<br/>Custom packages"]
        Local_Files["Local Files<br/>Development"]
    end
    
    subgraph "Package System"
        Package_API["Package<br/>open, resolve, get"]
        Cache_System["Local Cache<br/>~/.cache/earth2studio"]
        Progress_Track["Progress<br/>tqdm callbacks"]
    end
    
    subgraph "Model Loading"
        AutoMixin["AutoModelMixin<br/>load_default_package"]
        Model_Init["Model.__init__<br/>framework integration"]
        Optional_Deps["Optional Dependencies<br/>model-specific groups"]
    end
    
    NGC_Registry --> Package_API
    HuggingFace --> Package_API
    S3_Storage --> Package_API
    Local_Files --> Package_API
    
    Package_API --> Cache_System
    Package_API --> Progress_Track
    Package_API --> AutoMixin
    
    AutoMixin --> Model_Init
    AutoMixin --> Optional_Deps
```

The package system enables automatic model downloading with caching and dependency management through optional dependency groups defined in `pyproject.toml`.

Sources: [CHANGELOG.md:270-271](), [CHANGELOG.md:332-334](), [pyproject.toml:58-174]()

## Installation and Dependencies

earth2studio uses a modular dependency system with optional groups for specific functionality:

| Dependency Group | Purpose | Key Packages |
|------------------|---------|--------------|
| Core | Base functionality | `torch`, `xarray`, `zarr`, `fsspec` |
| Model-specific | Individual models | `anemoi-inference`, `microsoft-aurora`, `onnxruntime-gpu` |
| Data | External data sources | `cdsapi`, `eccodes`, `ecmwf-opendata` |
| Analysis | Statistics and metrics | `nvidia-physicsnemo`, `torch-harmonics` |

The framework requires Python 3.11+ and supports both CPU and GPU workflows with automatic PyTorch index selection based on platform.

Sources: [pyproject.toml:12-13](), [pyproject.toml:14-33](), [pyproject.toml:58-174](), [pyproject.toml:219-232]()

## Development and Versioning

earth2studio follows semantic versioning with a comprehensive changelog tracking:
- Model additions and updates
- API changes and improvements  
- Performance optimizations
- Bug fixes and security updates
- Dependency management

The current development version is 0.10.0 with regular releases adding new models, data sources, and capabilities. The framework uses `uv` for package management and `hatch` for building.

Sources: [CHANGELOG.md:9-38](), [pyproject.toml:177-216](), [pyproject.toml:273-278]()

---

