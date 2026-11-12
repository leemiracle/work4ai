<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/makani · page 4 Neural Network Models · fetched 2026-10-26 -->

# Neural Network Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [makani/__init__.py](makani/__init__.py)
- [makani/models/common/layers.py](makani/models/common/layers.py)
- [makani/models/networks/afnonet_v2.py](makani/models/networks/afnonet_v2.py)
- [makani/models/networks/sfnonet.py](makani/models/networks/sfnonet.py)

</details>



This page provides an overview of the neural network model architectures supported by Makani, including Spherical Fourier Neural Operators (SFNO), Adaptive Fourier Neural Operators (AFNO), and their shared building blocks. For detailed implementation specifics of individual model types, see [SFNO Models](#4.1) and [AFNO Models](#4.2). For information about how models are dynamically loaded and registered, see [Model Registry System](#3.2). For shared neural network components, see [Common Neural Network Layers](#4.3).

## Model Architecture Overview

Makani supports multiple neural operator architectures designed for weather and climate modeling on spherical grids. These models share common design patterns while specializing in different spectral transform approaches.

```mermaid
graph TB
    subgraph "Model Registry"
        ENTRY_POINTS["Entry Points<br/>makani.models.*"]
    end
    
    subgraph "Core Model Architectures"
        SFNO["SphericalFourierNeuralOperatorNet<br/>sfnonet.py"]
        FNO["FourierNeuralOperatorNet<br/>sfnonet.py"]
        AFNO["AdaptiveFourierNeuralOperatorNet<br/>afnonet_v2.py"]
    end
    
    subgraph "Spectral Transforms"
        SHT["Spherical Harmonic Transform<br/>torch_harmonics"]
        FFT["Fast Fourier Transform<br/>RealFFT2"]
        AFNO_BLOCKS["AFNO2D Blocks<br/>Adaptive Filtering"]
    end
    
    subgraph "Common Building Blocks"
        PATCH_EMBED["PatchEmbed<br/>layers.py"]
        MLP_BLOCKS["MLP<br/>layers.py"]
        ENCODER_DECODER["EncoderDecoder<br/>layers.py"]
        DROP_PATH["DropPath<br/>layers.py"]
        SPECTRAL_LAYERS["SpectralFilterLayer<br/>sfnonet.py"]
    end
    
    subgraph "Block Structures"
        FNO_BLOCK["FourierNeuralOperatorBlock<br/>sfnonet.py"]
        AFNO_BLOCK["Block<br/>afnonet_v2.py"]
    end
    
    ENTRY_POINTS --> SFNO
    ENTRY_POINTS --> FNO
    ENTRY_POINTS --> AFNO
    
    SFNO --> SHT
    FNO --> FFT
    AFNO --> AFNO_BLOCKS
    
    SFNO --> FNO_BLOCK
    FNO --> FNO_BLOCK
    AFNO --> AFNO_BLOCK
    
    FNO_BLOCK --> SPECTRAL_LAYERS
    FNO_BLOCK --> MLP_BLOCKS
    FNO_BLOCK --> ENCODER_DECODER
    FNO_BLOCK --> DROP_PATH
    
    AFNO_BLOCK --> AFNO_BLOCKS
    AFNO_BLOCK --> MLP_BLOCKS
    AFNO_BLOCK --> DROP_PATH
    
    AFNO --> PATCH_EMBED
    
    SPECTRAL_LAYERS --> SHT
    SPECTRAL_LAYERS --> FFT
```

Sources: [makani/models/networks/sfnonet.py:270-673](), [makani/models/networks/afnonet_v2.py:190-315](), [makani/models/common/layers.py:1-288]()

## Spherical Fourier Neural Operators (SFNO)

The `SphericalFourierNeuralOperatorNet` class implements neural operators that work in the spherical harmonic domain, making them well-suited for global climate modeling on spherical grids.

### Core Architecture

```mermaid
graph LR
    subgraph "SFNO Model Structure"
        ENCODER["EncoderDecoder<br/>Encoder"]
        FNO_BLOCKS["FourierNeuralOperatorBlock[]<br/>num_layers blocks"]
        DECODER["EncoderDecoder<br/>Decoder"]
        BIG_SKIP["Residual Transform<br/>big_skip connection"]
    end
    
    subgraph "Spectral Processing"
        TRANS_DOWN["trans_down<br/>SHT/FFT downscale"]
        TRANS["trans<br/>SHT/FFT intermediate"]
        ITRANS["itrans<br/>Inverse transform"]
        ITRANS_UP["itrans_up<br/>Inverse upscale"]
    end
    
    subgraph "Block Components"
        SPECTRAL_FILTER["SpectralFilterLayer<br/>Spectral convolution"]
        NORM_LAYERS["Normalization<br/>Instance/Layer norm"]
        MLP_LAYER["MLP<br/>Optional"]
    end
    
    INPUT["Input<br/>(B, inp_chans, H, W)"] --> ENCODER
    INPUT -.-> BIG_SKIP
    
    ENCODER --> FNO_BLOCKS
    FNO_BLOCKS --> DECODER
    DECODER --> OUTPUT["Output<br/>(B, out_chans, H, W)"]
    BIG_SKIP -.-> OUTPUT
    
    FNO_BLOCKS --> TRANS_DOWN
    FNO_BLOCKS --> TRANS
    FNO_BLOCKS --> ITRANS
    FNO_BLOCKS --> ITRANS_UP
    
    FNO_BLOCKS --> SPECTRAL_FILTER
    FNO_BLOCKS --> NORM_LAYERS
    FNO_BLOCKS --> MLP_LAYER
```

Sources: [makani/models/networks/sfnonet.py:270-311](), [makani/models/networks/sfnonet.py:386-430](), [makani/models/networks/sfnonet.py:587-641]()

### Key Components

| Component | Class | Purpose |
|-----------|-------|---------|
| Main Model | `SphericalFourierNeuralOperatorNet` | Complete SFNO architecture with spherical harmonic transforms |
| FFT Variant | `FourierNeuralOperatorNet` | SFNO using FFT instead of SHT |
| Core Block | `FourierNeuralOperatorBlock` | Individual layer with spectral filtering and MLP |
| Spectral Layer | `SpectralFilterLayer` | Wrapper for different spectral convolution types |

Sources: [makani/models/networks/sfnonet.py:270-273](), [makani/models/networks/sfnonet.py:657-659](), [makani/models/networks/sfnonet.py:119-146](), [makani/models/networks/sfnonet.py:51-69]()

## Adaptive Fourier Neural Operators (AFNO)

The `AdaptiveFourierNeuralOperatorNet` class implements neural operators using adaptive Fourier filtering with patch-based processing, following vision transformer patterns.

### Architecture Flow

```mermaid
graph TB
    subgraph "AFNO Processing Pipeline"
        PATCH["PatchEmbed<br/>Conv2d projection"]
        POS_EMBED["Positional Embedding<br/>pos_embed parameter"]
        BLOCKS["Block[]<br/>num_layers blocks"]
        HEAD["Head<br/>Conv2d output projection"]
        UNPATCH["Unpatch<br/>Reshape to spatial"]
    end
    
    subgraph "AFNO Block Details"
        NORM1["LayerNorm/InstanceNorm<br/>norm1"]
        AFNO2D["AFNO2D<br/>Adaptive spectral filtering"]
        SKIP1["Skip Connection<br/>skip_layer"]
        NORM2["LayerNorm/InstanceNorm<br/>norm2"]
        MLP_AFNO["MLP<br/>Feature processing"]
        DROP_PATH_AFNO["DropPath<br/>Stochastic depth"]
    end
    
    subgraph "AFNO2D Core"
        RFFT2["torch.fft.rfft2<br/>Real FFT"]
        SPECTRAL_CONV["Complex Multiplication<br/>compl_mul_add_fwd"]
        ACTIVATION["ComplexReLU<br/>Complex activation"]
        IRFFT2["torch.fft.irfft2<br/>Inverse FFT"]
        SOFT_THRESH["F.softshrink<br/>Sparsity threshold"]
    end
    
    INPUT_AFNO["Input<br/>(B, inp_chans, H, W)"] --> PATCH
    PATCH --> POS_EMBED
    POS_EMBED --> BLOCKS
    BLOCKS --> HEAD
    HEAD --> UNPATCH
    UNPATCH --> OUTPUT_AFNO["Output<br/>(B, out_chans, H, W)"]
    
    BLOCKS --> NORM1
    NORM1 --> AFNO2D
    AFNO2D --> SKIP1
    SKIP1 --> NORM2
    NORM2 --> MLP_AFNO
    MLP_AFNO --> DROP_PATH_AFNO
    
    AFNO2D --> RFFT2
    RFFT2 --> SPECTRAL_CONV
    SPECTRAL_CONV --> ACTIVATION
    ACTIVATION --> SPECTRAL_CONV
    SPECTRAL_CONV --> SOFT_THRESH
    SOFT_THRESH --> IRFFT2
```

Sources: [makani/models/networks/afnonet_v2.py:190-315](), [makani/models/networks/afnonet_v2.py:115-188](), [makani/models/networks/afnonet_v2.py:50-113]()

### AFNO Key Features

| Feature | Implementation | Location |
|---------|---------------|----------|
| Patch Processing | `PatchEmbed` with configurable patch sizes | [afnonet_v2.py:226]() |
| Adaptive Filtering | `AFNO2D` with learnable spectral weights | [afnonet_v2.py:50-113]() |
| Block Structure | `Block` with skip connections and normalization | [afnonet_v2.py:115-188]() |
| Complex Kernels | `compl_mul_add_fwd_c` for efficient complex ops | [afnonet_v2.py:41-48]() |

Sources: [makani/models/common/layers.py:65-84](), [makani/models/networks/afnonet_v2.py:50-52](), [makani/models/networks/afnonet_v2.py:115-117](), [makani/models/networks/afnonet_v2.py:42]()

## Common Building Blocks

All models share fundamental neural network components that provide consistent functionality across architectures.

### Shared Components

```mermaid
graph LR
    subgraph "Input Processing"
        PATCH_EMBED_COMP["PatchEmbed<br/>Conv2d projection"]
        ENCODER_COMP["EncoderDecoder<br/>Multi-layer projection"]
    end
    
    subgraph "Core Layers"
        MLP_COMP["MLP<br/>Feed-forward network"]
        DROP_PATH_COMP["DropPath<br/>Stochastic depth"]
        COMPLEX_RELU["ComplexReLU<br/>Complex activation"]
    end
    
    subgraph "Spectral Operations"
        REAL_FFT2["RealFFT2<br/>Forward FFT"]
        INVERSE_FFT2["InverseRealFFT2<br/>Inverse FFT"]
        SPECTRAL_CONV_COMP["SpectralConv<br/>Spectral convolution"]
    end
    
    subgraph "Utilities"
        DROP_PATH_FUNC["drop_path<br/>@torch.jit.script"]
        COMPLEX_MUL["compl_mul_add_fwd<br/>Complex multiplication"]
        CONTRACTIONS["_contract_diagonal<br/>Tensor contractions"]
    end
    
    PATCH_EMBED_COMP --> MLP_COMP
    ENCODER_COMP --> MLP_COMP
    MLP_COMP --> DROP_PATH_COMP
    
    REAL_FFT2 --> SPECTRAL_CONV_COMP
    INVERSE_FFT2 --> SPECTRAL_CONV_COMP
    
    DROP_PATH_COMP --> DROP_PATH_FUNC
    SPECTRAL_CONV_COMP --> COMPLEX_MUL
    COMPLEX_MUL --> CONTRACTIONS
```

Sources: [makani/models/common/layers.py:65-84](), [makani/models/common/layers.py:86-134](), [makani/models/common/layers.py:136-217](), [makani/models/common/layers.py:54-63](), [makani/models/common/layers.py:219-288]()

### Layer Specifications

| Layer Class | Key Parameters | Usage Pattern |
|-------------|---------------|---------------|
| `MLP` | `hidden_features`, `act_layer`, `input_format` | Feature transformation in both SFNO and AFNO |
| `PatchEmbed` | `patch_size`, `embed_dim`, `in_chans` | Input processing in AFNO models |
| `EncoderDecoder` | `num_layers`, `hidden_dim`, `act_layer` | Input/output processing in SFNO |
| `DropPath` | `drop_prob` | Regularization across all models |

Sources: [makani/models/common/layers.py:136-150](), [makani/models/common/layers.py:65-67](), [makani/models/common/layers.py:86-88](), [makani/models/common/layers.py:54-57]()

## Model Integration Patterns

The models integrate with the broader Makani system through standardized interfaces and distributed computing patterns.

### Model Instantiation Flow

```mermaid
graph TB
    subgraph "Configuration"
        YAML_CONFIG["YAML Config Files<br/>sfnonet.yaml, afnonet.yaml"]
        MODEL_PARAMS["Model Parameters<br/>embed_dim, num_layers, etc."]
    end
    
    subgraph "Factory Creation"
        MODEL_REGISTRY["Model Registry<br/>Dynamic loading"]
        ENTRY_POINT["Entry Points<br/>makani.models.*"]
        MODEL_FACTORY["Model Factory<br/>get_model()"]
    end
    
    subgraph "Model Classes"
        SFNO_INST["SphericalFourierNeuralOperatorNet<br/>Instance"]
        AFNO_INST["AdaptiveFourierNeuralOperatorNet<br/>Instance"]
        MODULUS_WRAPPER["Modulus Module Wrapper<br/>SFNO, FNO objects"]
    end
    
    subgraph "Distributed Setup"
        COMM_INIT["comm.init<br/>Process groups"]
        SPATIAL_PARALLEL["Spatial Parallelism<br/>H/W distribution"]
        MODEL_PARALLEL["Model Parallelism<br/>Feature distribution"]
    end
    
    YAML_CONFIG --> MODEL_PARAMS
    MODEL_PARAMS --> MODEL_REGISTRY
    MODEL_REGISTRY --> ENTRY_POINT
    ENTRY_POINT --> MODEL_FACTORY
    
    MODEL_FACTORY --> SFNO_INST
    MODEL_FACTORY --> AFNO_INST
    SFNO_INST --> MODULUS_WRAPPER
    AFNO_INST --> MODULUS_WRAPPER
    
    COMM_INIT --> SPATIAL_PARALLEL
    COMM_INIT --> MODEL_PARALLEL
    SPATIAL_PARALLEL --> SFNO_INST
    MODEL_PARALLEL --> SFNO_INST
```

Sources: [makani/models/networks/sfnonet.py:642-673](), [makani/models/networks/sfnonet.py:148-156](), [makani/models/networks/sfnonet.py:528-571]()

### Distributed Computing Integration

Both model architectures support multi-dimensional parallelism through the `comm` module and specialized distributed layers:

- **Spatial Parallelism**: Domain decomposition across H/W dimensions
- **Model Parallelism**: Feature/channel parallelism using `DistributedMLP` and `DistributedEncoderDecoder`
- **Spectral Parallelism**: Distributed spectral transforms via `torch_harmonics.distributed`

Sources: [makani/models/networks/sfnonet.py:37-44](), [makani/models/networks/sfnonet.py:342-365](), [makani/models/networks/sfnonet.py:218-231]()

---

