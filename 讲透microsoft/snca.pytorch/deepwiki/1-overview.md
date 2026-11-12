<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/snca.pytorch · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of the SNCA PyTorch repository, which implements **Scalable Neighborhood Component Analysis** for learning feature representations optimized for nearest neighbor classifiers. The repository contains a complete training and evaluation framework for contrastive learning using memory banks and specialized loss functions.

For detailed training procedures, see [Getting Started](#2). For in-depth algorithmic details, see [Core SNCA Components](#3). For model architecture specifics, see [Model Architectures](#4).

## What is Scalable Neighborhood Component Analysis

SNCA is a contrastive learning method that trains deep neural networks to produce feature representations optimized for nearest neighbor classification. Unlike traditional supervised learning that optimizes for softmax classification, SNCA learns embeddings where semantically similar samples are close in the feature space, enabling better generalization to new object categories.

The approach extends [Neighborhood Component Analysis (NCA)](http://www.cs.toronto.edu/~fritz/absps/nca.pdf) to work with deep networks and large-scale datasets by using a non-parametric memory bank system that stores feature representations of all training samples.

Sources: [README.md:3-6]()

## Repository Architecture

The following diagram shows the main code components and their relationships:

**SNCA System Components**

```mermaid
graph TB
    subgraph "Training Scripts"
        main["main.py<br/>ImageNet Training"]
        cifar["cifar.py<br/>CIFAR Training"]
    end
    
    subgraph "Core Algorithm Components"
        LinearAverage["LinearAverage<br/>Memory Bank System"]
        NCACrossEntropy["NCACrossEntropy<br/>Contrastive Loss Function"]
    end
    
    subgraph "Feature Extraction"
        resnet_std["models/resnet.py<br/>Standard ResNet Models"]
        resnet_cifar["models/resnet_cifar.py<br/>CIFAR ResNet Models"]
        normalize["lib/normalize.py<br/>L2 Normalization"]
    end
    
    subgraph "Data Loading"
        ImageFolderInstance["ImageFolderInstance<br/>Custom ImageNet Dataset"]
        CIFAR10Instance["CIFAR10Instance<br/>Index-tracked CIFAR10"]
        CIFAR100Instance["CIFAR100Instance<br/>Index-tracked CIFAR100"]
    end
    
    subgraph "Evaluation"
        test["test.py<br/>NN/kNN Evaluation"]
    end
    
    main --> LinearAverage
    main --> NCACrossEntropy
    main --> resnet_std
    main --> ImageFolderInstance
    
    cifar --> LinearAverage
    cifar --> NCACrossEntropy
    cifar --> resnet_cifar
    cifar --> CIFAR10Instance
    cifar --> CIFAR100Instance
    
    resnet_std --> normalize
    resnet_cifar --> normalize
    
    main --> test
    cifar --> test
    test --> LinearAverage
```

Sources: [README.md:35-64]()

## Training Pipeline Data Flow

The following diagram illustrates how data flows through the SNCA training process:

**SNCA Training Data Flow**

```mermaid
flowchart TD
    input["Input Batch<br/>(images, labels, indices)"]
    
    subgraph "Feature Extraction"
        resnet["ResNet Feature Extractor"]
        features["128-dim Features<br/>(low_dim parameter)"]
    end
    
    subgraph "Memory Bank Operations"
        LinearAverage_lookup["LinearAverage.forward()<br/>Lookup stored features"]
        LinearAverage_update["LinearAverage.update_weight()<br/>Update memory bank"]
    end
    
    subgraph "Loss Computation"
        NCACrossEntropy_loss["NCACrossEntropy.forward()<br/>Compute contrastive loss"]
        temperature["Temperature Scaling<br/>(default: 0.05)"]
    end
    
    subgraph "Evaluation"
        knn_eval["NN/kNN Classification<br/>test.py functions"]
        accuracy["Top-1/Top-5 Accuracy"]
    end
    
    input --> resnet
    resnet --> features
    features --> LinearAverage_lookup
    features --> LinearAverage_update
    LinearAverage_lookup --> NCACrossEntropy_loss
    temperature --> NCACrossEntropy_loss
    NCACrossEntropy_loss --> backprop["SGD Backpropagation"]
    backprop --> resnet
    
    features --> knn_eval
    LinearAverage_lookup --> knn_eval
    knn_eval --> accuracy
```

Sources: [README.md:44-50]()

## Key Features and Capabilities

### Pretrained Models
The repository provides three pretrained ResNet models with their corresponding feature databases:

| Model | Top-1 Accuracy | Components |
|-------|----------------|------------|
| ResNet-18 | 70.59% | Model weights + 600MB feature database |
| ResNet-34 | 74.41% | Model weights + 600MB feature database |
| ResNet-50 | 76.57% | Model weights + 600MB feature database |

### Dataset Support
- **ImageNet**: Full-scale training using `main.py` with `ImageFolderInstance`
- **CIFAR-10/100**: Specialized training using `cifar.py` with `CIFAR10Instance`/`CIFAR100Instance`

### Evaluation Methods
- **Training monitoring**: k=1 nearest neighbor for fast validation
- **Final evaluation**: k=30 nearest neighbor for comprehensive testing
- **Feature visualization**: Nearest neighbor retrieval comparisons

Sources: [README.md:15-31](), [README.md:46-50]()

## Memory and Performance Characteristics

### GPU Memory Imbalance
The `LinearAverage` module creates a significant memory bottleneck:

```mermaid
graph LR
    subgraph "Multi-GPU Setup"
        GPU0["GPU 0<br/>11GB Memory<br/>LinearAverage + ResNet"]
        GPU1["GPU 1-N<br/>2.5GB Memory<br/>ResNet only"]
    end
    
    subgraph "Mitigation Strategies"
        batch_size["-b 128<br/>Reduced Batch Size"]
        iter_size["--iter-size 2<br/>Gradient Accumulation"]
    end
    
    GPU0 --> batch_size
    batch_size --> iter_size
    GPU1 -.-> GPU0
```

### Memory Requirements
- **ResNet-18**: GPU 0 requires 11GB, others require 2.5GB each
- **Deeper networks**: Require Caffe-style batch size reduction and gradient accumulation
- **Training hardware**: Models trained on V100 machines for optimal performance

Sources: [README.md:52-59]()

## Integration with Related Work

This implementation extends the [lemniscate.pytorch](https://github.com/zhirongw/lemniscate.pytorch) unsupervised learning project, adapting its memory bank approach for supervised contrastive learning. The core algorithmic components (`LinearAverage`, `NCACrossEntropy`) build upon the foundational work while adding supervised signals for improved feature learning.

Sources: [README.md:8-9]()

---

