<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/3DObjectReconstruction · page 4 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/README.md](src/README.md)
- [src/nvidia/objectreconstruction/networks/nvbundlesdf.py](src/nvidia/objectreconstruction/networks/nvbundlesdf.py)

</details>



This document provides a comprehensive technical overview of the NVIDIA 3D Object Reconstruction system's software architecture. It covers the core framework design, component integration patterns, data flow architecture, and deployment infrastructure. For information about the AI algorithms and reconstruction pipeline details, see [Core Pipeline](#3). For configuration parameters and schemas, see [Configuration Management](#5).

## Architecture Overview

The system follows a modular architecture centered around the `NVBundleSDF` orchestration framework, which coordinates multiple AI components through a unified pipeline. The architecture supports both interactive (Jupyter notebook) and batch processing (CLI) workflows.

### High-Level System Structure

```mermaid
graph TB
    subgraph "User Interfaces"
        NOTEBOOK["3d_object_reconstruction_demo.ipynb"]
        CLI["nvidia-3d-reconstruct CLI"]
    end
    
    subgraph "Core Framework Layer"
        NVBUNDLE["NVBundleSDF<br/>(Main Orchestrator)"]
        DATALOADER["ReconstructionDataLoader"]
        CONFIG["Configuration Schema System"]
    end
    
    subgraph "AI Component Layer"
        FS["FoundationStereoProcessor"]
        SAM2["Sam2Infer"]
        ROMA["FeatureMatchingInfer"]
        NERF["NerfRunner"]
    end
    
    subgraph "Infrastructure Layer"
        BUNDLETRACK["my_cpp (BundleTrack C++)"]
        PYTORCH["PyTorch Ecosystem"]
        DOCKER["Docker Deployment"]
    end
    
    NOTEBOOK --> NVBUNDLE
    CLI --> NVBUNDLE
    NVBUNDLE --> DATALOADER
    NVBUNDLE --> CONFIG
    NVBUNDLE --> FS
    NVBUNDLE --> SAM2
    NVBUNDLE --> ROMA
    NVBUNDLE --> NERF
    NVBUNDLE --> BUNDLETRACK
    FS --> PYTORCH
    SAM2 --> PYTORCH
    ROMA --> PYTORCH
    NERF --> PYTORCH
    DOCKER --> NOTEBOOK
    DOCKER --> CLI
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:1-1067](), [src/README.md:1-135]()

## Core Framework Components

### NVBundleSDF Orchestrator

The `NVBundleSDF` class serves as the primary orchestration framework, managing the complete reconstruction pipeline through three main phases: tracking, global SDF optimization, and texture baking.

```mermaid
classDiagram
    class NVBundleSDF {
        +cfg_nerf: ConfigDict
        +cfg_bundletrack: ConfigDict
        +roma_config: ConfigDict
        +cfg_texture: ConfigDict
        +bundler: my_cpp.Bundler
        +roma: FeatureMatchingInfer
        +K: ndarray
        +run_track(reader)
        +run_global_sdf(reader)
        +run_texture_bake(reader)
        +run_bundletrack(color, depth, K, id_str, mask)
        +find_corres(frame_pairs)
        +make_frame(color, depth, K, id_str)
    }
    
    class FeatureMatchingInfer {
        +roma_config: ConfigDict
        +_process_batch(rgbAs, rgbBs)
    }
    
    class NerfRunner {
        +config: ConfigDict
        +train()
        +extract_mesh(voxel_size, isolevel)
        +load_weights(path)
    }
    
    NVBundleSDF --> FeatureMatchingInfer
    NVBundleSDF --> NerfRunner
    NVBundleSDF --> "my_cpp.Bundler"
```

The framework initializes with precision control for numerical stability in pose tracking operations:

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:151-203](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:74-99]()

### Pipeline Execution Phases

The `NVBundleSDF` orchestrator executes three distinct phases, each with specific responsibilities:

```mermaid
sequenceDiagram
    participant Reader as "DataLoader"
    participant NVB as "NVBundleSDF"
    participant Bundler as "my_cpp.Bundler"
    participant Roma as "FeatureMatchingInfer"
    participant Nerf as "NerfRunner"
    
    Note over NVB: Phase 1: Tracking
    loop "For each frame"
        Reader->>NVB: get_color(), get_depth(), get_mask()
        NVB->>NVB: make_frame()
        NVB->>Roma: find_corres()
        NVB->>Bundler: process_new_frame()
        Bundler->>NVB: pose optimization
    end
    
    Note over NVB: Phase 2: Global SDF
    NVB->>NVB: load keyframes.yml
    NVB->>Nerf: initialize with poses
    Nerf->>Nerf: train()
    Nerf->>NVB: extract_mesh()
    
    Note over NVB: Phase 3: Texture Baking
    NVB->>Nerf: load_weights()
    NVB->>NVB: build_texture_from_images()
    NVB->>NVB: export textured mesh
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:206-283](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:638-757](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:759-896]()

