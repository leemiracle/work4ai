<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TimeCraft · page 5 Model Components · fetched 2026-10-26 -->

# Model Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [TarDiff/configs/base/mimic_icustay_base.yaml](TarDiff/configs/base/mimic_icustay_base.yaml)
- [TarDiff/ldm/data/tsg_dataset.py](TarDiff/ldm/data/tsg_dataset.py)
- [diffusion/ldm/modules/encoders/__init__.py](diffusion/ldm/modules/encoders/__init__.py)

</details>



This document covers the core model components that form the foundation of the TimeCraft diffusion-based time series generation framework. These components include the diffusion model architecture, encoder modules, data processing systems, and their configuration mechanisms.

For information about training and inference workflows, see [Training and Inference](#6). For details about the overall framework architecture, see [Core Framework Architecture](#2).

## Core Diffusion Model Architecture

The TimeCraft framework is built around a latent diffusion model architecture that processes time series data through multiple stages. The core architecture consists of three main components: the diffusion model, the UNet backbone, and the conditioning system.

```mermaid
graph TB
    subgraph "LatentDiffusion Model"
        LDM["ldm.models.diffusion.ddpm.LatentDiffusion"]
        LDM --> UNET["ldm.modules.diffusionmodules.unet1d.UNetModel"]
        LDM --> FIRST["ldm.models.autoencoder.IdentityFirstStage"]
        LDM --> COND["ldm.modules.encoders.modules.DomainUnifiedEncoder"]
    end
    
    subgraph "Input Processing"
        DATA["TSClassCondDataset"] --> FIRST
        DATA --> COND
    end
    
    subgraph "UNet Configuration"
        UNET --> RESBLOCKS["num_res_blocks: 2"]
        UNET --> ATTENTION["attention_resolutions: [1,2,4]"]
        UNET --> CHANNELS["model_channels: 64"]
        UNET --> CONTEXT["context_dim: 32"]
    end
    
    subgraph "Conditioning System"
        COND --> PROTO["use_prototype: False"]
        COND --> LATENT["latent_dim: 32"]
        COND --> WINDOW["window: 24"]
    end
    
    COND --> UNET
    FIRST --> UNET
    
    style LDM fill:#f9f9f9,stroke:#333,stroke-width:2px
    style UNET fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/configs/base/mimic_icustay_base.yaml:2-68]()

The `LatentDiffusion` model serves as the primary orchestrator, coordinating between the UNet backbone for denoising operations and the conditioning system for context-aware generation. The model supports various conditioning modes including cross-attention (`conditioning_key: crossattn`) and configurable dropout for conditional parts.

## Encoder Module System

The encoder system provides domain-specific and unified encoding capabilities for time series data. The framework supports multiple encoder types for different use cases and conditioning modes.

```mermaid
graph TB
    subgraph "Encoder Interface"
        ENCODER_INIT["diffusion/ldm/modules/encoders/__init__.py"]
    end
    
    subgraph "Domain Unified Encoder"
        DOMAIN_ENC["DomainUnifiedEncoder"]
        DOMAIN_ENC --> DIM["dim: 32"]
        DOMAIN_ENC --> WINDOW_PARAM["window: 24"]
        DOMAIN_ENC --> LATENT_DIM["latent_dim: 32"]
        DOMAIN_ENC --> CHANNELS["num_channels: 7"]
        DOMAIN_ENC --> PROTO_FLAG["use_prototype: False"]
    end
    
    subgraph "Encoder Types"
        SPLIT_TS["SplitTSEqEncoder"]
        SINGLE_TS["SingleTSEncoder"]
        DOMAIN_ENC --> SPLIT_TS
        DOMAIN_ENC --> SINGLE_TS
    end
    
    subgraph "Context Processing"
        CONTEXT["context_dim: 32"]
        REPRE_EMB["repre_emb_channels: 32"]
        CONTEXT --> DOMAIN_ENC
        REPRE_EMB --> DOMAIN_ENC
    end
    
    style DOMAIN_ENC fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/configs/base/mimic_icustay_base.yaml:59-68](), [diffusion/ldm/modules/encoders/__init__.py:1-2]()

The encoder system is designed to handle multi-channel time series data with configurable dimensions and prototype-based conditioning. The `DomainUnifiedEncoder` can operate in different modes depending on the `use_prototype` flag and supports various time series encoding strategies.

## Data Processing Components

The data processing system provides comprehensive dataset handling, normalization, and batch preparation capabilities. The system is built around PyTorch Lightning data modules for efficient training and validation workflows.

