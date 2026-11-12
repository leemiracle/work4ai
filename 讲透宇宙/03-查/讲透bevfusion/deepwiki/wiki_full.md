# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



This document provides a comprehensive introduction to BEVFusion, a state-of-the-art multi-sensor fusion framework for 3D perception in autonomous driving. BEVFusion unifies camera and LiDAR data in a shared bird's-eye view (BEV) representation to achieve high-performance object detection and semantic segmentation.

## Purpose and Scope

BEVFusion is designed to address the challenges of multi-modal sensor fusion for autonomous driving perception tasks. The framework:

- Integrates camera and LiDAR data into a unified BEV representation
- Preserves both geometric and semantic information from different sensor modalities
- Supports multiple perception tasks including 3D object detection and BEV map segmentation
- Provides an efficient and scalable architecture for real-time autonomous driving applications

For detailed information about the system architecture, see [System Architecture](#2), and for specifics on the data processing pipeline, see [Data Processing Pipeline](#3).

Sources: [README.md:18-20]()

## Key Features and Innovations

BEVFusion introduces several key innovations in multi-sensor fusion:

1. **Unified BEV Representation**: Rather than using point-level fusion (augmenting LiDAR points with camera features), BEVFusion transforms features from both modalities into a shared BEV space.

2. **Efficient View Transformation**: The framework implements highly optimized BEV pooling operations that reduce latency by more than 40x compared to previous approaches.

3. **Task-Agnostic Design**: The architecture seamlessly supports different 3D perception tasks with minimal architectural changes.

4. **State-of-the-Art Performance**: BEVFusion achieves leading performance on major benchmarks including nuScenes and Waymo for 3D object detection and BEV map segmentation.

5. **Deployment Optimizations**: The framework has been optimized for deployment on edge devices, with TensorRT acceleration achieving 25 FPS on NVIDIA Jetson Orin platforms.

Sources: [README.md:18-20](), [README.md:9-15]()

## High-Level Architecture

BEVFusion's architecture consists of parallel processing branches for camera and LiDAR data that are eventually fused in a common BEV representation space.

```mermaid
flowchart TD
    subgraph "BEVFusion High-Level Architecture"
        A1["Camera Input"] --> B1["Camera Encoder"]
        A2["LiDAR Input"] --> B2["LiDAR Encoder"]
        
        B1 --> C1["View Transformation"]
        B2 --> C2["BEV Feature Extraction"]
        
        C1 --> D["Camera BEV Features"]
        C2 --> E["LiDAR BEV Features"]
        
        D --> F["Feature Fusion"]
        E --> F
        
        F --> G["Fused BEV Representation"]
        
        G --> H1["Detection Head"]
        G --> H2["Segmentation Head"]
        
        H1 --> I1["3D Object Detection"]
        H2 --> I2["BEV Map Segmentation"]
    end
```

Sources: [README.md:18-20]()

## Core Components

BEVFusion consists of several key components that work together to process multi-modal sensor data:

### 1. Sensor Encoders

- **Camera Encoder**: Processes multi-view camera images using a backbone network (typically SwinTransformer) followed by a feature pyramid network (FPN) to extract multi-scale features.
  
- **LiDAR Encoder**: Converts point cloud data into a structured representation through voxelization and processes it using a sparse convolutional network to extract 3D features.

### 2. View Transformation

- **LSSTransform/DepthLSSTransform**: Transforms 2D camera features into 3D BEV space using camera geometry (intrinsics and extrinsics).
  
- **BEV Pooling**: Efficiently projects features from the perspective view to the bird's-eye view using optimized CUDA operations.

### 3. Feature Fusion

- **Fusion Mechanism**: Combines the BEV features from camera and LiDAR branches, typically using concatenation or a convolutional fusion approach.

### 4. Task Heads

- **Detection Head**: Processes the fused BEV features to predict 3D bounding boxes for objects in the scene.
  
- **Segmentation Head**: Operates on the same fused BEV features to produce semantic segmentation maps.

```mermaid
graph TD
    subgraph "Component Relationships"
        A["BEVFusion Framework"] --> B["Data Processing"]
        A --> C["Model Architecture"]
        A --> D["Task Decoders"]
        
        B --> B1["Dataset Handling"]
        B --> B2["Data Loading"]
        B --> B3["Preprocessing"]
        B --> B4["Augmentation"]
        
        C --> C1["Camera Branch"]
        C --> C2["LiDAR Branch"]
        C --> C3["Fusion Module"]
        
        C1 --> C1_1["SwinTransformer"]
        C1 --> C1_2["FPN"]
        C1 --> C1_3["LSSTransform"]
        
        C2 --> C2_1["Voxelization"]
        C2 --> C2_2["SparseEncoder"]
        
        D --> D1["CenterHead/TransFusion"]
        D --> D2["MapHead"]
    end
```

Sources: [README.md:45-59](), [README.md:184-192]()

## Data Flow

The following diagram illustrates how data flows through the BEVFusion system, from input sensors to final outputs:

```mermaid
flowchart LR
    A["Input Data"] --> B["Data Processing"]
    B --> C["Feature Extraction"]
    C --> D["View Transformation"]
    D --> E["Feature Fusion"]
    E --> F["Task-Specific Heads"]
    F --> G["Perception Outputs"]
    
    subgraph "Input Data"
        A1["Multi-view Camera Images"]
        A2["LiDAR Point Clouds"]
    end
    
    subgraph "Data Processing"
        B1["LoadMultiViewImageFromFiles"]
        B2["LoadPointsFromFile"]
        B3["Data Augmentation"]
    end
    
    subgraph "Feature Extraction"
        C1["Camera Backbone (SwinTransformer)"]
        C2["LiDAR Backbone (VoxelNet)"]
    end
    
    subgraph "View Transformation"
        D1["LSSTransform"]
        D2["BEV_Pool"]
    end
    
    subgraph "Perception Outputs"
        G1["3D Bounding Boxes"]
        G2["BEV Semantic Maps"]
    end
    
    A --> A1
    A --> A2
    B --> B1
    B --> B2
    B --> B3
    C --> C1
    C --> C2
    D --> D1
    D --> D2
    G --> G1
    G --> G2
```

Sources: [README.md:60-72](), [README.md:106-128]()

## Technical Implementation

BEVFusion leverages several specialized techniques to achieve efficient multi-modal fusion:

### Custom CUDA Operations

BEVFusion implements highly optimized CUDA operations for BEV pooling, which is critical for transforming perspective view features to bird's-eye view representation. This optimization reduces the computational bottleneck in view transformation.

### Sparse Processing

For LiDAR data, sparse convolutional networks are used to efficiently process the inherently sparse point cloud data, reducing computational requirements while preserving geometric information.

### Modular Design

The framework is designed with modularity in mind, allowing for different configurations of:
- Camera backbones (e.g., SwinTransformer)
- LiDAR encoders (e.g., VoxelNet)
- Fusion strategies (e.g., ConvFuser, concatenation)
- Detection heads (e.g., CenterHead, TransFusion)
- Segmentation heads (e.g., MapHead)

Sources: [README.md:77-96](), [README.md:197-197]()

## Performance and Benchmarks

BEVFusion has achieved state-of-the-art performance on major autonomous driving benchmarks:

### nuScenes Dataset

| Model | Modality | mAP | NDS | mIoU (BEV Map) |
|:-----:|:--------:|:---:|:---:|:--------------:|
| BEVFusion | Camera + LiDAR | 68.52 | 71.38 | 62.95 |
| Camera-Only | Camera | 35.56 | 41.21 | 57.09 |
| LiDAR-Only | LiDAR | 64.68 | 69.28 | 48.56 |

### Deployment

The framework has been optimized for real-time performance:
- NVIDIA's TensorRT deployment solution achieves 25 FPS on Jetson Orin
- Integrated into NVIDIA DeepStream for sensor fusion applications

Sources: [README.md:22-59](), [README.md:9-11]()

## Available Configurations

BEVFusion supports various configurations for different use cases:

- Object detection with camera + LiDAR fusion
- Object detection with camera-only
- Object detection with LiDAR-only
- BEV map segmentation with camera + LiDAR fusion
- BEV map segmentation with camera-only
- BEV map segmentation with LiDAR-only

Sources: [README.md:45-59](), [README.md:160-192]()

## Summary

BEVFusion represents a significant advancement in multi-sensor fusion for autonomous driving perception. By unifying camera and LiDAR data in a shared bird's-eye view representation, it achieves superior performance across multiple perception tasks while maintaining computational efficiency. The framework's modular design and optimized implementation make it suitable for both research exploration and real-world deployment.

For more detailed information about specific components of BEVFusion, please refer to the following pages:
- [System Architecture](#2) - Detailed explanation of the overall architecture
- [Data Processing Pipeline](#3) - Information about data handling and preprocessing
- [Model Components](#4) - Details on each component of the model architecture
- [CUDA Operations](#5) - Explanation of custom CUDA operations for acceleration

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



This document provides a detailed overview of the BEVFusion system architecture, explaining the core components and their interactions. BEVFusion is a multi-sensor fusion framework for 3D perception that unifies camera and LiDAR data in a shared bird's-eye view (BEV) representation. For information about data processing workflows, see [Data Processing Pipeline](#3).

## Core Architecture Overview

BEVFusion employs a modular design that processes data from multiple sensor modalities (primarily camera and LiDAR), transforms them into a unified BEV representation, and uses this representation for downstream tasks such as 3D object detection and BEV map segmentation.

```mermaid
flowchart TD
    subgraph "BEVFusion Architecture"
        A1["Camera Input"] --> B1["Camera Encoder"]
        A2["LiDAR Input"] --> B2["LiDAR Encoder"]
        B1 --> C1["Camera BEV Features"]
        B2 --> C2["LiDAR BEV Features"]
        C1 --> D["Feature Fusion"]
        C2 --> D
        D --> E["Fused BEV Representation"]
        E --> F1["Detection Head"]
        E --> F2["Segmentation Head"]
        F1 --> G1["3D Object Detection"]
        F2 --> G2["BEV Map Segmentation"]
    end
```

Sources: [README.md:18-22]()

## Component Structure and Relationships

The BEVFusion architecture consists of multiple interrelated components organized into a processing pipeline. The system is designed to be modular, allowing for different configurations based on application requirements.

```mermaid
graph TD
    A["BEVFusion"] --> B["Encoders"]
    A --> C["View Transformation"]
    A --> D["Fusion Module"]
    A --> E["Task Heads"]
    
    B --> B1["Camera Encoder"]
    B --> B2["LiDAR Encoder"]
    
    B1 --> B1_1["SwinTransformer"]
    B1 --> B1_2["FPN Neck"]
    
    B2 --> B2_1["VoxelBackbone"]
    B2 --> B2_2["SparseEncoder"]
    
    C --> C1["LSSTransform"]
    C --> C2["DepthLSSTransform"]
    
    D --> D1["ConvFuser"]
    D --> D2["Concatenation"]
    
    E --> E1["CenterHead"]
    E --> E2["MapHead"]
    
    C1 --> D
    C2 --> D
    B2_2 --> D
    
    D --> E1
    D --> E2
```

Sources: [README.md:206-209]()

## Sensor-Specific Processing Paths

### Camera Branch

The camera branch processes multi-view image inputs through a feature extraction backbone and transforms the features into the BEV space:

1. **Input**: Multi-view camera images
2. **Feature Extraction**: SwinTransformer backbone followed by a Feature Pyramid Network (FPN)
3. **View Transformation**: LSS (Lift, Splat, Shoot) transform that projects 2D image features into the 3D BEV space

### LiDAR Branch

The LiDAR branch processes point cloud data through specialized operations:

1. **Input**: LiDAR point cloud
2. **Voxelization**: Converts the point cloud into voxel features
3. **Feature Extraction**: Processes voxels through a sparse encoder
4. **BEV Representation**: Creates BEV features directly from the 3D data

## BEV Transformation Process

A critical component of BEVFusion is the transformation of camera features into the BEV space, enabling fusion with LiDAR features.

```mermaid
flowchart LR
    A["Image Features"] --> B["LSS Transform"]
    B --> C["Geometry Calculation"]
    C --> D["Frustum Generation"]
    C --> E["BEV Pooling"]
    E --> G["Camera BEV Features"]
    
    H["Camera Intrinsics"] --> D
    I["Camera Extrinsics"] --> D
    
    subgraph "CUDA Operations"
        E1["bev_pool_forward"]
        E2["bev_pool_backward"]
    end
    
    E --> E1
    E --> E2
```

Sources: [README.md:51-52]()

The BEV pooling operation is a performance-critical component, implemented as custom CUDA operations for efficiency. This operation transforms view-dependent features into a view-independent BEV space, allowing them to be fused with LiDAR features.

## Multi-Modal Fusion

BEVFusion implements feature-level fusion after both camera and LiDAR data are transformed into the BEV space:

1. **ConvFuser**: Uses convolutional layers to fuse features
2. **Simple Concatenation**: Alternative approach that directly concatenates the feature maps

The fusion is performed in the BEV space, which preserves both geometric and semantic information from both modalities.

```mermaid
flowchart TD
    subgraph "Camera Branch"
        A1["Camera Images"] --> B1["SwinTransformer"]
        B1 --> C1["FPN Neck"]
        C1 --> D1["LSS Transform"]
        D1 --> E1["Camera BEV Features"]
    end
    
    subgraph "LiDAR Branch"
        A2["LiDAR Points"] --> B2["Voxelization"]
        B2 --> C2["SparseEncoder"]
        C2 --> D2["LiDAR BEV Features"]
    end
    
    E1 --> F["Feature Fusion Layer"]
    D2 --> F
    F --> G["Fused BEV Features"]
    G --> H["Task-specific Heads"]
```

Sources: [README.md:67-77]()

## Task-Specific Heads

BEVFusion supports multiple perception tasks through dedicated task heads:

1. **Detection Head**: For 3D object detection (CenterHead implementation)
2. **Segmentation Head**: For BEV map segmentation

These heads operate on the fused BEV features and are trained jointly or separately depending on the specific application.

## Implementation Details

### Custom CUDA Operations

BEVFusion implements several custom CUDA operations to achieve real-time performance:

1. **BEV Pooling**: Efficient transformation of perspective view features to BEV space
2. **Sparse Convolution**: Optimized processing of sparse point cloud data

These operations significantly accelerate the inference process, enabling real-time applications.

### Modular Configuration System

The system uses a configuration-based approach to define model architectures, allowing for easy experimentation with different combinations of components:

- Sensor modalities (camera-only, LiDAR-only, or both)
- Backbone architectures
- View transformation methods
- Fusion strategies
- Task-specific heads and losses

This modular design is reflected in the configuration files, where different components can be easily swapped or combined.

## Performance Considerations

BEVFusion achieves state-of-the-art performance while maintaining real-time inference capabilities:

- The optimized implementation can reach 25 FPS on NVIDIA Jetson Orin platforms
- The architecture makes efficient use of computational resources with optimized CUDA operations
- The BEV representation enables effective fusion of different sensor modalities with minimal information loss

For deployment details and optimization strategies, see [Deployment](#8).

Sources: [README.md:9-10]()

## Code Organization

The codebase is organized around the main architectural components:

```mermaid
graph TD
    subgraph "Main Components"
        A["mmdet3d"]
        A --> B["datasets"]
        A --> C["models"]
        A --> D["ops"]
        A --> E["core"]
    end
    
    subgraph "Models"
        C --> C1["encoders"]
        C --> C2["necks"]
        C --> C3["fusion_layers"]
        C --> C4["detectors"]
        C --> C5["heads"]
    end
    
    subgraph "Operations"
        D --> D1["bev_pool"]
        D --> D2["sparse_ops"]
        D --> D3["voxel"]
    end
    
    subgraph "Datasets"
        B --> B1["nuscenes"]
        B --> B2["pipelines"]
    end
```

Sources: [README.md:126-128]()

This organization reflects the modular nature of the architecture, where each component can be developed, tested, and optimized independently.

---

# Page: Data Flow

# Data Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/nuscenes_dataset.py](mmdet3d/datasets/nuscenes_dataset.py)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



## Purpose and Scope

This document describes the data flow in the BEVFusion system, tracing the journey of multi-modal data from input sensors through the processing pipeline to the final outputs. It covers how camera and LiDAR data are loaded, preprocessed, encoded, transformed into bird's-eye view (BEV) representation, fused, and finally processed by task-specific heads for 3D object detection and BEV map segmentation.

For information about specific model components, see [Model Components](#4).

## Overview of Data Flow

```mermaid
flowchart TD
    subgraph "Input Data"
        A1["Camera Images"] 
        A2["LiDAR Point Clouds"]
    end

    subgraph "Data Loading & Preprocessing"
        B1["NuScenesDataset"]
        B2["Data Pipeline"]
    end

    subgraph "Feature Extraction"
        C1["Camera Encoder"]
        C2["LiDAR Encoder"]
    end

    subgraph "View Transformation"
        D1["LSS Transform"]
        D2["Voxel to BEV"]
    end

    subgraph "Feature Fusion"
        E["ConvFuser/Concatenation"]
    end

    subgraph "Task-specific Heads"
        F1["Detection Head"] 
        F2["Segmentation Head"]
    end

    subgraph "Outputs"
        G1["3D Bounding Boxes"]
        G2["BEV Segmentation Maps"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    C1 --> D1
    C2 --> D2
    D1 --> E
    D2 --> E
    E --> F1
    E --> F2
    F1 --> G1
    F2 --> G2
```

Sources: [README.md:18-20]()

## Data Sources and Format

BEVFusion primarily works with the nuScenes dataset, which provides:

1. **Camera Images**: Multi-view camera images from 6 cameras (front, front left, front right, back, back left, back right)
2. **LiDAR Point Clouds**: 3D point cloud data from LiDAR sensors 
3. **Annotations**: Ground truth 3D bounding boxes and semantic maps

The system also supports data from multiple sweeps (temporal frames) to improve perception quality.

```mermaid
graph TD
    subgraph "nuScenes Dataset Structure"
        A1["samples"] --> B1["Sample"]
        A2["sweeps"] --> B2["Multiple LiDAR Sweeps"]
        A3["maps"] --> B3["BEV Map Annotations"]
        A4["v1.0-trainval"] --> B4["Ground Truth Annotations"]
        
        B1 --> C1["images"]
        B1 --> C2["lidar_points"]
        B1 --> C3["annotations"]
        
        C1 --> D1["CAM_FRONT.jpg"]
        C1 --> D2["CAM_FRONT_LEFT.jpg"]
        C1 --> D3["CAM_FRONT_RIGHT.jpg"]
        C1 --> D4["CAM_BACK.jpg"]
        C1 --> D5["CAM_BACK_LEFT.jpg"]
        C1 --> D6["CAM_BACK_RIGHT.jpg"]
        
        C2 --> D7["LIDAR_TOP.pcd.bin"]
        
        C3 --> D8["3D_boxes.json"]
        C3 --> D9["segment_labels.json"]
    end
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:193-207](), [README.md:105-128]()

## Data Loading Pipeline

The data loading stage uses `NuScenesDataset` to read and organize the raw sensor data and annotations.

```mermaid
flowchart TD
    A["NuScenesDataset"] --> B["load_annotations"]
    B --> C["get_data_info"]
    
    C --> D1["Load Camera Data"]
    C --> D2["Load LiDAR Data"] 
    C --> D3["Load Annotation Data"]
    
    D1 --> E1["Image Paths"]
    D1 --> E2["Camera Calibration"]
    
    D2 --> E3["Point Cloud Path"]
    D2 --> E4["LiDAR Calibration"]
    
    D3 --> E5["get_ann_info"]
    
    E2 --> F1["camera2ego Transform"]
    E2 --> F2["lidar2camera Transform"]
    E2 --> F3["camera Intrinsics"]
    
    E4 --> F4["lidar2ego Transform"]
    
    E5 --> F5["3D Bounding Boxes"]
    E5 --> F6["Class Labels"]

    G["Data Dict"] --> H["Training/Inference Pipeline"]
    
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G
    F6 --> G
    E1 --> G
    E3 --> G
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:209-285]()

For each sample, the system loads:

1. **Camera Data**:
   - Image paths
   - Camera-to-ego transforms
   - Camera intrinsic parameters
   - LiDAR-to-camera projections

2. **LiDAR Data**:
   - Point cloud paths
   - LiDAR-to-ego transforms
   - Temporal sweeps (optional)

3. **Annotation Data**:
   - 3D bounding boxes
   - Class labels
   - Instance attributes

Key transformation matrices computed in this stage:
- **ego2global**: Transform from ego vehicle coordinates to global coordinates
- **lidar2ego**: Transform from LiDAR coordinates to ego vehicle coordinates
- **lidar2camera**: Transform from LiDAR coordinates to camera coordinates
- **camera2ego**: Transform from camera coordinates to ego vehicle coordinates

These transformation matrices are essential for correctly aligning data from different sensors into a unified coordinate system.

Sources: [mmdet3d/datasets/nuscenes_dataset.py:227-281]()

## Data Preprocessing and Augmentation

After loading, the data undergoes preprocessing and augmentation through a configurable pipeline:

```mermaid
flowchart LR
    A["Raw Data"] --> B["Data Loading"]
    B --> C["Data Augmentation"]
    C --> D["Format & Collection"]
    D --> E["Data Batch"]
    
    subgraph "Data Loading"
        B1["LoadMultiViewImageFromFiles"]
        B2["LoadPointsFromFile"]
        B3["LoadPointsFromMultiSweeps"]
        B4["LoadAnnotations3D"]
    end
    
    subgraph "Data Augmentation"
        C1["GlobalRotScaleTrans"]
        C2["RandomFlip3D"]
        C3["ObjectPaste"]
        C4["PointShuffle"]
    end
    
    subgraph "Format & Collection"
        D1["DefaultFormatBundle3D"]
        D2["Collect3D"]
    end
```

Sources: [mmdet3d/datasets/pipelines/utils.py:310-384](), [README.md:156-194]()

The data augmentation includes:
- **Geometric Transforms**: Rotation, scaling, and translation
- **Random Flipping**: Horizontal flipping of images and point clouds
- **Object Paste**: Copying objects from one scene to another
- **Point Noise**: Adding noise to point cloud coordinates

For LiDAR data, specific augmentations include:
- **Points Shuffling**: Randomly shuffling points to increase robustness
- **Voxelization**: Converting raw point clouds into voxel grid representation

For camera data:
- **Image Resizing**: Resizing images to a standard input size
- **Photometric Distortion**: Adjusting brightness, contrast, saturation
- **Normalization**: Standardizing pixel values

Sources: [mmdet3d/datasets/pipelines/utils.py:11-109]()

## Feature Extraction

After preprocessing, the data enters parallel processing branches for feature extraction:

```mermaid
flowchart TD
    subgraph "Camera Branch"
        A1["Multi-view Images"] --> B1["SwinTransformer Backbone"]
        B1 --> C1["FPN Neck"]
        C1 --> D1["2D Image Features"]
    end
    
    subgraph "LiDAR Branch"
        A2["Point Cloud"] --> B2["Voxelization"]
        B2 --> C2["SparseEncoder"]
        C2 --> D2["3D Sparse Features"]
    end
```

Sources: [README.md:163-175]()

### Camera Feature Extraction
- **Input**: Multi-view camera images (typically 6 views)
- **Backbone**: Swin Transformer processes each image independently
- **Feature Pyramid Network (FPN)**: Generates multi-scale features
- **Output**: 2D feature maps for each camera view

### LiDAR Feature Extraction
- **Input**: LiDAR point cloud (single or multiple sweeps)
- **Voxelization**: Converts point cloud into sparse 3D voxel grid
- **Sparse 3D CNN**: Processes voxelized point cloud
- **Output**: 3D sparse feature volumes

## BEV View Transformation

A critical step in BEVFusion is transforming both camera and LiDAR features into a common bird's-eye view (BEV) representation:

```mermaid
flowchart LR
    subgraph "Camera BEV Transformation"
        A1["2D Image Features"] --> B1["LSS Transform"]
        B1 --> C1["Depth Estimation"]
        C1 --> D1["Frustum Pooling"]
        D1 --> E1["Camera BEV Features"]
    end
    
    subgraph "LiDAR BEV Transformation"
        A2["3D Sparse Features"] --> B2["Height Compression"]
        B2 --> C2["LiDAR BEV Features"]
    end
    
    E1 --> F["BEV Feature Fusion"]
    C2 --> F
```

Sources: [README.md:85-107]()

### Camera View Transformation
The camera-to-BEV transformation uses the Lift-Splat-Shoot (LSS) method:
1. **Feature Lifting**: 2D image features are "lifted" to 3D space using estimated depth
2. **Frustum Creation**: Creates a 3D frustum for each pixel in the image
3. **BEV Pooling**: Projects and aggregates 3D features into the BEV grid using efficient CUDA implementations

The camera transformation requires:
- Camera intrinsic parameters
- Camera-to-ego transformation matrices
- Estimated depth information (for DepthLSS variant)

### LiDAR View Transformation
The LiDAR-to-BEV transformation is more straightforward:
1. **Height Compression**: 3D voxel features are compressed along the height dimension
2. **Feature Reorganization**: Reorganized into a dense BEV grid

## Feature Fusion

After both modalities are transformed to BEV representation, they are fused:

```mermaid
flowchart LR
    A1["Camera BEV Features"] --> C["Fusion Module"]
    A2["LiDAR BEV Features"] --> C
    
    subgraph "Fusion Strategies"
        C --> D1["Concatenation"]
        C --> D2["ConvFuser"]
    end
    
    D1 --> E["Fused BEV Features"]
    D2 --> E
    
    E --> F1["Detection Head"]
    E --> F2["Segmentation Head"]
```

Sources: [README.md:184-190]()

The fusion module supports different strategies:
1. **Simple Concatenation**: Directly concatenating camera and LiDAR BEV features along the channel dimension
2. **ConvFuser**: Using convolutional layers to learn cross-modal feature interactions

The fused BEV features preserve both geometric information (from LiDAR) and semantic information (from cameras), creating a unified representation for downstream tasks.

## Task-specific Processing and Outputs

The fused BEV features are processed by task-specific heads:

```mermaid
flowchart TD
    A["Fused BEV Features"] --> B1["Detection Head"]
    A --> B2["Segmentation Head"]
    
    B1 --> C1["CenterPoint Detection"]
    C1 --> D1["3D Bounding Box Regression"]
    C1 --> D2["Classification"]
    C1 --> D3["Velocity Estimation"]
    
    B2 --> C2["Segmentation Decoder"]
    C2 --> D4["BEV Semantic Map"]
    
    D1 --> E1["Post-processing"]
    D2 --> E1
    D3 --> E1
    
    E1 --> F1["Final 3D Detections"]
    D4 --> F2["BEV Map Segmentation"]
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:337-407](), [mmdet3d/datasets/nuscenes_dataset.py:498-530]()

### Detection Head
- **CenterPoint Detection**: Identifies object centers in BEV space
- **Box Regression**: Estimates 3D box dimensions, orientation, and location
- **Classification**: Predicts object class (car, pedestrian, etc.)
- **Velocity Estimation**: Predicts object velocity (if enabled)

### Segmentation Head
- **Segmentation Decoder**: Processes BEV features to predict semantic classes
- **Output**: BEV semantic map with classes like road, sidewalk, vegetation, etc.

## Evaluation and Output Formatting

The final outputs are formatted and evaluated:

```mermaid
flowchart LR
    A1["3D Detections"] --> B1["Format Detections"]
    B1 --> C1["output_to_nusc_box"]
    C1 --> D1["lidar_nusc_box_to_global"]
    D1 --> E1["nuScenes Detection Format"]
    
    A2["BEV Segmentation"] --> B2["Calculate IoU"]
    B2 --> C2["Segmentation Metrics"]
    
    E1 --> F["Evaluation"]
    C2 --> F
    
    F --> G1["Detection Metrics"]
    F --> G2["Segmentation Metrics"]
    
    G1 --> H1["mAP"]
    G1 --> H2["NDS"]
    G2 --> H3["mIoU"]
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:410-465](), [mmdet3d/datasets/nuscenes_dataset.py:498-530](), [mmdet3d/datasets/nuscenes_dataset.py:532-572]()

For detection outputs:
1. Predicted boxes are converted to the nuScenes box format
2. Boxes are transformed from LiDAR to global coordinates
3. Attributes like object velocity and status are added
4. Evaluation metrics like mAP and NDS are calculated

For segmentation outputs:
1. IoU is calculated for each class across different thresholds
2. mIoU (mean Intersection over Union) is calculated for the BEV map segmentation

## Complete Data Flow Diagram

Here's the complete data flow diagram showing all main components:

```mermaid
flowchart TD
    A1["Camera Images"] --> B1["LoadMultiViewImageFromFiles"]
    A2["LiDAR Points"] --> B2["LoadPointsFromFile"]
    
    B1 --> C1["Image Augmentation"]
    B2 --> C2["Point Cloud Augmentation"]
    
    C1 --> D1["SwinTransformer"]
    C2 --> D2["VoxelBackbone + SparseEncoder"]
    
    D1 --> E1["FPN"]
    D2 --> E2["3D Sparse Features"]
    
    E1 --> F1["LSS Transform"]
    E2 --> F2["Height Compression"]
    
    F1 --> G1["Camera BEV Features"]
    F2 --> G2["LiDAR BEV Features"]
    
    G1 --> H["Feature Fusion (ConvFuser/Concat)"]
    G2 --> H
    
    H --> I1["CenterHead"]
    H --> I2["MapHead"]
    
    I1 --> J1["Box Prediction"]
    I1 --> J2["Classification"]
    I2 --> J3["Semantic Map"]
    
    J1 --> K1["NuScenes Format"]
    J2 --> K1
    J3 --> K2["IoU Calculation"]
    
    K1 --> L1["Detection Evaluation"]
    K2 --> L2["Segmentation Evaluation"]
    
    L1 --> M1["Final Detection Metrics"]
    L2 --> M2["Final Segmentation Metrics"]
```

Sources: [README.md:20-45](), [mmdet3d/datasets/nuscenes_dataset.py:5-653]()

## Coordinate Systems and Transformations

A critical aspect of the data flow is the handling of different coordinate systems:

```mermaid
graph TD
    subgraph "Coordinate Systems"
        A1["Global Coordinates"]
        A2["Ego Vehicle Coordinates"]
        A3["LiDAR Coordinates"]
        A4["Camera Coordinates"]
        A5["BEV Coordinates"]
    end
    
    subgraph "Transformation Matrices"
        B1["ego2global"]
        B2["lidar2ego"]
        B3["camera2ego"]
        B4["lidar2camera"]
        B5["camera2lidar"]
    end
    
    A1 <--> |"ego2global"| A2
    A2 <--> |"lidar2ego"| A3
    A2 <--> |"camera2ego"| A4
    A3 <--> |"lidar2camera"| A4
    A4 <--> |"camera2lidar"| A3
    A3 --> |"height compression"| A5
    A4 --> |"LSS transform"| A5
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:227-281]()

The system maintains these transformations to properly align multi-modal data:
- **Global → Ego**: Places data in ego-vehicle frame
- **Ego → Sensor**: Transforms between vehicle and sensor frames
- **Sensor → BEV**: Projects sensor data to bird's-eye view

The consistent handling of these coordinate transformations is crucial for accurate fusion of the multi-modal data.

---

# Page: Data Processing Pipeline

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/nuscenes/default.yaml](configs/nuscenes/default.yaml)
- [mmdet3d/datasets/nuscenes_dataset.py](mmdet3d/datasets/nuscenes_dataset.py)

</details>



## Purpose and Scope

This document explains the data processing pipeline in BEVFusion, which handles the preparation of multi-modal sensor data (camera images and LiDAR point clouds) for training and inference tasks. The pipeline covers data loading, preprocessing, augmentation, and formatting components essential for the fusion-based 3D object detection and segmentation. For information about the model components that process this data, see [Model Components](#4).

```mermaid
flowchart TD
    A["Raw Input Data"] --> B["Data Loading"]
    B --> C["Data Preprocessing"]
    C --> D["Data Augmentation"]
    D --> E["Data Formatting"]
    E --> F["Model Training/Inference"]

    subgraph "Pipeline Components"
        B1["Camera Images"]
        B2["LiDAR Points"]
        B3["Annotations"]
        B4["Map Data"]
    end

    A --> B1
    A --> B2
    A --> B3
    A --> B4
```

Sources: [configs/nuscenes/default.yaml:55-188](), [configs/nuscenes/default.yaml:190-264]()

## Dataset Structure

BEVFusion primarily uses the nuScenes dataset, which is handled by the `NuScenesDataset` class. This dataset contains synchronized camera images from multiple views, LiDAR point clouds, and 3D annotations for autonomous driving perception tasks.

### Key Dataset Components

| Component | Description | File Path Reference |
|-----------|-------------|---------------------|
| Object Classes | Classes for 3D object detection (e.g., car, truck, pedestrian) | [configs/nuscenes/default.yaml:25-35]() |
| Map Classes | Classes for BEV map segmentation (e.g., drivable_area, walkway) | [configs/nuscenes/default.yaml:37-47]() |
| Input Modalities | Sensor modalities used (LiDAR, camera) | [configs/nuscenes/default.yaml:48-53]() |

```mermaid
classDiagram
    class NuScenesDataset {
        +ann_file: str
        +dataset_root: str
        +load_annotations()
        +get_data_info()
        +get_ann_info()
        +evaluate()
    }
    
    class Custom3DDataset {
        +load_annotations()
        +get_data_info()
    }
    
    NuScenesDataset --|> Custom3DDataset
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:18-543]()

## Data Loading Pipeline

The data loading process transforms raw sensor data into a format suitable for model training or inference. BEVFusion uses separate specialized loaders for each data type.

### Data Loaders

| Loader | Purpose | Configuration Reference |
|--------|---------|-------------------------|
| `LoadMultiViewImageFromFiles` | Loads multiple camera images | [configs/nuscenes/default.yaml:56-58]() |
| `LoadPointsFromFile` | Loads LiDAR point cloud data | [configs/nuscenes/default.yaml:60-65]() |
| `LoadPointsFromMultiSweeps` | Loads and combines multiple LiDAR sweeps | [configs/nuscenes/default.yaml:67-74]() |
| `LoadAnnotations3D` | Loads 3D bounding box annotations | [configs/nuscenes/default.yaml:76-79]() |
| `LoadBEVSegmentation` | Loads bird's-eye view segmentation maps | [configs/nuscenes/default.yaml:133-137]() |

The core function `get_data_info` in the `NuScenesDataset` class prepares the sensor data and metadata:

```mermaid
flowchart LR
    A["Raw Data Files"] --> B["NuScenesDataset.get_data_info()"]
    B --> C1["Camera Data"]
    B --> C2["LiDAR Data"]
    B --> C3["Annotations"]
    B --> C4["Calibration Data"]
    
    C1 --> D["Data Dict"]
    C2 --> D
    C3 --> D
    C4 --> D
    
    D --> E["Pipeline Processing"]
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:209-285]()

## Data Preprocessing

Before augmentation, the raw sensor data undergoes preprocessing to ensure consistency and compatibility with the model inputs.

### Key Preprocessing Steps

1. **Point Cloud Range Filtering**: Removes points outside the defined detection range
2. **Object Range Filtering**: Filters out objects outside the detection range
3. **Object Name Filtering**: Keeps only objects from the specified classes
4. **Image Normalization**: Normalizes image pixel values

```mermaid
flowchart TD
    A["Loaded Raw Data"] --> B["Point Cloud Range Filter"]
    A --> C["Object Range Filter"]
    A --> D["Object Name Filter"]
    A --> E["Image Normalization"]
    
    B --> F["Preprocessed Data"]
    C --> F
    D --> F
    E --> F
```

Sources: [configs/nuscenes/default.yaml:141-152](), [configs/nuscenes/default.yaml:236-241]()

## Data Augmentation

Data augmentation increases the diversity of training samples to improve model generalization. BEVFusion implements separate augmentation strategies for camera images and LiDAR point clouds.

### 2D Augmentation (Camera Images)

| Technique | Purpose | Parameter Range |
|-----------|---------|-----------------|
| Resize | Changes image dimensions | 0.38-0.55 (train), 0.48 (test) |
| Rotation | Randomly rotates images | ±5.4° (train only) |
| Flip | Randomly flips images | True (train only) |
| GridMask | Applies grid-like mask | Probability configurable |

### 3D Augmentation (LiDAR Points)

| Technique | Purpose | Parameter Range |
|-----------|---------|-----------------|
| Global Rotation | Rotates point cloud | ±0.78539816 rad (±45°) |
| Global Scaling | Scales point cloud | 0.9-1.1 |
| Global Translation | Translates point cloud | ±0.5m |
| Random Flip | Randomly flips point cloud | Applied after other transforms |
| Point Shuffle | Randomly shuffles points | Applied before final formatting |

```mermaid
flowchart LR
    A["Preprocessed Data"] --> B["Image Augmentation"]
    A --> C["Point Cloud Augmentation"]
    
    subgraph "Image Augmentation"
        B1["ImageAug3D"]
        B2["GridMask"]
    end
    
    subgraph "Point Cloud Augmentation"
        C1["GlobalRotScaleTrans"]
        C2["RandomFlip3D"]
        C3["PointShuffle"]
    end
    
    B --> B1 --> B2
    C --> C1 --> C2 --> C3
    
    B2 --> D["Augmented Data"]
    C3 --> D
```

Sources: [configs/nuscenes/default.yaml:119-165](), [configs/nuscenes/default.yaml:216-228]()

### Object Paste Augmentation

A special augmentation technique called `ObjectPaste` samples objects from a database and pastes them into the current scene. This is particularly useful for increasing the frequency of rare object classes.

```mermaid
flowchart TD
    A["Scene Data"] --> B["ObjectPaste"]
    C["Object Database"] --> B
    B --> D["Augmented Scene"]
    
    subgraph "DB Sampler Configuration"
        E1["Sample Groups"]
        E2["Min Points Filter"]
    end
    
    C --> E1
    C --> E2
```

Sources: [configs/nuscenes/default.yaml:80-118]()

## Data Formatting and Collection

The final stage of the pipeline formats the processed data and collects it into a standardized dictionary structure for model training or inference.

### Formatting Process

1. **DefaultFormatBundle3D**: Converts data to the required tensor formats
2. **Collect3D**: Assembles the final data dictionary with all required keys
3. **GTDepth** (optional): Generates ground truth depth information for camera-based models

```mermaid
flowchart LR
    A["Augmented Data"] --> B["DefaultFormatBundle3D"]
    B --> C["Collect3D"]
    C --> D["GTDepth"]
    D --> E["Final Data Dictionary"]
    
    subgraph "Collected Keys"
        F1["Image Data"]
        F2["Point Cloud"]
        F3["GT Bboxes 3D"]
        F4["GT Labels 3D"]
        F5["GT Masks BEV"]
        F6["Metadata"]
    end
    
    E --> F1
    E --> F2
    E --> F3
    E --> F4
    E --> F5
    E --> F6
```

Sources: [configs/nuscenes/default.yaml:167-188](), [configs/nuscenes/default.yaml:243-264]()

## Train vs. Test Pipeline Differences

BEVFusion uses different data processing pipelines for training and testing/validation. The main differences are in the augmentation strategies.

| Component | Training Pipeline | Testing Pipeline |
|-----------|-------------------|------------------|
| Image Resize | Random 0.38-0.55 | Fixed 0.48 |
| Image Rotation | Random ±5.4° | No rotation (0°) |
| Image Flip | Random flip | No flip |
| Point Cloud Scaling | Random 0.9-1.1 | Fixed 1.0 |
| Point Cloud Rotation | Random ±45° | No rotation (0°) |
| Point Cloud Translation | Random ±0.5m | No translation (0m) |
| GridMask Augmentation | Applied | Not applied |
| ObjectPaste | Applied | Not applied |

These differences ensure diverse training samples while maintaining consistency during evaluation.

Sources: [configs/nuscenes/default.yaml:55-188](), [configs/nuscenes/default.yaml:190-264]()

## Dataset Implementation Details

The `NuScenesDataset` class in BEVFusion handles all dataset-specific operations and integrates with the data processing pipeline.

```mermaid
flowchart TD
    A["NuScenesDataset"] --> B["load_annotations()"]
    A --> C["get_data_info()"]
    A --> D["get_ann_info()"]
    
    B --> E["Data Loading"]
    C --> F["LiDAR & Camera Processing"]
    D --> G["Annotation Processing"]
    
    E --> H["Pipeline Processing"]
    F --> H
    G --> H
    
    H --> I["Training/Inference"]
```

Key implementation details:
- The dataset loads annotations from pickle files to efficiently access pre-processed metadata
- Calibration information (transformations between different sensor coordinate systems) is carefully calculated
- For each sample, the dataset provides a structured dictionary with all necessary information for the model
- The dataset implementation supports both training and testing modes with appropriate configurations

Sources: [mmdet3d/datasets/nuscenes_dataset.py:18-193](), [mmdet3d/datasets/nuscenes_dataset.py:194-207](), [mmdet3d/datasets/nuscenes_dataset.py:209-285](), [mmdet3d/datasets/nuscenes_dataset.py:287-335]()

---

# Page: Data Loading

# Data Loading

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/datasets/pipelines/loading.py](mmdet3d/datasets/pipelines/loading.py)

</details>



## Purpose and Scope

This document details the data loading components and processes in BEVFusion. It describes how the system loads data from various sources including camera images, LiDAR point clouds, radar data, and 3D annotations. The data loading module serves as the first step in the data processing pipeline, preparing raw data for subsequent preprocessing, augmentation, and model training/inference. For information about data augmentation, see [Data Augmentation & Transformation](#3.2).

```mermaid
flowchart TD
    subgraph "Data Loading Components"
        A["LoadMultiViewImageFromFiles"] --> B["Camera Images"]
        C["LoadPointsFromFile"] --> D["Single LiDAR Sweep"]
        E["LoadPointsFromMultiSweeps"] --> F["Multiple LiDAR Sweeps"]
        G["LoadRadarPointsMultiSweeps"] --> H["Multiple Radar Sweeps"]
        I["LoadAnnotations3D"] --> J["3D Bounding Boxes & Labels"]
        K["LoadBEVSegmentation"] --> L["BEV Segmentation Maps"]
    end
```

Sources: [mmdet3d/datasets/pipelines/loading.py:21-794]()

## Data Loading Components

BEVFusion employs several specialized data loading components to handle different data types. Each component is implemented as a callable class that can be integrated into the data processing pipeline.

### Image Data Loading

The `LoadMultiViewImageFromFiles` class is responsible for loading multi-view camera images, which are crucial for the camera branch of BEVFusion.

```mermaid
flowchart LR
    A["Input: image_paths"] --> B["LoadMultiViewImageFromFiles"]
    B --> C["Load images using PIL.Image.open()"]
    C --> D["Output: List of Image objects"]
    D --> E["Set metadata: img_shape, ori_shape, etc."]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:21-83]()

Key implementation details:
- Loads images from a list of file paths specified in `results["image_paths"]`
- Uses PIL's `Image.open()` to load images without any preprocessing
- Returns a list of image objects rather than a stacked array
- Sets metadata fields including `filename`, `img_shape`, `ori_shape`, `pad_shape`, and `scale_factor`

### Point Cloud Data Loading

The `LoadPointsFromFile` class handles loading point cloud data from a single file (typically LiDAR data).

```mermaid
flowchart LR
    A["Input: lidar_path"] --> B["LoadPointsFromFile"]
    B --> C["Load points using np.load() or np.fromfile()"]
    C --> D["Optional: reduce LiDAR beams"]
    D --> E["Extract required dimensions"]
    E --> F["Create BasePoints object"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:316-436]()

Key implementation details:
- Supports loading from `.npy` files or binary files
- Allows selection of specific dimensions to use (e.g., x, y, z, intensity)
- Can optionally reduce the number of LiDAR beams
- Supports optional augmented point cloud loading
- Creates a `BasePoints` object with the coordinate type (LIDAR, CAMERA, or DEPTH)

### Multi-sweep Point Cloud Loading

The `LoadPointsFromMultiSweeps` class loads point clouds from multiple time frames (sweeps) and combines them, which is essential for temporal information utilization.

```mermaid
flowchart TD
    A["Input: points & sweeps"] --> B["LoadPointsFromMultiSweeps"]
    B --> C["Load current frame points"]
    C --> D["Load previous sweep points"]
    D --> E["Transform points to current frame's coordinate"]
    E --> F["Add timestamp difference feature"]
    F --> G["Concatenate all sweep points"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:86-240]()

Key implementation details:
- Loads points from the current frame and several previous frames
- Transforms points from previous frames to the current frame's coordinate system
- Adds a temporal dimension (timestamp difference) to each point
- Supports random or sequential sweep selection for training and testing
- Can optionally remove points too close to the ego vehicle

### Radar Data Loading

The `LoadRadarPointsMultiSweeps` class loads radar point clouds from multiple sweeps, similar to the LiDAR multi-sweep loader but with radar-specific processing.

```mermaid
flowchart TD
    A["Input: radar sweeps"] --> B["LoadRadarPointsMultiSweeps"]
    B --> C["Load radar points from files"]
    C --> D["Apply sensor2lidar transformation"]
    D --> E["Optional: velocity compensation"]
    E --> F["Add time difference feature"]
    F --> G["Apply feature encoding"]
    G --> H["Optional: normalize features"]
    H --> I["Create RadarPoints object"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:575-794]()

Key implementation details:
- Loads radar points using the `RadarPointCloud` class
- Performs coordinate transformations to the LiDAR frame
- Can compensate velocity based on ego motion
- Applies feature encoding (one-hot, ordinal, or filtering-based)
- Optionally normalizes features to a specified range
- Pads or drops points to maintain a consistent output size

### 3D Annotation Loading

The `LoadAnnotations3D` class loads 3D annotations including bounding boxes, labels, and attribute labels.

```mermaid
flowchart LR
    A["Input: ann_info"] --> B["LoadAnnotations3D"]
    B --> C["Load 3D bounding boxes"]
    B --> D["Load 3D labels"]
    B --> E["Optional: Load attribute labels"]
    B --> F["Optional: Load 2D annotations"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:437-563]()

Key implementation details:
- Extends `LoadAnnotations` from MMDetection
- Supports loading 3D bounding boxes, labels, and attribute labels
- Can optionally load 2D annotations (bounding boxes, labels, masks)
- Also supports loading 2.5D annotations (centers2d and depths)

### BEV Segmentation Loading

The `LoadBEVSegmentation` class loads bird's-eye view segmentation maps, which are used for training the segmentation head.

```mermaid
flowchart TD
    A["Input: location, pose data"] --> B["LoadBEVSegmentation"]
    B --> C["Calculate patch box and angle"]
    C --> D["Load map layers from NuScenesMap"]
    D --> E["Process layers based on class mappings"]
    E --> F["Create binary segmentation masks"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:243-313]()

Key implementation details:
- Requires dataset root and location information
- Uses `NuScenesMap` to load map data for the specific location
- Creates masks for different map elements based on class mappings
- Transforms map data to the current ego vehicle's coordinate system
- Outputs binary segmentation masks for each class

## Data Loading Pipeline

In BEVFusion, the data loading components are organized into a pipeline that processes raw data into a format suitable for model training and inference. Each component is registered to the PIPELINES registry and can be configured in the dataset config file.

```mermaid
flowchart LR
    A["Raw Dataset"] --> B["Data Loading Pipeline"]
    
    subgraph "B"
        B1["LoadMultiViewImageFromFiles"] --> B2["LoadPointsFromFile"]
        B2 --> B3["LoadPointsFromMultiSweeps"]
        B3 --> B4["LoadRadarPointsMultiSweeps (optional)"]
        B4 --> B5["LoadAnnotations3D"]
        B5 --> B6["LoadBEVSegmentation (optional)"]
    end
    
    B --> C["Data Preprocessing"]
    C --> D["Data Augmentation"]
    D --> E["Data Formatting"]
    E --> F["Model Training/Inference"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:21-794]()

The pipeline follows these general steps:

1. Load multi-view camera images
2. Load LiDAR point cloud data for the current frame
3. Load and combine point clouds from multiple frames (if needed)
4. Load radar data from multiple frames (if used)
5. Load 3D annotations (for training)
6. Load BEV segmentation maps (if segmentation is used)

Each component in the pipeline takes a `results` dictionary as input, processes it, and returns the updated dictionary with additional data and metadata. This incremental approach allows for flexibility in constructing different data loading pipelines for different tasks.

## Key Implementation Details

### Data Format Standardization

All data loading components standardize their outputs to ensure compatibility with subsequent pipeline stages:

- Images are stored as lists of PIL Image objects
- Point clouds are converted to subclasses of `BasePoints` (e.g., `LiDARPoints`, `RadarPoints`)
- 3D bounding boxes are stored in the format expected by the detection head
- Segmentation masks are stored as binary arrays

### Coordinate System Handling

When loading data from multiple sensors or timestamps, coordinate transformations are applied to ensure all data is in a consistent coordinate system:

```mermaid
flowchart TD
    A["Sensor Coordinate System"] --> B["Ego Vehicle Coordinate System"]
    B --> C["LiDAR Coordinate System"]
    C --> D["Global Coordinate System"]
```

Sources: [mmdet3d/datasets/pipelines/loading.py:86-240](), [mmdet3d/datasets/pipelines/loading.py:575-794]()

- Camera-to-LiDAR transformations are applied using `sensor2lidar_rotation` and `sensor2lidar_translation`
- Previous sweeps are transformed to the current frame using temporal transformations
- Map data is transformed to the ego vehicle's coordinate system for BEV segmentation

### Temporal Information Management

For multi-sweep loading, temporal information is preserved:

- Points from previous sweeps are tagged with a timestamp difference
- Velocity information is optionally compensated based on ego vehicle motion
- Sweeps can be selected randomly (for training) or sequentially (for testing)

### Feature Encoding

Point cloud and radar data can undergo feature encoding:

- One-hot encoding for categorical features
- Ordinal encoding for ordered features
- Custom filtering based on feature values
- Feature normalization to specified ranges

## Conclusion

The data loading components in BEVFusion provide a flexible and efficient way to load, transform, and prepare multimodal data for 3D object detection and segmentation. By supporting various data sources and formats, BEVFusion can effectively utilize camera, LiDAR, and radar data in a unified framework.

For information about what happens to the data after loading, see [Data Augmentation & Transformation](#3.2) and [Data Formatting](#3.3).

---

# Page: Data Augmentation & Transformation

# Data Augmentation & Transformation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/datasets/pipelines/transforms_3d.py](mmdet3d/datasets/pipelines/transforms_3d.py)

</details>



## Purpose and Scope

This document details the data augmentation and transformation techniques used in the BEVFusion framework for 3D object detection and segmentation. These operations are crucial for enhancing model robustness, preventing overfitting, and adapting input data to the required formats. The document covers transformations for both LiDAR point clouds and camera images, as well as transformations that operate on 3D bounding boxes and other metadata.

For information about data loading, see [Data Loading](#3.1), and for data formatting, see [Data Formatting](#3.3).

## Overview of Augmentation Pipeline

Data augmentation in BEVFusion follows a sequential pipeline where various transformations are applied to the input data. These transformations can be broadly categorized into camera-based transformations, LiDAR-based transformations, and joint transformations.

```mermaid
flowchart TD
    subgraph "Data Augmentation Pipeline"
        A["Raw Input Data"] --> B["Global Transformations"]
        B --> C["Modality-Specific Transformations"]
        C --> D["Object-level Transformations"]
        D --> E["Point-level Transformations"]
        E --> F["Filtering Operations"]
        F --> G["Final Augmented Data"]
    end

    subgraph "Global Transformations"
        B1["GlobalRotScaleTrans"]
        B2["RandomFlip3D"]
    end

    subgraph "Modality-Specific Transformations"
        C1["Camera Image Augmentations"]
        C2["LiDAR Point Cloud Augmentations"]
    end

    subgraph "Camera Image Augmentations"
        C1_1["ImageAug3D"]
        C1_2["ImagePad"]
        C1_3["ImageNormalize"]
        C1_4["ImageDistort"]
        C1_5["GridMask"]
    end

    subgraph "LiDAR Point Cloud Augmentations"
        C2_1["PointShuffle"]
        C2_2["PointSample"]
        C2_3["VoxelBasedPointSampler"]
        C2_4["FrameDropout"]
    end

    subgraph "Object-level Transformations"
        D1["ObjectPaste"]
        D2["ObjectNoise"]
    end

    subgraph "Filtering Operations"
        F1["PointsRangeFilter"]
        F2["ObjectRangeFilter"]
        F3["ObjectNameFilter"]
        F4["BackgroundPointsFilter"]
    end
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:196-232](), [mmdet3d/datasets/pipelines/transforms_3d.py:323-353](), [mmdet3d/datasets/pipelines/transforms_3d.py:97-192](), [mmdet3d/datasets/pipelines/transforms_3d.py:935-988](), [mmdet3d/datasets/pipelines/transforms_3d.py:991-1006](), [mmdet3d/datasets/pipelines/transforms_3d.py:1009-1091](), [mmdet3d/datasets/pipelines/transforms_3d.py:236-320](), [mmdet3d/datasets/pipelines/transforms_3d.py:527-531](), [mmdet3d/datasets/pipelines/transforms_3d.py:638-736](), [mmdet3d/datasets/pipelines/transforms_3d.py:798-932](), [mmdet3d/datasets/pipelines/transforms_3d.py:508-524](), [mmdet3d/datasets/pipelines/transforms_3d.py:356-450](), [mmdet3d/datasets/pipelines/transforms_3d.py:452-505](), [mmdet3d/datasets/pipelines/transforms_3d.py:584-616](), [mmdet3d/datasets/pipelines/transforms_3d.py:534-581](), [mmdet3d/datasets/pipelines/transforms_3d.py:617-635](), [mmdet3d/datasets/pipelines/transforms_3d.py:740-795]()

## Global Transformations

Global transformations affect all aspects of the data, including point clouds, images, and annotations simultaneously to maintain consistency across different modalities.

### GlobalRotScaleTrans

This transformation applies global rotation, scaling, and translation to the entire scene, affecting both point clouds and ground-truth boxes.

```mermaid
flowchart LR
    A["Input Data"] --> B["GlobalRotScaleTrans"]
    B --> C["Output Data"]
    
    subgraph "Parameters"
        P1["resize_lim: Scale factor range"]
        P2["rot_lim: Rotation angle range"]
        P3["trans_lim: Translation range"]
        P4["is_train: Training mode flag"]
    end
    
    subgraph "Transformations"
        T1["Points Rotation"]
        T2["Points Translation"]
        T3["Points Scaling"]
        T4["Ground Truth Boxes Transformation"]
        T5["Augmentation Matrix Generation"]
    end
    
    B --> T1
    B --> T2
    B --> T3
    B --> T4
    B --> T5
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:196-232]()

### RandomFlip3D

Randomly flips the point clouds, objects, and masks in either horizontal or vertical direction.

| Parameter | Description |
|-----------|-------------|
| None | This class does not require parameters. It randomly decides whether to flip horizontally and vertically. |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:323-353]()

## Camera Image Transformations

These transformations specifically target the camera images to improve model generalization on image data.

### ImageAug3D

`ImageAug3D` applies a series of geometric transformations to the camera images:

```mermaid
flowchart TD
    A["Input Image"] --> B["Resize"]
    B --> C["Crop"]
    C --> D["Random Flip (Optional)"]
    D --> E["Rotation"]
    E --> F["Transform Matrix Calculation"]
    F --> G["Augmented Image + Transform Matrix"]

    subgraph "Parameters"
        P1["final_dim: Target dimensions"]
        P2["resize_lim: Resize scale range"]
        P3["bot_pct_lim: Bottom crop percentage"]
        P4["rot_lim: Rotation angle range"]
        P5["rand_flip: Enable random flipping"]
        P6["is_train: Training mode flag"]
    end
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:97-192]()

### ImageNormalize

Normalizes images using mean and standard deviation values.

| Parameter | Description |
|-----------|-------------|
| `mean` | Mean values for each channel |
| `std` | Standard deviation values for each channel |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:991-1006]()

### ImagePad

Pads images to either a fixed size or to a size divisible by a specific number.

| Parameter | Description |
|-----------|-------------|
| `size` | Fixed padding size (tuple) |
| `size_divisor` | The divisor of padded size (int) |
| `pad_val` | Padding value (default: 0) |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:935-988]()

### ImageDistort

Applies photometric distortions to improve model robustness to lighting changes.

```mermaid
flowchart TD
    A["Input Image"] --> B["Random Brightness"]
    B --> C{"Mode?"}
    C -->|"Mode 0"| D0["Random Contrast"]
    C -->|"Mode 1"| D1["Skip Contrast"]
    D0 --> E["Convert BGR to HSV"]
    D1 --> E
    E --> F["Random Saturation"]
    F --> G["Random Hue"]
    G --> H["Convert HSV to BGR"]
    H --> I{"Mode?"}
    I -->|"Mode 0"| J0["Skip Contrast"]
    I -->|"Mode 1"| J1["Random Contrast"]
    J0 --> K["Random Channel Swap"]
    J1 --> K
    K --> L["Distorted Image"]
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:1009-1091]()

### GridMask

Applies a grid mask to images for regularization.

| Parameter | Description |
|-----------|-------------|
| `use_h` | Whether to apply grid mask on height |
| `use_w` | Whether to apply grid mask on width |
| `max_epoch` | Maximum epoch for probability calculation |
| `rotate` | Mask rotation options |
| `offset` | Whether to use offset |
| `ratio` | Ratio of grid to cell size |
| `mode` | Mode of operation (0 or 1) |
| `prob` | Initial probability |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:236-320]()

## LiDAR Point Cloud Transformations

These transformations are specific to point cloud data to enhance model generalization on LiDAR inputs.

### PointShuffle

Randomly shuffles the point cloud to eliminate any order bias.

| Parameter | Description |
|-----------|-------------|
| None | This class does not require parameters |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:527-531]()

