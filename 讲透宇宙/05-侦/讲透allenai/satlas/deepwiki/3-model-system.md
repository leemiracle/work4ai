<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlas · page 3 Model System · fetched 2026-10-26 -->

# Model System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DataValidationReport.md](DataValidationReport.md)
- [ModelArchitecture.md](ModelArchitecture.md)
- [images/satlasnet.svg](images/satlasnet.svg)
- [requirements.txt](requirements.txt)
- [satlas/model/classify.py](satlas/model/classify.py)
- [satlas/model/dataset.py](satlas/model/dataset.py)
- [satlas/model/model.py](satlas/model/model.py)
- [satlas/model/models.py](satlas/model/models.py)
- [satlas/transforms/augment.py](satlas/transforms/augment.py)

</details>



This page provides an overview of the SatlasNet model system, its architecture, components, and how they work together to process satellite imagery for various tasks. For details on model training, see [Training Pipeline](#3.2), and for information about using trained models for inference, see [Inference Pipeline](#3.3).

## Overview

The Model System in Satlas is built around SatlasNet, a flexible neural network architecture designed specifically for satellite imagery analysis. The system provides a modular framework where different components can be combined to create models for various geospatial tasks, such as object detection, segmentation, and regression.

```mermaid
flowchart TD
    subgraph "Model System"
        Config["Configuration"]
        Backbone["Backbone Networks"]
        Intermediates["Intermediate Processing"]
        Heads["Task-specific Heads"]
        
        Config --> |"Defines"| Backbone
        Config --> |"Defines"| Intermediates
        Config --> |"Defines"| Heads
        
        Backbone --> |"Feature maps"| Intermediates
        Intermediates --> |"Processed features"| Heads
        
        Heads --> Detect["Detection Output"]
        Heads --> Segment["Segmentation Output"]
        Heads --> Regress["Regression Output"]
    end
```

Sources: [satlas/model/model.py:1-26](). [satlas/model/models.py:1-9]().

## Key Components

The SatlasNet model architecture consists of three main component types:

1. **Backbone** - Extracts feature maps from input images at different resolutions
2. **Intermediates** - Process feature maps from the backbone (optional)
3. **Heads** - Task-specific components that produce the final outputs

These components are configured through a configuration system that allows for flexible model creation.

```mermaid
classDiagram
    class Model {
        backbone
        intermediates
        heads
        forward()
    }
    
    class Backbone {
        out_channels
        forward()
    }
    
    class Intermediate {
        out_channels
        forward()
    }
    
    class Head {
        forward()
    }
    
    Model --> "1" Backbone
    Model --> "0..n" Intermediate
    Model --> "1..n" Head
    
    class SwinBackbone {
        arch
        backbone
        out_channels
    }
    
    class ResnetBackbone {
        resnet
        out_channels
    }
    
    class AggregationBackbone {
        backbone
        aggregation_op
        groups
    }
    
    Backbone <|-- SwinBackbone
    Backbone <|-- ResnetBackbone
    Backbone <|-- AggregationBackbone
    
    class Fpn {
        fpn
        out_channels
    }
    
    class Upsample {
        layers
        out_channels
    }
    
    Intermediate <|-- Fpn
    Intermediate <|-- Upsample
    
    class FrcnnHead {
        rpn
        roi_heads
    }
    
    class SimpleHead {
        loss
        num_outputs
    }
    
    Head <|-- FrcnnHead
    Head <|-- SimpleHead
```

Sources: [satlas/model/model.py:27-31](). [ModelArchitecture.md:1-23]().

## Model Architecture

The Model System uses a flexible architecture that processes satellite imagery through several stages:

1. Multiple aligned images are input to a backbone network
2. Features are extracted at different resolutions
3. Intermediate layers can process and refine these features
4. Task-specific heads produce various outputs for different purposes

```mermaid
flowchart TD
    Input["Multiple Aligned Images"] --> Normalize["Image Normalization"]
    Normalize --> Backbone["Backbone Network\n(Swin-v2-Base/ResNet)"]
    
    Backbone --> |"Feature Maps"| Intermediates["Intermediate Processing\n(FPN/Temporal Pooling)"]
    Intermediates --> TaskHeads["Task-specific Heads"]
    
    subgraph "Outputs by Task Type"
        TaskHeads --> FRCNNHead["FRCNN Head\n(for Detection Tasks)"]
        TaskHeads --> SimpleHead["Simple Head\n(for Segmentation/Regression)"]
        
        FRCNNHead --> Points["Point Detections\n(wind turbines, platforms)"]
        SimpleHead --> Segments["Segmentation Maps\n(solar farms, tree cover)"]
        SimpleHead --> Values["Regression Values"]
    end
```

Sources: [satlas/model/model.py:10-26](). [ModelArchitecture.md:1-16]().

## Backbone Networks

The backbone is responsible for extracting features from input images. Satlas supports several backbone architectures:

### Swin Transformer Backbone

The Swin Transformer backbone is the default backbone used in SatlasNet. It's a hierarchical vision transformer that uses shifted windows to process images efficiently.

```mermaid
flowchart LR
    Input["Input Images"] --> Patch["Patch Embedding"]
    Patch --> Stage1["Swin Stage 1"]
    Stage1 --> Stage2["Swin Stage 2"]
    Stage2 --> Stage3["Swin Stage 3"]
    Stage3 --> Stage4["Swin Stage 4"]
    
    Stage1 --> |"Feature Map 1\n(1/4 resolution)"| Output1["Output Features"]
    Stage2 --> |"Feature Map 2\n(1/8 resolution)"| Output2["Output Features"]
    Stage3 --> |"Feature Map 3\n(1/16 resolution)"| Output3["Output Features"]
    Stage4 --> |"Feature Map 4\n(1/32 resolution)"| Output4["Output Features"]
```

Sources: [satlas/model/model.py:32-118](). [ModelArchitecture.md:2-11]().

### ResNet Backbone

The ResNet backbone provides an alternative feature extraction approach using residual connections.

```mermaid
flowchart LR
    Input["Input Images"] --> Conv1["Conv1 + BN + ReLU"]
    Conv1 --> MaxPool["MaxPool"]
    MaxPool --> Layer1["Layer1"]
    Layer1 --> Layer2["Layer2"]
    Layer2 --> Layer3["Layer3"]
    Layer3 --> Layer4["Layer4"]
    
    Layer1 --> |"Feature Map 1\n(1/4 resolution)"| Output1["Output Features"]
    Layer2 --> |"Feature Map 2\n(1/8 resolution)"| Output2["Output Features"]
    Layer3 --> |"Feature Map 3\n(1/16 resolution)"| Output3["Output Features"]
    Layer4 --> |"Feature Map 4\n(1/32 resolution)"| Output4["Output Features"]
```

Sources: [satlas/model/model.py:120-191]().

### Aggregation Backbone

The Aggregation Backbone is a special backbone that processes multiple aligned images and combines their features using various operations (max pooling, mean, convolutional RNN, etc.).

```mermaid
flowchart TD
    Inputs["Multiple Aligned Images"] --> Split["Split by Channels"]
    
    Split --> BB1["Underlying Backbone\nInstance 1"]
    Split --> BB2["Underlying Backbone\nInstance 2"]
    Split --> BBN["Underlying Backbone\nInstance N"]
    
    BB1 --> |"Feature Maps"| Agg["Aggregation Layer\n(max, mean, convrnn, conv3d, conv1d)"]
    BB2 --> |"Feature Maps"| Agg
    BBN --> |"Feature Maps"| Agg
    
    Agg --> Output["Aggregated Feature Maps"]
```

Sources: [satlas/model/model.py:193-322]().

## Intermediate Processing

Intermediates are optional components that process feature maps from the backbone before they're sent to the heads.

### Feature Pyramid Network (FPN)

The FPN combines high-level semantically strong features with low-level spatially accurate features to improve performance on tasks requiring multi-scale predictions.

```mermaid
flowchart TD
    FM1["Feature Map 1\n(1/4 resolution)"] --> FPN["Feature Pyramid Network"]
    FM2["Feature Map 2\n(1/8 resolution)"] --> FPN
    FM3["Feature Map 3\n(1/16 resolution)"] --> FPN
    FM4["Feature Map 4\n(1/32 resolution)"] --> FPN
    
    FPN --> OFMS["Output Feature Maps\nwith Unified Channel Count"]
```

Sources: [satlas/model/model.py:324-348](). [ModelArchitecture.md:12]().

### Upsample

The Upsample intermediate creates a feature map at the input resolution, which can be useful for high-resolution tasks like segmentation.

```mermaid
flowchart LR
    FM["Input Feature Maps"] --> USM["Upsample Module"]
    
    subgraph "Upsample Processing"
        USM --> Conv["Conv2D"]
        Conv --> ReLU["ReLU"]
        ReLU --> TransConv["Transpose Conv2D"]
        TransConv --> OutReLU["ReLU"]
    end
    
    OutReLU --> Output["Higher Resolution Feature Map"]
```

Sources: [satlas/model/model.py:350-425]().

## Task-Specific Heads

The heads are responsible for transforming feature maps into task-specific outputs.

### Faster R-CNN Head (Detection Tasks)

Used for object detection tasks like identifying wind turbines or offshore platforms. It consists of a Region Proposal Network (RPN) and ROI Heads.

```mermaid
flowchart TD
    FM["Feature Maps"] --> RPN["Region Proposal Network"]
    FM --> ROI["ROI Heads"]
    RPN --> |"Proposals"| ROI
    
    ROI --> BoxHead["Box Head"]
    ROI --> MaskHead["Mask Head\n(for Instance Segmentation)"]
    
    BoxHead --> BoxOutput["Bounding Boxes\nand Class Labels"]
    MaskHead --> MaskOutput["Instance Masks"]
```

Sources: [satlas/model/model.py:447-546]().

### Simple Head (Segmentation and Regression Tasks)

Used for segmentation tasks (like solar farm identification) and regression tasks (like tree cover measurement).

```mermaid
flowchart LR
    FM["Feature Maps"] --> Conv["Conv Layers"]
    Conv --> Output["Task Output\n(Segmentation Masks\nor Regression Values)"]
```

Sources: [satlas/model/model.py:548-786]().

## Data Flow

The following diagram illustrates how data flows through the model system during inference:

```mermaid
sequenceDiagram
    participant I as Input Images
    participant B as Backbone
    participant Int as Intermediates
    participant H as Heads
    participant O as Outputs
    
    I->>B: Multiple aligned images
    B->>Int: Feature maps at different resolutions
    Int->>H: Processed feature maps
    H->>O: Task-specific outputs
    
    Note over B,Int: Temporal max pooling for multi-image input
    Note over Int,H: Feature pyramid network combines multi-scale features
    Note over H,O: Faster R-CNN for detection<br>Simple Head for segmentation/regression
```

Sources: [satlas/model/model.py](). [ModelArchitecture.md]().

## Dataset and Tasks

The model system supports various geospatial tasks defined in the dataset configuration:

| Task Type | Description | Examples |
|-----------|-------------|----------|
| `detect` | Object detection with bounding boxes | Wind turbines, offshore platforms |
| `instance` | Instance segmentation with masks | Buildings, solar farms |
| `segment` | Semantic segmentation | Land cover types |
| `bin_segment` | Binary segmentation for multiple categories | Roads, rivers, runways |
| `regress` | Regression values | Tree cover percentage |
| `classification` | Image-level classification | Sport type, park type |

Sources: [satlas/model/dataset.py:16-331]().

## Model Creation Process

The model system creates models based on a configuration object that specifies the backbone, intermediates, and heads to use:

```mermaid
flowchart TD
    Config["Configuration File"] --> ModelInfo["Model Information"]
    
    ModelInfo --> CreateModel["get_model()"]
    
    CreateModel --> Model["Model Instance"]
    
    Model --> InitBackbone["Initialize Backbone"]
    Model --> InitIntermediates["Initialize Intermediates"]
    Model --> InitHeads["Initialize Heads for Tasks"]
    
    InitBackbone --> ForwardPass["Forward Pass"]
    InitIntermediates --> ForwardPass
    InitHeads --> ForwardPass
    
    ForwardPass --> Output["Task Outputs"]
```

Sources: [satlas/model/models.py:1-9](). [satlas/model/model.py]().

## Integration with Data Augmentation

The model system integrates with data augmentation techniques to improve training:

| Augmentation | Description |
|--------------|-------------|
| CropFlip | Randomly crops and flips images |
| Pad | Pads images to a specified size |
| MixChannels | Mixes channels in specified groups |
| Noise | Adds random noise to images |
| Brightness | Adjusts brightness randomly |
| Resize | Resizes images to random sizes |

Sources: [satlas/transforms/augment.py:8-366]().

## Key Operations in Multi-temporal Processing

When processing multiple temporal images, the model can use various aggregation operations:

| Aggregation | Description |
|-------------|-------------|
| max | Maximum value across temporal dimension |
| mean | Average value across temporal dimension |
| convrnn | Convolutional recurrent neural network |
| conv3d | 3D convolution across temporal dimension |
| conv1d | 1D convolution across temporal dimension |

Sources: [satlas/model/model.py:193-322]().

## Summary

The Model System in Satlas provides a flexible architecture for processing satellite imagery for various geospatial tasks. It combines state-of-the-art backbones like Swin Transformers with task-specific heads to create models that can detect objects, segment regions, and perform regression tasks on satellite imagery.

The modular design allows for easy customization and extension to support new tasks and model architectures while maintaining compatibility with the overall Satlas framework.

---

