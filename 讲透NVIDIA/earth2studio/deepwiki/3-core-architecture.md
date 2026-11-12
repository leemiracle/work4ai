<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2studio · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [docs/modules/datasources.rst](docs/modules/datasources.rst)
- [earth2studio/data/__init__.py](earth2studio/data/__init__.py)
- [earth2studio/lexicon/__init__.py](earth2studio/lexicon/__init__.py)
- [earth2studio/lexicon/base.py](earth2studio/lexicon/base.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This page describes the high-level architecture of earth2studio, focusing on the core framework design, component interactions, and key abstractions that enable weather and climate AI workflows. For specific information about data sources, see [Data Sources](#3.1). For details about individual models, see [Models](#3.2). For I/O system specifics, see [I/O Systems](#3.3).

## Design Principles

Earth2studio follows a modular, protocol-based architecture designed around several key principles:

- **Standardized Interfaces**: Common protocols for data sources, models, and I/O backends enable interoperability
- **Asynchronous Operations**: Built-in support for async data fetching and non-blocking I/O operations
- **Auto-loading and Caching**: Intelligent model package management with local caching for performance
- **Variable Standardization**: Unified lexicon system for mapping variables across different data sources
- **Flexible Dependencies**: Optional dependency groups allow minimal installations or full feature sets

The framework is built on a foundation of scientific Python libraries including PyTorch, Xarray, Zarr, and fsspec, providing both CPU and GPU execution capabilities.

**Sources:** [pyproject.toml:1-50](), [CHANGELOG.md:1-50]()

## Core Components Architecture

The earth2studio architecture consists of four primary layers that work together to provide end-to-end weather and climate AI workflows:

```mermaid
graph TB
    subgraph "Application Layer"
        Workflows["Workflows & Examples"]
        Statistics["Statistics & Metrics"]
        Perturbations["Perturbation Methods"]
    end
    
    subgraph "Model Layer"
        PX["Prognostic Models (PX)<br/>AIFS, Aurora, GraphCast<br/>FuXi, Pangu, SFNO"]
        DX["Diagnostic Models (DX)<br/>CorrDiff, CBottle<br/>ClimateNet, AFNO"]
        AutoModel["AutoModelMixin<br/>load_default_package<br/>load_model"]
    end
    
    subgraph "Data Layer"
        DataSources["DataSource Protocol<br/>GFS, HRRR, ARCO<br/>WB2ERA5, CDS"]
        Lexicon["Lexicon System<br/>E2STUDIO_VOCAB<br/>Variable Mapping"]
        CoordSystem["CoordSystem<br/>OrderedDict"]
    end
    
    subgraph "Infrastructure Layer"
        IOBackends["I/O Backends<br/>AsyncZarrBackend<br/>NetCDF4Backend"]
        Package["Package System<br/>NGC, HuggingFace<br/>S3, Local"]
        Utils["Utilities<br/>fetch_data<br/>prep_data_array"]
    end
    
    Workflows --> PX
    Workflows --> DX
    Statistics --> CoordSystem
    
    PX --> AutoModel
    DX --> AutoModel
    AutoModel --> Package
    
    PX --> DataSources
    DX --> DataSources
    DataSources --> Lexicon
    DataSources --> CoordSystem
    
    DataSources --> IOBackends
    PX --> IOBackends
    DX --> IOBackends
    
    IOBackends --> Utils
    Package --> Utils
```

**Sources:** [earth2studio/data/__init__.py:17-41](), [pyproject.toml:58-174]()

## Data Flow Architecture

Data flows through earth2studio following a standardized pipeline from external sources through processing to model execution and output storage:

```mermaid
graph LR
    subgraph "External Sources"
        AWS["AWS S3<br/>GFS, HRRR, GEFS"]
        GCS["Google Cloud<br/>ARCO, WB2ERA5"]  
        CDS["Copernicus CDS"]
        NGC["NVIDIA NGC<br/>Model Registry"]
    end
    
    subgraph "Data Acquisition"
        GFS["GFS DataSource"]
        HRRR["HRRR DataSource"] 
        ARCO["ARCO DataSource"]
        WB2["WB2ERA5 DataSource"]
    end
    
    subgraph "Variable Standardization"
        GFSLex["GFSLexicon"]
        HRRRLex["HRRRLexicon"]
        ARCOLex["ARCOLexicon"] 
        WB2Lex["WB2Lexicon"]
        E2Vocab["E2STUDIO_VOCAB"]
    end
    
    subgraph "Coordinate Processing"
        CoordSys["CoordSystem"]
        PrepData["prep_data_array"]
        FetchData["fetch_data"]
    end
    
    subgraph "Model Execution"
        AutoLoad["AutoModelMixin"]
        Models["Prognostic/Diagnostic<br/>Models"]
    end
    
    subgraph "Output Storage"
        AsyncZarr["AsyncZarrBackend"]
        NetCDF["NetCDF4Backend"]
    end
    
    AWS --> GFS
    GCS --> ARCO
    CDS --> WB2
    
    GFS --> GFSLex
    HRRR --> HRRRLex
    ARCO --> ARCOLex
    WB2 --> WB2Lex
    
    GFSLex --> E2Vocab
    HRRRLex --> E2Vocab
    ARCOLex --> E2Vocab
    WB2Lex --> E2Vocab
    
    E2Vocab --> CoordSys
    CoordSys --> PrepData
    PrepData --> FetchData
    
    FetchData --> Models
    NGC --> AutoLoad
    AutoLoad --> Models
    
    Models --> AsyncZarr
    Models --> NetCDF
```

**Sources:** [earth2studio/lexicon/base.py:28-200](), [earth2studio/lexicon/__init__.py:17-29]()

## Model Management Architecture

Earth2studio provides a sophisticated auto-loading system for managing AI models from various sources with local caching and dependency management:

```mermaid
graph TB
    subgraph "Model Sources"
        NGC["NGC ModelFileSystem<br/>NVIDIA Registry"]
        HF["HuggingFace Hub"]
        S3["S3 Storage"] 
        Local["Local Files"]
    end
    
    subgraph "Package System"
        Package["Package Interface<br/>open, resolve, get"]
        Cache["Local Cache<br/>~/.cache/earth2studio"]
        Progress["Progress Tracking<br/>tqdm callbacks"]
    end
    
    subgraph "Auto Loading"
        AutoMixin["AutoModelMixin"]
        LoadDefault["load_default_package"]
        LoadModel["load_model"]
    end
    
    subgraph "Model Types"
        PyTorch["PyTorch Models<br/>torch.nn.Module"]
        JAX["JAX Models<br/>GraphCast"]
        ONNX["ONNX Models<br/>FuXi, Pangu"]
    end
    
    subgraph "Optional Dependencies"
        Aurora["aurora<br/>microsoft-aurora"]
        AIFS["aifs<br/>anemoi-*"]
        SFNO["sfno<br/>makani"]
        GraphCast["graphcast<br/>dm-haiku, jax"]
    end
    
    NGC --> Package
    HF --> Package
    S3 --> Package
    Local --> Package
    
    Package --> Cache
    Package --> Progress
    Cache --> AutoMixin
    
    AutoMixin --> LoadDefault
    AutoMixin --> LoadModel
    
    LoadModel --> PyTorch
    LoadModel --> JAX  
    LoadModel --> ONNX
    
    PyTorch --> Aurora
    JAX --> GraphCast
    ONNX --> SFNO
```

**Sources:** [pyproject.toml:74-174](), [CHANGELOG.md:120-130]()

## Coordinate and Variable Systems

The framework uses a standardized coordinate system and lexicon for managing spatial, temporal, and ensemble dimensions across different data sources and models:

| Component | Purpose | Key Classes |
|-----------|---------|-------------|
| `CoordSystem` | Ordered dictionary of coordinate arrays | `OrderedDict` interface |
| `E2STUDIO_VOCAB` | Standardized variable vocabulary | 200+ meteorological variables |
| Lexicon Classes | Data source-specific variable mapping | `GFSLexicon`, `ARCOLexicon`, etc. |
| Coordinate Arrays | Spatial/temporal coordinates | `lat`, `lon`, `time`, `level` |
| Batch Dimensions | Ensemble and sample handling | `batch`, `ensemble`, `member` |

The lexicon system enables seamless integration between different data sources by providing standardized variable names and units. Each data source implements its own lexicon that maps native variable names to the standardized `E2STUDIO_VOCAB`.

**Sources:** [earth2studio/lexicon/base.py:20-30](), [earth2studio/lexicon/base.py:28-200]()

## I/O and Storage Systems

Earth2studio provides multiple I/O backends optimized for different use cases, with emphasis on asynchronous operations for performance:

```mermaid
graph TB
    subgraph "I/O Backends"
        AsyncZarr["AsyncZarrBackend<br/>Non-blocking writes<br/>Thread pool execution"]
        SyncZarr["ZarrBackend<br/>Synchronous writes<br/>Chunked storage"]
        NetCDF["NetCDF4Backend<br/>Scientific data<br/>CF conventions"]
    end
    
    subgraph "Storage Features"
        Compression["Compression Codecs<br/>zarr_codecs parameter"]
        Chunking["Chunking Strategy<br/>lead_time chunks = 1"]
        Async["Async Operations<br/>Per-thread event loops"]
    end
    
    subgraph "Coordinate Handling"
        TimeCoord["Time Coordinates<br/>datetime64, timedelta"]
        SpatialCoord["Spatial Coordinates<br/>lat, lon, level"]
        BatchCoord["Batch Coordinates<br/>ensemble, member"]
    end
    
    subgraph "Data Formats"
        Zarr3["Zarr 3.0 Support<br/>Datetime as int64"]
        NetCDF4["NetCDF4 Format<br/>Proleptic gregorian"]
        XArray["Xarray Integration<br/>DataArray, Dataset"]
    end
    
    AsyncZarr --> Compression
    SyncZarr --> Chunking
    NetCDF --> Async
    
    Compression --> TimeCoord
    Chunking --> SpatialCoord
    Async --> BatchCoord
    
    TimeCoord --> Zarr3
    SpatialCoord --> NetCDF4
    BatchCoord --> XArray
```

The I/O system is designed for high-performance parallel workflows with non-blocking writes and intelligent caching. The `AsyncZarrBackend` enables concurrent model execution and data writing, critical for large-scale ensemble forecasting.

**Sources:** [CHANGELOG.md:43-70](), [CHANGELOG.md:220-230]()

---