## AI Component Integration

### Component Processor Architecture

Each AI component is wrapped in a processor class that provides a standardized interface for the `NVBundleSDF` framework:

| Component | Class | Primary Function | Key Methods |
|-----------|--------|------------------|-------------|
| Stereo Depth | `FoundationStereoProcessor` | Sub-pixel depth estimation | `run()` |
| Segmentation | `Sam2Infer` | Object mask generation | `run(rgb_path, mask_path)` |
| Feature Matching | `FeatureMatchingInfer` | Correspondence finding | `_process_batch()` |
| Neural SDF | `NerfRunner` | 3D reconstruction | `train()`, `extract_mesh()` |

**Sources:** [src/README.md:35-41](), [src/README.md:58-82]()

### Feature Matching Integration

The `FeatureMatchingInfer` component integrates RoMa feature matching with the BundleTrack framework:

```mermaid
graph LR
    subgraph "Feature Matching Pipeline"
        PAIRS["frame_pairs"]
        PREPROCESS["getProcessedImagePairs()"]
        ROMA["roma._process_batch()"]
        TRANSFORM["transform_pts()"]
        RANSAC["runRansacMultiPairGPU()"]
    end
    
    PAIRS --> PREPROCESS
    PREPROCESS --> ROMA
    ROMA --> TRANSFORM
    TRANSFORM --> RANSAC
    
    subgraph "Data Flow"
        IMGS["array_imgs<br/>(uint8)"]
        TENSORS["rgbAs, rgbBs<br/>(float32)"]
        CORRES["correspondences<br/>(uint16)"]
    end
    
    PREPROCESS --> IMGS
    IMGS --> TENSORS
    ROMA --> CORRES
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:543-637](), [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:568-625]()

## Data Flow Architecture

### Multi-Scale Data Processing

The system processes data at multiple scales through specialized loaders:

```mermaid
graph TB
    subgraph "Input Data Structure"
        LEFT["left/ (RGB images)"]
        RIGHT["right/ (RGB images)"]
        DEPTH["depth/ (depth maps)"]
        MASKS["masks/ (segmentation)"]
        POSES["poses/ (camera poses)"]
    end
    
    subgraph "ReconstructionDataLoader"
        TRACK_LOADER["track_dataset<br/>(Pose Estimation Scale)"]
        NERF_LOADER["nerf_dataset<br/>(Training Scale)"]
        TEXTURE_LOADER["texture_dataset<br/>(Asset Generation Scale)"]
    end
    
    subgraph "Processing Stages"
        BUNDLETRACK["BundleTrack Processing"]
        SDF_TRAIN["SDF Model Training"]
        TEXTURE_BAKE["Texture Baking"]
    end
    
    LEFT --> TRACK_LOADER
    RIGHT --> TRACK_LOADER
    DEPTH --> TRACK_LOADER
    MASKS --> TRACK_LOADER
    
    LEFT --> NERF_LOADER
    DEPTH --> NERF_LOADER
    MASKS --> NERF_LOADER
    
    LEFT --> TEXTURE_LOADER
    POSES --> TEXTURE_LOADER
    
    TRACK_LOADER --> BUNDLETRACK
    NERF_LOADER --> SDF_TRAIN
    TEXTURE_LOADER --> TEXTURE_BAKE
