<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/3DObjectReconstruction · page 6 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/README.md](src/README.md)
- [src/nvidia/objectreconstruction/networks/nvbundlesdf.py](src/nvidia/objectreconstruction/networks/nvbundlesdf.py)

</details>



This page provides comprehensive technical documentation for the NVIDIA 3D Object Reconstruction API. It covers the core classes, methods, and interfaces available to developers for integrating and extending the reconstruction pipeline.

The API is organized around the main `NVBundleSDF` orchestration framework and its component processors. For detailed configuration management, see [Configuration Management](#5). For getting started with basic usage, see [Getting Started](#2).

## API Architecture Overview

The API follows a modular design with clear separation between orchestration, AI components, and data handling:

```mermaid
graph TB
    subgraph "Main API Layer"
        NVBundleSDF["NVBundleSDF<br/>(Main Orchestrator)"]
    end
    
    subgraph "AI Component APIs"
        FoundationStereoProcessor["FoundationStereoProcessor<br/>(Stereo Depth Estimation)"]
        Sam2Infer["Sam2Infer<br/>(Object Segmentation)"]
        FeatureMatchingInfer["FeatureMatchingInfer<br/>(Feature Matching)"]
        NerfRunner["NerfRunner<br/>(Neural Rendering)"]
    end
    
    subgraph "Configuration APIs"
        NVBundleSDFConfig["NVBundleSDFConfig<br/>(Main Config Schema)"]
        ComponentConfigs["Component Config Classes<br/>(FoundationStereoConfig, SAM2Config, etc.)"]
    end
    
    subgraph "Data Processing APIs"
        ReconstructionDataLoader["ReconstructionDataLoader<br/>(Multi-modal Data Loading)"]
        UtilityClasses["Utility Classes<br/>(TensorUtils, PoseUtils, etc.)"]
    end
    
    subgraph "External Integrations"
        BundleTrackCPP["my_cpp.Bundler<br/>(C++ Bundle Adjustment)"]
        RomaLibrary["roma_outdoor<br/>(RoMa Feature Matching)"]
    end
    
    NVBundleSDF --> FoundationStereoProcessor
    NVBundleSDF --> Sam2Infer
    NVBundleSDF --> FeatureMatchingInfer
    NVBundleSDF --> NerfRunner
    NVBundleSDF --> NVBundleSDFConfig
    NVBundleSDF --> ReconstructionDataLoader
    NVBundleSDF --> BundleTrackCPP
    FeatureMatchingInfer --> RomaLibrary
    ComponentConfigs --> NVBundleSDFConfig
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:1-1067](), [src/README.md:1-135]()

## Core API Entry Points

The primary API provides three main entry points for different use cases:

| Entry Point | Purpose | Primary Method | Configuration |
|-------------|---------|----------------|---------------|
| **Programmatic API** | Direct class instantiation and method calls | `NVBundleSDF.__init__()` | Config objects |
| **Package Import API** | Simplified imports with default configurations | Module-level functions | YAML files |
| **Command Line API** | Batch processing and automation | `nvidia-3d-reconstruct` | CLI arguments |

### Main Workflow API

```mermaid
sequenceDiagram
    participant Client
    participant NVBundleSDF
    participant Components as "AI Components"
    participant DataLoader as "ReconstructionDataLoader"
    participant BundleTrack as "my_cpp.Bundler"
    
    Client->>NVBundleSDF: "__init__(config_nerf, cfg_bundletrack, roma_config, cfg_texture)"
    NVBundleSDF->>Components: "Initialize processors"
    NVBundleSDF->>DataLoader: "Setup data pipeline"
    
    Client->>NVBundleSDF: "run_track(reader)"
    NVBundleSDF->>BundleTrack: "Process frames sequentially"
    BundleTrack-->>NVBundleSDF: "Camera poses"
    
    Client->>NVBundleSDF: "run_global_sdf(reader)"
    NVBundleSDF->>Components: "Neural surface training"
    Components-->>NVBundleSDF: "3D mesh"
    
    Client->>NVBundleSDF: "run_texture_bake(reader)"
    NVBundleSDF->>Components: "Texture generation"
    Components-->>Client: "Textured 3D asset"
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:151-203](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:206-284]()

## Class Hierarchy and Type System

The API uses a well-defined type system with specific tensor types and data structures:

