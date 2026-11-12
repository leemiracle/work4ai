<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/FlexOlmo · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/FlexOlmo_Logo.png](assets/FlexOlmo_Logo.png)
- [src/flexolmo/internal/common.py](src/flexolmo/internal/common.py)

</details>



This document provides an overview of FlexOlmo's system architecture, covering the core components, their interactions, and the overall design principles that enable collaborative model development without direct data sharing. For detailed information about specific subsystems, see [MoE Router System](#2.1), [Model Components](#2.2), and [Configuration System](#2.3).

## System Overview

FlexOlmo implements a Mixture of Experts (MoE) architecture that enables independent training of domain-specific expert models, which are then combined into a unified model through an intelligent routing system. The system supports a three-stage training pipeline: public model training, expert specialization, and model combination with optional router training.

```mermaid
graph TB
    subgraph "FlexOlmo Core Architecture"
        A[ExperimentConfig] --> B[TransformerConfig]
        A --> C[NumpyDatasetConfig]
        A --> D[TransformerTrainModuleConfig]
        A --> E[TrainerConfig]
        
        B --> F["FlexOlmo-7x7B Model<br/>(33B parameters)"]
        C --> G[CustomDataMix]
        D --> H[AdamWConfig]
        E --> I[CheckpointerCallback]
        E --> J[WandBCallback]
        E --> K[LMEvaluatorCallbackConfig]
    end
    
    subgraph "Expert Architecture"
        L["Public Expert<br/>(7B params)"]
        M["Math Expert<br/>(7B params)"]
        N["News Expert<br/>(7B params)"]
        O["Code Expert<br/>(7B params)"]
        P["Creative Expert<br/>(7B params)"]
        Q["Academic Expert<br/>(7B params)"]
        R["Reddit Expert<br/>(7B params)"]
    end
    
    subgraph "Training Components"
        S[CommonComponents]
        T[build_common_components]
        U[build_experiment_config]
    end
    
    F --> L
    F --> M
    F --> N
    F --> O
    F --> P
    F --> Q
    F --> R
    
    T --> S
    S --> A
    U --> A
```

**Sources:** [README.md:22-49](), [src/flexolmo/internal/common.py:55-76]()

## Core Architecture Components

The FlexOlmo architecture is built around several key components that work together to enable flexible model composition and training:

### Configuration Hierarchy

```mermaid
graph TD
    A[build_experiment_config] --> B[CommonComponents]
    B --> C[run_name]
    B --> D[save_folder]
    B --> E[TokenizerConfig]
    B --> F[NumpyDatasetConfig]
    B --> G[NumpyDataLoaderConfig]
    B --> H[TransformerTrainModuleConfig]
    B --> I[TrainerConfig]
    B --> J["callbacks<br/>(Dict[str, Callback])"]
    
    K[ExperimentConfig] --> L[TransformerConfig]
    K --> M[NumpyDatasetConfig]
    K --> N[TransformerTrainModuleConfig]
    K --> O[TrainerConfig]
    K --> P[init_seed]
    
    A --> K
    B --> K
    
    E --> Q[TokenizerConfig.dolma2]
    F --> R[DataMix.OLMoE_mix_0824]
    H --> S[AdamWConfig]
    H --> T[TransformerDataParallelConfig]
    H --> U[Float8Config]
    
    J --> V[CheckpointerCallback]
    J --> W[WandBCallback]
    J --> X[BeakerCallback]
    J --> Y[LMEvaluatorCallbackConfig]
```

**Sources:** [src/flexolmo/internal/common.py:94-244](), [src/flexolmo/internal/common.py:247-351]()

### Model Architecture Components

| Component | Class | Purpose |
|-----------|-------|---------|
| Model Configuration | `TransformerConfig` | Defines model architecture parameters |
| Data Configuration | `NumpyDatasetConfig` | Specifies dataset sources and preprocessing |
| Training Module | `TransformerTrainModuleConfig` | Configures optimization and training parameters |
| Data Loading | `NumpyDataLoaderConfig` | Manages data loading and batching |
| Training Control | `TrainerConfig` | Controls training lifecycle and checkpointing |

**Sources:** [src/flexolmo/internal/common.py:68-76]()

## Training Pipeline Architecture

The FlexOlmo training pipeline follows a three-stage architecture that enables independent expert development:

