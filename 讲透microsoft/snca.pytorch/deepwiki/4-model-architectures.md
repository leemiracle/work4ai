<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/snca.pytorch · page 4 Model Architectures · fetched 2026-10-26 -->

# Model Architectures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [models/__init__.py](models/__init__.py)
- [models/resnet.py](models/resnet.py)
- [models/resnet_cifar.py](models/resnet_cifar.py)

</details>



This section documents the ResNet model architectures used for feature extraction in the SNCA framework. The repository provides two variants of ResNet implementations: standard ResNet models optimized for ImageNet-scale images and CIFAR-optimized ResNet models designed for smaller 32x32 images.

For information about how these models integrate with the memory bank system, see [LinearAverage](#3.1). For details about the normalization components used in these models, see [Normalization Utilities](#7.1).

## Architecture Overview

The SNCA implementation modifies standard ResNet architectures to output low-dimensional feature representations instead of classification logits. Both model variants share the same core design principles but differ in their layer configurations to accommodate different input image sizes.

### SNCA-Modified ResNet Architecture Flow

```mermaid
flowchart TD
    A["Input Image"] --> B["Initial Convolution"]
    B --> C["Batch Normalization"]
    C --> D["ReLU Activation"]
    D --> E["Max Pooling (ImageNet only)"]
    E --> F["Layer 1 (64 channels)"]
    F --> G["Layer 2 (128 channels)"]
    G --> H["Layer 3 (256 channels)"]
    H --> I["Layer 4 (512 channels)"]
    I --> J["Global Average Pooling"]
    J --> K["Linear Layer"]
    K --> L["L2 Normalization"]
    L --> M["128-dim Feature Vector"]
    
    style B fill:#e1f5fe
    style K fill:#ffecb3
    style L fill:#ffcdd2
    style M fill:#c8e6c9
```

Sources: [models/resnet.py:132-148](), [models/resnet_cifar.py:92-102]()

## Model Variants

The repository provides two distinct ResNet implementations optimized for different datasets:

| Model Type | File | Target Dataset | Input Size | Initial Conv | Max Pool | Global Pool |
|------------|------|----------------|------------|--------------|----------|-------------|
| Standard ResNet | `models/resnet.py` | ImageNet | 224x224 | 7x7, stride=2 | 3x3, stride=2 | 7x7 |
| CIFAR ResNet | `models/resnet_cifar.py` | CIFAR-10/100 | 32x32 | 3x3, stride=1 | None | 4x4 |

### Key Architectural Differences

```mermaid
graph LR
    subgraph "Standard ResNet (ImageNet)"
        A1["224x224 Input"] --> B1["7x7 Conv, stride=2"]
        B1 --> C1["BatchNorm + ReLU"]
        C1 --> D1["3x3 MaxPool, stride=2"]
        D1 --> E1["ResNet Layers"]
        E1 --> F1["7x7 AvgPool"]
        F1 --> G1["Linear + L2Norm"]
    end
    
    subgraph "CIFAR ResNet"
        A2["32x32 Input"] --> B2["3x3 Conv, stride=1"]
        B2 --> C2["BatchNorm + ReLU"]
        C2 --> E2["ResNet Layers"]
        E2 --> F2["4x4 AvgPool"]
        F2 --> G2["Linear + L2Norm"]
    end
    
    G1 --> H["128-dim Features"]
    G2 --> H
```

Sources: [models/resnet.py:94-105](), [models/resnet_cifar.py:75-82]()

## Standard ResNet Implementation

The standard ResNet implementation in [models/resnet.py]() provides the classic ResNet architectures adapted for SNCA feature learning.

### Block Types

The implementation includes two fundamental building blocks:

- **BasicBlock**: Used in ResNet-18 and ResNet-34, with expansion factor of 1
- **Bottleneck**: Used in ResNet-50, ResNet-101, and ResNet-152, with expansion factor of 4

### Available Model Configurations

| Model | Block Type | Layer Configuration | Parameters |
|-------|------------|-------------------|------------|
| `resnet18` | BasicBlock | [2, 2, 2, 2] | ~11M |
| `resnet34` | BasicBlock | [3, 4, 6, 3] | ~21M |
| `resnet50` | Bottleneck | [3, 4, 6, 3] | ~23M |
| `resnet101` | Bottleneck | [3, 4, 23, 3] | ~42M |
| `resnet152` | Bottleneck | [3, 8, 36, 3] | ~58M |

### ResNet Class Structure

```mermaid
classDiagram
    class ResNet {
        +int inplanes
        +Conv2d conv1
        +BatchNorm2d bn1
        +ReLU relu
        +MaxPool2d maxpool
        +Sequential layer1
        +Sequential layer2
        +Sequential layer3
        +Sequential layer4
        +AvgPool2d avgpool
        +Linear fc
        +Normalize l2norm
        +__init__(block, layers, low_dim)
        +_make_layer(block, planes, blocks, stride)
        +forward(x)
    }
    
    class BasicBlock {
        +int expansion = 1
        +Conv2d conv1
        +BatchNorm2d bn1
        +Conv2d conv2
        +BatchNorm2d bn2
        +Sequential downsample
        +forward(x)
    }
    
    class Bottleneck {
        +int expansion = 4
        +Conv2d conv1
        +BatchNorm2d bn1
        +Conv2d conv2
        +BatchNorm2d bn2
        +Conv2d conv3
        +BatchNorm2d bn3
        +Sequential downsample
        +forward(x)
    }
    
    ResNet --> BasicBlock
    ResNet --> Bottleneck
```

Sources: [models/resnet.py:89-148](), [models/resnet.py:18-47](), [models/resnet.py:50-86]()

## CIFAR-Optimized ResNet Implementation

The CIFAR ResNet implementation in [models/resnet_cifar.py]() is specifically optimized for 32x32 pixel images used in CIFAR-10 and CIFAR-100 datasets.

### CIFAR-Specific Optimizations

1. **No Initial Downsampling**: Uses 3x3 convolution with stride=1 instead of 7x7 with stride=2
2. **No Max Pooling**: Removes the initial max pooling layer that would be too aggressive for small images
3. **Smaller Global Pooling**: Uses 4x4 average pooling instead of 7x7
4. **Simplified Interface**: Uses direct function calls instead of factory pattern

### CIFAR ResNet Architecture Flow

```mermaid
flowchart TD
    A["32x32x3 Input"] --> B["conv1: 3x3, 64 filters, stride=1"]
    B --> C["bn1 + ReLU"]
    C --> D["layer1: 64 channels"]
    D --> E["layer2: 128 channels, stride=2"]
    E --> F["layer3: 256 channels, stride=2"]
    F --> G["layer4: 512 channels, stride=2"]
    G --> H["AvgPool2d(4x4)"]
    H --> I["View(-1)"]
    I --> J["linear: 512*expansion -> low_dim"]
    J --> K["l2norm"]
    K --> L["128-dim output"]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style J fill:#ffecb3
    style K fill:#ffcdd2
    style L fill:#c8e6c9
```

Sources: [models/resnet_cifar.py:92-102]()

### Available CIFAR Model Functions

The CIFAR implementation provides these factory functions:

- `ResNet18(low_dim=128)` → ResNet with BasicBlock [2,2,2,2]
- `ResNet34(low_dim=128)` → ResNet with BasicBlock [3,4,6,3]
- `ResNet50(low_dim=128)` → ResNet with Bottleneck [3,4,6,3]
- `ResNet101(low_dim=128)` → ResNet with Bottleneck [3,4,23,3]
- `ResNet152(low_dim=128)` → ResNet with Bottleneck [3,8,36,3]

Sources: [models/resnet_cifar.py:105-118]()

## SNCA-Specific Modifications

Both ResNet implementations include critical modifications for SNCA compatibility:

### Feature Dimensionality

All models output 128-dimensional feature vectors by default, controlled by the `low_dim` parameter. This low-dimensional representation is essential for the contrastive learning approach used in SNCA.

### L2 Normalization

Both implementations include L2 normalization as the final layer using the `Normalize(2)` module from [lib/normalize.py](). This ensures all feature vectors lie on the unit hypersphere, which is crucial for the neighborhood component analysis loss function.

### Weight Initialization

The standard ResNet implementation includes specific weight initialization:
- Convolutional layers: Normal distribution with std = sqrt(2/n)
- Batch normalization: weights=1, bias=0

Sources: [models/resnet.py:107-113](), [models/resnet.py:104-105](), [models/resnet_cifar.py:81-82]()

## Module Integration

The models integrate with other SNCA components through a well-defined interface:

```mermaid
graph LR
    A["Input Batch"] --> B["ResNet Model"]
    B --> C["128-dim Features"]
    C --> D["LinearAverage"]
    C --> E["NCACrossEntropy"]
    
    subgraph "Model Variants"
        F["models.resnet18()"]
        G["models.ResNet18()"]
    end
    
    F --> B
    G --> B
    
    D --> H["Memory Bank Update"]
    E --> I["Contrastive Loss"]
```

Both model variants are imported through [models/__init__.py]() and can be instantiated using their respective factory functions. The choice between standard and CIFAR variants depends on the target dataset as configured in the training scripts.

Sources: [models/__init__.py:1-2](), [models/resnet.py:151-208](), [models/resnet_cifar.py:105-118]()

---

