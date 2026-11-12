<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/3DObjectReconstruction · page 3 Core Pipeline · fetched 2026-10-26 -->

# Core Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [data/docs/pipeline_overview.png](data/docs/pipeline_overview.png)
- [notebooks/3d_object_reconstruction_demo.ipynb](notebooks/3d_object_reconstruction_demo.ipynb)

</details>



This document provides a comprehensive technical overview of the 3D Object Reconstruction pipeline architecture, including its AI components, data flow, and processing stages. The pipeline orchestrates multiple state-of-the-art models to transform stereo video input into production-ready 3D textured assets.

For detailed configuration parameters and schemas, see [Configuration Management](#5). For API reference and class documentation, see [API Reference](#6).

## Pipeline Architecture Overview

The core pipeline integrates four primary AI models through a multi-stage processing workflow. The `NVBundleSDF` class serves as the main orchestrator, coordinating data flow between processing stages and managing the reconstruction pipeline.

```mermaid
graph TB
    subgraph "Input Processing"
        StereoInput["Stereo Video Input<br/>left/ + right/"]
        UserBBox["User Bounding Box<br/>Interactive Selection"]
    end
    
    subgraph "AI Processing Components"
        FoundationStereo["FoundationStereoProcessor<br/>run_depth_estimation()"]
        SAM2["Sam2Infer<br/>run_mask_extraction()"]
        RoMa["FeatureMatchingInfer<br/>RoMa Feature Matching"]
    end
    
    subgraph "3D Reconstruction Pipeline"
        NVBundle["NVBundleSDF<br/>Main Orchestrator"]
        BundleTrack["run_track()<br/>Pose Estimation"]
        NeRFTraining["run_global_sdf()<br/>Neural SDF Training"]
        TextureBake["run_texture_bake()<br/>Asset Generation"]
    end
    
    subgraph "Data Management"
        TrackLoader["ReconstructionDataLoader<br/>bundletrack scale"]
        NeRFLoader["ReconstructionDataLoader<br/>nerf scale"]
        TextureLoader["ReconstructionDataLoader<br/>texture scale"]
    end
    
    subgraph "Outputs"
        DepthMaps["Sub-pixel Depth Maps<br/>depth/"]
        ObjectMasks["Object Segmentation<br/>masks/"]
        CameraPoses["Camera Poses<br/>keyframes.yml"]
        TexturedMesh["Textured 3D Asset<br/>textured_mesh.obj"]
    end
    
    StereoInput --> FoundationStereo
    StereoInput --> SAM2
    UserBBox --> SAM2
    
    FoundationStereo --> DepthMaps
    SAM2 --> ObjectMasks
    
    DepthMaps --> TrackLoader
    ObjectMasks --> TrackLoader
    TrackLoader --> NVBundle
    
    NVBundle --> BundleTrack
    BundleTrack --> CameraPoses
    
    CameraPoses --> NeRFLoader
    NeRFLoader --> NeRFTraining
    NeRFTraining --> TextureLoader
    TextureLoader --> TextureBake
    TextureBake --> TexturedMesh
    
    RoMa --> BundleTrack
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:535-733]()

## Data Flow and Processing Stages

The pipeline processes data through three distinct scales, each optimized for different computational requirements. The `ReconstructionDataLoader` handles multi-scale data preparation with configurable downscaling factors.

```mermaid
flowchart LR
    subgraph "Stage 1: Preprocessing"
        RawStereo["Raw Stereo Frames<br/>4K Resolution"]
        DepthEst["FoundationStereo<br/>Depth Estimation"]
        Segmentation["SAM2<br/>Object Segmentation"]
        
        RawStereo --> DepthEst
        RawStereo --> Segmentation
    end
    
    subgraph "Stage 2: Pose Estimation"
        TrackScale["Track Dataset<br/>downscale=bundletrack.downscale"]
        FeatureMatch["RoMa Feature Matching<br/>Dense Correspondences"]
        PoseOpt["Bundle Adjustment<br/>Camera Pose Optimization"]
        
        TrackScale --> FeatureMatch
        FeatureMatch --> PoseOpt
    end
    
    subgraph "Stage 3: Neural Reconstruction"
        NeRFScale["NeRF Dataset<br/>downscale=nerf.downscale"]
        SDFTrain["Neural SDF Training<br/>Implicit Surface Learning"]
        MeshExtract["Mesh Extraction<br/>Marching Cubes"]
        
        NeRFScale --> SDFTrain
        SDFTrain --> MeshExtract
    end
    
    subgraph "Stage 4: Asset Generation"
        TextureScale["Texture Dataset<br/>downscale=texture_bake.downscale"]
        UVMap["UV Mapping<br/>Texture Coordinate Generation"]
        TextureBake["Texture Baking<br/>High-Resolution Asset"]
        
        TextureScale --> UVMap
        UVMap --> TextureBake
    end
    
    DepthEst --> TrackScale
    Segmentation --> TrackScale
    PoseOpt --> NeRFScale
    MeshExtract --> TextureScale
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:634-656](), [notebooks/3d_object_reconstruction_demo.ipynb:671-733]()