### PointSample

Samples a subset of points from the point cloud, optionally prioritizing points based on distance.

```mermaid
flowchart LR
    A["Input Points"] --> B["PointSample"]
    B --> C["Output Points"]
    
    subgraph "Parameters"
        P1["num_points: Number of points to sample"]
        P2["sample_range: Prioritize points within range"]
        P3["replace: Sample with replacement"]
    end
    
    subgraph "Algorithm"
        S1["Calculate depths"]
        S2["Separate far and near points"]
        S3["Sample from near points"]
        S4["Combine with far points"]
        S5["Shuffle combined points"]
    end
    
    B --> S1 --> S2 --> S3 --> S4 --> S5
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:638-736]()

### VoxelBasedPointSampler

Samples points based on voxel representation, useful for balancing point distribution.

| Parameter | Description |
|-----------|-------------|
| `cur_sweep_cfg` | Config for sampling current sweep points |
| `prev_sweep_cfg` | Config for sampling previous sweep points |
| `time_dim` | Index of time dimension in point feature |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:798-932]()

### FrameDropout

Randomly drops temporal frames from the point cloud to simulate sensor data loss.

| Parameter | Description |
|-----------|-------------|
| `prob` | Probability of dropping a frame |
| `time_dim` | Index of time dimension in point feature |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:508-524]()

## Object-level Transformations

These transformations operate on 3D objects (bounding boxes) to augment the training data.

### ObjectPaste

Pastes objects from a database into the current scene, useful for augmenting rare classes.

```mermaid
flowchart TD
    A["Input Data"] --> B["ObjectPaste"]
    B --> C["Sample objects from database"]
    C --> D["Remove points in sampled box regions"]
    D --> E["Add sampled objects' points"]
    E --> F["Update GT bounding boxes"]
    F --> G["Augmented Data"]

    subgraph "Parameters"
        P1["db_sampler: Database sampler configuration"]
        P2["sample_2d: Whether to paste 2D image patches"]
        P3["stop_epoch: Epoch to stop this augmentation"]
    end
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:356-450]()

