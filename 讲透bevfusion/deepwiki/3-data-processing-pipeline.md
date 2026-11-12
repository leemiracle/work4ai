<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/bevfusion · page 3 Data Processing Pipeline · fetched 2026-10-30 -->

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