```mermaid
graph TB
    subgraph "Data Module Hierarchy"
        BASE_DM["pl.LightningDataModule"]
        BASE_DM --> TSG_DM["TSGDataModule"]
        BASE_DM --> TSG_TEXT_DM["TSGtextDataModule"]
        BASE_DM --> TSG_COND_DM["TSClassCondTrainDataModule"]
    end
    
    subgraph "Dataset Classes"
        TSG_DATASET["TSGDataset"]
        TSG_TEXT_DATASET["TSGtextDataset"]
        TSG_COND_DATASET["TSClassCondDataset"]
    end
    
    subgraph "Data Loading"
        LOAD_FUNC["load_data_from_file"]
        LOAD_TEXT_FUNC["load_data_text_from_file"]
        PREPROCESS_FUNC["preprocess_text_data"]
        
        LOAD_FUNC --> CSV[".csv files"]
        LOAD_FUNC --> TSF[".tsf files"]
        LOAD_FUNC --> NPY[".npy files"]
        LOAD_FUNC --> PKL[".pkl files"]
    end
    
    subgraph "Normalization Methods"
        NORM_ZSCORE["zscore"]
        NORM_ROBUST["robust_iqr"]
        NORM_MAD["robust_mad"]
        NORM_PIT["pit"]
        NORM_CENTERED["centered_pit"]
        NORM_MINMAX["minmax"]
    end
    
    TSG_DM --> TSG_DATASET
    TSG_TEXT_DM --> TSG_TEXT_DATASET
    TSG_COND_DM --> TSG_COND_DATASET
    
    LOAD_FUNC --> TSG_DM
    LOAD_TEXT_FUNC --> TSG_TEXT_DM
    
    style TSG_DM fill:#f9f9f9,stroke:#333,stroke-width:2px
    style TSG_TEXT_DM fill:#f9f9f9,stroke:#333,stroke-width:2px
    style TSG_COND_DM fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/ldm/data/tsg_dataset.py:15-991]()

### Dataset Classes and Their Roles

The framework provides specialized dataset classes for different use cases:

| Dataset Class | Purpose | Key Features |
|---------------|---------|--------------|
| `TSGDataset` | Basic time series generation | Cross-domain data handling, reweighting |
| `TSGtextDataset` | Text-conditioned generation | Text embedding integration, multi-modal support |
| `TSClassCondDataset` | Classification-conditioned generation | Label-based conditioning, balanced sampling |

**Sources:** [TarDiff/ldm/data/tsg_dataset.py:283-331](), [TarDiff/ldm/data/tsg_dataset.py:475-532](), [TarDiff/ldm/data/tsg_dataset.py:15-46]()

### Normalization System

The normalization system supports multiple strategies for time series data preprocessing:

```mermaid
graph TB
    subgraph "Normalization Pipeline"
        FIT["fit_normalizer()"]
        TRANSFORM["transform()"]
        INVERSE["inverse_transform()"]
    end
    
    subgraph "Normalization Methods"
        ZSCORE["Z-Score Normalization"]
        ROBUST_IQR["Robust IQR Normalization"]
        ROBUST_MAD["Robust MAD Normalization"]
        PIT["Probability Integral Transform"]
        CENTERED_PIT["Centered PIT"]
        MINMAX["Min-Max Normalization"]
    end
    
    subgraph "Statistical Components"
        MEAN["mean, std"]
        MEDIAN["median, iqr/mad"]
        ECDF["Empirical CDF"]
        MINMAX_VALS["min, max"]
    end
    
    FIT --> ZSCORE
    FIT --> ROBUST_IQR
    FIT --> ROBUST_MAD
    FIT --> PIT
    FIT --> CENTERED_PIT
    FIT --> MINMAX
    
    ZSCORE --> MEAN
    ROBUST_IQR --> MEDIAN
    ROBUST_MAD --> MEDIAN
    PIT --> ECDF
    CENTERED_PIT --> ECDF
    MINMAX --> MINMAX_VALS
    
    TRANSFORM --> INVERSE
    
    style FIT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style TRANSFORM fill:#f9f9f9,stroke:#333,stroke-width:2px
    style INVERSE fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/ldm/data/tsg_dataset.py:211-281](), [TarDiff/ldm/data/tsg_dataset.py:412-472](), [TarDiff/ldm/data/tsg_dataset.py:603-662]()