### ObjectNoise

Adds noise to ground truth objects' position, rotation, and global orientation.

| Parameter | Description |
|-----------|-------------|
| `translation_std` | Standard deviation for translation noise |
| `global_rot_range` | Range for global rotation noise |
| `rot_range` | Range for per-object rotation noise |
| `num_try` | Number of attempts for valid noise application |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:452-505]()

## Filtering Operations

These operations filter data points based on various criteria to focus on relevant information.

### PointsRangeFilter

Filters points outside a specified 3D range.

| Parameter | Description |
|-----------|-------------|
| `point_cloud_range` | 3D range specification [x_min, y_min, z_min, x_max, y_max, z_max] |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:584-616]()

### ObjectRangeFilter

Filters objects whose centers are outside a specified BEV (bird's-eye view) range.

| Parameter | Description |
|-----------|-------------|
| `point_cloud_range` | 3D range specification [x_min, y_min, z_min, x_max, y_max, z_max] |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:534-581]()

### ObjectNameFilter

Filters objects based on their class names.

| Parameter | Description |
|-----------|-------------|
| `classes` | List of class names to keep |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:617-635]()

### BackgroundPointsFilter

Removes background points near ground truth bounding boxes.

| Parameter | Description |
|-----------|-------------|
| `bbox_enlarge_range` | Range to enlarge bounding boxes for filtering |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:740-795]()

## Integration with Data Pipeline

The augmentation and transformation operations are integrated into the BEVFusion data pipeline using a modular design. Each transformation is registered with the `PIPELINES` registry and can be configured in the pipeline configuration files.

```mermaid
flowchart LR
    A["Raw Data"] --> B["Data Loading"]
    B --> C["Data Augmentation & Transformation"]
    C --> D["Data Formatting"]
    D --> E["Model Training/Inference"]
    
    subgraph "Pipeline Registration"
        R1["@PIPELINES.register_module()"]
        R2["Pipeline Configuration"]
        R3["Transform Class Implementation"]
    end
    
    R1 --> R3
    R2 --> C
    
    subgraph "Data Augmentation & Transformation"
        C1["Global Transformations"]
        C2["Camera Image Transformations"]
        C3["LiDAR Point Cloud Transformations"]
        C4["Object-level Transformations"]
        C5["Filtering Operations"]
    end
```

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:25-1091]()

## Commonly Used Transformation Combinations

Based on the BEVFusion implementation, here are commonly used transformation combinations for different scenarios:

### For Camera-only Models

| Transformation | Purpose |
|----------------|---------|
| `ImageAug3D` | Geometric augmentations |
| `ImageNormalize` | Normalize image values |
| `ImagePad` | Ensure consistent image sizes |
| `ImageDistort` | Photometric augmentations |

### For LiDAR-only Models

| Transformation | Purpose |
|----------------|---------|
| `GlobalRotScaleTrans` | Global geometric augmentations |
| `RandomFlip3D` | Additional geometric augmentation |
| `PointsRangeFilter` | Focus on relevant region |
| `ObjectRangeFilter` | Remove out-of-range objects |
| `PointShuffle` | Eliminate order bias |
| `ObjectPaste` | Augment rare classes |

### For Multi-modal Fusion Models

A combination of both camera and LiDAR transformations is used, with special attention to maintaining consistency between the two modalities through the use of transformation matrices that are shared between modalities.

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:25-1091]()

## Special Transformations for Multi-modal Fusion

### GTDepth

Generates ground truth depth maps from LiDAR point clouds, which is crucial for certain multi-modal fusion approaches.

| Parameter | Description |
|-----------|-------------|
| `keyframe_only` | Whether to use only keyframe points |

Sources: [mmdet3d/datasets/pipelines/transforms_3d.py:25-94]()

## Conclusion

BEVFusion employs a comprehensive set of data augmentation and transformation techniques to enhance model robustness and performance. These techniques are carefully designed to work with both camera and LiDAR modalities, ensuring consistent transformations across different data sources. The modular design allows for easy configuration and combination of different transformations based on specific requirements.

---

# Page: Data Formatting

# Data Formatting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/datasets/pipelines/formating.py](mmdet3d/datasets/pipelines/formating.py)

</details>



