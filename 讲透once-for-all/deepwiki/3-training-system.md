<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/once-for-all · page 3 Training System · fetched 2026-10-30 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [figures/ofa-tutorial.jpg](figures/ofa-tutorial.jpg)
- [train_ofa_net.py](train_ofa_net.py)
- [tutorial/README.md](tutorial/README.md)

</details>



The Training System is a core component of the Once for All (OFA) framework responsible for training elastic neural networks that can be specialized for efficient deployment across diverse hardware platforms. This document explains the architecture and implementation of the OFA training system, focusing on the progressive shrinking methodology and distributed training approach.

For information about using pre-trained OFA networks, see [Model Zoo](#2).

## Overview

The OFA Training System implements the "train once, specialize for deployment" paradigm by training a single supernet that encompasses a broad architecture space. The system enables training across multiple dimensions of network flexibility, including:

- Elastic kernel sizes
- Elastic network depths
- Elastic channel widths (expansion ratios)

```mermaid
flowchart TD
    A["Training System"] --> B["Progressive Shrinking"]
    A --> C["Knowledge Distillation"]
    A --> D["Distributed Training"]
    
    B --> B1["Elastic Kernel Training"]
    B --> B2["Elastic Depth Training"]
    B --> B3["Elastic Width Training"]
    
    C --> C1["Teacher Model"]
    C --> C2["Student Network"]
    
    D --> D1["Horovod Integration"]
    D --> D2["Multi-GPU Synchronization"]
```

Sources: [train_ofa_net.py](), [README.md:162-169]()

## Progressive Shrinking Training Methodology

Progressive shrinking is the core training methodology of OFA. Instead of training all possible subnet configurations simultaneously, OFA progressively trains the network in stages:

```mermaid
flowchart LR
    A["Full Network Training"] --> B["Elastic Kernel Size Training"]
    B --> C["Elastic Depth Training"]
    C --> D["Elastic Width/Expansion Training"]
    D --> E["Final OFA Network"]
    
    B -.-> F["Kernel Space: 3,5,7"]
    C -.-> G["Depth Space: 2,3,4"]
    D -.-> H["Expansion Space: 3,4,6"]
```

Sources: [train_ofa_net.py:254-313]()

The progressive shrinking process follows these steps:

1. **Initial Training**: Begin with the largest network in the search space
2. **Kernel Size Shrinking**: Train the network to support multiple kernel sizes (e.g., 3×3, 5×5, 7×7)
3. **Depth Shrinking**: Introduce depth flexibility to support different layer counts
4. **Width Shrinking**: Introduce width flexibility to support different channel counts

This approach ensures knowledge transfer from larger sub-networks to smaller ones, significantly improving the performance of resource-constrained models.

## Training Tasks

The training system supports three main tasks corresponding to the different elastic dimensions:

| Task | Configuration | Architecture Space | Training Phases |
|------|--------------|-------------------|----------------|
| Kernel | Dynamic batch size: 1<br>Epochs: 120<br>Base LR: 3e-2 | Kernel sizes: 3,5,7<br>Expand ratio: 6<br>Depth: 4 | Single phase |
| Depth | Dynamic batch size: 2<br>Epochs: 25-120<br>Base LR: 2.5e-3 to 7.5e-3 | Phase 1: Depths 3,4<br>Phase 2: Depths 2,3,4 | Two phases |
| Expand | Dynamic batch size: 4<br>Epochs: 25-120<br>Base LR: 2.5e-3 to 7.5e-3 | Phase 1: Expand 4,6<br>Phase 2: Expand 3,4,6 | Two phases |

Sources: [train_ofa_net.py:42-91]()

## Knowledge Distillation

The training system employs knowledge distillation to transfer knowledge from a large pre-trained teacher model to the elastic student network:

```mermaid
sequenceDiagram
    participant Teacher as "Teacher Model (MobileNetV3Large)"
    participant OFA as "OFA Network"
    participant Loss as "Distillation Loss"
    
    Note over Teacher,OFA: Initialization
    
    Teacher->>Teacher: Load pretrained weights
    OFA->>OFA: Sample active subnet
    
    Note over Teacher,Loss: Training Loop
    
    Teacher->>Teacher: Generate soft targets
    OFA->>OFA: Forward pass
    OFA->>Loss: Predictions
    Teacher->>Loss: Soft targets
    Loss->>OFA: Gradient with KD loss
    OFA->>OFA: Update parameters
```

Sources: [train_ofa_net.py:207-238]()

Key knowledge distillation components:
- Teacher model: MobileNetV3Large with fixed parameters (depth=4, kernel size=7, expand ratio=6)
- KD ratio: Controls the weight of the distillation loss
- KD type: Determines the type of distillation loss (e.g., cross-entropy)

## Distributed Training Architecture

OFA implements distributed training using Horovod, which enables efficient scaling across multiple GPUs and servers:

```mermaid
flowchart TD
    A["train_ofa_net.py"] --> B["Initialize Horovod"]
    B --> C["Set GPU Device"]
    C --> D["Create OFA Network"]
    D --> E["Setup DistributedRunManager"]
    E --> F["Broadcast Model"]
    F --> G["Progressive Training"]
    G --> H["Validate"]
    H --> G
    
    subgraph "Each GPU Worker"
    I["Local Gradient Computation"] --> J["Synchronize Gradients"]
    J --> K["Update Model"]
    end
    
    G --> I
```

Sources: [train_ofa_net.py:134-138](), [train_ofa_net.py:222-232]()

The distributed training system includes:
- Horovod initialization to coordinate multiple processes
- GPU device assignment for each process
- Gradient synchronization across workers
- Linear learning rate scaling based on the number of GPUs
- Optional gradient compression for efficient communication

## Training Configuration

The training system provides extensive configuration options:

| Category | Parameters | Description |
|----------|------------|-------------|
| Learning Rate | Base LR, warmup epochs, scheduler | Cosine LR schedule with optional warmup |
| Optimization | SGD with momentum (0.9), weight decay (3e-5) | Standard optimization settings |
| Architecture Space | Kernel sizes, expansion ratios, depths | Defines the search space of the OFA network |
| Data Augmentation | Image sizes (128-224), distortion, scaling | Multi-size training with augmentation |
| Batch Size | Base batch size (64), dynamic batch steps | Controls memory usage and training stability |
| Knowledge Distillation | KD ratio (1.0), KD type (ce) | Controls the influence of the teacher model |

Sources: [train_ofa_net.py:92-130]()

## Training Workflow

The OFA training workflow consists of the following steps:

```mermaid
sequenceDiagram
    participant User
    participant RunManager as "DistributedRunManager"
    participant OFANetwork
    participant Validator
    
    User->>RunManager: Initialize with configuration
    RunManager->>OFANetwork: Build OFA network
    
    alt Kernel Training
        User->>OFANetwork: Load pretrained backbone
        User->>RunManager: Train with elastic kernels
    else Depth Training
        User->>OFANetwork: Load kernel-elastic network
        User->>RunManager: Train with elastic depths (Phase 1)
        User->>RunManager: Train with elastic depths (Phase 2)
    else Expansion Training
        User->>OFANetwork: Load depth-elastic network
        User->>RunManager: Train with elastic expansion (Phase 1)
        User->>RunManager: Train with elastic expansion (Phase 2)
    end
    
    RunManager->>Validator: Validate network
    Validator->>User: Return validation metrics
```

Sources: [train_ofa_net.py:254-313]()

## Validation System

During training, the system periodically validates the OFA network across different architectural configurations:

```mermaid
flowchart LR
    A["Validation Process"] --> B["Image Size Sampling"]
    A --> C["Kernel Size Sampling"]
    A --> D["Expansion Ratio Sampling"]
    A --> E["Depth Sampling"]
    
    B --> B1["Multiple Resolutions (160px, 224px)"]
    C --> C1["Min and Max Kernel Sizes"]
    D --> D1["Min and Max Expansion Ratios"]
    E --> E1["Min and Max Network Depths"]
    
    B1 & C1 & D1 & E1 --> F["Subnet Validation"]
    F --> G["Accuracy Metrics"]
```

Sources: [train_ofa_net.py:246-253]()

The validation system tests the model on key combinations of:
- Different image sizes (typically 160px and 224px)
- Minimum and maximum kernel sizes from the elastic space
- Minimum and maximum expansion ratios from the elastic space
- Minimum and maximum depths from the elastic space

This comprehensive validation ensures the OFA network maintains accuracy across the entire architectural search space.

## Running Distributed Training

The OFA training system can be launched using either MPI or Horovod commands:

```bash
# Using MPI
mpirun -np 32 -H <server1_ip>:8,<server2_ip>:8,<server3_ip>:8,<server4_ip>:8 \
    -bind-to none -map-by slot \
    -x NCCL_DEBUG=INFO -x LD_LIBRARY_PATH -x PATH \
    python train_ofa_net.py

# Using Horovod
horovodrun -np 32 -H <server1_ip>:8,<server2_ip>:8,<server3_ip>:8,<server4_ip>:8 \
    python train_ofa_net.py
```

Sources: [README.md:164-174]()

Key command-line arguments include:
- `--task`: Specifies the training task (kernel, depth, expand)
- `--phase`: For depth and expand tasks, specifies training phase (1 or 2)
- `--resume`: Resumes training from a checkpoint

The training system automatically downloads appropriate pre-trained models for each training phase to ensure a smooth progressive training process.

Sources: [train_ofa_net.py:27-41]()

---

