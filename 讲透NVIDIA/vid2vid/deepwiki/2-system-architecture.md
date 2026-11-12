<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/vid2vid · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [models/base_model.py](models/base_model.py)
- [models/models.py](models/models.py)
- [train.py](train.py)

</details>



This document provides a comprehensive overview of the vid2vid system architecture, explaining how different components interact to enable high-resolution photorealistic video-to-video translation. The vid2vid system translates videos from one domain to another (e.g., semantic maps to photo-realistic videos, face edges to talking faces, or poses to human motions) while maintaining temporal consistency.

For specific implementation details about individual components, see [Generator Architecture](#2.1), [Discriminator Architecture](#2.2), and [Optical Flow Estimation (FlowNet)](#2.3).

## Core Architecture Overview

The vid2vid system consists of several interacting components that work together to achieve video-to-video translation:

```mermaid
graph TD
    subgraph "Core Components"
        G["Vid2VidModelG"]
        D["Vid2VidModelD"]
        F["FlowNet"]
    end
    
    subgraph "Training Process"
        TP["train.py"]
        TP --> G
        TP --> D
        TP --> F
    end
    
    subgraph "Testing Process"
        TST["test.py"]
        TST --> G
        TST --> F
    end
    
    subgraph "Data Pipeline"
        DL["CreateDataLoader"]
        DS["Dataset Classes"]
        DL --> DS
        DL --> TP
        DL --> TST
    end
    
    subgraph "Configuration"
        BO["BaseOptions"]
        TO["TrainOptions"]
        TSO["TestOptions"]
        BO --> TO
        BO --> TSO
        TO --> TP
        TSO --> TST
    end
    
    G --> O["Generated Frames"]
    D --> L["Loss Computation"]
    F --> FL["Optical Flow"]
    FL --> G
```

Sources: [train.py:14-128](), [models/models.py:61-84]()

## Component Architecture and Relationships

All models in the vid2vid system inherit from a common `BaseModel` class that provides shared functionality:

```mermaid
classDiagram
    BaseModel <|-- Vid2VidModelG
    BaseModel <|-- Vid2VidModelD
    BaseModel <|-- FlowNet
    
    class BaseModel {
        +initialize(opt)
        +forward()
        +save(label)
        +load_network()
        +update_learning_rate()
        +grid_sample()
        +resample()
        +build_pyr()
    }
    
    class Vid2VidModelG {
        +forward(input_A, input_B, inst_A, fake_B_prev_last)
        +generate_frame_train()
        +generate_first_frame()
        +inference()
        +compute_fake_B_prev()
    }
    
    class Vid2VidModelD {
        +forward(scale_T, tensors_list)
        +compute_loss_D()
        +compute_loss_D_T()
        +get_all_skipped_frames()
        +get_losses()
    }
    
    class FlowNet {
        +forward(real_B, real_B_prev)
        +compute_flow_and_conf()
    }
```

Sources: [models/base_model.py:6-196](), [models/models.py:61-84]()

### Component Responsibilities

1. **Generator (Vid2VidModelG)**:
   - Transforms input from the source domain to the target domain
   - Handles temporal consistency via flow-based warping
   - Works across multiple spatial scales
   - Can generate the first frame or use a separate pre-trained model

2. **Discriminator (Vid2VidModelD)**:
   - Contains both spatial and temporal discriminators
   - Evaluates frame quality individually and as sequences
   - Operates at multiple spatial and temporal scales
   - Computes various losses (adversarial, feature matching, etc.)

3. **FlowNet**:
   - Estimates optical flow between consecutive frames
   - Produces confidence maps for the flow estimates
   - Provides reference flow to guide the generator

4. **Data Loader System**:
   - Handles different types of datasets (face, pose, cityscapes)
   - Prepares data batches for the models
   - Manages sequence length and temporal sampling

5. **Options System**:
   - Configures all aspects through command-line arguments
   - Provides default values and validates parameters
   - Organizes related parameters in hierarchical classes

## Training Data Flow

The training process involves a complex flow of data between multiple models. Here's how data flows through the system during training:

```mermaid
flowchart TD
    subgraph "Data Preparation"
        A["input_A (Source Domain)"] 
        B["input_B (Target Domain)"]
        I["inst_A (Instance Maps)"]
        PFL["fake_B_prev_last (Previous Output)"]
    end
    
    subgraph "Generator Forward Pass"
        G["modelG.forward()"]
        A --> G
        B --> G
        I --> G
        PFL --> G
        G --> FB["fake_B (Generated Frame)"]
        G --> FBR["fake_B_raw (Raw Output)"]
        G --> FL["flow (Predicted Flow)"]
        G --> W["weight (Flow Confidence)"]
        G --> RA["real_A (Processed Input)"]
        G --> RBP["real_Bp (Real Frames Sequence)"]
        G --> FBL["fake_B_last (Latest Generated)"]
    end
    
    subgraph "Flow Estimation"
        FN["flowNet.forward()"]
        RB["real_B (Current Real Frame)"] --> FN
        RBPV["real_B_prev (Previous Real Frame)"] --> FN
        FN --> FR["flow_ref (Reference Flow)"]
        FN --> CR["conf_ref (Reference Confidence)"]
    end
    
    subgraph "Discriminator Forward Pass"
        D["modelD.forward()"]
        RB --> D
        FB --> D
        FBR --> D
        RA --> D
        RBPV --> D
        FBP["fake_B_prev (Prev Generated)"] --> D
        FL --> D
        W --> D
        FR --> D
        CR --> D
        D --> LD["loss_dict (Spatial Losses)"]
        D --> LDT["loss_dict_T (Temporal Losses)"]
    end
    
    RBP --> RB
    RBP --> RBPV
    FB --> FBP
    FBL --> PFL
    
    subgraph "Loss Computation and Backprop"
        LC["modelD.get_losses()"]
        LD --> LC
        LDT --> LC
        LC --> LG["loss_G (Generator Loss)"]
        LC --> LD_OUT["loss_D (Spatial Disc Loss)"]
        LC --> LDT_OUT["loss_D_T (Temporal Disc Loss)"]
        
        LG --> OG["optimizer_G.step()"]
        LD_OUT --> OD["optimizer_D.step()"]
        LDT_OUT --> ODT["optimizer_D_T.step()"]
    end
```

Sources: [train.py:49-94]()

## Multi-Scale Processing Architecture

A key feature of vid2vid is its multi-scale approach in both spatial and temporal dimensions:

```mermaid
graph TD
    subgraph "Spatial Scales"
        S1["Scale 0 (Finest)"]
        S2["Scale 1 (Medium)"]
        S3["Scale 2 (Coarsest)"]
    end
    
    subgraph "Temporal Scales"
        T1["Scale 0 (Original Frame Rate)"]
        T2["Scale 1 (Subsampled x n_frames_D)"]
        T3["Scale 2 (Subsampled x n_frames_D²)"]
    end
    
    subgraph "Generator Network"
        G0["netG0 (Finest Scale)"]
        G1["netG1 (Medium Scale)"]
        G2["netG2 (Coarsest Scale)"]
        
        G2 --> G1
        G1 --> G0
    end
    
    subgraph "Discriminator Network"
        D0["netD0 (Spatial)"]
        D1["netD_T0 (Temporal Scale 0)"]
        D2["netD_T1 (Temporal Scale 1)"]
        D3["netD_T2 (Temporal Scale 2)"]
    end
    
    S1 --> G0
    S2 --> G1
    S3 --> G2
    
    S1 --> D0
    
    T1 --> D1
    T2 --> D2
    T3 --> D3
```

Sources: [models/base_model.py:122-134](), [README.md:175-181]()

This multi-scale approach allows the system to:
- Handle different levels of spatial detail (from coarse structure to fine details)
- Capture temporal dynamics at different time scales
- Train efficiently through a coarse-to-fine strategy

## Multi-GPU Architecture

The vid2vid system has a sophisticated multi-GPU processing architecture to handle the computational demands of video generation:

```mermaid
graph TD
    subgraph "GPU Allocation Strategy"
        OPT["n_gpus_gen parameter"]
        OPT --> |"Value = total GPUs"| S1["All Models use DataParallel"]
        OPT --> |"Value < total GPUs"| S2["Split GPUs between G and D"]
    end
    
    subgraph "Split GPU Mode"
        GG["Generator GPUs (0 to n_gpus_gen-1)"]
        DG["Discriminator GPUs (0 and n_gpus_gen to end)"]
        FG["FlowNet GPUs (Same as Discriminator)"]
        
        G1["GPU 0: First frames"] --> G2["GPU 1: Next frames"] --> G3["..."]
        D1["Discriminator processes completed sequences"]
    end
    
    subgraph "Sequential Frame Generation"
        F1["Frame t"] --> F2["Frame t+1"] --> F3["Frame t+2"]
        F1 --> |"Input to next"| F2
        F2 --> |"Input to next"| F3
    end
```

Sources: [models/models.py:10-60](), [README.md:175-187]()

The system offers two main modes of GPU utilization:

1. **Split GPU Mode**: Separate GPUs for generator and discriminator
   - First `n_gpus_gen` GPUs dedicated to the generator
   - Remaining GPUs used for discriminator and FlowNet
   - Sequential generation of frames across generator GPUs

2. **DataParallel Mode**: All models use standard PyTorch DataParallel
   - Used when `n_gpus_gen` equals the total number of GPUs
   - Both generator and discriminator distributed across all GPUs

## Training Process Architecture

The training process follows a sophisticated schedule to gradually increase complexity:

```mermaid
graph TD
    subgraph "Training Schedule"
        E1["Initial epochs"]
        E2["Middle epochs"]
        E3["Final epochs"]
        
        E1 --> |"Increase sequence length"| E2
        E2 --> |"Finetune all scales"| E3
        E3 --> |"Learning rate decay"| EF["Training complete"]
    end
    
    subgraph "Sequence Length Growth"
        SL["n_frames_total parameter"]
        NS["niter_step parameter"]
        
        NS --> |"Every niter_step epochs"| DB["Double sequence length"]
        DB --> SL
    end
    
    subgraph "Scale Training Strategy"
        FS["niter_fix_global parameter"]
        FS --> |"After niter_fix_global epochs"| AS["Train all scales together"]
    end
    
    subgraph "Learning Rate Schedule"
        NI["niter parameter"]
        ND["niter_decay parameter"]
        
        NI --> |"After niter epochs"| LRD["Linear learning rate decay"]
        ND --> |"For niter_decay epochs"| LRD
    end
```

Sources: [train.py:37-128](), [models/models.py:151-164](), [README.md:175-187]()

The training process incorporates several strategies:

1. **Gradual Sequence Length Increase**:
   - Starts with short sequences and gradually increases length
   - Controlled by `niter_step` parameter

2. **Coarse-to-Fine Training**:
   - Initially trains only the finest spatial scale
   - After `niter_fix_global` epochs, trains all scales together

3. **Learning Rate Schedule**:
   - Maintains constant learning rate for `niter` epochs
   - Linearly decays learning rate for `niter_decay` epochs

## Configuration System Architecture

The vid2vid configuration system has a hierarchical structure:

```mermaid
graph TD
    BO["BaseOptions"]
    TO["TrainOptions"] 
    TSO["TestOptions"]
    
    BO --> TO
    BO --> TSO
    
    subgraph "BaseOptions Parameters"
        BP1["Model Architecture"]
        BP2["Input/Output Specifications"]
        BP3["GPU Settings"]
        BP4["Dataset Configuration"]
    end
    
    subgraph "TrainOptions Parameters"
        TP1["Training Schedule"]
        TP2["Loss Weights"]
        TP3["Optimization Settings"]
        TP4["Multi-scale Parameters"]
    end
    
    subgraph "TestOptions Parameters"
        TSP1["Results Directory"]
        TSP2["Number of Test Examples"]
        TSP3["Batch Settings"]
    end
    
    BO --> BP1
    BO --> BP2
    BO --> BP3
    BO --> BP4
    
    TO --> TP1
    TO --> TP2
    TO --> TP3
    TO --> TP4
    
    TSO --> TSP1
    TSO --> TSP2
    TSO --> TSP3
```

Sources: [train.py:15](), [README.md:175-192]()

The configuration system provides:
- Separation between common, training-specific, and testing-specific parameters
- Command-line argument parsing
- Default values for all parameters
- Parameter validation and interdependency enforcement

## Summary

The vid2vid system architecture is designed for efficient and high-quality video-to-video translation through:

1. **Multi-Model Approach**: Specialized generator, discriminator, and flow estimation networks
2. **Temporal Consistency**: Flow-based warping and temporal discriminators
3. **Multi-Scale Processing**: Both spatial and temporal scales for comprehensive quality
4. **Efficient GPU Utilization**: Sophisticated strategies for multi-GPU processing
5. **Progressive Training**: Gradual complexity increase for stable and efficient training
6. **Flexible Configuration**: Comprehensive parameter system for experimentation

This architecture enables the system to generate high-resolution, temporally coherent videos across a variety of domains including city scenes, human faces, and human poses.

Sources: [README.md:8-13](), [train.py:14-147](), [models/models.py:61-164](), [models/base_model.py:6-196]()

---