The normalization system uses a three-stage process: fitting normalizers on training data, transforming data during training and inference, and inverse transforming generated samples back to original scale.

## Configuration System Integration

The model components are configured through YAML files that define the complete pipeline from data loading to model architecture. The configuration system uses target-based instantiation for flexible component selection.

```mermaid
graph TB
    subgraph "Configuration Structure"
        CONFIG["mimic_icustay_base.yaml"]
        CONFIG --> MODEL_CONFIG["model"]
        CONFIG --> DATA_CONFIG["data"]
        CONFIG --> LIGHTNING_CONFIG["lightning"]
    end
    
    subgraph "Model Configuration"
        MODEL_CONFIG --> TARGET["target: ldm.models.diffusion.ddpm.LatentDiffusion"]
        MODEL_CONFIG --> UNET_CONFIG["unet_config"]
        MODEL_CONFIG --> FIRST_STAGE["first_stage_config"]
        MODEL_CONFIG --> COND_STAGE["cond_stage_config"]
        
        UNET_CONFIG --> UNET_TARGET["target: ldm.modules.diffusionmodules.unet1d.UNetModel"]
        FIRST_STAGE --> FIRST_TARGET["target: ldm.models.autoencoder.IdentityFirstStage"]
        COND_STAGE --> COND_TARGET["target: ldm.modules.encoders.modules.DomainUnifiedEncoder"]
    end
    
    subgraph "Data Configuration"
        DATA_CONFIG --> DATA_TARGET["target: ldm.data.tsg_dataset.TSClassCondTrainDataModule"]
        DATA_CONFIG --> DATA_PARAMS["data_path_dict"]
        DATA_CONFIG --> BATCH_SIZE["batch_size: 256"]
        DATA_CONFIG --> NORMALIZE["normalize: centered_pit"]
    end
    
    subgraph "Training Configuration"
        LIGHTNING_CONFIG --> CALLBACKS["callbacks"]
        LIGHTNING_CONFIG --> TRAINER["trainer"]
        CALLBACKS --> LOGGER["image_logger"]
        LOGGER --> LOGGER_TARGET["target: utils.callback_utils.TSLogger"]
    end
    
    style CONFIG fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MODEL_CONFIG fill:#f9f9f9,stroke:#333,stroke-width:2px
    style DATA_CONFIG fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/configs/base/mimic_icustay_base.yaml:1-98]()

The configuration system uses target strings to specify exact class paths, enabling flexible component swapping without code changes. Key configuration parameters include sequence length (`seq_length: 24`), model channels (`model_channels: 64`), and attention resolutions (`attention_resolutions: [1, 2, 4]`).

## Component Integration and Data Flow

The model components work together in a coordinated pipeline that processes time series data through multiple stages of encoding, conditioning, and generation.

```mermaid
graph TB
    subgraph "Data Flow Pipeline"
        RAW_DATA["Raw Time Series Data"]
        DATASET["TSClassCondDataset"]
        DATAMODULE["TSClassCondTrainDataModule"]
        ENCODER["DomainUnifiedEncoder"]
        DIFFUSION["LatentDiffusion"]
        UNET["UNet1D"]
        OUTPUT["Generated Time Series"]
    end
    
    subgraph "Processing Steps"
        LOAD["load_data_from_file()"]
        NORMALIZE["fit_normalizer() + transform()"]
        SPLIT["split_train_val()"]
        BATCH["DataLoader"]
        ENCODE["encode_context()"]
        DENOISE["denoise_timestep()"]
        DECODE["decode_output()"]
    end
    
    RAW_DATA --> LOAD
    LOAD --> NORMALIZE
    NORMALIZE --> SPLIT
    SPLIT --> DATASET
    DATASET --> DATAMODULE
    DATAMODULE --> BATCH
    BATCH --> ENCODER
    ENCODER --> ENCODE
    ENCODE --> DIFFUSION
    DIFFUSION --> UNET
    UNET --> DENOISE
    DENOISE --> DECODE
    DECODE --> OUTPUT
    
    style RAW_DATA fill:#f9f9f9,stroke:#333,stroke-width:2px
    style OUTPUT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style DIFFUSION fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [TarDiff/ldm/data/tsg_dataset.py:48-210](), [TarDiff/configs/base/mimic_icustay_base.yaml:35-68]()

The integration follows a modular design where each component can be configured independently through the YAML configuration system. The data modules handle preprocessing and batching, encoders provide contextual representations, and the diffusion model coordinates the generation process through the UNet architecture.

---

