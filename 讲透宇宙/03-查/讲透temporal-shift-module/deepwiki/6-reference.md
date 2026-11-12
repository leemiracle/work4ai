<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/temporal-shift-module · page 6 Reference · fetched 2026-10-30 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ops/temporal_shift.py](ops/temporal_shift.py)

</details>



This page serves as a comprehensive reference for the Temporal Shift Module (TSM) codebase, documenting supported model architectures, datasets, and performance benchmarks. For implementation details of the Temporal Shift Module itself, see [Core Components](#2) and [Temporal Shift Module](#2.1).

## Supported Model Architectures

TSM is designed to be compatible with standard 2D CNN architectures, allowing them to capture temporal information without additional parameters. The following backbone architectures are officially supported:

```mermaid
flowchart LR
    TSM["Temporal Shift Module"]
    
    subgraph "Supported Backbone Architectures"
        ResNet50["ResNet50"]
        ResNet101["ResNet101"]
        ResNext101["ResNext101"]
        MobileNetV2["MobileNetV2"]
        BNInception["BNInception"]
    end
    
    TSM --> ResNet50
    TSM --> ResNet101
    TSM --> ResNext101
    TSM --> MobileNetV2
    TSM --> BNInception
    
    ResNet50 --> Kinetics["Kinetics-400"]
    ResNet50 --> Something1["Something-Something-V1"]
    ResNet50 --> Something2["Something-Something-V2"]
    
    ResNet101 --> Kinetics
    ResNet101 --> Something1
    ResNet101 --> Something2
    
    ResNext101 --> Kinetics
    
    MobileNetV2 --> Kinetics
    MobileNetV2 --> OnlineDemo["Real-time Demos"]
```

Sources: [README.md:85-114](), [README.md:141-155]()

### ResNet Family

ResNet models (ResNet50, ResNet101, ResNext101) serve as the primary backbones for TSM implementation. They offer a balance between accuracy and computational efficiency. The temporal shift operation is applied to specific layers in the ResNet architecture.

#### Integration Method

TSM can be integrated into ResNet models in two ways:
- **Block mode**: Applies temporal shift to all blocks
- **Blockres mode**: Applies temporal shift only to residual blocks at specific intervals

```mermaid
flowchart TD
    subgraph "make_temporal_shift Function"
        direction LR
        Input["Input CNN Model"]
        CheckType["Check Model Type"]
        ApplyTSM["Apply TSM to Layers"]
        Output["Output TSM-enabled Model"]
        
        Input --> CheckType
        CheckType --> ApplyTSM
        ApplyTSM --> Output
    end
    
    subgraph "TSM Integration Options"
        Block["block: Apply to all blocks"]
        BlockRes["blockres: Apply to residual blocks"]
    end
    
    CheckType --> Block
    CheckType --> BlockRes
    
    BlockRes --> ResNet["ResNet Layers with TSM"]
```

Sources: [ops/temporal_shift.py:97-139]()

### MobileNetV2

MobileNetV2 is specifically used for efficient deployment scenarios, such as the real-time hand gesture recognition demo. It provides a more lightweight alternative to ResNet models, achieving 69.5% accuracy on Kinetics-400 with 8-frame input.

Sources: [README.md:114](), [README.md:256-260]()

## Supported Datasets

TSM has been successfully trained and evaluated on various action recognition datasets:

```mermaid
flowchart LR
    subgraph "Video Understanding Datasets"
        Kinetics["Kinetics-400
        400 action classes
        ~240k training videos"]
        
        SomethingV1["Something-Something-V1
        174 action classes
        ~110k videos"]
        
        SomethingV2["Something-Something-V2
        174 action classes
        ~220k videos"]
        
        UCF101["UCF101
        101 action classes
        ~13k videos"]
        
        HMDB51["HMDB51
        51 action classes
        ~7k videos"]
        
        Jester["Jester
        27 hand gestures
        ~150k videos"]
    end
    
    Kinetics --> GeneralActions["General Action Recognition"]
    SomethingV1 --> TemporalReasoning["Temporal Reasoning"]
    SomethingV2 --> TemporalReasoning
    UCF101 --> GeneralActions
    HMDB51 --> GeneralActions
    Jester --> Deployment["Real-time Deployment"]
```

Sources: [README.md:61-62]()

### Dataset Processing Pipeline

For all datasets, the processing follows a similar pipeline:
1. Extract frames from videos using tools like [tools/vid2img_kinetics.py]() or [tools/vid2img_sthv2.py]()
2. Generate annotations using dataset-specific scripts like [tools/gen_label_kinetics.py]()
3. Configure dataset paths in [ops/dataset_configs.py]()

Sources: [README.md:57-66]()

## Performance Reference

### Kinetics-400 Performance

#### Dense Sampling Protocol

Results using I3D dense sampling protocol (8-frame and 16-frame):

| Model | Frames × Clips | Kinetics Accuracy |
|-------|----------------|------------------|
| TSN ResNet50 (2D) | 8 × 10 | 70.6% |
| TSM ResNet50 | 8 × 10 | 74.1% |
| TSM ResNet50 NL | 8 × 10 | 75.6% |
| TSM ResNext101 | 8 × 10 | 76.3% |
| TSM MobileNetV2 | 8 × 10 | 69.5% |

Sources: [README.md:92-114]()

#### Uniform Sampling Protocol

Results using uniform sampled frames (more efficient):

| Model | Frames × Clips | 1-crop Accuracy | 10-crop Accuracy |
|-------|----------------|-----------------|------------------|
| TSN ResNet50 (2D) | 8 × 1 | 68.8% | 69.9% |
| TSM ResNet50 | 8 × 1 | 71.2% | 72.8% |
| TSM ResNet50 | 16 × 1 | 72.6% | 73.7% |

Sources: [README.md:118-125]()

### Something-Something Performance

#### Something-Something-V1

| Model | Frames | Center crop × 1clip | Full res × 2clip |
|-------|--------|---------------------|------------------|
| TSM ResNet50 | 8 | 45.6% | 47.2% |
| TSM ResNet50 | 16 | 47.2% | 48.4% |
| TSM ResNet101 | 8 | 46.9% | 48.7% |

Sources: [README.md:142-146]()

#### Something-Something-V2

| Model | Frames × Clips | Accuracy |
|-------|----------------|----------|
| TSM ResNet50 | 8 × 2 | 61.2% |
| TSM ResNet50 | 16 × 2 | 63.1% |
| TSM ResNet101 | 8 × 2 | 63.3% |

Sources: [README.md:152-156]()

## Implementation Reference

### TSM Key Parameters

The Temporal Shift Module has several key parameters that control its behavior:

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `n_segment` | Number of frames in a video segment | 8, 16 |
| `n_div` | Number of divisions for channel shift | 8 (default) |
| `inplace` | Whether to perform shift operation in-place | False (default) |
| `fold_div` | Portion of channels to shift (derived from n_div) | n_div (default: 8) |
| `place` | Where to insert TSM in the network | 'blockres' (default) |

Sources: [ops/temporal_shift.py:12-20](), [ops/temporal_shift.py:97-139]()

### Shift Operation Implementation

The core TSM implementation shifts channels along the temporal dimension:

```mermaid
flowchart LR
    subgraph "TemporalShift.shift Function"
        direction TB
        Input["Input tensor (n×t×c×h×w)"]
        Reshape["Reshape to (n_batch, n_segment, c, h, w)"]
        CalculateFold["Calculate fold = c / fold_div"]
        
        subgraph "Channel Shifting"
            ShiftLeft["Shift left: out[:, :-1, :fold] = x[:, 1:, :fold]"]
            ShiftRight["Shift right: out[:, 1:, fold:2*fold] = x[:, :-1, fold:2*fold]"]
            NoShift["No shift: out[:, :, 2*fold:] = x[:, :, 2*fold:]"]
        end
        
        Restore["Restore shape to (nt, c, h, w)"]
        Output["Output tensor"]
        
        Input --> Reshape
        Reshape --> CalculateFold
        CalculateFold --> ShiftLeft
        CalculateFold --> ShiftRight
        CalculateFold --> NoShift
        ShiftLeft --> Restore
        ShiftRight --> Restore
        NoShift --> Restore
        Restore --> Output
    end
```

Sources: [ops/temporal_shift.py:26-44]()

## Testing Configurations

Various testing configurations are available for different performance-accuracy tradeoffs:

### Efficient Setting
- Center crop
- Single clip
- Example command: `python test_models.py something --test_segments=8 --test_crops=1`

### Accurate Setting
- Full resolution
- Multiple clips (2 or 10)
- Example command: `python test_models.py something --test_segments=8 --test_crops=3 --twice_sample`

### Dense Sampling Setting
- Full resolution
- Dense temporal sampling
- Example command: `python test_models.py kinetics --test_segments=8 --test_crops=3 --dense_sample --full_res`

Sources: [README.md:159-214]()

## Pre-trained Model References

Pre-trained models are available for:
- TSM models with RGB input on Kinetics-400 (8-frame and 16-frame)
- TSM models with RGB input on Something-Something-V1 and V2
- TSM models with optical flow input on Kinetics-400

These models can be used directly for inference or as initialization for fine-tuning on other datasets.

Sources: [README.md:85-133]()

---