## Core Component Integration

The `NVBundleSDF` framework coordinates multiple specialized processors, each handling specific aspects of the reconstruction pipeline. The system uses a hierarchical configuration approach to manage component parameters.

```mermaid
graph TD
    subgraph "NVBundleSDF Framework"
        MainClass["NVBundleSDF<br/>src/nvidia/objectreconstruction/networks/nvbundlesdf.py"]
        
        subgraph "Component Processors"
            FS["FoundationStereoProcessor<br/>networks/foundationstereo.py"]
            SAM2Proc["Sam2Infer<br/>networks/sam2infer.py"]
            RoMaProc["FeatureMatchingInfer<br/>networks/feature_matching.py"]
            NeRFRun["NerfRunner<br/>Neural SDF Training"]
        end
        
        subgraph "Data Pipeline"
            DataLoader["ReconstructionDataLoader<br/>dataloader/reconstruction_dataloader.py"]
            ConfigSchema["Configuration Schema<br/>configs/schema.py"]
        end
    end
    
    subgraph "External Dependencies"
        RoMaLib["romatch<br/>RoMa Feature Matching Library"]
        BundleAdj["my_cpp<br/>C++ Bundle Adjustment"]
        PyTorchEco["PyTorch Ecosystem<br/>Neural Network Training"]
    end
    
    MainClass --> FS
    MainClass --> SAM2Proc
    MainClass --> RoMaProc
    MainClass --> NeRFRun
    
    MainClass --> DataLoader
    MainClass --> ConfigSchema
    
    RoMaProc --> RoMaLib
    MainClass --> BundleAdj
    NeRFRun --> PyTorchEco
    
    DataLoader --> ConfigSchema
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:654-656](), [notebooks/3d_object_reconstruction_demo.ipynb:232-241]()

## Processing Stage Execution

Each processing stage follows a specific execution pattern with defined inputs, outputs, and configuration parameters. The pipeline maintains state through file-based checkpoints and intermediate results.

| Processing Stage | Primary Function | Input Data | Output Data | Key Configuration |
|------------------|------------------|------------|-------------|-------------------|
| **Depth Estimation** | `run_depth_estimation()` | Stereo pairs from `left/`, `right/` | Dense depth maps in `depth/` | `foundation_stereo.intrinsic`, `foundation_stereo.baseline` |
| **Object Segmentation** | `run_mask_extraction()` | RGB frames, user bounding box | Object masks in `masks/` | `sam2.bbox`, `sam2.checkpoint` |
| **Pose Estimation** | `run_track()` | Depth maps, masks, RGB frames | Camera poses in `keyframes.yml` | `bundletrack.downscale`, `roma.model_path` |
| **SDF Training** | `run_global_sdf()` | Poses, masked RGB, depth data | Neural SDF model weights | `nerf.iterations`, `nerf.downscale` |
| **Texture Baking** | `run_texture_bake()` | SDF model, high-res RGB frames | `textured_mesh.obj`, `material_0.png` | `texture_bake.resolution`, `texture_bake.downscale` |

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:394-409](), [notebooks/3d_object_reconstruction_demo.ipynb:497-511](), [notebooks/3d_object_reconstruction_demo.ipynb:672-678](), [notebooks/3d_object_reconstruction_demo.ipynb:715-717](), [notebooks/3d_object_reconstruction_demo.ipynb:732-733]()

## Multi-Scale Data Processing

The `ReconstructionDataLoader` implements multi-scale processing to optimize computational efficiency across different pipeline stages. Each stage operates at its optimal resolution while maintaining geometric consistency.

```mermaid
graph LR
    subgraph "Input Resolution Management"
        OrigRes["Original Input<br/>4K (4000x3000)"]
        
        subgraph "Scale Configurations"
            TrackConf["bundletrack.downscale<br/>bundletrack.min_resolution"]
            NeRFConf["nerf.downscale<br/>nerf.min_resolution"]
            TextureConf["texture_bake.downscale<br/>texture_bake.min_resolution"]
        end
    end
    
    subgraph "Scaled Datasets"
        TrackDS["track_dataset<br/>Lower resolution for speed"]
        NeRFDS["nerf_dataset<br/>Medium resolution for training"]
        TextureDS["texture_dataset<br/>High resolution for quality"]
    end
    
    subgraph "Processing Optimization"
        FastTrack["Fast Pose Estimation<br/>Feature matching efficiency"]
        BalancedTrain["Balanced SDF Training<br/>Memory vs quality"]
        HighQuality["High-Quality Textures<br/>Maximum detail preservation"]
    end
    
    OrigRes --> TrackConf
    OrigRes --> NeRFConf
    OrigRes --> TextureConf
    
    TrackConf --> TrackDS
    NeRFConf --> NeRFDS
    TextureConf --> TextureDS
    
    TrackDS --> FastTrack
    NeRFDS --> BalancedTrain
    TextureDS --> HighQuality
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:634-653]()