This document details the data formatting subsystem of BEVFusion, which is responsible for transforming processed data into model-ready formats. Data formatting is the final step in the data preprocessing pipeline before the data is fed into the model for training or inference. For information about data loading and augmentation, see [Data Loading](#3.1) and [Data Augmentation & Transformation](#3.2).

## Overview of Data Formatting

Data formatting in BEVFusion serves to standardize the representation of various data types (images, point clouds, bounding boxes, labels, etc.) into consistent formats that can be efficiently processed by deep learning models. The formatting process handles both data type conversion and structural organization.

```mermaid
flowchart LR
    A["Augmented/Transformed Data"] --> B["DefaultFormatBundle3D"]
    B --> C["Formatted Data"]
    C --> D["Collect3D"]
    D --> E["Model-Ready Data"]
    
    subgraph "Data Elements"
        F1["Points"]
        F2["Voxels"]
        F3["Images"]
        F4["Bounding Boxes"]
        F5["Labels"]
        F6["Metadata"]
    end
    
    F1 --> B
    F2 --> B
    F3 --> B
    F4 --> B
    F5 --> B
    F6 --> D
```

Sources: [mmdet3d/datasets/pipelines/formating.py:13-127]()

## Key Components

BEVFusion implements two primary components for data formatting:

1. **DefaultFormatBundle3D**: Converts various data types to tensors and wraps them in DataContainer objects
2. **Collect3D**: Organizes the formatted data and metadata into the final structure expected by the model

### DefaultFormatBundle3D

The `DefaultFormatBundle3D` class handles the conversion of various data elements into the appropriate tensor formats and wraps them in `DataContainer` objects for efficient batch processing.

```mermaid
classDiagram
    class DefaultFormatBundle3D {
        +class_names: list
        +with_gt: bool
        +with_label: bool
        +__call__(results): dict
    }
    
    class "Data Types" {
        +Points
        +Radar data
        +Voxels
        +GT bounding boxes
        +GT labels
        +Images
    }
    
    class "Converted Types" {
        +Tensors
        +DataContainer objects
    }
    
    DefaultFormatBundle3D --> "Data Types" : Processes
    DefaultFormatBundle3D --> "Converted Types" : Produces
```

Sources: [mmdet3d/datasets/pipelines/formating.py:13-127]()

The `DefaultFormatBundle3D` handles the following types of data:

| Data Type | Processing |
|-----------|------------|
| Points | Converted to tensor and wrapped in DataContainer |
| Radar | Converted to tensor and wrapped in DataContainer |
| Voxels/Coordinates | Converted to tensor and wrapped in DataContainer |
| Ground-truth 3D bounding boxes | Processed based on masks, converted to tensor, and wrapped in DataContainer |
| Ground-truth labels | Generated from class names and converted to appropriate format |
| Images | Stacked into a single tensor and wrapped in DataContainer |

Key features of DefaultFormatBundle3D:

1. **Mask Application**: Applies masks to filter out invalid bounding boxes and their associated labels
2. **Label Conversion**: Converts class names to numeric indices based on the provided class list
3. **Tensor Conversion**: Transforms numpy arrays into PyTorch tensors
4. **DataContainer Wrapping**: Wraps the tensors in DataContainer objects for efficient batch processing

Sources: [mmdet3d/datasets/pipelines/formating.py:13-127]()

### Collect3D

The `Collect3D` class is responsible for collecting and organizing the formatted data and metadata into the final structure that will be passed to the model.

```mermaid
classDiagram
    class Collect3D {
        +keys: list
        +meta_keys: tuple
        +meta_lis_keys: tuple
        +__call__(results): dict
    }
    
    class "Data" {
        +img
        +points
        +voxels
        +gt_bboxes
        +gt_labels
        +etc.
    }
    
    class "Meta Keys" {
        +camera_intrinsics
        +camera2ego
        +img_aug_matrix
        +lidar_aug_matrix
    }
    
    class "Meta List Keys" {
        +filename
        +timestamp
        +lidar2image
        +box_mode_3d
        +etc.
    }
    
    class "Output" {
        +data: dict
        +metas: DataContainer
    }
    
    Collect3D --> "Data" : Collects
    Collect3D --> "Meta Keys" : Processes
    Collect3D --> "Meta List Keys" : Processes
    Collect3D --> "Output" : Produces
```

Sources: [mmdet3d/datasets/pipelines/formating.py:130-200]()

`Collect3D` organizes the data into two main components:

1. **Data**: Contains the actual data elements (images, points, voxels, etc.) that will be processed by the model
2. **Metas**: Contains metadata (camera parameters, file paths, etc.) that provides context for the data

The keys to be included in each component are specified during initialization:

| Component | Key Types | Examples |
|-----------|-----------|----------|
| Data | Main data keys | 'img', 'points', 'voxels', 'gt_bboxes', 'gt_labels' |
| Data | Meta keys | 'camera_intrinsics', 'camera2ego', 'img_aug_matrix', 'lidar_aug_matrix' |
| Metas | List keys | 'filename', 'timestamp', 'lidar2image', 'box_mode_3d', etc. |

Sources: [mmdet3d/datasets/pipelines/formating.py:130-200]()

## Data Container

The `DataContainer` (DC) class from MMCV is a key component used throughout the formatting process. It serves as a wrapper for various data types and provides additional functionality for batch processing.

Key features of DataContainer:

1. **Stack Control**: Determines whether the data should be stacked into batches
2. **Padding Control**: Controls padding behavior for tensors of different shapes
3. **CPU/GPU Control**: Specifies whether the data should be kept on CPU or transferred to GPU

```mermaid
flowchart LR
    A["Raw Data"] --> B["to_tensor()"]
    B --> C["DataContainer"]
    C --> D1["stack=True"]
    C --> D2["stack=False"]
    C --> D3["cpu_only=True"]
    
    subgraph "Processing Path"
        E1["Images"] --> D1
        E2["Voxels"] --> D2
        E3["Metadata"] --> D3
    end
```

Sources: [mmdet3d/datasets/pipelines/formating.py:53-62](), [mmdet3d/datasets/pipelines/formating.py:104-126](), [mmdet3d/datasets/pipelines/formating.py:190-199]()

## Integration in the Data Pipeline

The formatting components are typically the final stages in the data processing pipeline, coming after data loading, preprocessing, and augmentation. They prepare the data for efficient batch processing during model training or inference.

```mermaid
flowchart LR
    A["Raw Data"] --> B["Data Loading"]
    B --> C["Data Preprocessing"]
    C --> D["Data Augmentation"]
    D --> E["DefaultFormatBundle3D"]
    E --> F["Collect3D"]
    F --> G["Model Training/Inference"]
    
    subgraph "Data Formatting"
        E
        F
    end
```

In the BEVFusion pipeline, these formatters are registered as pipeline components using the MMDET framework's registry system, which allows them to be easily configured and inserted into the data processing pipeline.

Sources: [mmdet3d/datasets/pipelines/formating.py:13-14](), [mmdet3d/datasets/pipelines/formating.py:130-131]()

## Example Data Flow

To better understand how data moves through the formatting process, let's trace the path of different data types:

1. **Point Cloud Data**:
   - Input: BasePoints object
   - DefaultFormatBundle3D: Converts to tensor and wraps in DataContainer
   - Collect3D: Includes in output data dictionary if specified in keys

2. **Image Data**:
   - Input: List of tensors (one per camera)
   - DefaultFormatBundle3D: Stacks into a single tensor and wraps in DataContainer
   - Collect3D: Includes in output data dictionary if specified in keys

3. **3D Bounding Boxes**:
   - Input: BaseInstance3DBoxes object or array
   - DefaultFormatBundle3D: Filters using masks, converts to tensor, wraps in DataContainer
   - Collect3D: Includes in output data dictionary if specified in keys

4. **Metadata**:
   - Input: Various formats
   - DefaultFormatBundle3D: Generally does not process metadata
   - Collect3D: Collects specified metadata keys and wraps in a CPU-only DataContainer

Sources: [mmdet3d/datasets/pipelines/formating.py:40-127](), [mmdet3d/datasets/pipelines/formating.py:170-200]()

## Summary

The data formatting subsystem in BEVFusion ensures that all data is properly prepared for efficient processing by the model. It converts various data types to appropriate tensor formats, applies necessary transformations, and organizes the data into a structured format that facilitates batch processing during training and inference.

The combination of `DefaultFormatBundle3D` and `Collect3D` provides a flexible and efficient pipeline for formatting multi-modal data from cameras and LiDAR sensors, which is essential for the fusion-based approach of BEVFusion.

---

# Page: Model Components

# Model Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



This page provides an overview of the key components that form the BEVFusion model architecture. BEVFusion integrates data from camera and LiDAR sensors into a unified bird's-eye view (BEV) representation for 3D perception tasks in autonomous driving.

For information about the overall system architecture, see [System Architecture](#2), and for details on data processing prior to model components, see [Data Processing Pipeline](#3).

## Architecture Overview

BEVFusion's model architecture consists of five primary components:

1. **Camera Encoder**: Processes image data and extracts features
2. **LiDAR Encoder**: Processes point cloud data and extracts features
3. **View Transformation**: Transforms camera features to bird's-eye view
4. **Multi-Modal Fusion**: Combines camera and LiDAR features
5. **Task-Specific Heads**: Performs detection and segmentation tasks

```mermaid
flowchart TD
    subgraph "BEVFusion Model"
        A1["Camera Input"] --> B1["Camera Encoder"]
        A2["LiDAR Input"] --> B2["LiDAR Encoder"]
        B1 --> C1["LSSTransform"]
        C1 --> D1["Camera BEV Features"]
        B2 --> D2["LiDAR BEV Features"]
        D1 --> E["ConvFuser/Concatenation"]
        D2 --> E
        E --> F["Fused BEV Features"]
        F --> G1["CenterHead"]
        F --> G2["MapHead"]
        G1 --> H1["3D Object Detection"]
        G2 --> H2["BEV Map Segmentation"]
    end
```

Sources: [README.md:8-20]()

## Component Relationships

The following diagram details the relationships between model components and their specific implementations in the codebase:

```mermaid
graph TD
    A["BEVFusion Model"] --> B["Camera Encoder"]
    A --> C["LiDAR Encoder"]
    A --> D["View Transformation"]
    A --> E["Feature Fusion"]
    A --> F["Task Heads"]
    
    B --> B1["SwinTransformer"]
    B --> B2["FPN Neck"]
    
    C --> C1["VoxelBackbone"]
    C --> C2["SparseEncoder"]
    
    D --> D1["LSSTransform"]
    D --> D2["DepthLSSTransform"]
    
    E --> E1["ConvFuser"]
    E --> E2["Concatenation"]
    
    F --> F1["CenterHead"]
    F --> F2["MapHead"]
```

Sources: [README.md:10-60]()

## Camera Encoder

The Camera Encoder processes multi-view camera inputs to extract feature representations. It consists of two main components:

1. **Backbone**: Typically a SwinTransformer that extracts features from images
2. **Neck**: A Feature Pyramid Network (FPN) that builds a feature hierarchy

The camera encoder output is later transformed into a bird's-eye view representation through the View Transformation component.

```mermaid
flowchart LR
    A["Multi-view Images"] --> B["SwinTransformer"]
    B --> C["Feature Pyramid Network"]
    C --> D["2D Image Features"]
```

Sources: [README.md:30-50]()

## LiDAR Encoder

The LiDAR Encoder processes point cloud data to extract features. It employs efficient sparse convolutional networks to handle the sparse nature of LiDAR data.

The processing pipeline includes:

1. **Voxelization**: Converting point cloud into a regular grid of voxels
2. **Feature Extraction**: Using sparse convolutions to extract features
3. **BEV Projection**: Projecting features to the bird's-eye view

```mermaid
flowchart LR
    A["Point Cloud"] --> B["Voxelization"]
    B --> C["SparseEncoder"]
    C --> D["LiDAR BEV Features"]
```

Sources: [README.md:30-50]()

## View Transformation

The View Transformation component converts 2D image features from the camera's perspective to a 3D bird's-eye view representation. This is a critical step for aligning camera features with LiDAR features in a common coordinate space.

BEVFusion implements two types of view transformations:

1. **LSSTransform**: The standard Lift-Splat-Shoot transformation
2. **DepthLSSTransform**: An enhanced version that incorporates depth information

The key operations in this process include:

| Operation | Description |
|-----------|-------------|
| Frustum Calculation | Computes view frustums based on camera intrinsics and extrinsics |
| Geometry Computation | Determines the mapping between image space and BEV space |
| BEV Pooling | Efficiently pools features into the BEV grid using custom CUDA operations |

This component is significantly optimized in BEVFusion, with the BEV pooling operation reducing latency by more than 40x compared to previous methods.

```mermaid
flowchart TD
    A["2D Image Features"] --> B["get_geometry"]
    C["Camera Intrinsics"] --> B
    D["Camera Extrinsics"] --> B
    B --> E["Frustum Calculation"]
    E --> F["bev_pool"]
    F --> G["Camera BEV Features"]
```

Sources: [README.md:20-52]()

## Multi-Modal Fusion

The Multi-Modal Fusion component combines features from camera and LiDAR modalities into a unified representation. BEVFusion supports two main fusion strategies:

1. **ConvFuser**: Uses convolutional layers to fuse features
2. **Concatenation**: Simple concatenation of features along the channel dimension

Both approaches operate on features already transformed to the bird's-eye view, which preserves both geometric and semantic information from different sensors.

```mermaid
flowchart LR
    A["Camera BEV Features"] --> C{"Fusion Strategy"}
    B["LiDAR BEV Features"] --> C
    C -->|"ConvFuser"| D["Convolutional Fusion"]
    C -->|"Concatenation"| E["Channel Concatenation"]
    D --> F["Fused BEV Features"]
    E --> F
```

Sources: [README.md:20-52]()

## Detection and Segmentation Heads

The Task-Specific Heads component processes the fused BEV features to perform specific perception tasks. BEVFusion supports two main types of heads:

### Detection Head (CenterHead)

The detection head localizes and classifies 3D objects in the scene. It outputs:
- 3D bounding boxes
- Class probabilities
- Orientation estimates

### Segmentation Head (MapHead)

The segmentation head performs BEV map segmentation, identifying areas such as:
- Drivable areas
- Pedestrian crossings
- Lane markings

```mermaid
flowchart TD
    A["Fused BEV Features"] --> B["SECOND Decoder"]
    B --> C["CenterHead"]
    B --> D["MapHead"]
    C --> E["3D Object Detections"]
    D --> F["BEV Map Segmentation"]
```

Sources: [README.md:30-60]()

## Performance Metrics

BEVFusion achieves state-of-the-art performance on several benchmarks:

### 3D Object Detection (nuScenes validation)

| Model | Modality | mAP | NDS |
|-------|----------|-----|-----|
| BEVFusion | Camera+LiDAR | 68.52 | 71.38 |
| Camera-Only | Camera | 35.56 | 41.21 |
| LiDAR-Only | LiDAR | 64.68 | 69.28 |

### BEV Map Segmentation (nuScenes validation)

| Model | Modality | mIoU |
|-------|----------|------|
| BEVFusion | Camera+LiDAR | 62.95 |
| Camera-Only | Camera | 57.09 |
| LiDAR-Only | LiDAR | 48.56 |

Sources: [README.md:30-60]()

## Implementation Efficiency

BEVFusion is designed with computational efficiency in mind:

- Optimized BEV pooling operations reduce latency by more than 40x
- The architecture maintains real-time inference capabilities
- Optimized deployment solutions can achieve 25 FPS on NVIDIA Jetson Orin platforms

These optimizations make BEVFusion practical for real-world autonomous driving applications where computational resources may be limited and real-time performance is critical.

Sources: [README.md:10-20]()

---

# Page: Camera Encoder

# Camera Encoder

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml](configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml)
- [configs/nuscenes/det/centerhead/lssfpn/camera/default.yaml](configs/nuscenes/det/centerhead/lssfpn/camera/default.yaml)

</details>



## Purpose and Scope

This document details the Camera Encoder component within the BEVFusion framework. The Camera Encoder processes raw camera image inputs and transforms them into bird's-eye view (BEV) feature representations. These BEV features can then be fused with LiDAR BEV features as part of the multi-modal fusion process. For information about LiDAR processing, see [LiDAR Encoder](#4.2), and for details on how these features are combined, see [Multi-Modal Fusion](#4.4).

## Architecture Overview

The Camera Encoder consists of three main sequential components: a backbone network for feature extraction, a neck network for feature refinement, and a view transformation module for converting perspective view features to BEV representation.

```mermaid
flowchart LR
    subgraph "Camera_Encoder"
        direction LR
        A["Camera Images"] --> B["SwinTransformer\nBackbone"]
        B --> C["GeneralizedLSSFPN\nNeck"]
        C --> D["LSSTransform\nView Transformation"]
        D --> E["Camera BEV Features"]
    end
```

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:2-46](), [configs/nuscenes/det/centerhead/lssfpn/camera/default.yaml:8-17]()

## Components

### SwinTransformer Backbone

The Camera Encoder uses the Swin Transformer (Shifted Window Transformer) as its backbone network. This hierarchical vision transformer is particularly effective for visual feature extraction.

```mermaid
flowchart TD
    A["Input Images"] --> B["Patch Embedding"]
    B --> C["Swin Transformer Block (Stage 1)\ndepth=2, dim=96, heads=3"]
    C --> D["Patch Merging"]
    D --> E["Swin Transformer Block (Stage 2)\ndepth=2, dim=192, heads=6"]
    E --> F["Patch Merging"]
    F --> G["Swin Transformer Block (Stage 3)\ndepth=6, dim=384, heads=12"]
    G --> H["Patch Merging"]
    H --> I["Swin Transformer Block (Stage 4)\ndepth=2, dim=768, heads=24"]
    C -- "out_indices[0]" --> J["Output Features"]
    E -- "out_indices[1]" --> J
    G -- "out_indices[2]" --> J
```

#### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| embed_dims | 96 | Initial embedding dimension |
| depths | [2, 2, 6, 2] | Number of transformer blocks in each stage |
| num_heads | [3, 6, 12, 24] | Number of attention heads in each stage |
| window_size | 7 | Size of the attention window |
| mlp_ratio | 4 | Expansion ratio for MLP layers |
| drop_path_rate | 0.2 | Stochastic depth rate |
| out_indices | [1, 2, 3] | Indices of output stages (zero-indexed) |
| init_cfg | Pretrained | Uses pretrained weights |

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:4-22]()

### GeneralizedLSSFPN Neck

The neck component is a Generalized Lift-Splat-Shoot Feature Pyramid Network (GeneralizedLSSFPN) that processes and refines the multi-scale features from the backbone.

```mermaid
flowchart LR
    A["Backbone Features\n[192, 384, 768]"] --> B["GeneralizedLSSFPN"]
    B --> C["Unified Feature Map\n(out_channels=256)"]

    subgraph "GeneralizedLSSFPN"
        direction TB
        D["Lateral Connections"] --> E["Feature Fusion"]
        E --> F["Upsampling"]
        F --> G["BN + ReLU"]
    end
```

#### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| in_channels | [192, 384, 768] | Input channel dimensions from backbone |
| out_channels | 256 | Output channel dimension |
| start_level | 0 | Starting level from input |
| num_outs | 3 | Number of output scales |
| norm_cfg | BN2d | Batch normalization type |
| act_cfg | ReLU, inplace=true | Activation function |
| upsample_cfg | bilinear, align_corners=false | Upsampling method |

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:23-37]()

### LSSTransform View Transformation

The LSSTransform module converts the 2D image features into a 3D BEV representation, which is a critical step for fusion with LiDAR features.

```mermaid
flowchart TD
    A["Image Features\n(256 channels)"] --> B["LSSTransform"]
    C["Camera Intrinsics"] --> B
    D["Camera Extrinsics"] --> B
    
    subgraph "LSSTransform"
        direction TB
        E["Feature Projection"] --> F["Depth Prediction"]
        F --> G["3D Frustum Generation"]
        G --> H["BEV Pooling"]
    end
    
    B --> I["BEV Features\n(80 channels)"]
```

#### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| type | LSSTransform | Lift-Splat-Shoot transformation |
| in_channels | 256 | Input channel dimension |
| out_channels | 80 | Output channel dimension |
| feature_size | [image_height/8, image_width/8] | Feature map size |
| xbound | [-51.2, 51.2, 0.4] | X-axis range and resolution |
| ybound | [-51.2, 51.2, 0.4] | Y-axis range and resolution |
| zbound | [-10.0, 10.0, 20.0] | Z-axis range and resolution |
| dbound | [1.0, 60.0, 0.5] | Depth range and resolution |
| downsample | 2 | Downsample factor for BEV features |

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:38-46](), [configs/nuscenes/det/centerhead/lssfpn/camera/default.yaml:10-17]()

## Integration with BEVFusion

The Camera Encoder is a fundamental component in the BEVFusion pipeline, working in parallel with the LiDAR Encoder to produce complementary BEV features that are subsequently fused.

```mermaid
flowchart TD
    subgraph "BEVFusion Architecture"
        direction LR
        A1["Camera Input"] --> B1["Camera Encoder"]
        A2["LiDAR Input"] --> B2["LiDAR Encoder"]
        
        subgraph "Camera_Encoder_Details"
            direction TB
            C1["SwinTransformer"] --> D1["GeneralizedLSSFPN"]
            D1 --> E1["LSSTransform"]
        end
        
        B1 -.-> C1
        E1 --> F1["Camera BEV Features"]
        B2 --> F2["LiDAR BEV Features"]
        F1 --> G["Feature Fusion"]
        F2 --> G
        G --> H["Fused BEV Features"]
        H --> I1["Detection Head"]
        H --> I2["Segmentation Head"]
    end
```

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:2-46](), [configs/nuscenes/det/centerhead/lssfpn/camera/default.yaml:8-17]()

## Training Configuration

The Camera Encoder has specific optimization parameters to ensure effective training:

```mermaid
flowchart TD
    A["Optimizer Configuration"] --> B["Parameter-wise Settings"]
    B --> C["Backbone Learning Rate\n(lr_mult=0.1)"]
    B --> D["Position Embedding\n(decay_mult=0)"]
    B --> E["Relative Position Bias\n(decay_mult=0)"]
    
    F["Learning Rate Policy"] --> G["Cyclic Schedule"]
    G --> H["target_ratio=5.0\ncyclic_times=1\nstep_ratio_up=0.4"]
    
    I["Momentum Config"] --> J["Cyclic Schedule"]
    J --> K["cyclic_times=1\nstep_ratio_up=0.4"]
```

The Camera Encoder backbone uses a lower learning rate multiplier (0.1) compared to other components, which helps stabilize training since it uses pretrained weights.

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:62-82]()

## Batch Size Configuration

The default batch size for training with camera-only data is 4 samples per GPU.

Sources: [configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml:84-85]()

---

# Page: LiDAR Encoder

# LiDAR Encoder

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/nuscenes/det/centerhead/lssfpn/default.yaml](configs/nuscenes/det/centerhead/lssfpn/default.yaml)

</details>



The LiDAR Encoder is a critical component of the BEVFusion system responsible for processing 3D point cloud data from LiDAR sensors and transforming it into bird's-eye view (BEV) features. This document explains the architecture, processing workflow, and implementation details of the LiDAR encoding pipeline. For information about processing camera data, see [Camera Encoder](#4.1), and for details on how the outputs of both encoders are combined, see [Multi-Modal Fusion](#4.4).

## Overview

The LiDAR Encoder converts sparse, unstructured 3D point cloud data into structured BEV feature maps that can be effectively processed by subsequent neural network layers. Its primary functions include:

- Converting raw point cloud data into voxel representations
- Processing these voxels through sparse convolutional networks
- Generating BEV feature maps that capture the geometric information of the scene

```mermaid
flowchart LR
    A["Raw LiDAR Points"] --> B["Voxelization"]
    B --> C["VoxelBackbone"]
    C --> D["SparseEncoder"]
    D --> E["LiDAR BEV Features"]
    
    style A fill:none,stroke:#333
    style B fill:none,stroke:#333
    style C fill:none,stroke:#333
    style D fill:none,stroke:#333
    style E fill:none,stroke:#333
```

