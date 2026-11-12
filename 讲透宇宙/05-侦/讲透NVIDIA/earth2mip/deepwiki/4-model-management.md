<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2mip · page 4 Model Management · fetched 2026-10-26 -->

# Model Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [Makefile](Makefile)
- [README.md](README.md)
- [earth2mip/_cli_utils.py](earth2mip/_cli_utils.py)
- [earth2mip/_config.py](earth2mip/_config.py)
- [earth2mip/model_registry.py](earth2mip/model_registry.py)
- [earth2mip/score_ensemble_outputs.py](earth2mip/score_ensemble_outputs.py)
- [earth2mip/weather_events.py](earth2mip/weather_events.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



This document covers the model management system in Earth-2 MIP, including model registration, package management, and loading interfaces. The system provides a unified way to discover, download, and instantiate AI weather models from various sources including NGC (NVIDIA GPU Cloud), local storage, and cloud storage.

For information about using loaded models for inference, see [Inference and Forecasting](#6). For details about the TimeLoop interface that models implement, see [Model Interface (TimeLoop)](#3.2).

## Model Registry System

The model registry provides centralized management of AI weather model packages through the `ModelRegistry` class. It supports both local filesystem and cloud storage backends, with automatic downloading and caching of model packages.

### Registry Architecture

```mermaid
graph TB
    subgraph "Model Registry Core"
        Registry[ModelRegistry]
        Package[Package]
        Metadata[metadata.json]
    end
    
    subgraph "Storage Backends"
        LocalFS["Local Filesystem"]
        S3["S3 Storage"]
        NGC["NGC Downloads"]
    end
    
    subgraph "Built-in Packages"
        FCNPkg["FCNPackage"]
        DLWPPkg["DLWPPackage"] 
        PanguPkg["PanguPackage"]
        GraphCast["GraphCast GCS"]
    end
    
    subgraph "Entry Points"
        EntryPoints["pyproject.toml entries"]
        NetworksLoad["networks.get_model()"]
    end
    
    Registry --> Package
    Package --> Metadata
    Registry --> LocalFS
    Registry --> S3
    Registry --> NGC
    
    Registry --> FCNPkg
    Registry --> DLWPPkg
    Registry --> PanguPkg
    Registry --> GraphCast
    
    EntryPoints --> NetworksLoad
    NetworksLoad --> Registry
    
    FCNPkg --> NGC
    DLWPPkg --> NGC
    PanguPkg --> NGC
```

Sources: [earth2mip/model_registry.py:224-285](), [earth2mip/_config.py:28-34]()

### Registry Configuration

The model registry location is configured through the `MODEL_REGISTRY` setting, which defaults to `~/.cache/earth2mip/models`. The registry supports both local paths and S3 URLs.

```mermaid
graph LR
    subgraph "Configuration Sources"
        EnvVar[".env file"]
        Default["~/.cache/earth2mip/models"]
        Settings["_config.Settings"]
    end
    
    subgraph "Registry Path Resolution"
        ModelRegistry["ModelRegistry(path)"]
        LocalCache["LOCAL_CACHE"]
        ModelRegPath["MODEL_REGISTRY"]
    end
    
    EnvVar --> Settings
    Default --> Settings
    Settings --> LocalCache
    Settings --> ModelRegPath
    ModelRegPath --> ModelRegistry
```

Sources: [earth2mip/_config.py:28-34](), [earth2mip/_config.py:51]()

## Package Management

Each model is organized as a package with a standardized directory structure containing model weights, metadata, and normalization statistics.

### Package Structure

The standard package layout includes:

| File | Purpose |
|------|---------|
| `metadata.json` | Model configuration and schema |
| `weights.tar` | Model checkpoint with `model_state` key |
| `global_means.npy` | Normalization means (optional) |
| `global_stds.npy` | Normalization standard deviations (optional) |
| `about.txt` | Optional information and source path |

### Package Types

```mermaid
graph TB
    subgraph "Package Types"
        GenericPkg[Package]
        FCNPkg[FCNPackage]
        DLWPPkg[DLWPPackage] 
        PanguPkg[PanguPackage]
        FCNv2Pkg[FCNv2Package]
        DiagPkg[NGCDiagnosticPackage]
    end
    
    subgraph "Download Sources"
        NGC["NGC API"]
        ECMWF["ECMWF Repository"]
        GCS["Google Cloud Storage"]
    end
    
    subgraph "Operations"
        Download["download_ngc_package()"]
        GetFile["package.get(path)"]
        LoadMeta["package.metadata()"]
    end
    
    FCNPkg --> NGC
    DLWPPkg --> NGC
    FCNv2Pkg --> NGC
    DiagPkg --> NGC
    PanguPkg --> ECMWF
    
    FCNPkg --> Download
    DLWPPkg --> Download
    FCNv2Pkg --> Download
    
    GenericPkg --> GetFile
    GenericPkg --> LoadMeta
```

Sources: [earth2mip/model_registry.py:98-121](), [earth2mip/model_registry.py:141-181](), [earth2mip/model_registry.py:183-222]()

### Built-in Package Handlers

The registry includes specialized package handlers for different model sources:

- **NGC Packages**: `FCNPackage`, `DLWPPackage`, `FCNv2Package` download from NVIDIA GPU Cloud
- **Pangu Models**: `PanguPackage` downloads ONNX files from ECMWF repository  
- **GraphCast**: Direct access to Google Cloud Storage buckets
- **Diagnostic Models**: `NGCDiagnosticPackage` for specialized diagnostic models

## Model Loading Interface

The primary interface for loading models is through the `networks.get_model()` function, which resolves model names through the registry and entry point system.

### Entry Point System

Model loading is configured through Python entry points defined in `pyproject.toml`:

```mermaid
graph LR
    subgraph "Entry Points Definition"
        PyProject["pyproject.toml"]
        EntryPoints["earth2mip.networks"]
    end
    
    subgraph "Model Mappings"
        FCNEntry["fcn → earth2mip.networks.fcn:load"]
        DLWPEntry["dlwp → earth2mip.networks.dlwp:load"] 
        PanguEntry["pangu → earth2mip.networks.pangu:load"]
        GraphEntry["graphcast → earth2mip.networks.graphcast:load_time_loop"]
    end
    
    subgraph "Loading Functions"
        FCNLoad["fcn.load()"]
        DLWPLoad["dlwp.load()"]
        PanguLoad["pangu.load()"]
        GraphLoad["graphcast.load_time_loop()"]
    end
    
    PyProject --> EntryPoints
    EntryPoints --> FCNEntry
    EntryPoints --> DLWPEntry
    EntryPoints --> PanguEntry
    EntryPoints --> GraphEntry
    
    FCNEntry --> FCNLoad
    DLWPEntry --> DLWPLoad
    PanguEntry --> PanguLoad
    GraphEntry --> GraphLoad
```

Sources: [pyproject.toml:91-101]()

### Model Loading Flow

```mermaid
sequenceDiagram
    participant User
    participant GetModel["get_model()"]
    participant Registry["ModelRegistry"]
    participant Package["Package"]
    participant Loader["Model Loader"]
    participant TimeLoop["TimeLoop"]
    
    User->>GetModel: get_model("e2mip://pangu")
    GetModel->>Registry: get_model("e2mip://pangu")
    Registry->>Registry: get_builtin_model()
    Registry->>Package: PanguPackage()
    Package->>Package: download if needed
    Package-->>Registry: Package instance
    Registry-->>GetModel: Package
    GetModel->>Package: metadata()
    Package-->>GetModel: Model schema
    GetModel->>Loader: load via entry point
    Loader->>Package: get("pangu_weather_6.onnx")
    Package-->>Loader: local file path
    Loader->>TimeLoop: instantiate model
    TimeLoop-->>Loader: TimeLoop instance
    Loader-->>GetModel: TimeLoop
    GetModel-->>User: TimeLoop
```

Sources: [earth2mip/model_registry.py:233-237](), [earth2mip/model_registry.py:239-262](), [earth2mip/_cli_utils.py:71-78]()

## Supported Models

The system supports multiple AI weather models with different architectures and capabilities:

### Model Catalog

| Model ID | Architecture | Type | Source | Entry Point |
|----------|-------------|------|--------|-------------|
| `fcn` | Adaptive Fourier Neural Operator | Global Weather | NGC | `earth2mip.networks.fcn:load` |
| `dlwp` | Convolutional Encoder-Decoder | Global Weather | NGC | `earth2mip.networks.dlwp:load` |
| `pangu` | Vision Transformer (Hierarchical) | Global Weather | ECMWF | `earth2mip.networks.pangu:load` |
| `pangu_6` | Vision Transformer (6hr) | Global Weather | ECMWF | `earth2mip.networks.pangu:load_6` |
| `pangu_24` | Vision Transformer (24hr) | Global Weather | ECMWF | `earth2mip.networks.pangu:load_24` |
| `fcnv2_sm` | Spherical Harmonics AFNO | Global Weather | NGC | `earth2mip.networks.fcnv2_sm:load` |
| `graphcast` | Graph Neural Network | Global Weather | GCS | `earth2mip.networks.graphcast:load_time_loop` |

### Model Dependencies

Some models require additional dependencies specified as optional extras:

- **Pangu models**: Require `onnxruntime-gpu>=1.15.1`
- **GraphCast models**: Require JAX/Flax stack with specific versions

```mermaid
graph TB
    subgraph "Model Dependencies"
        Pangu["Pangu Models"]
        GraphCast["GraphCast Models"]
        PyTorchModels["PyTorch Models"]
    end
    
    subgraph "Runtime Dependencies"
        ONNX["onnxruntime-gpu"]
        JAX["jax==0.4.16"]
        Flax["flax==0.7.3"]
        PyTorch["torch>=1.13"]
    end
    
    Pangu --> ONNX
    GraphCast --> JAX
    GraphCast --> Flax
    PyTorchModels --> PyTorch
```

Sources: [pyproject.toml:62-71](), [README.md:116-129]()

## Configuration and Metadata

### Model Metadata Schema

Each model package includes a `metadata.json` file conforming to the `earth2mip.schema.Model` schema:

```mermaid
graph TB
    subgraph "Metadata Structure"
        Schema["schema.Model"]
        Architecture["architecture"]
        History["n_history"] 
        Grid["grid"]
        Channels["in_channels/out_channels"]
        Entrypoint["entrypoint"]
    end
    
    subgraph "Example Values"
        ArchEx["'sfno_73ch'"]
        HistEx["0"]
        GridEx["'721x1440'"]
        ChanEx["[0, 1, ...]"]
        EntryEx["{'name': 'earth2mip.networks.fcn:load'}"]
    end
    
    Schema --> Architecture
    Schema --> History
    Schema --> Grid
    Schema --> Channels
    Schema --> Entrypoint
    
    Architecture --> ArchEx
    History --> HistEx
    Grid --> GridEx
    Channels --> ChanEx
    Entrypoint --> EntryEx
```

Sources: [earth2mip/model_registry.py:43-57](), [earth2mip/model_registry.py:115-119]()

### CLI Integration

The model management system integrates with CLI tools through utility functions that parse model arguments and metadata:

- `add_model_args()`: Adds model-related command line arguments
- `model_from_args()`: Loads models from parsed command line arguments
- Supports custom metadata file override via `--model-metadata`

Sources: [earth2mip/_cli_utils.py:58-78]()

---