```mermaid
classDiagram
    class NVBundleSDF {
        +ConfigDict cfg_nerf
        +ConfigDict cfg_bundletrack
        +ConfigDict roma_config
        +Path debug_dir
        +FeatureMatchingInfer roma
        +run_track(reader) void
        +run_global_sdf(reader) void
        +run_texture_bake(reader) void
        +make_frame(color, depth, K, id_str) Frame
        +process_new_frame(frame) void
        +find_corres(frame_pairs) void
    }
    
    class FeatureMatchingInfer {
        +ConfigDict roma_config
        +_process_batch(rgbAs, rgbBs) ndarray
    }
    
    class NerfRunner {
        +ConfigDict cfg_nerf
        +train() void
        +extract_mesh(voxel_size) Mesh
        +load_weights(path) void
    }
    
    class Frame {
        +ImageArray _color
        +DepthMap _depth
        +PoseMatrix _pose_in_model
        +str _id_str
        +int _id
        +MaskArray _fg_mask
        +invalidatePixelsByMask(mask) void
        +countValidPoints() int
    }
    
    NVBundleSDF --> FeatureMatchingInfer
    NVBundleSDF --> NerfRunner
    NVBundleSDF --> Frame
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:63-72](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:151-203]()

## Type Definitions and Precision Management

The API enforces specific tensor types for numerical stability:

```mermaid
graph LR
    subgraph "Tensor Type System"
        FloatTensor["torch.float32<br/>(Default Precision)"]
        ROMATensors["ROMA_TYPES<br/>(rgbAs, rgbBs, warp, certainty)"]
        NumPyArrays["numpy.ndarray<br/>(ImageArray, DepthMap, PoseMatrix)"]
    end
    
    subgraph "Type Utilities"
        TensorUtils["TensorUtils.ensure_tensor_type()"]
        TypeConversion["ensure_tensor_types()"]
        PrecisionMgmt["set_nvbundlesdf_precision()"]
    end
    
    FloatTensor --> ROMATensors
    ROMATensors --> TensorUtils
    TensorUtils --> TypeConversion
    PrecisionMgmt --> FloatTensor
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:74-150](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:102-108]()

## Method Call Patterns

### Frame Processing Pipeline

The core processing follows a consistent pattern across all frame operations:

| Stage | Method | Input Types | Output Types |
|-------|--------|-------------|--------------|
| **Frame Creation** | `make_frame()` | `ImageArray`, `DepthMap`, `np.ndarray` | `Frame` |
| **Frame Processing** | `process_new_frame()` | `Frame` | `void` (side effects) |
| **Correspondence Finding** | `find_corres()` | `List[FramePair]` | `void` (updates internal state) |
| **Bundle Adjustment** | `bundler.optimizeGPU()` | `List[Frame]` | `void` (updates poses) |

### Configuration Management

Configuration objects follow a hierarchical pattern:

```mermaid
graph TD
    NVBundleSDFConfig["NVBundleSDFConfig<br/>(Root Configuration)"]
    
    subgraph "Component Configurations"
        NeRFConfig["NeRFConfig<br/>(cfg_nerf)"]
        BundleTrackConfig["BundleTrackConfig<br/>(cfg_bundletrack)"]
        RomaConfig["RomaConfig<br/>(roma_config)"]
        TextureConfig["TextureConfig<br/>(cfg_texture)"]
    end
    
    subgraph "Sub-configurations"
        CameraConfig["CameraConfig"]
        DepthProcessing["depth_processing"]
        FeatureCorres["feature_corres"]
    end
    
    NVBundleSDFConfig --> NeRFConfig
    NVBundleSDFConfig --> BundleTrackConfig
    NVBundleSDFConfig --> RomaConfig
    NVBundleSDFConfig --> TextureConfig
    BundleTrackConfig --> CameraConfig
    BundleTrackConfig --> DepthProcessing
    BundleTrackConfig --> FeatureCorres
```

**Sources:** [src/README.md:43-50](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:169-203]()

## Error Handling and Status Management

The API uses a consistent error handling pattern with frame status tracking:

| Status | Constant | Meaning | Recovery Action |
|--------|----------|---------|-----------------|
| **SUCCESS** | `Frame.SUCCESS` | Frame processed successfully | Continue pipeline |
| **FAIL** | `Frame.FAIL` | Frame processing failed | `bundler.forgetFrame()` |
| **INSUFFICIENT_POINTS** | Custom validation | Too few valid points | Skip frame |
| **INSUFFICIENT_MATCHES** | Custom validation | Too few correspondences | Try alternative reference |

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:428-431](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:463-467]()

## Memory Management and Resource Cleanup

The API includes explicit memory management for GPU resources:

```mermaid
graph TD
    subgraph "Resource Lifecycle"
        Init["Initialization<br/>set_nvbundlesdf_precision()"]
        Processing["Processing<br/>Tensor operations"]
        Cleanup["Cleanup<br/>del bundler, torch.cuda.empty_cache()"]
    end
    
    subgraph "Memory Patterns"
        TensorCreation["ensure_tensor_type()"]
        BatchProcessing["_process_batch()"]
        ExplicitDeletion["del corres, array_imgs"]
    end
    
    Init --> Processing
    Processing --> Cleanup
    TensorCreation --> BatchProcessing
    BatchProcessing --> ExplicitDeletion
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:281-284](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:610-611]()

## API Subsections

For detailed documentation of specific API components:

- **[Core Classes](#6.1)** - Complete reference for `NVBundleSDF`, component processors, and utility classes
- **[Data Loaders](#6.2)** - Technical documentation for `ReconstructionDataLoader` and data handling utilities

Each subsection provides comprehensive method signatures, parameter descriptions, return types, and usage examples for the respective API components.

---