*Diagram: High-level processing flow of the LiDAR Encoder*

Sources: System architecture diagrams provided in the introduction

## Architecture Components

The LiDAR Encoder consists of several key components that work together to process point cloud data efficiently:

### Voxelization

The first step in the LiDAR encoding process is voxelization, which discretizes the continuous 3D point cloud into a grid of voxels (3D volumes).

Key characteristics:
- Converts irregular point clouds into regular 3D grids
- Reduces computational complexity by grouping points
- Creates a sparse tensor representation where only occupied voxels are processed

### VoxelBackbone

The VoxelBackbone is responsible for initial feature extraction from voxelized point cloud data:

- Processes voxel features through a series of 3D sparse convolutions
- Maintains sparsity of the data to ensure computational efficiency
- Extracts hierarchical features at multiple scales

### SparseEncoder

The SparseEncoder is the core component that efficiently processes the sparse voxel representation:

- Implements sparse convolutions to handle the sparse nature of LiDAR data
- Focuses computation only on occupied voxels, significantly reducing memory and computational requirements
- Builds increasingly abstract feature representations through multiple layers

```mermaid
flowchart TD
    subgraph "LiDAR Encoder Architecture"
        A["Point Cloud Input"] --> B["Voxelization"]
        B --> |"Sparse Voxel Tensor"| C["VoxelBackbone"]
        C --> D["SparseEncoder"]
        
        subgraph "SparseEncoder Internals"
            D1["Sparse Convolution Blocks"]
            D2["Downsampling Layers"]
            D3["Feature Extraction"]
        end
        
        D --- D1
        D --- D2
        D --- D3
        
        D --> E["BEV Feature Projection"]
        E --> F["LiDAR BEV Features"]
    end
    
    style A fill:none,stroke:#333
    style B fill:none,stroke:#333
    style C fill:none,stroke:#333
    style D fill:none,stroke:#333
    style D1 fill:none,stroke:#333
    style D2 fill:none,stroke:#333
    style D3 fill:none,stroke:#333
    style E fill:none,stroke:#333
    style F fill:none,stroke:#333
```

*Diagram: Detailed architecture of the LiDAR Encoder*

Sources: System architecture diagrams provided in the introduction

## Processing Pipeline

The LiDAR processing pipeline follows a systematic approach to transform raw point cloud data into structured BEV features:

1. **Point Cloud Preprocessing**:
   - Loading point cloud data from files
   - Filtering and sampling points to manage density
   - Applying initial transformations (rotation, translation)

2. **Voxelization Process**:
   - Defining voxel grid dimensions and resolution
   - Assigning points to voxels
   - Computing voxel features (e.g., mean of points within each voxel)

3. **Sparse Convolution Processing**:
   - Converting voxel grid to sparse tensors
   - Applying 3D sparse convolutions
   - Feature aggregation across multiple scales

4. **BEV Projection**:
   - Collapsing the height dimension through operations like max-pooling or concatenation
   - Creating a 2D bird's-eye view feature map

```mermaid
flowchart LR
    subgraph "Point Cloud Processing"
        A1["LoadPointsFromFile"] --> A2["LoadPointsFromMultiSweeps"]
        A2 --> A3["Point Cloud Filtering"]
    end
    
    subgraph "Voxelization"
        B1["Define Voxel Grid"] --> B2["Assign Points to Voxels"]
        B2 --> B3["Compute Voxel Features"]
    end
    
    subgraph "Sparse Processing"
        C1["Sparse Tensor Conversion"] --> C2["3D Sparse Convolutions"]
        C2 --> C3["Multi-scale Feature Extraction"]
    end
    
    subgraph "BEV Conversion"
        D1["Height Dimension Collapse"] --> D2["2D BEV Feature Map"]
    end
    
    A3 --> B1
    B3 --> C1
    C3 --> D1
    
    style A1 fill:none,stroke:#333
    style A2 fill:none,stroke:#333
    style A3 fill:none,stroke:#333
    style B1 fill:none,stroke:#333
    style B2 fill:none,stroke:#333
    style B3 fill:none,stroke:#333
    style C1 fill:none,stroke:#333
    style C2 fill:none,stroke:#333
    style C3 fill:none,stroke:#333
    style D1 fill:none,stroke:#333
    style D2 fill:none,stroke:#333
```

*Diagram: LiDAR data processing pipeline*

Sources: System architecture diagrams provided in the introduction

## Integration with BEVFusion

The LiDAR Encoder plays a critical role in the overall BEVFusion framework:

1. It processes LiDAR data independently from the Camera Encoder
2. Its output (LiDAR BEV features) is combined with Camera BEV features through the fusion mechanism
3. The fused features are used for both 3D object detection and BEV map segmentation

### Feature Dimensions and Compatibility

For successful fusion with camera features, the LiDAR BEV features need to:
- Match the spatial dimensions and resolution of the camera BEV features
- Be compatible in terms of feature channels for effective fusion
- Be aligned in the same coordinate system

Based on the configuration file, the final output channels from the decoder backbone are configured to be compatible with the fusion module:

| Component | Input Channels | Output Channels | Notes |
|-----------|---------------|-----------------|-------|
| Backbone | 336 | [160, 320, 640] | Multi-scale features |
| LSSFPN | [640, 160] | 256 | Feature aggregation |
| Detection Head | 256 | - | For object detection |

Sources: [configs/nuscenes/det/centerhead/lssfpn/default.yaml:11-28]()

## Technical Implementation Considerations

### Sparse Operations

The LiDAR Encoder heavily relies on sparse convolutional operations to efficiently process point cloud data. These operations:
- Avoid unnecessary computation on empty voxels
- Significantly reduce memory usage compared to dense operations
- Enable real-time processing of large point clouds

### Performance Optimizations

Several techniques are employed to optimize the LiDAR Encoder's performance:
- Strategic downsampling to balance detail and computational efficiency
- Hierarchical feature extraction to capture both local and global information
- Efficient implementation of sparse operations using CUDA

### Model Configuration

The decoder configuration (which processes the output of the LiDAR Encoder) uses:
- A GeneralizedResNet backbone with specific block configurations
- An LSSFPN neck to process multi-scale features
- Configurable output channels to interface with detection heads

```mermaid
flowchart TD
    subgraph "BEVFusion Context"
        LidarInput["LiDAR Input"] --> LidarEncoder["LiDAR Encoder"]
        CameraInput["Camera Input"] --> CameraEncoder["Camera Encoder"]
        
        LidarEncoder --> LidarBEV["LiDAR BEV Features"]
        CameraEncoder --> CameraBEV["Camera BEV Features"]
        
        LidarBEV --> Fusion["Feature Fusion"]
        CameraBEV --> Fusion
        
        Fusion --> FusedBEV["Fused BEV Features"]
        FusedBEV --> DetHead["Detection Head"]
        FusedBEV --> SegHead["Segmentation Head"]
        
        DetHead --> Detection["3D Object Detection"]
        SegHead --> Segmentation["BEV Map Segmentation"]
    end
    
    style LidarInput fill:none,stroke:#333
    style LidarEncoder fill:none,stroke:#333,stroke-width:3px
    style CameraInput fill:none,stroke:#333
    style CameraEncoder fill:none,stroke:#333
    style LidarBEV fill:none,stroke:#333
    style CameraBEV fill:none,stroke:#333
    style Fusion fill:none,stroke:#333
    style FusedBEV fill:none,stroke:#333
    style DetHead fill:none,stroke:#333
    style SegHead fill:none,stroke:#333
    style Detection fill:none,stroke:#333
    style Segmentation fill:none,stroke:#333
```

*Diagram: LiDAR Encoder in the context of the BEVFusion architecture*

Sources: System architecture diagrams provided in the introduction, [configs/nuscenes/det/centerhead/lssfpn/default.yaml:11-28]()

## Conclusion

The LiDAR Encoder is a specialized component designed to efficiently process point cloud data in the BEVFusion framework. Through voxelization and sparse convolution operations, it transforms unstructured 3D points into structured BEV feature maps that can be effectively fused with camera features for 3D perception tasks. The implementation emphasizes computational efficiency and feature quality, enabling real-time performance for autonomous driving applications.

---

# Page: View Transformation

# View Transformation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/models/vtransforms/base.py](mmdet3d/models/vtransforms/base.py)
- [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp](mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp)

</details>



## Purpose and Scope

The View Transformation component is responsible for converting 2D camera-based features into a bird's-eye view (BEV) representation. This critical process enables the multi-modal fusion of camera and LiDAR data by projecting both sensor modalities into a unified coordinate system. This page describes the architecture, process, and implementation of the view transformation module in BEVFusion.