```mermaid
flowchart TD
    A["Public Dataset<br/>(1T tokens)"] --> B[train_public_model.sh]
    B --> C["Dense 7B Model<br/>(Flex-public-7B-1T)"]
    C --> D[Annealing Process]
    D --> E["Unsharded Model<br/>(save_folder)"]
    E --> F[Upcycle to MoE]
    F --> G["Public MoE Expert<br/>(2x7B architecture)"]
    
    H["Domain Data<br/>(50B tokens each)"] --> I[train_expert_model.sh]
    I --> J["Math Expert<br/>(Flex-math-2x7B-1T)"]
    I --> K["News Expert<br/>(Flex-news-2x7B-1T)"]
    I --> L["Code Expert<br/>(Flex-code-2x7B-1T)"]
    I --> M["Creative Expert<br/>(Flex-creative-2x7B-1T)"]
    I --> N["Academic Expert<br/>(Flex-pes2o-2x7B-1T)"]
    I --> O["Reddit Expert<br/>(Flex-reddit-2x7B-1T)"]
    
    G --> P[combine_experts.sh]
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q["FlexOlmo-7x7B-1T<br/>(33B parameters)"]
    
    R["Proxy Data<br/>(Router Training)"] --> S[Router Training]
    Q --> S
    S --> T["FlexOlmo-7x7B-1T-RT<br/>(Final Model)"]
    
    U["Domain Embeddings<br/>(grit/)"] --> S
```

**Sources:** [README.md:42-49](), [README.md:51-55]()

## Configuration Architecture

The FlexOlmo configuration system uses a hierarchical approach to manage complex experimental setups:

```mermaid
graph LR
    A[build_common_components] --> B[get_root_dir]
    A --> C[get_save_dir]
    A --> D[TokenizerConfig.dolma2]
    A --> E[NumpyDatasetConfig.from_data_mix]
    A --> F[NumpyDataLoaderConfig]
    A --> G[TransformerTrainModuleConfig]
    A --> H[TrainerConfig]
    
    E --> I[DataMix.OLMoE_mix_0824]
    E --> J[VSLCurriculumConfig]
    
    G --> K[AdamWConfig]
    G --> L[TransformerDataParallelConfig]
    G --> M[Float8Config]
    G --> N[CosWithWarmup]
    
    H --> O[get_save_dir]
    H --> P[Duration.tokens]
    
    Q[build_experiment_config] --> R[model_config_builder]
    Q --> S[train_module_config_builder]
    Q --> T[dataset_config_builder]
    Q --> U[trainer_config_builder]
    
    A --> V[CommonComponents]
    V --> Q
    Q --> W[ExperimentConfig]
    
    X[CustomDataMix] --> Y[get_mixture_dataset_config]
    W --> X
```

**Sources:** [src/flexolmo/internal/common.py:94-159](), [src/flexolmo/internal/common.py:247-351]()

## Data Flow Architecture

The data flow architecture supports flexible data mixing and domain-specific training:

```mermaid
graph TB
    subgraph "Data Sources"
        A[DataMix.OLMoE_mix_0824]
        B[CustomDataMix]
        C["Domain-Specific Data<br/>(News, Math, Code, etc.)"]
    end
    
    subgraph "Data Configuration"
        D[NumpyDatasetConfig.from_data_mix]
        E[get_mixture_dataset_config]
        F[TokenizerConfig.dolma2]
        G[VSLCurriculumConfig]
    end
    
    subgraph "Data Loading"
        H[NumpyDataLoaderConfig]
        I[global_batch_size]
        J[sequence_length]
        K[num_workers]
    end
    
    subgraph "Training Pipeline"
        L[TransformerTrainModuleConfig]
        M[rank_microbatch_size]
        N[max_sequence_length]
        O[AdamWConfig]
    end
    
    A --> D
    B --> E
    C --> D
    D --> F
    D --> G
    
    F --> H
    G --> H
    H --> I
    H --> J
    H --> K
    
    H --> L
    L --> M
    L --> N
    L --> O
    
    P["get_work_dir"] --> D
    Q["mix_base_dir"] --> D
    R["root_dir"] --> Q
```

**Sources:** [src/flexolmo/internal/common.py:106-118](), [src/flexolmo/internal/common.py:120-122](), [src/flexolmo/internal/common.py:324-350]()

## System Integration Points

The architecture provides several key integration points that enable flexible model composition:

| Integration Point | Implementation | Purpose |
|-------------------|----------------|---------|
| Model Builders | `model_config_builder` | Customize model architecture |
| Data Builders | `dataset_config_builder` | Configure data sources |
| Training Builders | `train_module_config_builder` | Modify training parameters |
| Callback System | `callbacks: Dict[str, Callback]` | Extend training pipeline |
| Configuration Overrides | `config.merge(overrides)` | Runtime parameter modification |

The `build_experiment_config` function serves as the central orchestrator, accepting builder functions that customize each component while maintaining system coherence.

**Sources:** [src/flexolmo/internal/common.py:256-263](), [src/flexolmo/internal/common.py:275-297](), [src/flexolmo/internal/common.py:343]()

---

