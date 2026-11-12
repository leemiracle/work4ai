<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/tinyml · page 3 NetAug: Network Augmentation for Tiny Networks · fetched 2026-10-30 -->

# NetAug: Network Augmentation for Tiny Networks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [netaug/README.md](netaug/README.md)

</details>



## Purpose and Scope

NetAug is a training technique designed specifically for tiny neural networks that addresses the fundamental challenge that training tiny networks is different from training large networks. The system provides network augmentation during the training process to give tiny networks more supervision, ultimately improving their performance on resource-constrained edge devices.

This page covers the NetAug methodology, training procedures, evaluation framework, and pretrained models. For on-device learning techniques that complement NetAug, see [TinyTL: On-Device Learning](#2). For broader project context and setup instructions, see [Getting Started Guide](#5).

**Sources:** [netaug/README.md:1-87]()

## Core Methodology

NetAug addresses the key insight that tiny neural networks require different training strategies than large networks. The approach augments tiny networks during training to provide additional supervision signals that help overcome the limitations of reduced model capacity.

### Training Challenges for Tiny Networks

```mermaid
graph TB
    subgraph "Large Networks"
        LN1["High Model Capacity"]
        LN2["Abundant Parameters"]
        LN3["Standard Training Works"]
    end
    
    subgraph "Tiny Networks"
        TN1["Limited Model Capacity"]
        TN2["Few Parameters"]
        TN3["Training Difficulties"]
    end
    
    subgraph "NetAug Solution"
        NA1["Network Augmentation"]
        NA2["More Supervision"]
        NA3["Channel Sorting"]
        NA4["Width Multiplier Management"]
    end
    
    TN3 --> NA1
    NA1 --> NA2
    NA2 --> NA3
    NA2 --> NA4
    
    NA3 --> RESULT["Improved Tiny Network Performance"]
    NA4 --> RESULT
```

### NetAug Training Pipeline

```mermaid
flowchart TD
    subgraph "Training Process"
        TP1["torchpack dist-run"]
        TP2["bash/imagenet scripts"]
        TP3["Network Augmentation"]
        TP4["Channel L1 Sorting"]
        TP5["Width Multiplier Control"]
    end
    
    subgraph "Post-Training"
        PT1["BN Statistics Re-estimation"]
        PT2["eval.py Evaluation"]
        PT3["Model Profiling"]
    end
    
    subgraph "Outputs"
        OUT1["Trained Models"]
        OUT2["Performance Metrics"]
        OUT3["Pretrained Weights"]
    end
    
    TP1 --> TP2
    TP2 --> TP3
    TP3 --> TP4
    TP4 --> TP5
    TP5 --> PT1
    PT1 --> PT2
    PT2 --> PT3
    PT3 --> OUT1
    OUT1 --> OUT2
    OUT1 --> OUT3
```

**Sources:** [netaug/README.md:19-27](), [netaug/README.md:66-74]()

## Technical Implementation Details

### Key Implementation Considerations

NetAug includes several critical technical modifications for training tiny networks effectively:

| Component | Implementation Detail | Rationale |
|-----------|----------------------|-----------|
| Initialization | `nn.init.kaiming_uniform` | `fout` initialization fails for high expand ratios |
| Channel Sorting | L1 value sorting per epoch | Forces target model to use most important channels |
| Width Multiplier | Ratio = 1.0 in second half | Improves results in later training phases |
| BN Statistics | Re-estimation with training subset | Running mean/var become inaccurate during augmentation |

### Training Script Organization

```mermaid
graph TB
    subgraph "Training Scripts"
        TS1["bash/imagenet/"]
        TS2["ImageNet Training Scripts"]
        TS3["Model-Specific Configurations"]
    end
    
    subgraph "Transfer Learning"
        TL1["bash/transfer/"]
        TL2["Transfer Learning Scripts"]
        TL3["Pretrained Model Loading"]
    end
    
    subgraph "Evaluation"
        EV1["eval.py"]
        EV2["torchpack dist-run"]
        EV3["Model Profiling"]
    end
    
    TS1 --> TS2
    TS2 --> TS3
    TL1 --> TL2
    TL2 --> TL3
    EV1 --> EV2
    EV2 --> EV3
    
    TS3 --> EV1
    TL3 --> EV1
```

**Sources:** [netaug/README.md:66-74](), [netaug/README.md:75-76]()

## Environment and Dependencies

### System Requirements

The NetAug system requires specific environment configurations:

- **Python**: 3.8.5
- **PyTorch**: 1.8.2
- **torchpack**: Distributed training framework
- **torchprofile**: Model profiling utilities

### Dependency Integration

```mermaid
graph TB
    subgraph "Core Dependencies"
        CD1["Python 3.8.5"]
        CD2["PyTorch 1.8.2"]
    end
    
    subgraph "Training Framework"
        TF1["torchpack"]
        TF2["Distributed Training"]
        TF3["Multi-GPU Support"]
    end
    
    subgraph "Profiling Tools"
        PT1["torchprofile"]
        PT2["Model Analysis"]
        PT3["Performance Metrics"]
    end
    
    CD1 --> CD2
    CD2 --> TF1
    TF1 --> TF2
    TF2 --> TF3
    CD2 --> PT1
    PT1 --> PT2
    PT2 --> PT3
```

**Sources:** [netaug/README.md:40-44]()

## Pretrained Models

### Available Model Configurations

NetAug provides pretrained models for various tiny network architectures:

| Model Architecture | Parameters | MACs | ImageNet Top1 | Pretrained Weights |
|-------------------|------------|------|---------------|-------------------|
| MobileNetV2-Tiny + NetAug | 0.75M | 23.5M | 53.3% | Google Drive |
| MCUNet + NetAug | 0.74M | 81.8M | 62.7% | Google Drive |
| ProxylessNAS-Mobile + NetAug | 1.8M | 35.7M | 60.8% | Google Drive |

### Model Evaluation Framework

```mermaid
graph LR
    subgraph "Evaluation Process"
        EP1["eval.py"]
        EP2["torchpack dist-run"]
        EP3["Model Loading"]
        EP4["Dataset Processing"]
        EP5["Performance Metrics"]
    end
    
    subgraph "Configuration"
        CF1["--dataset imagenet"]
        CF2["--data_path /dataset/imagenet/"]
        CF3["--image_size 160"]
        CF4["--model proxylessnas-0.35"]
        CF5["--init_from <pretrained_weight>"]
    end
    
    EP1 --> EP2
    EP2 --> EP3
    EP3 --> EP4
    EP4 --> EP5
    
    CF1 --> EP4
    CF2 --> EP4
    CF3 --> EP4
    CF4 --> EP3
    CF5 --> EP3
```

**Sources:** [netaug/README.md:46-64]()

## Training Procedures

### ImageNet Training

Training scripts for NetAug models are organized under `bash/imagenet/` and utilize the `torchpack` distributed training framework. The training process incorporates the key NetAug techniques:

1. **Channel Sorting**: Channels are sorted by L1 value at the beginning of each epoch
2. **Width Multiplier Management**: Augmentation ratio is set to 1.0 in the second half of training
3. **Initialization Strategy**: Uses `nn.init.kaiming_uniform` instead of `fout` initialization
4. **BN Statistics Correction**: Post-training re-estimation using training subset

### Training Workflow

```mermaid
sequenceDiagram
    participant U as "User"
    participant TS as "Training Script"
    participant NA as "NetAug Process"
    participant BN as "BN Re-estimation"
    participant E as "Evaluation"
    
    U->>TS: Execute bash/imagenet script
    TS->>NA: Initialize with kaiming_uniform
    
    loop Each Epoch
        NA->>NA: Sort channels by L1 value
        NA->>NA: Apply width multiplier
        Note over NA: Second half: ratio = 1.0
    end
    
    NA->>BN: Re-estimate running mean/var
    BN->>E: Updated model statistics
    E->>U: Trained model ready
```

**Sources:** [netaug/README.md:66-74]()

## Transfer Learning Capabilities

### Transfer Learning Pipeline

NetAug-trained models can be fine-tuned for downstream tasks using transfer learning. The system provides scripts under `bash/transfer/` for this purpose.

```mermaid
graph TB
    subgraph "Pretrained Models"
        PM1["NetAug ImageNet Models"]
        PM2["MobileNetV2-Tiny + NetAug"]
        PM3["MCUNet + NetAug"]
        PM4["ProxylessNAS + NetAug"]
    end
    
    subgraph "Transfer Learning"
        TL1["bash/transfer/ scripts"]
        TL2["Fine-tuning Process"]
        TL3["Target Dataset Adaptation"]
    end
    
    subgraph "Deployment"
        DP1["Edge Device Models"]
        DP2["Task-Specific Performance"]
        DP3["Memory-Efficient Inference"]
    end
    
    PM1 --> PM2
    PM1 --> PM3
    PM1 --> PM4
    
    PM2 --> TL1
    PM3 --> TL1
    PM4 --> TL1
    
    TL1 --> TL2
    TL2 --> TL3
    TL3 --> DP1
    DP1 --> DP2
    DP1 --> DP3
```

**Sources:** [netaug/README.md:75-76]()

## Integration with TinyML Ecosystem

### Related Projects

NetAug is part of the broader TinyML ecosystem and works in conjunction with:

- **TinyTL**: Focuses on reducing activations for on-device learning
- **MCUNet**: Provides system-algorithm co-design for IoT deployment
- **Once for All**: Train-once-deploy-everywhere approach
- **ProxylessNAS**: Direct neural architecture search framework

### Research Foundation

```mermaid
graph TB
    subgraph "Foundational Work"
        FW1["ProxylessNAS (ICLR'19)"]
        FW2["Once for All (ICLR'20)"]
        FW3["MCUNet (NeurIPS'20)"]
    end
    
    subgraph "NetAug Contribution"
        NC1["Network Augmentation (ICLR'22)"]
        NC2["Tiny Network Training"]
        NC3["Edge Device Optimization"]
    end
    
    subgraph "TinyML Integration"
        TI1["TinyTL On-Device Learning"]
        TI2["MCUNet System Design"]
        TI3["Unified Edge AI Framework"]
    end
    
    FW1 --> NC1
    FW2 --> NC1
    FW3 --> NC1
    
    NC1 --> NC2
    NC2 --> NC3
    NC3 --> TI1
    NC3 --> TI2
    NC3 --> TI3
```

**Sources:** [netaug/README.md:78-86]()

---