```

**Sources:** [src/README.md:1-135]() (inferred from data structure descriptions)

### Frame Processing Pipeline

Individual frames flow through a structured processing pipeline within the BundleTrack system:

```mermaid
flowchart TD
    INPUT["Frame Input<br/>(color, depth, mask)"] --> MAKE_FRAME["make_frame()"]
    MAKE_FRAME --> VALIDATE["Frame Validation"]
    VALIDATE --> FIRST_FRAME{"First Frame?"}
    
    FIRST_FRAME -->|Yes| SET_KEYFRAME["setNewInitCoordinate()<br/>Add as keyframe"]
    FIRST_FRAME -->|No| FIND_REF["Find Reference Frame"]
    
    FIND_REF --> FIND_CORRES["find_corres()"]
    FIND_CORRES --> CHECK_MATCHES{"Sufficient Matches?"}
    
    CHECK_MATCHES -->|No| TRY_ALT["Try Alternative<br/>Reference Frames"]
    CHECK_MATCHES -->|Yes| PROCRUSTES["Procrustes Alignment<br/>Update Pose"]
    
    TRY_ALT --> CHECK_MATCHES
    PROCRUSTES --> BA_SELECT["selectKeyFramesForBA()"]
    BA_SELECT --> OPTIMIZE["optimizeGPU()"]
    OPTIMIZE --> ADD_KEYFRAME["checkAndAddKeyframe()"]
    
    SET_KEYFRAME --> SAVE["Save Results"]
    ADD_KEYFRAME --> SAVE
```

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:385-541]()

## Configuration Management Architecture

### Hierarchical Configuration System

The system uses a hierarchical configuration architecture with specialized schema classes:

```mermaid
classDiagram
    class NVBundleSDFConfig {
        +nerf: NeRFConfig
        +bundletrack: BundleTrackConfig
        +foundation_stereo: FoundationStereoConfig
        +sam2: SAM2Config
        +roma: RoMaConfig
        +texture: TextureBakeConfig
    }
    
    class NeRFConfig {
        +n_step: int
        +save_dir: str
        +mesh_resolution: float
        +translation: List[float]
        +sc_factor: float
    }
    
    class BundleTrackConfig {
        +debug_dir: str
        +erode_mask: int
        +depth_processing: Dict
        +feature_corres: Dict
        +bundle: Dict
    }
    
    class SAM2Config {
        +bbox: List[int]
        +checkpoint_path: str
        +model_cfg: str
    }
    
    NVBundleSDFConfig --> NeRFConfig
    NVBundleSDFConfig --> BundleTrackConfig
    NVBundleSDFConfig --> SAM2Config
```

**Sources:** [src/README.md:43-50](), [src/README.md:87-100]()

### Configuration Loading and Validation

The `NVBundleSDF` framework loads and validates configuration through YAML processing:

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:209-224]()

## Deployment Architecture

### Docker-Based Infrastructure

The system deploys through a containerized architecture supporting both interactive and batch processing modes:

```mermaid
graph TB
    subgraph "Deployment Infrastructure"
        DEPLOY["deploy.sh<br/>(Setup Script)"]
        COMPOSE["docker-compose.yml<br/>(Container Orchestration)"]
        DOCKERFILE["Dockerfile<br/>(GPU-enabled Image)"]
    end
    
    subgraph "Container Services"
        JUPYTER["Jupyter Service<br/>(Interactive Mode)"]
        CLI_SERVICE["CLI Service<br/>(Batch Processing)"]
    end
    
    subgraph "Runtime Environment"
        CUDA["NVIDIA CUDA Runtime"]
        PYTORCH["PyTorch + Dependencies"]
        CPP_LIBS["C++ Libraries<br/>(BundleTrack)"]
    end
    
    DEPLOY --> COMPOSE
    COMPOSE --> DOCKERFILE
    DOCKERFILE --> JUPYTER
    DOCKERFILE --> CLI_SERVICE
    
    JUPYTER --> CUDA
    CLI_SERVICE --> CUDA
    CUDA --> PYTORCH
    PYTORCH --> CPP_LIBS
```

The deployment requires specific hardware requirements and system dependencies as defined in the project specifications.

**Sources:** [src/README.md:120-126]()

### Runtime Component Integration

At runtime, the system integrates multiple software components through standardized interfaces:

| Layer | Components | Integration Method |
|-------|------------|-------------------|
| Application | Jupyter notebooks, CLI tools | Direct Python imports |
| Framework | `NVBundleSDF`, data loaders | Configuration-driven initialization |
| AI Models | PyTorch models, pre-trained weights | Dynamic loading and inference |
| C++ Libraries | BundleTrack (`my_cpp`) | Python bindings |
| System | CUDA runtime, Docker | Environment-based configuration |

**Sources:** [src/nvidia/objectreconstruction/networks/nvbundlesdf.py:50-51](), [src/README.md:104-110]()

---