## Configuration and State Management

The pipeline uses a hierarchical configuration system where each component maintains its own parameter namespace while sharing common data paths and camera calibration information.

```mermaid
graph TD
    subgraph "Configuration Hierarchy"
        BaseConfig["base.yaml<br/>Master Configuration"]
        
        subgraph "Component Configs"
            CameraConfig["camera_config<br/>Intrinsics, Baseline, Step Size"]
            FSConfig["foundation_stereo<br/>Model Path, Scale Factor"]
            SAM2Config["sam2<br/>Checkpoint, Bounding Box"]
            RoMaConfig["roma<br/>Model Path, Matching Params"]
            BundleConfig["bundletrack<br/>Debug Dir, Downscale"]
            NeRFConfig["nerf<br/>Save Dir, Iterations"]
            TextureConfig["texture_bake<br/>Resolution, Quality"]
        end
    end
    
    subgraph "Runtime State"
        WorkDir["workdir<br/>Experiment Directory"]
        
        subgraph "Intermediate Files"
            DepthDir["depth/<br/>Depth Maps"]
            MaskDir["masks/<br/>Segmentation"]
            KeyFrames["keyframes.yml<br/>Camera Poses"]
            SDFWeights["SDF Model Weights"]
        end
    end
    
    BaseConfig --> CameraConfig
    BaseConfig --> FSConfig
    BaseConfig --> SAM2Config
    BaseConfig --> RoMaConfig
    BaseConfig --> BundleConfig
    BaseConfig --> NeRFConfig
    BaseConfig --> TextureConfig
    
    CameraConfig --> WorkDir
    FSConfig --> DepthDir
    SAM2Config --> MaskDir
    BundleConfig --> KeyFrames
    NeRFConfig --> SDFWeights
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:277-325](), [notebooks/3d_object_reconstruction_demo.ipynb:375-377](), [notebooks/3d_object_reconstruction_demo.ipynb:591-626]()

## Error Handling and Validation

The pipeline implements checkpoint-based validation to ensure each stage completes successfully before proceeding to the next. Critical validation points include pose estimation success and SDF model convergence.

```mermaid
flowchart TD
    subgraph "Validation Checkpoints"
        DepthCheck["Depth Maps Generated<br/>depth/ directory populated"]
        MaskCheck["Masks Generated<br/>masks/ directory populated"]
        PoseCheck["Poses Estimated<br/>keyframes.yml exists"]
        SDFCheck["SDF Training Complete<br/>Model weights saved"]
        AssetCheck["Assets Generated<br/>textured_mesh.obj exists"]
    end
    
    subgraph "Error Handling"
        DepthFail["FoundationStereo Failure<br/>Check GPU memory, input format"]
        MaskFail["SAM2 Failure<br/>Verify bounding box, model weights"]
        PoseFail["Bundle Adjustment Failure<br/>Insufficient features, poor depth"]
        SDFFail["SDF Training Failure<br/>Pose quality, memory constraints"]
        TextureFail["Texture Baking Failure<br/>Mesh quality, UV mapping"]
    end
    
    DepthCheck -->|Success| MaskCheck
    DepthCheck -->|Failure| DepthFail
    
    MaskCheck -->|Success| PoseCheck
    MaskCheck -->|Failure| MaskFail
    
    PoseCheck -->|Success| SDFCheck
    PoseCheck -->|Failure| PoseFail
    
    SDFCheck -->|Success| AssetCheck
    SDFCheck -->|Failure| SDFFail
    
    AssetCheck -->|Failure| TextureFail
```

**Sources:** [notebooks/3d_object_reconstruction_demo.ipynb:404-409](), [notebooks/3d_object_reconstruction_demo.ipynb:505-511](), [notebooks/3d_object_reconstruction_demo.ipynb:675-678]()

---