For information about how the transformed camera features are fused with LiDAR features, see [Multi-Modal Fusion](#4.4).

Sources: [mmdet3d/models/vtransforms/base.py:24-177]()

## Architecture Overview

The view transformation pipeline consists of several key components that work together to transform camera-based features into BEV space.

```mermaid
flowchart TD
    subgraph "View Transformation Pipeline"
        A["Image Features"] --> B["Frustum Creation"]
        B --> C["Geometry Calculation"]
        C --> D["BEV Pooling"]
        D --> E["BEV Features"]
        
        F["Camera Intrinsics"] --> C
        G["Camera Extrinsics"] --> C
        H["Coordinate Transforms"] --> C
    end
```

The foundation of this process is implemented through the `BaseTransform` class, which provides the core functionality for transforming camera features into BEV space.

Sources: [mmdet3d/models/vtransforms/base.py:24-235]()

## Key Components

### BaseTransform Class

The `BaseTransform` class is the fundamental implementation of the view transformation module. It contains:

- Parameter initialization for BEV grid dimensions and depth bounds
- Frustum creation for camera view representation
- Coordinate transformations between camera, LiDAR, and BEV spaces
- BEV pooling operations to aggregate features into the BEV grid

```mermaid
classDiagram
    class BaseTransform {
        +in_channels: int
        +out_channels: int
        +image_size: Tuple[int, int]
        +feature_size: Tuple[int, int]
        +xbound, ybound, zbound: Tuple[float, float, float]
        +dbound: Tuple[float, float, float]
        +frustum: Parameter
        +create_frustum()
        +get_geometry()
        +get_cam_feats()
        +bev_pool()
        +forward()
    }
    
    class BaseDepthTransform {
        +forward()
    }
    
    BaseTransform <|-- BaseDepthTransform
```

Sources: [mmdet3d/models/vtransforms/base.py:24-235](), [mmdet3d/models/vtransforms/base.py:238-361]()

## The Transformation Process

### 1. Frustum Creation

The frustum is a 3D representation of the camera's field of view at different depths. It serves as the basis for projecting 2D image features into 3D space.

```mermaid
flowchart LR
    subgraph "create_frustum()"
        A["Define depth range"] --> B["Create depth grid"]
        B --> C["Create x-y coordinates grid"]
        C --> D["Stack coordinates to form frustum"]
        D --> E["Return frustum as Parameter"]
    end
```

The frustum is created with dimensions corresponding to the feature map size and the depth range specified in the configuration.

Sources: [mmdet3d/models/vtransforms/base.py:65-89]()

### 2. Geometry Calculation

The `get_geometry` method performs the necessary coordinate transformations to convert points from camera view space to BEV space.

```mermaid
flowchart TD
    subgraph "get_geometry()"
        A["Frustum points"] --> B["Undo post-transformation"]
        B --> C["Apply camera-to-lidar transform"]
        C --> D["Apply additional rotations/translations"]
        D --> E["Return transformed points"]
    end
```

This process involves multiple matrix operations to transform the coordinates properly:
1. Undoing post-processing transformations
2. Applying camera-to-LiDAR transformations
3. Applying additional rotations/translations if specified

Sources: [mmdet3d/models/vtransforms/base.py:91-135]()

### 3. BEV Pooling

The BEV pooling operation aggregates image features from different views and depths into a unified BEV grid.

```mermaid
flowchart TD
    subgraph "bev_pool()"
        A["Flatten features"] --> B["Transform coordinates to BEV grid indices"]
        B --> C["Filter points outside BEV bounds"]
        C --> D["Call CUDA bev_pool operation"]
        D --> E["Collapse Z dimension"]
        E --> F["Return BEV features"]
    end
```

This step is the most computationally intensive part and is accelerated using a custom CUDA implementation.

Sources: [mmdet3d/models/vtransforms/base.py:140-176](), [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:13-47]()

## BEV Pooling CUDA Operation

The actual BEV pooling is implemented using a custom CUDA operation for efficiency. This operation maps the transformed 3D points to the BEV grid cells and aggregates the corresponding features.

```mermaid
flowchart LR
    subgraph "bev_pool CUDA Operation"
        A["Input Features (n, c)"] --> B["Input Coordinates (n, 4)"]
        B --> C["Calculate grid indices"]
        C --> D["Aggregate features by index"]
        D --> E["Output BEV Features (b, d, h, w, c)"]
    end
```

The CUDA operation takes the following inputs:
- Feature vectors from image features
- Geometric indices indicating where each feature maps to in the BEV grid
- Interval information for efficient aggregation
- Output dimensions for the BEV grid

Sources: [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:22-47](), [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:60-87]()

## Depth-Based View Transformation

For improved accuracy, BEVFusion also implements a depth-aware view transformation through the `BaseDepthTransform` class. This class enhances the basic transformation by incorporating depth information.

```mermaid
flowchart TD
    subgraph "BaseDepthTransform"
        A["Image Features"] --> B["Point Cloud Data (LiDAR/Radar)"]
        B --> C["Generate Depth Information"]
        C --> D["Standard View Transformation"]
        D --> E["BEV Features"]
    end
```

Key aspects of depth-based transformation:
- Can use either LiDAR or radar points for depth information
- Options for depth representation (scalar values or one-hot encoding)
- Optional feature enrichment by adding point features to depth information

Sources: [mmdet3d/models/vtransforms/base.py:238-361]()

## Forward Pass Implementation

The forward pass ties all these components together, implementing the full view transformation process.

```mermaid
flowchart LR
    subgraph "forward() Method"
        A["Extract transformation matrices"] --> B["Call get_geometry()"]
        B --> C["Extract camera features"]
        C --> D["Call bev_pool()"]
        D --> E["Return BEV features"]
    end
```

The forward method handles:
1. Extracting transformation matrices from inputs
2. Calculating geometry for the transformation
3. Extracting camera features
4. Applying BEV pooling
5. Returning the resulting BEV features

Sources: [mmdet3d/models/vtransforms/base.py:178-234]()

## Integration with BEVFusion

View transformation is a critical component in the BEVFusion pipeline, serving as the bridge between camera-based perception and 3D space.

```mermaid
flowchart LR
    subgraph "BEVFusion Data Flow"
        A["Camera Input"] --> B["Camera Encoder"]
        B --> C["BaseTransform/BaseDepthTransform"]
        C --> D["Camera BEV Features"]
        
        E["LiDAR Input"] --> F["LiDAR Encoder"]
        F --> G["LiDAR BEV Features"]
        
        D --> H["Feature Fusion"]
        G --> H
        H --> I["Detection/Segmentation Heads"]
    end
```

The view transformation converts camera features into the same coordinate system as LiDAR features, enabling effective multi-modal fusion.

Sources: [mmdet3d/models/vtransforms/base.py:24-361]()

## Coordinate System Handling

The view transformation process involves several coordinate system transformations, which are managed through a series of matrix operations.

```mermaid
flowchart TD
    subgraph "Coordinate Transformations"
        A["Camera Coordinates"] -->|"camera2lidar_rots, camera2lidar_trans"| B["LiDAR Coordinates"]
        B -->|"lidar2ego_rots, lidar2ego_trans"| C["Ego Vehicle Coordinates"]
        A -->|"camera2ego"| C
        D["Image Pixels"] -->|"camera_intrinsics"| A
        E["Image Augmentation"] -->|"img_aug_matrix"| D
        F["LiDAR Augmentation"] -->|"lidar_aug_matrix"| B
    end
```

These transformations ensure that features from different coordinate systems are properly aligned in the final BEV representation.

Sources: [mmdet3d/models/vtransforms/base.py:91-135](), [mmdet3d/models/vtransforms/base.py:194-215]()

## Technical Considerations

When implementing or modifying the view transformation component, consider:

1. **Memory Efficiency**: The transformation process can be memory-intensive, especially with high-resolution feature maps.
2. **Computational Performance**: The BEV pooling operation is computationally expensive and benefits from GPU acceleration.
3. **Coordinate System Consistency**: Ensure that all coordinate transformations are correctly defined and applied.
4. **Depth Information Quality**: When using depth-based transformation, the quality of depth information significantly affects the results.

Sources: [mmdet3d/models/vtransforms/base.py:140-176](), [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:13-47]()

---

# Page: Multi-Modal Fusion

# Multi-Modal Fusion

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



## Purpose and Scope

This document details how BEVFusion combines features from camera and LiDAR sensors into a unified representation. The multi-modal fusion component represents a critical innovation in BEVFusion's architecture, allowing it to leverage the complementary strengths of both sensor types. Unlike traditional point-level fusion approaches, BEVFusion performs fusion in the bird's-eye view (BEV) space, preserving both geometric and semantic information from different modalities.

For information about how individual modalities are processed before fusion, see [Camera Encoder](#4.1), [LiDAR Encoder](#4.2), and [View Transformation](#4.3).

## Fusion Architecture Overview

BEVFusion's multi-modal fusion differs fundamentally from traditional approaches by first transforming features from each modality into a shared BEV representation before fusion, rather than projecting camera features onto LiDAR points.

```mermaid
flowchart TD
    subgraph "Multi-Modal Fusion Pipeline"
        A1["Camera BEV Features"] --> C["Feature Fusion"]
        A2["LiDAR BEV Features"] --> C
        C --> D["Fused BEV Features"]
        D --> E1["Detection Head"]
        D --> E2["Segmentation Head"]
    end
    
    subgraph "Feature Space Alignments"
        B1["Camera Features: [B, C_cam, H, W]"] -.- A1
        B2["LiDAR Features: [B, C_lidar, H, W]"] -.- A2
        D -.- F["Fused Features: [B, C_fused, H, W]"]
    end
```

Sources: README.md

## Fusion Methods

BEVFusion supports two primary fusion methods for combining camera and LiDAR BEV features:

### 1. Concatenation Fusion

The simplest fusion approach is direct feature concatenation along the channel dimension. This preserves all information from both modalities without any information loss.

```mermaid
flowchart LR
    A1["Camera BEV Features\n[B, C_cam, H, W]"] --> B["Concatenation\nOperation"]
    A2["LiDAR BEV Features\n[B, C_lidar, H, W]"] --> B
    B --> C["Fused Features\n[B, C_cam+C_lidar, H, W]"]
```

Sources: README.md

### 2. ConvFuser

The more sophisticated approach uses a ConvFuser module, which applies convolutional layers after concatenation to blend and reduce the feature dimensions.

```mermaid
flowchart TD
    A1["Camera BEV Features\n[B, C_cam, H, W]"] --> B["Concatenation"]
    A2["LiDAR BEV Features\n[B, C_lidar, H, W]"] --> B
    B --> C["Concatenated Features\n[B, C_cam+C_lidar, H, W]"]
    C --> D["ConvFuser\n(Convolutional Layers)"]
    D --> E["Fused Features\n[B, C_fused, H, W]"]
    
    subgraph "ConvFuser Implementation"
        D1["Conv2D"] --> D2["BatchNorm"] --> D3["ReLU"]
    end
```

Sources: README.md

## BEV Representation Advantages

Fusing in the BEV space offers several key advantages over traditional point-level fusion:

1. **Preservation of Information Density**: Camera features retain their dense semantic information rather than being sparsely projected onto LiDAR points
2. **Spatial Alignment**: Both modalities naturally align in the bird's-eye view coordinate system
3. **Computational Efficiency**: Avoiding point-level correspondence reduces computational overhead

```mermaid
flowchart LR
    subgraph "Traditional Point-Level Fusion"
        A1["Camera Features"] --> B1["Project to\nLiDAR Points"]
        C1["LiDAR Points"] --> D1["Point-Level\nFeature Fusion"]
        B1 --> D1
    end
    
    subgraph "BEVFusion Approach"
        A2["Camera Features"] --> B2["View\nTransformation"]
        C2["LiDAR Features"] --> D2["BEV\nRepresentation"]
        B2 --> E["BEV-Level\nFeature Fusion"]
        D2 --> E
    end
```

Sources: README.md

## Implementation Details

The fusion implementation is modular and configurable through the configuration system. The primary fusion options can be specified in the config files:

### Fusion Configuration

In the configuration files, fusion can be specified as either a simple concatenation or using the ConvFuser module. For example, in the detection task, the fusion method is specified in the model configuration:

```
model:
  encoders:
    camera: {...}
    lidar: {...}
  fuser:
    type: ConvFuser  # or 'ConcatFuser'
    in_channels: [80, 256]  # [camera_channels, lidar_channels]
    out_channels: 256
```

Sources: README.md

## Performance Characteristics

### Computational Efficiency

BEVFusion's approach to multi-modal fusion is designed for computational efficiency, achieving:

| Metric | Value | Comparison to Point-Level Fusion |
|--------|-------|---------------------------------|
| Computation Cost | 1.9× lower | vs. comparable point-level fusion approaches |
| BEV Operation Latency | >40× reduction | with optimized BEV pooling |

Sources: README.md

### Accuracy Improvements

The fusion approach demonstrates significant performance gains over single-modality baselines:

| Task | Metric | Camera-Only | LiDAR-Only | BEVFusion (Improvement) |
|------|--------|-------------|------------|-------------------------|
| 3D Object Detection | mAP | 35.56 | 64.68 | 68.52 (+3.84) |
| 3D Object Detection | NDS | 41.21 | 69.28 | 71.38 (+2.10) |
| BEV Map Segmentation | mIoU | 57.09 | 48.56 | 62.95 (+5.86) |

Sources: README.md

## Code Integration

The fusion component integrates with both detection and segmentation task heads, providing a unified representation that works effectively for multiple perception tasks.

```mermaid
flowchart TD
    subgraph "BEVFusion Architecture Code Mapping"
        A1["Camera Encoder"] --> B1["View Transformation\n(LSS/DepthLSS)"]
        B1 --> C1["Camera BEV Features"]
        
        A2["LiDAR Encoder\n(SparseEncoder)"] --> C2["LiDAR BEV Features"]
        
        C1 --> D["ConvFuser/ConcatFuser"]
        C2 --> D
        
        D --> E["Fused BEV Features"]
        E --> F1["Detection Head\n(CenterHead)"]
        E --> F2["Segmentation Head\n(MapHead)"]
    end
```

Sources: README.md

## Comparison to Point-Level Fusion Approaches

BEVFusion's design directly addresses limitations of traditional point-level fusion approaches:

| Aspect | Point-Level Fusion | BEVFusion's BEV-Level Fusion |
|--------|-------------------|------------------------------|
| Information Preservation | Loses camera feature density when projecting to sparse points | Preserves dense camera features in BEV space |
| Processing Efficiency | Requires point-to-pixel correspondence computation | Aligns features in a common BEV grid |
| Task Flexibility | Often optimized for specific tasks | Naturally supports multiple perception tasks |
| Feature Resolution | Limited by point cloud density | Configurable BEV grid resolution |

Sources: README.md

## Task-Agnostic Design

A key advantage of BEVFusion's fusion approach is its task-agnostic nature. The same fused representation effectively supports both 3D object detection and BEV map segmentation with minimal architectural modifications.

```mermaid
flowchart LR
    A["Feature Fusion"] --> B["Fused BEV Representation"]
    B --> C1["3D Object Detection\n(CenterHead)"]
    B --> C2["BEV Map Segmentation\n(MapHead)"]
    B --> C3["Future Task Extensions"]
```

Sources: README.md

## Summary

BEVFusion's multi-modal fusion approach represents a significant advancement over traditional point-level fusion methods. By transforming features from both modalities into a unified BEV representation before fusion, the system preserves critical information from each sensor while enabling efficient processing. The modular design supports both simple concatenation and more sophisticated convolutional fusion approaches, providing flexibility for different application requirements.

---

# Page: Detection and Segmentation Heads

# Detection and Segmentation Heads

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/nuscenes/det/centerhead/lssfpn/default.yaml](configs/nuscenes/det/centerhead/lssfpn/default.yaml)

</details>



This document details the detection and segmentation heads used in the BEVFusion framework for 3D object detection and bird's-eye view (BEV) map segmentation. These task-specific heads operate on the fused BEV features to produce the final perception outputs. For information about how these features are generated and fused, see [Multi-Modal Fusion](#4.4).

## Overview

Detection and segmentation heads are the final components in the BEVFusion pipeline that transform the fused BEV features into meaningful perception outputs:

1. **Detection Head**: Predicts 3D bounding boxes around objects with classification scores and attributes
2. **Segmentation Head**: Generates semantic segmentation maps in the bird's-eye view

```mermaid
flowchart LR
    subgraph "BEVFusion Pipeline"
        A["Fused BEV Features"] --> B["Detection Head"]
        A --> C["Segmentation Head"]
        B --> D["3D Object Detection\n(Boxes, Classes, Attributes)"]
        C --> E["BEV Map Segmentation\n(Semantic Classes)"]
    end
```

Sources: [configs/nuscenes/det/centerhead/lssfpn/default.yaml:26-28]()

## Detection Head

The primary detection head in BEVFusion is the `CenterHead`, which is designed for center-based 3D object detection. This design approach represents objects as points at their centers and regresses to other object properties.

### Architecture

The `CenterHead` consists of several task-specific branches that handle different prediction aspects:

```mermaid
flowchart TD
    subgraph "CenterHead"
        A["BEV Features\n(256 channels)"] --> B["Shared Convolutional Layers"]
        B --> C1["Center Heatmap Branch"]
        B --> C2["Center Offset Branch"]
        B --> C3["Z-coordinate Branch"]
        B --> C4["Dimension Branch"]
        B --> C5["Rotation Branch"]
        B --> C6["Velocity Branch"]
        
        C1 --> D1["Class-specific Heatmaps"]
        C2 --> D2["Center Offsets"]
        C3 --> D3["Height Predictions"]
        C4 --> D4["3D Dimensions"]
        C5 --> D5["Rotation Angles"]
        C6 --> D6["Velocity Vectors"]
    end
```

### Implementation Details

The detection head processes the BEV features (typically 256 channels as specified in the configuration) through several prediction branches:

1. **Center Heatmap Branch**: Produces class-specific heatmaps indicating object center probabilities
2. **Center Offset Branch**: Predicts offsets to refine the center positions
3. **Z-coordinate Branch**: Estimates the height (z-coordinate) of objects
4. **Dimension Branch**: Predicts the 3D dimensions (length, width, height) of objects
5. **Rotation Branch**: Estimates the rotation angles of objects
6. **Velocity Branch**: Predicts velocity vectors for dynamic objects (when applicable)

The head uses a shared convolutional backbone followed by task-specific convolutional layers for each branch. The configuration allows customization of the input channel count and other architectural details.

Sources: [configs/nuscenes/det/centerhead/lssfpn/default.yaml:26-28]()

## Segmentation Head

The `MapHead` handles BEV semantic segmentation, producing pixel-wise classification of the environment in bird's-eye view.

### Architecture

```mermaid
flowchart TD
    subgraph "MapHead"
        A["BEV Features"] --> B["Convolutional Layers"]
        B --> C["Class-specific Segmentation Maps"]
        
        subgraph "Segmentation Classes"
            D1["Drivable Area"]
            D2["Road Divider"]
            D3["Lane Boundary"]
            D4["Other Map Elements"]
        end
        
        C --> D1
        C --> D2
        C --> D3
        C --> D4
    end
```

### Implementation Details

The segmentation head takes the fused BEV features and applies a series of convolutional layers to produce class-specific segmentation masks. These masks represent different semantic classes in the bird's-eye view, such as:

1. Drivable area
2. Pedestrian crossing
3. Road boundaries
4. Lane dividers
5. Other map elements

The output is typically a set of probability maps with the same spatial dimensions as the BEV feature representation, but with channels corresponding to the number of semantic classes being segmented.

## Integration with Decoder Architecture

Both heads connect to the BEV features that have been processed by the decoder, which consists of a backbone network and neck component:

```mermaid
flowchart LR
    subgraph "Decoder"
        A["Fused BEV Features\n(336 channels)"] --> B["GeneralizedResNet Backbone"]
        B --> C["LSSFPN Neck"]
        C --> D["Output Features\n(256 channels)"]
    end
    
    D --> E["Detection Head\n(CenterHead)"]
    D --> F["Segmentation Head\n(MapHead)"]
```

The decoder's architecture is specified in the configuration, with:
1. A `GeneralizedResNet` backbone that processes the initial fused BEV features
2. An `LSSFPN` (Large Scale Sparse Feature Pyramid Network) neck that refines and aggregates features at different scales
3. Output features with 256 channels that feed into both the detection and segmentation heads

Sources: [configs/nuscenes/det/centerhead/lssfpn/default.yaml:11-28]()

## Configuration

The heads can be configured through YAML configuration files, which specify:

1. Input channel dimensions
2. Network architecture parameters
3. Loss function weights
4. Other task-specific hyperparameters

Example configuration from the default YAML:

```yaml
model:
  decoder:
    backbone:
      type: GeneralizedResNet
      in_channels: 336
      blocks:
        - [2, 160, 2]
        - [2, 320, 2]
        - [2, 640, 1]
    neck:
      type: LSSFPN
      in_indices: [-1, 0]
      in_channels: [640, 160]
      out_channels: 256
      scale_factor: 2
  heads:
    object:
      in_channels: 256
```

This configuration shows:
- The detection head (`object`) receives 256-channel features
- The decoder uses a `GeneralizedResNet` backbone and `LSSFPN` neck to process the 336-channel fused BEV features
- The `LSSFPN` neck outputs 256 channels that feed into the detection and segmentation heads

Sources: [configs/nuscenes/det/centerhead/lssfpn/default.yaml:11-28]()

## Performance Considerations

The heads are designed to be computationally efficient while maintaining high accuracy:

| Head Type | Input Channels | Output Type | Computational Cost |
|-----------|---------------|-------------|-------------------|
| Detection (CenterHead) | 256 | 3D Bounding Boxes + Attributes | Medium |
| Segmentation (MapHead) | 256 | Semantic Class Maps | Medium-High |

The overall performance of these heads contributes significantly to BEVFusion's state-of-the-art results on benchmarks like nuScenes, while maintaining the capability for real-time inference.

---

# Page: CUDA Operations

# CUDA Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)
- [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp](mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp)

</details>



This page documents the specialized CUDA operations used in BEVFusion to accelerate the transformation of features into Bird's-Eye View (BEV) representation. These operations are critical for achieving real-time performance in multi-modal 3D perception tasks, with optimized versions of BEVFusion reaching 25 FPS on NVIDIA Jetson Orin platforms.

For information about the view transformation pipeline that uses these operations, see [View Transformation](#4.3).

## Overview

BEVFusion implements custom CUDA operations to efficiently transform features from different modalities into a unified BEV representation. The most significant of these is the BEV pooling operation, which dramatically improves performance by optimizing how 3D features are projected and aggregated in the BEV space.

Through these optimizations, BEVFusion reduces the transformation latency by more than 40x compared to standard implementations, making real-time multi-modal fusion feasible even on edge devices.

```mermaid
flowchart LR
    subgraph "CUDA Operations Overview"
        A["Feature Inputs"] --> B["bev_pool_forward"]
        B --> C["BEV Feature Grid"]
        D["Gradients"] --> E["bev_pool_backward"]
        E --> F["Feature Gradients"]
    end
```

Sources: [README.md:20-20]()

## BEV Pooling Operation

The BEV pooling operation is a specialized CUDA kernel that efficiently maps features from image or point cloud representations into a bird's-eye view grid. This operation is fundamental for the fusion process, allowing features from different sensors to be represented in a common spatial reference frame.

### Forward Pass

The forward pass of BEV pooling takes input features (typically from camera or LiDAR) and maps them into a BEV grid based on geometric information. This operation handles the transformation of features from their original representation to the unified BEV space.

```mermaid
flowchart TD
    subgraph "BEV Pool Forward Pass"
        Input["Input Features (n, c)"] --> Geom["Geometry Mapping"]
        Geom --> Alloc["Memory Allocation"]
        Alloc --> Pooling["Parallel Feature Pooling"]
        Pooling --> Output["Output BEV Features (b, d, h, w, c)"]
    end
```

Sources: [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:13-47]()

### Backward Pass

The backward pass computes gradients with respect to the input features, enabling end-to-end training of the network. This operation is essential for propagating gradients through the BEV transformation layer during backpropagation.

```mermaid
flowchart TD
    subgraph "BEV Pool Backward Pass"
        Grad["Output Gradients (b, d, h, w, c)"] --> Lookup["Geometry Lookup"]
        Lookup --> Alloc["Memory Allocation"]
        Alloc --> GradComp["Parallel Gradient Computation"]
        GradComp --> InputGrad["Input Feature Gradients (n, c)"]
    end
```

Sources: [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:50-87]()

## Implementation Details

The BEV pooling operation is implemented using a combination of C++ interfaces and CUDA kernels. The operations are defined with the following interfaces:

### Forward Function

```
bev_pool_forward(
  const at::Tensor _x,
  const at::Tensor _geom_feats, 
  const at::Tensor _interval_lengths, 
  const at::Tensor _interval_starts,
  int b, int d, int h, int w
)
```

This function takes the following parameters:
- `_x`: Input features with shape `(n, c)` where `n` is the number of points and `c` is the feature dimension
- `_geom_feats`: Geometry features with shape `(n, 4)` indicating the mapping positions
- `_interval_lengths`: Lengths of each pooling interval
- `_interval_starts`: Starting positions for each pooling interval
- `b, d, h, w`: Dimensions of the output BEV feature grid

### Backward Function

```
bev_pool_backward(
  const at::Tensor _out_grad,
  const at::Tensor _geom_feats, 
  const at::Tensor _interval_lengths, 
  const at::Tensor _interval_starts,
  int b, int d, int h, int w
)
```

This function takes the following parameters:
- `_out_grad`: Gradients with respect to the output with shape `(b, d, h, w, c)`
- `_geom_feats`, `_interval_lengths`, `_interval_starts`: Same as in the forward pass
- `b, d, h, w`: Dimensions of the BEV feature grid

Sources: [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:22-87]()

## Data Flow and Memory Layout

The BEV pooling operation processes data through several stages, each optimized for parallel execution on GPU hardware.

```mermaid
flowchart LR
    subgraph "BEV Pool Data Flow"
        A["Input Features\n(n, c)"] --> B["Geometric Mapping"]
        B --> C["Feature Distribution"]
        C --> D["Parallel Accumulation"]
        D --> E["BEV Grid\n(b, d, h, w, c)"]
    end
```

### Memory Layout Optimization

The memory layout of the BEV features is specifically designed to optimize cache utilization and minimize memory accesses:

| Parameter | Description | Shape |
|-----------|-------------|-------|
| Input Features | Original feature vectors | (n, c) |
| Geometry Features | Mapping to BEV coordinates | (n, 4) |
| Interval Lengths | Number of points per BEV cell | (n_intervals) |
| Interval Starts | Starting indices for pooling | (n_intervals) |
| Output BEV Features | Final BEV representation | (b, d, h, w, c) |

Sources: [mmdet3d/ops/bev_pool/src/bev_pool_cpu.cpp:22-47]()

## Integration with BEVFusion Pipeline

The CUDA operations are integrated into the BEVFusion pipeline, primarily in the View Transformation stage, where features from cameras or LiDAR are transformed into the BEV space.

```mermaid
flowchart TD
    subgraph "BEVFusion Pipeline Integration"
        subgraph "Camera Branch"
            CamInput["Camera Images"] --> CamBackbone["Backbone Network"]
            CamBackbone --> CamFeats["2D Feature Maps"]
            CamFeats --> ViewTrans["View Transformation"]
        end
        
        subgraph "LiDAR Branch"
            LidarInput["LiDAR Points"] --> Voxelization["Voxelization"]
            Voxelization --> SparseConv["Sparse Convolution"]
            SparseConv --> LidarBEV["LiDAR BEV Features"]
        end
        
        ViewTrans --> BEVPool["BEV Pool CUDA Op"]
        BEVPool --> CamBEV["Camera BEV Features"]
        
        CamBEV --> Fusion["Feature Fusion"]
        LidarBEV --> Fusion
        Fusion --> FusedBEV["Fused BEV Features"]
        FusedBEV --> DetHead["Detection Head"]
        FusedBEV --> SegHead["Segmentation Head"]
    end
```

Sources: [README.md:18-20](), [README.md:51-52]()

## Performance Impact

The optimized CUDA operations significantly improve the performance of BEVFusion:

1. **Reduced Latency**: The BEV pooling operation reduces the latency of view transformation by more than 40x compared to naive implementations.

2. **Improved Throughput**: The optimized CUDA kernels enable real-time processing of sensor data, with the full BEVFusion system achieving up to 25 FPS on NVIDIA Jetson Orin platforms.

3. **Lower Computation Cost**: Despite achieving higher accuracy, BEVFusion with these optimized operations has 1.9x lower computation cost compared to previous methods.

| Operation | Speed Improvement | Memory Usage Reduction |
|-----------|-------------------|------------------------|
| BEV Pooling Forward | >40x faster | Constant memory usage |
| BEV Pooling Backward | >40x faster | Constant memory usage |

Sources: [README.md:20-20](), [README.md:10-10]()

## Compilation and Setup

The CUDA operations are compiled as extensions to PyTorch. To use these operations, users need to compile them during the setup process using the following command:

```
python setup.py develop
```

This command compiles the CUDA kernels and makes them available in the Python environment. The operations can also be built in a Docker environment, which is supported through the provided Dockerfile.

Sources: [README.md:77-81](), [README.md:95-100]()

## Summary

The custom CUDA operations in BEVFusion, particularly the BEV pooling operation, are critical components that enable efficient transformation of features into the BEV space. These operations significantly improve the performance of the system, making real-time multi-modal fusion feasible for autonomous driving applications.

By optimizing these GPU-accelerated operations, BEVFusion achieves state-of-the-art performance in 3D object detection and BEV map segmentation while maintaining real-time inference capabilities.

---

# Page: Point Cloud Processing Operations

# Point Cloud Processing Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/ops/ball_query/src/ball_query_cpu.cpp](mmdet3d/ops/ball_query/src/ball_query_cpu.cpp)
- [mmdet3d/ops/furthest_point_sample/src/furthest_point_sample_cpu.cpp](mmdet3d/ops/furthest_point_sample/src/furthest_point_sample_cpu.cpp)
- [mmdet3d/ops/gather_points/src/gather_points_cpu.cpp](mmdet3d/ops/gather_points/src/gather_points_cpu.cpp)
- [mmdet3d/ops/group_points/src/group_points_cpu.cpp](mmdet3d/ops/group_points/src/group_points_cpu.cpp)
- [mmdet3d/ops/interpolate/src/interpolate.cpp](mmdet3d/ops/interpolate/src/interpolate.cpp)
- [mmdet3d/ops/knn/src/knn_cpu.cpp](mmdet3d/ops/knn/src/knn_cpu.cpp)

</details>



## Purpose and Scope

This document describes the specialized CUDA operations used for processing point cloud data in the BEVFusion framework. These operations provide efficient implementations of fundamental point cloud processing algorithms that support LiDAR feature extraction in the system's perception pipeline. For information on sparse convolution operations used in conjunction with these point operations, see [Sparse Convolution Operations](#5.2).

```mermaid
flowchart TD
    subgraph "Point Cloud Processing Overview"
        A["Raw Point Cloud Data"] --> B["Point Sampling Operations"]
        B --> C["Neighbor Search Operations"]
        C --> D["Feature Aggregation Operations"]
        D --> E["Feature Interpolation"]
        E --> F["BEV LiDAR Features"]
        F --> G["Fusion with Camera Features"]
    end
```

Sources: All provided files

## Core Point Cloud Operations

The BEVFusion framework implements several CUDA-accelerated operations for efficient point cloud processing. These operations are fundamental building blocks for processing 3D point cloud data and are particularly important for the LiDAR encoder branch of the system.

```mermaid
flowchart LR
    subgraph "Point Cloud CUDA Operations"
        direction LR
        A["Point Cloud Data"] --> B["furthest_point_sampling"]
        A --> C["knn"]
        A --> D["ball_query"]
        B --> E["gather_points"]
        C --> F["group_points"]
        D --> F
        E --> G["Feature Extraction"]
        F --> G
        G --> H["three_nn"]
        H --> I["three_interpolate"]
        I --> J["Processed Features"]
    end
```

Sources: All provided files

### Sampling Operations

Sampling operations reduce the number of points while maintaining the structural characteristics of the point cloud.

#### Furthest Point Sampling (FPS)

Furthest Point Sampling selects a subset of points where each new point is the furthest from the previously selected points. This ensures good coverage of the entire point cloud with reduced data.

```mermaid
graph TD
    subgraph "Furthest Point Sampling"
        A["Input Point Cloud<br>(b, n, 3)"] --> B["furthest_point_sampling_kernel_launcher"]
        B --> C["Sampled Points<br>(b, m, 3)"]
        D["Input Distance Matrix<br>(optional)"] --> E["furthest_point_sampling_with_dist_kernel_launcher"]
        E --> F["Sampled Points with Distance<br>(b, m, 3)"]
    end
```

**Implementation Details:**
- Two variants implemented:
  1. Standard FPS using Euclidean distance
  2. FPS with pre-computed distance matrix
- Time complexity reduced through CUDA parallelization

Sources: [mmdet3d/ops/furthest_point_sample/src/furthest_point_sample_cpu.cpp:10-62]()

### Neighbor Search Operations

Neighbor search operations find points in proximity to query points, essential for local feature aggregation.

#### Ball Query

Ball Query finds all points within a specified radius around each query point. This operation is used to identify local neighborhoods for feature aggregation.

```mermaid
graph TD
    subgraph "Ball Query Operation"
        A["Query Points<br>(b, m, 3)"] --> C["ball_query_kernel_launcher"]
        B["Input Points<br>(b, n, 3)"] --> C
        D["min_radius"] --> C
        E["max_radius"] --> C
        F["nsample"] --> C
        C --> G["Neighbor Indices<br>(b, m, nsample)"]
    end
```

**Implementation Details:**
- Parameters include minimum radius, maximum radius, and maximum number of samples
- Returns indices of neighboring points within the specified radii
- Used to identify local regions for feature extraction

Sources: [mmdet3d/ops/ball_query/src/ball_query_cpu.cpp:1-45]()

#### K-Nearest Neighbors (KNN)

KNN finds the k closest points to each query point based on Euclidean distance.

```mermaid
graph TD
    subgraph "K-Nearest Neighbors"
        A["Query Points<br>(b, m, 3)"] --> C["knn_kernel_launcher"]
        B["Input Points<br>(b, n, 3)"] --> C
        D["k (nsample)"] --> C
        C --> E["Neighbor Indices<br>(b, m, k)"]
        C --> F["Distances<br>(b, m, k)"]
    end
```

**Implementation Details:**
- Returns both indices and squared distances to the k-nearest neighbors
- Efficient implementation using CUDA heap-based priority queue

Sources: [mmdet3d/ops/knn/src/knn_cpu.cpp:1-44]()

### Feature Aggregation Operations

These operations aggregate features from identified neighborhoods to capture local geometric structures.

#### Gather Points

Gathers points or features from a point cloud based on specified indices.

```mermaid
graph TD
    subgraph "Gather Points"
        A["Input Features<br>(b, c, n)"] --> C["gather_points_kernel_launcher"]
        B["Indices<br>(b, npoints)"] --> C
        C --> D["Gathered Features<br>(b, c, npoints)"]
        E["Gradients<br>(b, c, npoints)"] --> F["gather_points_grad_kernel_launcher"]
        B --> F
        F --> G["Input Gradients<br>(b, c, n)"]
    end
```

**Implementation Details:**
- Forward pass: Selects features based on provided indices
- Backward pass: Propagates gradients back to the original points
- Typically used after sampling operations to collect features of sampled points

Sources: [mmdet3d/ops/gather_points/src/gather_points_cpu.cpp:1-57]()

#### Group Points

Groups points or features based on neighborhood indices, typically obtained from ball query or KNN.

```mermaid
graph TD
    subgraph "Group Points"
        A["Input Features<br>(b, c, n)"] --> C["group_points_kernel_launcher"]
        B["Indices<br>(b, npoints, nsample)"] --> C
        C --> D["Grouped Features<br>(b, c, npoints, nsample)"]
        E["Gradients<br>(b, c, npoints, nsample)"] --> F["group_points_grad_kernel_launcher"]
        B --> F
        F --> G["Input Gradients<br>(b, c, n)"]
    end
```

**Implementation Details:**
- Aggregates features from neighborhoods defined by indices
- Supports backpropagation through gradient operation
- Essential for capturing local geometric patterns in point clouds

Sources: [mmdet3d/ops/group_points/src/group_points_cpu.cpp:1-60]()

### Feature Interpolation Operations

Interpolation operations transfer features between different point sets, which is crucial for multi-scale feature learning.

#### Three Nearest Neighbors (3NN)

Finds the three nearest neighbors for each query point to support feature interpolation.

```mermaid
graph TD
    subgraph "Three Nearest Neighbors"
        A["Query Points<br>(b, n, 3)"] --> C["three_nn_kernel_launcher"]
        B["Known Points<br>(b, m, 3)"] --> C
        C --> D["Neighbor Indices<br>(b, n, 3)"]
        C --> E["Squared Distances<br>(b, n, 3)"]
    end
```

**Implementation Details:**
- Returns both indices and squared distances to three nearest neighbors
- Used as input for the three_interpolate operation

Sources: [mmdet3d/ops/interpolate/src/interpolate.cpp:44-54]()

#### Three Interpolate

Performs feature interpolation using inverse distance weighted average of the three nearest neighbors.

```mermaid
graph TD
    subgraph "Three Interpolate"
        A["Known Features<br>(b, c, m)"] --> C["three_interpolate_kernel_launcher"]
        B["Neighbor Indices<br>(b, n, 3)"] --> C
        F["Weights<br>(b, n, 3)"] --> C
        C --> D["Interpolated Features<br>(b, c, n)"]
        E["Output Gradients<br>(b, c, n)"] --> G["three_interpolate_grad_kernel_launcher"]
        B --> G
        F --> G
        G --> H["Input Gradients<br>(b, c, m)"]
    end
```

**Implementation Details:**
- Forward pass: Interpolates features based on distances to three nearest neighbors
- Backward pass: Propagates gradients back to the original points
- Typically used to propagate features between point sets of different densities

Sources: [mmdet3d/ops/interpolate/src/interpolate.cpp:56-91]()

## Integration with BEVFusion Pipeline

These point cloud processing operations form the foundation of the LiDAR branch in the BEVFusion system. They enable efficient processing of sparse 3D point clouds before fusion with camera features in the bird's-eye view representation.

```mermaid
flowchart TD
    subgraph "Integration with BEVFusion"
        A["Raw LiDAR Points"] --> B["Voxelization"]
        B --> C["Point Sampling (FPS)"]
        C --> D1["KNN/Ball Query"]
        D1 --> E["Group Points"]
        E --> F["Feature Extraction"]
        F --> G["Interpolation (3NN)"]
        G --> H["LiDAR BEV Features"]
        H --> I["Fusion with Camera BEV"]
        I --> J["Detection/Segmentation Heads"]
    end
```

Sources: All provided files

## Performance Considerations

The CUDA implementations of these point cloud operations provide significant acceleration compared to CPU implementations, which is critical for real-time performance in autonomous driving applications.

| Operation | Time Complexity | Memory Usage | Performance Impact |
|-----------|-----------------|--------------|-------------------|
| FPS | O(n×m) | O(n+m) | Reduces point cloud density while preserving structure |
| Ball Query | O(n×m) | O(m×nsample) | Identifies local neighborhoods efficiently |
| KNN | O(n×m×log(k)) | O(m×k) | More precise neighbor selection than ball query |
| Gather Points | O(n×c) | O(m×c) | Low overhead feature selection |
| Group Points | O(m×nsample×c) | O(m×nsample×c) | Moderate compute for feature aggregation |
| 3NN/Interpolate | O(n×m) | O(n×3) | Efficient feature transfer between point sets |

Sources: All provided files

## Summary

The point cloud processing operations implemented in BEVFusion provide efficient CUDA accelerated algorithms for processing 3D LiDAR data. These operations enable the system to effectively extract features from sparse point clouds, which are then transformed into a bird's-eye view representation for fusion with camera features. The optimized CUDA implementations ensure that these operations can be performed with minimal latency, which is critical for real-time perception in autonomous driving applications.

---

# Page: Sparse Convolution Operations

# Sparse Convolution Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mmdet3d/ops/spconv/include/tensorview/tensorview.h](mmdet3d/ops/spconv/include/tensorview/tensorview.h)
- [mmdet3d/ops/spconv/src/indice_cpu.cc](mmdet3d/ops/spconv/src/indice_cpu.cc)
- [mmdet3d/ops/spconv/src/maxpool_cpu.cc](mmdet3d/ops/spconv/src/maxpool_cpu.cc)

</details>



## Purpose and Overview

This document explains the sparse convolution operations used in BEVFusion for efficient processing of sparse point cloud data from LiDAR sensors. Sparse convolution is a key optimization that significantly improves computational efficiency by only processing non-zero elements in the input data, which is particularly important for LiDAR data where most of the 3D space is empty.

For information about general point cloud processing operations, see [Point Cloud Processing Operations](#5.1).

## Understanding Sparse Convolution

Traditional (dense) convolution operations process every element in an input tensor, which is inefficient for sparse data like point clouds. Sparse convolution addresses this by:

1. Only processing occupied voxels (non-zero elements)
2. Tracking the spatial relationships between these occupied voxels
3. Applying convolution operations only where data exists

```mermaid
flowchart LR
    A["LiDAR Points"] --> B["Voxelization"]
    B --> C["Sparse Tensor\n(Non-empty Voxels)"]
    C --> D["Sparse Convolution"]
    D --> E["Filtered Sparse\nFeatures"]
    E --> F["BEV Features"]
    
    subgraph "Dense vs. Sparse Computation"
        G["Dense Conv (Processes all voxels)"] -.-> H["Inefficient for\nPoint Clouds"]
        I["Sparse Conv (Processes only\noccupied voxels)"] -.-> J["Efficient for\nPoint Clouds"]
    end
```

Sources: [mmdet3d/ops/spconv/src/indice_cpu.cc:1-85]()

## Core Components of Sparse Convolution System

The sparse convolution system in BEVFusion consists of several key components:

### 1. Tensor Representation (TensorView)

`TensorView` is the fundamental data structure that handles tensor operations for sparse convolution:

```mermaid
classDiagram
    class TensorView {
        +T* mPtr
        +Shape mShape
        +TensorView()
        +operator()
        +subview()
        +reshape()
        +view()
        +squeeze()
    }
    
    class Shape {
        +push_back()
        +subshape()
        +squeeze()
        +ndim()
        +size()
    }
    
    TensorView --> Shape : contains
```

Sources: [mmdet3d/ops/spconv/include/tensorview/tensorview.h:525-1061]()

### 2. Indice Generation

The indice generation system creates mappings between input and output sparse tensors for convolution operations:

```mermaid
flowchart TD
    A["Input Indices\n(Locations of Non-empty Voxels)"] --> B["CreateConvIndicePairFunctor"]
    B --> C["Output Indices\n(New Locations After Conv)"]
    B --> D["Indice Pairs\n(Mapping Between Input/Output)"]
    
    E["Kernel Size"] --> B
    F["Stride"] --> B
    G["Padding"] --> B
    H["Dilation"] --> B
    I["Output Shape"] --> B
```

Sources: [mmdet3d/ops/spconv/src/indice_cpu.cc:21-65]()

### 3. Sparse Operations

BEVFusion implements several sparse operations, including convolution and max pooling:

#### Sparse Max Pooling

```mermaid
flowchart LR
    A["Input Features"] --> B["SparseMaxPoolForwardFunctor"]
    C["Indices"] --> B
    B --> D["Output Features"]
    
    E["Output Features"] --> F["SparseMaxPoolBackwardFunctor"]
    G["Input Features"] --> F
    H["Gradient Output"] --> F
    I["Indices"] --> F
    F --> J["Gradient Input"]
```

Sources: [mmdet3d/ops/spconv/src/maxpool_cpu.cc:20-64]()

## Integration with BEVFusion Pipeline

Sparse convolution operations are a critical part of the LiDAR processing branch in BEVFusion:

```mermaid
flowchart TD
    subgraph "LiDAR Processing Branch"
        A["LiDAR Points"] --> B["Voxelization"]
        B --> C["SparseEncoder"]
        C --> D["3D Sparse Convolution"]
        D --> E["LiDAR BEV Features"]
    end
    
    subgraph "Camera Branch"
        F["Camera Images"] --> G["CNN Backbone"]
        G --> H["View Transformation"]
        H --> I["Camera BEV Features"]
    end
    
    E --> J["Feature Fusion"]
    I --> J
    J --> K["Fused BEV Features"]
    K --> L["Detection/Segmentation Heads"]
```

## Technical Implementation Details

### Sparse Convolution Indexing

The core of sparse convolution is the creation of indice pairs that map between input and output locations:

1. For each occupied voxel in the input:
   - Calculate potential output locations based on kernel, stride, and dilation
   - Create mappings between input and output indices
   - Store only the non-empty relationships

2. Supported convolution types:
   - Regular sparse convolution (`getIndicePairsConv`)
   - Submanifold sparse convolution (`getIndicePairsSubM`)
   - Transposed sparse convolution (`getIndicePairsDeConv`)

```
For a 3x3 kernel in 2D sparse convolution:
- Each occupied input location potentially affects 9 output locations
- Only locations that interact with other occupied voxels are processed
```

Sources: [mmdet3d/ops/spconv/src/indice_cpu.cc:35-45]()

### CPU Implementation

The BEVFusion framework provides CPU implementations for sparse operations, making it possible to run on systems without GPU acceleration:

```cpp
// Example of sparse max pooling forward pass (simplified)
for (int row = 0; row < size; row++) {
  idxi = indicesIn[row] * stride;  // Input feature index
  idxo = indicesOut[row] * stride; // Output feature index
  for (int plane = 0; plane < stride; ++plane)
    if (outFeaturesData[idxo + plane] < inFeaturesData[idxi + plane])
      outFeaturesData[idxo + plane] = inFeaturesData[idxi + plane];
}
```

The implementation supports:
- Multiple dimensions (1D to 4D)
- Different index types (int, long)
- Various data types (float, double, half-precision)

Sources: [mmdet3d/ops/spconv/src/maxpool_cpu.cc:22-39](), [mmdet3d/ops/spconv/src/maxpool_cpu.cc:72-77]()

### Performance Considerations

Sparse convolution provides significant performance benefits over dense convolution for LiDAR data:

| Aspect | Dense Convolution | Sparse Convolution |
|--------|------------------|-------------------|
| Memory Usage | Proportional to volume (x×y×z) | Proportional to number of points |
| Computation | Processes all voxels | Processes only non-empty voxels |
| Scaling with Resolution | Poor (cubic growth) | Good (near-linear with points) |
| Implementation Complexity | Lower | Higher |

For typical autonomous driving LiDAR data with millions of points but billions of potential voxels, sparse convolution can be orders of magnitude more efficient.

## Relationship to Other Components

The sparse convolution operations sit within the LiDAR branch of BEVFusion's architecture:

```mermaid
flowchart LR
    subgraph "LiDAR Processing Chain"
        A["LoadPointsFromFile"] --> B["PointsToVoxels"]
        B --> C["VoxelBackbone"] 
        C --> D["SparseEncoder"]
        D --> E["LiDAR BEV Features"]
    end
    
    subgraph "Sparse Convolution Operations"
        F["CreateConvIndicePairFunctor"] --> G["SparseConvolution"]
        F["CreateConvIndicePairFunctor"] --> H["SparseMaxPool"]
        F["CreateConvIndicePairFunctor"] --> I["SubmanifoldSparseConv"]
    end
    
    D -.-> F
    G --> D
    H --> D
    I --> D
```

Sources: [mmdet3d/ops/spconv/src/indice_cpu.cc:20-46](), [mmdet3d/ops/spconv/src/maxpool_cpu.cc:20-40]()

## Conclusion

Sparse convolution operations are a critical optimization in BEVFusion that enable efficient processing of LiDAR point cloud data. By focusing computation only on non-empty voxels, these operations dramatically reduce memory usage and computational requirements while preserving geometric information needed for accurate 3D object detection.

---

# Page: Training and Evaluation

# Training and Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/nuscenes_dataset.py](mmdet3d/datasets/nuscenes_dataset.py)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



This document details the training and evaluation processes for the BEVFusion framework, a multi-sensor fusion system for 3D object detection and BEV map segmentation. It covers how to train different model variants (camera-only, LiDAR-only, and multi-modal fusion) and how to evaluate their performance using standard benchmarks.

## Overview

BEVFusion uses a distributed training framework based on torchpack and supports comprehensive evaluation on nuScenes and Waymo datasets. The system provides dedicated tools for both training new models and evaluating pre-trained checkpoints.

```mermaid
flowchart TD
    A["Configuration Files"] --> B["Training Pipeline"]
    B --> C["Model Checkpoints"]
    C --> D["Evaluation Pipeline"]
    D --> E["Performance Metrics"]
    
    subgraph "Train/Test Tools"
        B1["tools/train.py"]
        D1["tools/test.py"]
    end
    
    subgraph "Dataset Interface"
        F["NuScenesDataset"]
    end
    
    B --> B1
    D --> D1
    B1 --> F
    D1 --> F
```

Sources: [README.md:156-193]()

## Training Pipeline

The training process in BEVFusion allows for training different model variants including camera-only, LiDAR-only, and multi-modal fusion models. The system uses PyTorch with distributed training support through torchpack.

### Distributed Training Framework

BEVFusion uses torchpack's `dist-run` command to facilitate distributed training across multiple GPUs, enabling efficient utilization of computational resources. The framework is built with OpenMPI integration for inter-process communication.

```mermaid
flowchart LR
    A["torchpack dist-run"] --> B["Multiple GPU Processes"]
    B --> C["Data Parallelism"]
    C --> D["Gradient Synchronization"]
    D --> E["Model Update"]
    
    subgraph "Training Command Structure"
        F["torchpack dist-run -np [#GPUs] python tools/train.py [config_path] [options]"]
    end
```

Sources: [README.md:156-193](), [docker/Dockerfile:3-23]()

### Model Initialization

BEVFusion supports initializing models from pre-trained checkpoints, which is particularly important for components like the Swin Transformer backbone. This transfer learning approach helps accelerate training and improve performance.

For example, when training a camera-only detector, the Swin Transformer backbone is initialized from a checkpoint pre-trained on nuImages:

```
--model.encoders.camera.backbone.init_cfg.checkpoint pretrained/swint-nuimages-pretrained.pth
```

When training fusion models, you can initialize from modality-specific pre-trained models:

```
--load_from pretrained/lidar-only-det.pth
```

Sources: [README.md:156-193]()

### Training Process Workflow

```mermaid
flowchart TD
    A["Configuration Loading"] --> B["Dataset Preparation"]
    B --> C["Model Initialization"]
    C --> D["Distributed Training Setup"]
    D --> E["Training Loop"]
    E --> F["Checkpoint Saving"]
    
    subgraph "Model Variants"
        G1["Camera-Only"]
        G2["LiDAR-Only"]
        G3["BEVFusion"]
    end
    
    subgraph "NuScenesDataset"
        H1["load_annotations"]
        H2["get_data_info"]
        H3["get_ann_info"]
    end
    
    B --> H1 --> H2 --> H3
    C --> G1
    C --> G2
    C --> G3
```

Sources: [README.md:156-193](), [mmdet3d/datasets/nuscenes_dataset.py:193-336]()

### Example Training Commands

BEVFusion provides dedicated training commands for different model variants:

1. **Camera-Only Detection**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/det/centerhead/lssfpn/camera/256x704/swint/default.yaml --model.encoders.camera.backbone.init_cfg.checkpoint pretrained/swint-nuimages-pretrained.pth
   ```

2. **Camera-Only BEV Segmentation**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/seg/camera-bev256d2.yaml --model.encoders.camera.backbone.init_cfg.checkpoint pretrained/swint-nuimages-pretrained.pth
   ```

3. **LiDAR-Only Detection**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/det/transfusion/secfpn/lidar/voxelnet_0p075.yaml
   ```

4. **LiDAR-Only BEV Segmentation**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/seg/lidar-centerpoint-bev128.yaml
   ```

5. **BEVFusion Detection**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/det/transfusion/secfpn/camera+lidar/swint_v0p075/convfuser.yaml --model.encoders.camera.backbone.init_cfg.checkpoint pretrained/swint-nuimages-pretrained.pth --load_from pretrained/lidar-only-det.pth
   ```

6. **BEVFusion Segmentation**:
   ```bash
   torchpack dist-run -np 8 python tools/train.py configs/nuscenes/seg/fusion-bev256d2-lss.yaml --model.encoders.camera.backbone.init_cfg.checkpoint pretrained/swint-nuimages-pretrained.pth
   ```

Sources: [README.md:156-193]()

## Evaluation Pipeline

The evaluation pipeline in BEVFusion provides a comprehensive framework for assessing model performance on various tasks, including 3D object detection and BEV map segmentation.

### Evaluation Process

```mermaid
flowchart TD
    A["Model Checkpoint"] --> B["Config File"]
    B --> C["tools/test.py"]
    C --> D["Evaluation Task"]
    
    subgraph "NuScenesDataset Evaluation"
        E1["evaluate Method"]
        E2["_evaluate_single Method"]
        E3["evaluate_map Method"]
        E4["format_results Method"]
    end
    
    D --> D1["Object Detection"] 
    D --> D2["BEV Map Segmentation"]
    
    D1 --> E1 --> E2
    D1 --> E1 --> E4
    D2 --> E1 --> E3
    
    E1 --> F["Evaluation Metrics"]
```

Sources: [README.md:130-155](), [mmdet3d/datasets/nuscenes_dataset.py:410-572]()

### Object Detection Evaluation

For 3D object detection, BEVFusion uses the nuScenes evaluation protocols. The evaluation pipeline supports measuring metrics like mean Average Precision (mAP) and nuScenes Detection Score (NDS).

The object detection evaluation process involves:

1. Converting model outputs to nuScenes box format
2. Transforming predictions to global coordinate system
3. Calculating detection metrics including precision, recall, and error analysis

The evaluation metrics for object detection include:

| Metric | Description |
|--------|-------------|
| mAP | Mean Average Precision across classes |
| NDS | nuScenes Detection Score (composite metric) |
| mATE | Mean Average Translation Error |
| mASE | Mean Average Scale Error |
| mAOE | Mean Average Orientation Error |
| mAVE | Mean Average Velocity Error |
| mAAE | Mean Average Attribute Error |

Sources: [mmdet3d/datasets/nuscenes_dataset.py:410-465](), [README.md:22-41]()

### BEV Map Segmentation Evaluation

For BEV map segmentation, the evaluation focuses on the IoU (Intersection over Union) metric across different classes and thresholds.

The `evaluate_map` method calculates IoU metrics by:
1. Processing model predictions and ground truth masks
2. Computing true positives, false positives, and false negatives
3. Calculating IoU scores across different thresholds
4. Reporting per-class and mean IoU scores

```mermaid
flowchart LR
    A["Segmentation Predictions"] --> B["evaluate_map Method"]
    B --> C["IoU Calculation"]
    C --> D["Per-class IoU"]
    C --> E["Mean IoU"]
    
    subgraph "IoU Threshold Analysis"
        F["Multiple Thresholds"]
        G["Max IoU"]
    end
    
    C --> F --> G
```

Sources: [mmdet3d/datasets/nuscenes_dataset.py:498-530](), [README.md:52-59]()

### Example Evaluation Commands

BEVFusion provides the following commands for evaluating pre-trained models:

1. **Downloading Pre-trained Models**:
   ```bash
   ./tools/download_pretrained.sh
   ```

2. **Evaluating Detection Models**:
   ```bash
   torchpack dist-run -np 8 python tools/test.py configs/nuscenes/det/transfusion/secfpn/camera+lidar/swint_v0p075/convfuser.yaml pretrained/bevfusion-det.pth --eval bbox
   ```

3. **Evaluating Segmentation Models**:
   ```bash
   torchpack dist-run -np 8 python tools/test.py configs/nuscenes/seg/fusion-bev256d2-lss.yaml pretrained/bevfusion-seg.pth --eval map
   ```

The `--eval` flag specifies the evaluation metric, where `bbox` is used for object detection evaluation and `map` for BEV map segmentation evaluation.

Sources: [README.md:130-155]()

## Results and Benchmarks

BEVFusion reports state-of-the-art results on multiple benchmarks:

### 3D Object Detection (Waymo test)

| Model | mAP-L1 | mAPH-L1 | mAP-L2 | mAPH-L2 |
|-------|--------|---------|--------|---------|
| BEVFusion | 82.72 | 81.35 | 77.65 | 76.33 |
| BEVFusion-TTA | 86.04 | 84.76 | 81.22 | 79.97 |

### 3D Object Detection (nuScenes test)

| Model | Modality | mAP | NDS |
|-------|----------|-----|-----|
| BEVFusion-e | C+L | 74.99 | 76.09 |
| BEVFusion | C+L | 70.23 | 72.88 |
| BEVFusion-base* | C+L | 71.72 | 73.83 |

### 3D Object Detection (nuScenes validation)

| Model | Modality | mAP | NDS |
|-------|----------|-----|-----|
| BEVFusion | C+L | 68.52 | 71.38 |
| Camera-Only Baseline | C | 35.56 | 41.21 |
| LiDAR-Only Baseline | L | 64.68 | 69.28 |

### BEV Map Segmentation (nuScenes validation)

| Model | Modality | mIoU |
|-------|----------|------|
| BEVFusion | C+L | 62.95 |
| Camera-Only Baseline | C | 57.09 |
| LiDAR-Only Baseline | L | 48.56 |

Sources: [README.md:22-59]()

## Best Practices and Tips

1. **Training Order**: Start by training modality-specific models (camera-only and LiDAR-only) before training fusion models. This allows for better initialization of the fusion model.

2. **Evaluation Metrics**: Use the appropriate evaluation metric for each task:
   - `--eval bbox` for object detection
   - `--eval map` for BEV map segmentation

3. **Model Selection**: For best performance:
   - Use fusion models for both detection and segmentation tasks
   - Choose camera-only models when LiDAR is unavailable or for lower computational requirements
   - Use LiDAR-only models when camera data is unavailable or in low light conditions

4. **Final Evaluation**: Always run the test script separately after training to get the final evaluation metrics:
   ```bash
   torchpack dist-run -np 8 python tools/test.py [config_file] [checkpoint] --eval [metric]
   ```

Sources: [README.md:156-193]()

## Summary

The BEVFusion training and evaluation framework provides a comprehensive pipeline for developing multi-modal 3D perception models. The system supports training various model configurations, from single-modality to fusion models, and offers robust evaluation protocols for measuring performance on standard benchmarks.

By following the provided commands and guidelines, researchers and practitioners can train their own BEVFusion models and evaluate their performance on 3D object detection and BEV map segmentation tasks.

---

# Page: Configuration System

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)

</details>



## Purpose and Scope

The Configuration System in BEVFusion provides a structured way to customize and control all aspects of the framework, from model architecture and data processing pipelines to training parameters and runtime settings. This document explains how the configuration system works, its components, and how to use it for different tasks, datasets, and hardware environments.

For information about deploying configured models, see [Deployment](#8).

## Configuration Overview

BEVFusion uses a configuration-based approach that separates model definition from execution code, allowing researchers and engineers to experiment with different architectures and parameters without modifying core code.

```mermaid
graph TD
    A["Configuration Files (.py)"] --> B["Config Registry"]
    B --> C["Model Configuration"]
    B --> D["Dataset Configuration"]
    B --> E["Training Configuration"]
    B --> F["Runtime Configuration"]
    C --> G["BEVFusion Model Components"]
    D --> H["Data Processing Pipeline"]
    E --> I["Training Loop & Optimization"]
    F --> J["Hardware Utilization"]
```

**Title: Configuration System Flow**

Sources: mmcv/mmcv/utils/config.py, tools/train.py

## Configuration File Structure

The configuration system uses Python files for defining configuration parameters. Each configuration file typically includes:

```mermaid
classDiagram
    class Config {
        +model: dict
        +data: dict
        +optimizer: dict
        +optimizer_config: dict
        +lr_config: dict
        +runner: dict
        +evaluation: dict
        +checkpoint_config: dict
        +log_config: dict
    }
    
    class ModelConfig {
        +type: str
        +encoders: dict
        +decoder: dict
        +heads: dict
    }
    
    class DataConfig {
        +samples_per_gpu: int
        +workers_per_gpu: int
        +train: dict
        +val: dict
        +test: dict
    }
    
    class OptimizationConfig {
        +type: str
        +lr: float
        +weight_decay: float
    }
    
    Config --> ModelConfig
    Config --> DataConfig
    Config --> OptimizationConfig
```

**Title: Configuration Component Relationships**

Sources: configs/nuscenes, configs/nuscenes/det

## Configuration Registry and Inheritance

BEVFusion's configuration system supports inheritance, allowing users to build configurations hierarchically:

```mermaid
graph TD
    A["Base Configuration"] --> B["Model-specific Config"]
    B --> C["Dataset-specific Config"]
    C --> D["Task-specific Config"]
    D --> E["Experiment Config"]
```

**Title: Configuration Inheritance Structure**

Sources: configs/nuscenes/det/transfusion/secfpn, configs/nuscenes/det/centerhead

## Model Configuration Components

### Encoders Configuration

```mermaid
classDiagram
    class EncodersConfig {
        +camera: dict
        +lidar: dict
    }
    
    class CameraConfig {
        +backbone: dict
        +neck: dict
        +view_transform: dict
    }
    
    class LidarConfig {
        +voxelize: dict
        +backbone: dict
        +neck: dict
    }
    
    EncodersConfig --> CameraConfig
    EncodersConfig --> LidarConfig
```

**Title: Encoder Configuration Structure**

Sources: mmdet3d/models/detectors/bevfusion.py

### Fusion and Decoder Configuration

```mermaid
classDiagram
    class FusionConfig {
        +type: str
        +in_channels: list
        +out_channels: int
    }
    
    class HeadsConfig {
        +detection: dict
        +segmentation: dict
    }
    
    class DetectionHeadConfig {
        +type: str
        +in_channels: int
        +tasks: list
        +bbox_coder: dict
        +common_heads: dict
    }
    
    class SegmentationHeadConfig {
        +type: str
        +in_channels: int
        +num_classes: int
    }
    
    HeadsConfig --> DetectionHeadConfig
    HeadsConfig --> SegmentationHeadConfig
```

**Title: Head Configuration Structure**

Sources: mmdet3d/models/fusion_layers, mmdet3d/models/heads

## Data Processing Configuration

The data configuration defines dataset specifics, preprocessing steps, and data loaders:

```mermaid
classDiagram
    class DatasetConfig {
        +type: str
        +data_root: str
        +ann_file: str
        +pipeline: list
    }
    
    class PipelineConfig {
        +load_operations: list
        +transform_operations: list
        +format_operations: list
    }
    
    class LoadOperations {
        +LoadMultiViewImageFromFiles
        +LoadPointsFromFile
        +LoadAnnotations3D
    }
    
    class TransformOperations {
        +GlobalRotScaleTrans
        +RandomFlip3D
        +PointsRangeFilter
        +ObjectRangeFilter
    }
    
    DatasetConfig --> PipelineConfig
    PipelineConfig --> LoadOperations
    PipelineConfig --> TransformOperations
```

**Title: Data Pipeline Configuration**

Sources: mmdet3d/datasets/pipelines, configs/nuscenes

## Configuration Usage

### Basic Configuration Loading

The configuration system loads Python files using a utility from MMCV:

```python
from mmcv import Config
cfg = Config.fromfile('configs/nuscenes/det/transfusion/secfpn/camera+lidar/resnet50/convfuser.py')
```

### Command-line Modification

Configuration can be modified via command-line arguments using the `--cfg-options` flag:

```
python tools/train.py configs/nuscenes/det/transfusion/secfpn/camera+lidar/resnet50/convfuser.py \
    --cfg-options model.encoders.camera.backbone.type=ResNet101 \
    data.samples_per_gpu=2 \
    runner.max_epochs=24
```

Sources: tools/train.py

## Configuring Different Components

### LiDAR Encoder Configuration

The LiDAR encoder typically requires configuration for voxelization and point cloud processing:

```python
# Example LiDAR encoder configuration
lidar_encoder = dict(
    voxelize=dict(
        max_num_points=10,
        point_cloud_range=-54, -54, -5.0, 54, 54, 3.0],
        voxel_size=[0.075, 0.075, 0.2],
        max_voxels=(120000, 160000)
    ),
    backbone=dict(
        type='SparseEncoder',
        in_channels=5,
        sparse_shape=[41, 1440, 1440],
        output_channels=128,
        order=('conv', 'norm', 'act')
    )
)
```

Sources: mmdet3d/models/voxel_encoders, mmdet3d/models/middle_encoders

### Camera Encoder Configuration

Camera encoder configuration defines the image backbone and transformation to BEV space:

```python
# Example Camera encoder configuration
camera_encoder = dict(
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=False),
        norm_eval=True,
        style='caffe',
    ),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        num_outs=5
    ),
    view_transform=dict(
        type='LSSTransform',
        input_size=(256, 704),
        in_channels=256,
        out_channels=80
    )
)
```

Sources: mmdet3d/models/backbones, mmdet3d/models/view_transforms

### Fusion Configuration

Fusion configuration specifies how camera and LiDAR features are combined:

```python
# Example fusion configuration
fusion_layer = dict(
    type='ConvFuser',
    in_channels=[80, 256],  # camera, lidar channels
    out_channels=256
)
```

Sources: mmdet3d/models/fusion_layers

## Training Configuration

Training configuration includes optimizer settings, learning rate schedules, and other training parameters:

| Parameter | Description | Example Values |
|-----------|-------------|---------------|
| optimizer | Optimizer type and parameters | `dict(type='AdamW', lr=0.0001, weight_decay=0.01)` |
| lr_config | Learning rate schedule | `dict(policy='cyclic', target_ratio=(10, 0.0001), cyclic_times=1, step_ratio_up=0.4)` |
| runner | Training iterations | `dict(type='EpochBasedRunner', max_epochs=20)` |
| checkpoint_config | Checkpoint saving | `dict(interval=1)` |
| evaluation | Evaluation settings | `dict(interval=1, pipeline=test_pipeline)` |

Sources: configs/nuscenes/det/transfusion/secfpn

## Example Configuration

A complete BEVFusion configuration typically includes model definition, dataset configuration, and training parameters:

```python
# Model configuration
model = dict(
    type='BEVFusion',
    encoders=dict(
        camera=camera_encoder,  # As defined above
        lidar=lidar_encoder,    # As defined above
    ),
    fusion_layer=fusion_layer,  # As defined above
    decoder=dict(
        type='TransFusionDecoder',
        in_channels=256,
        out_channels=256
    ),
    heads=dict(
        detection=dict(
            type='CenterHead',
            in_channels=256,
            tasks=[
                dict(num_class=10, class_names=[...]),  # Classes list
            ],
            common_heads=dict(
                reg=(2, 2), height=(1, 2), dim=(3, 2), rot=(2, 2)
            ),
            bbox_coder=dict(
                type='CenterPointBBoxCoder',
                post_center_range=[-61.2, -61.2, -10.0, 61.2, 61.2, 10.0],
                max_num=500,
                score_threshold=0.1,
                pc_range=[-51.2, -51.2],
                out_size_factor=8,
                voxel_size=[0.1, 0.1]
            ),
            separate_head=dict(
                type='SeparateHead', init_bias=-2.19, final_kernel=3
            ),
            loss_cls=dict(type='GaussianFocalLoss', reduction='mean'),
            loss_bbox=dict(type='L1Loss', reduction='mean', loss_weight=0.25),
            norm_bbox=True
        ),
        segmentation=dict(
            type='MapHead',
            in_channels=256,
            num_classes=5,  # Map elements to segment
            loss_weight=10.0
        )
    )
)

