<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mu-Protein · page 5 API Reference · fetched 2026-10-26 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mu-former/src/criterion.py](mu-former/src/criterion.py)
- [mu-former/src/data.py](mu-former/src/data.py)
- [mu-former/src/model.py](mu-former/src/model.py)

</details>



This document provides comprehensive API documentation for the μProtein framework's key classes, functions, and modules. It covers the core interfaces for model architectures, data processing pipelines, and training utilities used across the three-stage μProtein system.

For detailed training procedures and workflows, see [Training & Development](#4). For configuration and setup of individual components, see [Configuration & Setup](#6).

## Overview

The μProtein API is organized into three primary modules that correspond to the framework's architectural components:

```mermaid
graph TB
    subgraph "API Structure"
        subgraph "Core Models (5.1)"
            MUFORMER["Muformer"]
            SIAMESE["SiameseMuformerDecoder"] 
            MONO["MonoMuformerDecoder"]
            BLOCKS["ResnetBlock1d, MaskedConv1d"]
        end
        
        subgraph "Data Processing (5.2)"
            PAIRED["PairedDataset"]
            META["MetagenesisData"]
            ENCODER_LM["FairseqLMEncoder"]
            UTILS["index_encoding, _pad_sequences"]
        end
        
        subgraph "Training Utilities (5.3)"
            CRITERION["CRITERION dict"]
            PEARSON["pearson_loss, pearson_correlation_loss"]
            SPEARMAN["SpearmanLoss"]
            LOSSES["get_criterion"]
        end
    end
    
    MUFORMER --> SIAMESE
    MUFORMER --> MONO
    PAIRED --> META
    PAIRED --> ENCODER_LM
    CRITERION --> PEARSON
    CRITERION --> SPEARMAN
```

Sources: [mu-former/src/model.py:225-315](), [mu-former/src/data.py:139-453](), [mu-former/src/criterion.py:103-115]()

## Module Architecture

The API follows a hierarchical structure where higher-level classes compose lower-level utilities:

```mermaid
graph TB
    subgraph "Model Hierarchy"
        MUFORMER_CLASS["`**Muformer**
        Main model class`"]
        DECODER_TYPES["`**Decoder Types**
        SiameseMuformerDecoder
        MonoMuformerDecoder`"]
        CONV_LAYERS["`**Convolutional Layers**
        ResnetBlock1d
        MaskedConv1d`"]
        POOLING["`**Pooling**
        LengthMaxPool1D`"]
    end
    
    subgraph "Data Pipeline"
        DATASET_MAIN["`**PairedDataset**
        Main dataset orchestrator`"]
        DATASET_IMPL["`**MetagenesisData**
        Dataset implementation`"]
        LM_ENCODER["`**FairseqLMEncoder**
        Sequence tokenization`"]
        ENCODING_UTILS["`**Encoding Utilities**
        index_encoding
        _pad_sequences`"]
    end
    
    subgraph "Loss Functions"
        CRITERION_REGISTRY["`**CRITERION Registry**
        mae, mse, pearson, spearman`"]
        LOSS_IMPL["`**Loss Implementations**
        pearson_loss
        pearson_correlation_loss
        SpearmanLoss`"]
    end
    
    MUFORMER_CLASS --> DECODER_TYPES
    DECODER_TYPES --> CONV_LAYERS
    DECODER_TYPES --> POOLING
    
    DATASET_MAIN --> DATASET_IMPL
    DATASET_MAIN --> LM_ENCODER
    LM_ENCODER --> ENCODING_UTILS
    
    CRITERION_REGISTRY --> LOSS_IMPL
```

Sources: [mu-former/src/model.py:1-315](), [mu-former/src/data.py:1-453](), [mu-former/src/criterion.py:1-115]()

## Key Interface Patterns

### Model Construction Pattern

The framework uses a consistent pattern for model initialization:

| Component | Class | Key Parameters | Purpose |
|-----------|-------|----------------|---------|
| Main Model | `Muformer` | `encoder`, `decoder_name`, `freeze_lm` | Orchestrates encoder-decoder architecture |
| Decoders | `SiameseMuformerDecoder`, `MonoMuformerDecoder` | `encoder_dim`, `hidden_size`, `activate` | Processes encoded sequences |
| Convolution | `ResnetBlock1d`, `MaskedConv1d` | `kernel_size`, `hidden_size` | Feature extraction from sequences |

Sources: [mu-former/src/model.py:225-271](), [mu-former/src/model.py:93-159](), [mu-former/src/model.py:50-82]()

### Data Processing Pattern

The data pipeline follows a builder pattern with progressive refinement:

| Stage | Class/Function | Input | Output | Purpose |
|-------|----------------|-------|--------|---------|
| Dataset Setup | `PairedDataset.__init__` | TSV files, FASTA | Dataset object | Configure data sources |
| Sequence Encoding | `FairseqLMEncoder.encode` | Raw sequences | Tokenized tensors | Convert text to model input |
| Data Loading | `PairedDataset.get_dataloader` | Mode, batch_size | DataLoader | Batch preparation |
| Mutation Processing | `MetagenesisData.__getitem__` | Index | Sample pairs | Generate training pairs |

Sources: [mu-former/src/data.py:139-211](), [mu-former/src/data.py:48-84](), [mu-former/src/data.py:406-452](), [mu-former/src/data.py:116-137]()

### Loss Function Registry

The criterion system uses a dictionary registry pattern:

```mermaid
graph LR
    GET_CRITERION["`**get_criterion(name)**
    mu-former/src/criterion.py:110-114`"]
    CRITERION_DICT["`**CRITERION dict**
    Lines 103-108`"]
    
    subgraph "Available Losses"
        MAE["`**'mae'**
        nn.L1Loss()`"]
        MSE["`**'mse'**
        nn.MSELoss()`"]
        PEARSON["`**'pearson'**
        pearson_correlation_loss`"]
        SPEARMAN["`**'spearman'**
        SpearmanLoss()`"]
    end
    
    GET_CRITERION --> CRITERION_DICT
    CRITERION_DICT --> MAE
    CRITERION_DICT --> MSE  
    CRITERION_DICT --> PEARSON
    CRITERION_DICT --> SPEARMAN
```

Sources: [mu-former/src/criterion.py:103-115]()

## Detailed API Documentation

For comprehensive documentation of specific API components:

- **[Core Models](#5.1)** - `Muformer`, decoder architectures, and neural network components
- **[Data Processing](#5.2)** - `PairedDataset`, `MetagenesisData`, and sequence encoding utilities  
- **[Training Utilities](#5.3)** - Loss functions, criterions, and training infrastructure

Each sub-section provides detailed parameter specifications, return types, and usage examples for the respective API components.

---