# Dataset configuration
dataset_type = 'NuScenesDataset'
data_root = 'data/nuscenes/'
class_names = [...]  # List of class names

# Data processing pipelines
train_pipeline = [...]  # List of data processing operations
test_pipeline = [...]  # List of evaluation processing operations

data = dict(
    samples_per_gpu=2,
    workers_per_gpu=4,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_train.pkl',
        pipeline=train_pipeline,
        classes=class_names,
    ),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_val.pkl',
        pipeline=test_pipeline,
        classes=class_names,
    ),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_val.pkl',
        pipeline=test_pipeline,
        classes=class_names,
    )
)

# Training configuration
optimizer = dict(
    type='AdamW',
    lr=0.0001,
    weight_decay=0.01,
    paramwise_cfg=dict(
        custom_keys=dict(
            backbone=dict(lr_mult=0.1),
        )
    )
)
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
lr_config = dict(
    policy='cyclic',
    target_ratio=(10, 0.0001),
    cyclic_times=1,
    step_ratio_up=0.4,
)
momentum_config = dict(
    policy='cyclic',
    target_ratio=(0.8947368421052632, 1),
    cyclic_times=1,
    step_ratio_up=0.4,
)
runner = dict(type='EpochBasedRunner', max_epochs=20)
```

Sources: configs/nuscenes/det/transfusion/secfpn

## Best Practices

### Configuration for Different Hardware

When configuring BEVFusion for different hardware environments:

| Parameter | Low-end Hardware | High-end Hardware |
|-----------|------------------|-------------------|
| samples_per_gpu | 1-2 | 4-8 |
| voxel_size | Larger (e.g., 0.1) | Smaller (e.g., 0.075) |
| max_voxels | Lower (e.g., 80000) | Higher (e.g., 160000) |
| backbone depth | Lighter (e.g., ResNet18) | Heavier (e.g., ResNet101) |
| fp16 | Enabled | Optional |

Sources: tools/train.py, configs/nuscenes

### Configuration for Different Tasks

1. **Detection-only**: Focus on CenterHead configuration, remove segmentation head
2. **Segmentation-only**: Focus on MapHead configuration, remove detection head
3. **Camera-only**: Configure only camera encoder, remove LiDAR components
4. **LiDAR-only**: Configure only LiDAR encoder, remove camera components
5. **Multi-modal fusion**: Configure both encoders and fusion layer

Sources: mmdet3d/models/detectors/bevfusion.py

## Troubleshooting Common Configuration Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Out of memory | Batch size too large | Reduce `samples_per_gpu` |
| Training instability | Learning rate too high | Adjust `lr_config` parameters |
| Slow training | Too many dataloader workers | Optimize `workers_per_gpu` |
| Poor performance | Incorrect point cloud range | Verify `point_cloud_range` matches dataset |
| Model loading error | Configuration mismatch | Ensure config matches saved checkpoint |

Sources: tools/train.py, mmdet3d/datasets

## Conclusion

The BEVFusion configuration system provides a flexible framework for customizing all aspects of the perception pipeline. Understanding how to properly configure each component allows researchers and engineers to adapt BEVFusion to different tasks, datasets, and hardware environments, enabling state-of-the-art 3D perception for autonomous driving applications.

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/demo.gif](assets/demo.gif)
- [docker/Dockerfile](docker/Dockerfile)
- [mmdet3d/datasets/pipelines/utils.py](mmdet3d/datasets/pipelines/utils.py)

</details>



This page provides guidelines for deploying BEVFusion models in production environments, including optimization techniques for different hardware platforms. It covers containerization, TensorRT acceleration, and performance benchmarks to help users achieve optimal inference speed.

## Deployment Requirements

Before deploying BEVFusion, ensure your environment meets the following requirements:

| Component | Requirement |
|-----------|-------------|
| Hardware  | NVIDIA GPU with compute capability ≥ 6.0 |
| CUDA      | 11.3.1 or compatible |
| Operating System | Linux (Ubuntu 20.04 recommended) |
| Python    | 3.8 (not compatible with Python 3.9+) |
| PyTorch   | 1.9 to 1.10.2 |
| Memory    | ≥16GB RAM for inference |

The codebase's dependencies are listed in the README and formalized in the Dockerfile:

```
- Python >= 3.8, <3.9
- OpenMPI = 4.0.4 and mpi4py = 3.0.3
- Pillow = 8.4.0 
- PyTorch >= 1.9, <= 1.10.2
- tqdm
- torchpack
- mmcv = 1.4.0
- mmdetection = 2.20.0
- nuscenes-dev-kit
```

Sources: [README.md:66-76](), [docker/Dockerfile:1-24]()

## Docker-based Deployment

BEVFusion provides a Docker container for simplified deployment. The container includes all necessary dependencies and CUDA support.

### Building the Docker Image

```bash
cd docker && docker build . -t bevfusion
```

### Running the Container

```bash
nvidia-docker run -it -v `pwd`/../data:/dataset --shm-size 16g bevfusion /bin/bash
```

Inside the container, install the BEVFusion code:

```bash
cd home && git clone https://github.com/mit-han-lab/bevfusion && cd bevfusion
python setup.py develop
```

The Docker deployment workflow is illustrated below:

```mermaid
flowchart TD
    A["Clone Repository"] --> B["Build Docker Image"]
    B --> C["Run Container with Dataset Mount"]
    C --> D["Install BEVFusion Inside Container"]
    D --> E["Run Inference"]
    
    subgraph "Docker Container"
        D
        E
        F["CUDA 11.3.1"]
        G["PyTorch 1.10.1"]
        H["BEVFusion Dependencies"]
    end
    
    I["Host GPU"] --> F
    J["Host Dataset"] --> E
```

Sources: [README.md:83-102](), [docker/Dockerfile:1-24]()

## TensorRT Deployment

NVIDIA has developed an optimized TensorRT deployment solution for BEVFusion called CUDA-BEVFusion, achieving 25 FPS on Jetson Orin platforms.

### TensorRT Integration Benefits

- INT8 quantization for acceleration
- Optimized CUDA kernels for BEV transformation
- Memory optimization for edge devices
- Real-time performance (25 FPS) on NVIDIA Jetson Orin

```mermaid
flowchart LR
    A["PyTorch Model (.pth)"] --> B["Model Export"]
    B --> C["TensorRT Conversion"]
    C --> D["INT8 Calibration"]
    D --> E["Optimized TensorRT Engine"]
    E --> F["Real-time Inference"]
    
    subgraph "CUDA-BEVFusion"
        G["Custom BEV Pooling"]
        H["Sparse Convolution Optimization"]
        I["Sensor Fusion Acceleration"]
    end
    
    G --> E
    H --> E
    I --> E
```

To use NVIDIA's TensorRT implementation, refer to the [CUDA-BEVFusion repository](https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution/tree/master/CUDA-BEVFusion).

Sources: [README.md:9-10](), [README.md:196-197]()

## Deployment Pipeline

The complete deployment pipeline for BEVFusion includes data processing, model inference, and visualization components:

```mermaid
flowchart TD
    A["Raw Sensor Data"] --> B["Data Preprocessing"]
    B --> C["BEVFusion Model Inference"]
    C --> D["Post-processing"]
    D --> E["Visualization/Application"]
    
    subgraph "BEVFusion Model"
        F["Camera Encoder"]
        G["LiDAR Encoder"]
        H["View Transformation"]
        I["Feature Fusion"]
        J["Detection/Segmentation Heads"]
        
        F --> H
        G --> I
        H --> I
        I --> J
    end
    
    B --> F
    B --> G
    J --> D
```

### Inference Workflow

1. **Data Loading**: Load camera images and LiDAR point clouds
2. **Preprocessing**: Apply normalization and transformations
3. **Model Inference**: Pass data through the BEVFusion model
4. **Post-processing**: Convert model outputs to detections/segmentation maps
5. **Visualization**: Render results for display or downstream applications

Sources: [README.md:44-59]()

## Model Evaluation and Export

Before deployment, evaluate your model's performance using the testing script:

```bash
torchpack dist-run -np [number of gpus] python tools/test.py [config file path] [checkpoint path] --eval [evaluation type]
```

Example for detection model evaluation:

```bash
torchpack dist-run -np 8 python tools/test.py configs/nuscenes/det/transfusion/secfpn/camera+lidar/swint_v0p075/convfuser.yaml pretrained/bevfusion-det.pth --eval bbox
```

For segmentation model evaluation:

```bash
torchpack dist-run -np 8 python tools/test.py configs/nuscenes/seg/fusion-bev256d2-lss.yaml pretrained/bevfusion-seg.pth --eval map
```

Sources: [README.md:132-154]()

## Performance Optimization

### Optimizing for Inference Speed

BEVFusion includes a custom CUDA implementation of BEV pooling that significantly improves performance:

```mermaid
flowchart LR
    A["Camera Features"] --> B["BEV Pooling"]
    C["Camera Parameters"] --> B
    B --> D["BEV Features"]
    
    subgraph "Optimized CUDA Implementation"
        E["bev_pool_forward"]
        F["bev_pool_backward"]
    end
    
    B --> E
    E --> D
```

Key optimizations in BEVFusion include:

1. **Efficient BEV Pooling**: Custom CUDA operations that reduce view transformation latency by more than 40x
2. **Sparse Convolution**: Efficient processing of sparse point cloud data
3. **Optimized Feature Fusion**: Lightweight fusion mechanisms to combine camera and LiDAR features
4. **Task-agnostic Design**: Unified architecture for both detection and segmentation

Sources: [README.md:18-20](), [README.md:51-52]()

### Performance Benchmarks

The following table shows benchmark results across different hardware platforms:

| Hardware Platform | Model Variant | FPS | Memory Usage |
|-------------------|---------------|-----|--------------|
| NVIDIA A100 | BEVFusion (Full) | 35+ | ~16GB |
| NVIDIA RTX 3090 | BEVFusion (Full) | 20+ | ~14GB |
| NVIDIA Jetson AGX Orin | BEVFusion-TRT | 25 | ~8GB |

Sources: [README.md:9-10]()

## Integrations

BEVFusion has been integrated into several frameworks for easier deployment:

1. **NVIDIA DeepStream**: Integration for sensor fusion capabilities (2024)
2. **MMDetection3D**: Integrated as part of the MMDetection3D project
3. **TensorRT**: Optimized deployment through NVIDIA's CUDA-BEVFusion

```mermaid
flowchart TD
    A["BEVFusion"] --> B["MMDetection3D Integration"]
    A --> C["DeepStream Integration"]
    A --> D["TensorRT (CUDA-BEVFusion)"]
    
    subgraph "Use Cases"
        E["Autonomous Driving"]
        F["Robotics"]
        G["Industrial Automation"]
    end
    
    B --> E
    C --> E
    D --> E
    D --> F
    D --> G
```

Sources: [README.md:7-14]()

## Troubleshooting Deployment Issues

Common deployment issues and their solutions:

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce batch size or image resolution |
| Slow inference | Enable TensorRT optimization, check CUDA version compatibility |
| Import errors | Ensure correct environment setup according to README |
| Numba errors | Install compatible numba version (0.48.0) |
| Missing weights | Use the provided script to download pretrained models |

Consider using Python `numba` for further optimization of data processing pipelines:

```python
@numba.njit
def performance_critical_function(data):
    # Optimized processing
    return result
```

Sources: [mmdet3d/datasets/pipelines/utils.py:1-385]()

## Additional Resources

- NVIDIA CUDA-BEVFusion: https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution/tree/master/CUDA-BEVFusion
- MMDetection3D integration: https://github.com/open-mmlab/mmdetection3d/tree/main/projects/BEVFusion