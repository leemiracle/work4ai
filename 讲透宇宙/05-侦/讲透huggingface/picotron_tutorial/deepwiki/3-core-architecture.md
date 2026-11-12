<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/picotron_tutorial · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [step1_modeling/model.py](step1_modeling/model.py)
- [step3_dataloader/model.py](step3_dataloader/model.py)
- [step3_dataloader/utils.py](step3_dataloader/utils.py)

</details>



This document provides a comprehensive overview of the fundamental components that power the Picotron distributed training system. The core architecture consists of three primary subsystems: the LLaMA transformer model implementation, the data loading pipeline, and the process group management layer that coordinates distributed training operations.

For specific implementation details of tensor parallelism, data parallelism, and pipeline parallelism strategies, see [Parallelism Strategies](#4). For information about how these components integrate in complete training workflows, see [Training Integration](#5).

## System Overview

The Picotron architecture is designed around a modular approach where core components can be composed together to support different parallelism configurations. The system progresses from single-process training to sophisticated 3D parallelism while maintaining a consistent interface across all tutorial steps.

**Core Architecture Components**

```mermaid
graph TB
    subgraph "Core Architecture Layer"
        MODEL["Llama<br/>Transformer Model"]
        DATALOADER["MicroBatchDataLoader<br/>Data Pipeline"]
        PGM["ProcessGroupManager<br/>Distributed Coordination"]
    end
    
    subgraph "Model Architecture"
        EMBED["nn.Embedding<br/>Token Embedding"]
        DECODER_STACK["DecoderLayer Stack<br/>Transformer Layers"]
        FINAL_NORM["TritonRMSNorm<br/>Final Normalization"]
        PROJ["nn.Linear<br/>Output Projection"]
        
        EMBED --> DECODER_STACK
        DECODER_STACK --> FINAL_NORM
        FINAL_NORM --> PROJ
    end
    
    subgraph "DecoderLayer Components"
        ATTN["Attention<br/>Multi-Head Attention"]
        MLP_BLOCK["MLP<br/>Feed-Forward Network"]
        NORM1["TritonRMSNorm<br/>Pre-Attention Norm"]
        NORM2["TritonRMSNorm<br/>Pre-MLP Norm"]
        
        NORM1 --> ATTN
        NORM2 --> MLP_BLOCK
    end
    
    subgraph "Data Processing Pipeline"
        TOKENIZER["AutoTokenizer<br/>Text Processing"]
        SAMPLER["DistributedSampler<br/>Data Sharding"]
        COLLATOR["Collation Functions<br/>Batch Formation"]
        
        TOKENIZER --> SAMPLER
        SAMPLER --> COLLATOR
    end
    
    MODEL --> DECODER_STACK
    DECODER_STACK --> ATTN
    DECODER_STACK --> MLP_BLOCK
    
    DATALOADER --> TOKENIZER
    
    PGM -.->|"Coordinates"| MODEL
    PGM -.->|"Coordinates"| DATALOADER
    
    style MODEL fill:#f9f,stroke:#333,stroke-width:2px
    style DATALOADER fill:#bbf,stroke:#333,stroke-width:2px
    style PGM fill:#9f9,stroke:#333,stroke-width:2px
```

Sources: [step1_modeling/model.py:118-148](), [step3_dataloader/model.py:118-148]()

## LLaMA Model Architecture

The `Llama` class serves as the main model interface and implements a standard transformer architecture optimized for autoregressive language modeling. The implementation uses several key architectural components that are designed for efficient distributed training.

**Model Component Hierarchy**

```mermaid
graph TD
    subgraph "Llama Model Class"
        LLAMA_INIT["__init__<br/>Model Configuration"]
        LLAMA_FORWARD["forward<br/>Input Processing"]
    end
    
    subgraph "Core Model Components"
        EMBEDDING["self.embedding<br/>nn.Embedding"]
        DECODER_LAYERS["self.decoder_layers<br/>nn.ModuleList"]
        FINAL_PROJ["self.final_proj<br/>nn.Linear"]
        FINAL_NORM["self.final_norm<br/>TritonRMSNorm"]
    end
    
    subgraph "DecoderLayer Implementation"
        INPUT_NORM["self.input_layernorm<br/>TritonRMSNorm"]
        ATTENTION["self.attention<br/>Attention"]
        POST_ATTN_NORM["self.post_attention_layernorm<br/>TritonRMSNorm"]
        MLP["self.mlp<br/>MLP"]
    end
    
    subgraph "Attention Components"
        Q_PROJ["self.q_proj<br/>nn.Linear"]
        K_PROJ["self.k_proj<br/>nn.Linear"]
        V_PROJ["self.v_proj<br/>nn.Linear"]
        OUT_PROJ["self.out_proj<br/>nn.Linear"]
        FLASH_ATTN["flash_attention<br/>FlashAttention Function"]
        ROPE["apply_rotary_emb<br/>RoPE Positioning"]
    end
    
    subgraph "MLP Components"
        UP_PROJ["self.up_proj<br/>nn.Linear"]
        GATE_PROJ["self.gate_proj<br/>nn.Linear"]
        DOWN_PROJ["self.down_proj<br/>nn.Linear"]
        SILU["F.silu<br/>Activation Function"]
    end
    
    LLAMA_INIT --> EMBEDDING
    LLAMA_INIT --> DECODER_LAYERS
    LLAMA_INIT --> FINAL_PROJ
    LLAMA_INIT --> FINAL_NORM
    
    DECODER_LAYERS --> INPUT_NORM
    DECODER_LAYERS --> ATTENTION
    DECODER_LAYERS --> POST_ATTN_NORM
    DECODER_LAYERS --> MLP
    
    ATTENTION --> Q_PROJ
    ATTENTION --> K_PROJ
    ATTENTION --> V_PROJ
    ATTENTION --> OUT_PROJ
    ATTENTION --> FLASH_ATTN
    ATTENTION --> ROPE
    
    MLP --> UP_PROJ
    MLP --> GATE_PROJ
    MLP --> DOWN_PROJ
    MLP --> SILU
```

Sources: [step1_modeling/model.py:118-148](), [step1_modeling/model.py:100-117](), [step1_modeling/model.py:48-87](), [step1_modeling/model.py:89-98]()

### Key Architectural Features

The model implementation includes several optimizations for distributed training:

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **Attention Mechanism** | `flash_attention` function with `flash_attn_func` | Memory-efficient attention computation |
| **Positional Encoding** | `get_cos_sin` with RoPE via `apply_rotary_emb` | Rotary position embeddings for better length generalization |
| **Normalization** | `TritonRMSNorm` using `layer_norm_fn` | Efficient RMSNorm implementation via Triton |
| **Activation** | `F.silu` in MLP gating | SiLU activation for improved training dynamics |

The `DecoderLayer` follows the standard pre-normalization transformer pattern: `TritonRMSNorm -> Attention -> Residual -> TritonRMSNorm -> MLP -> Residual` as documented in [step1_modeling/model.py:101]().

Sources: [step1_modeling/model.py:8-12](), [step1_modeling/model.py:14-23](), [step1_modeling/model.py:25-46](), [step1_modeling/model.py:96-98]()

## Data Processing Pipeline

The data loading system provides efficient batch generation and distributed sampling capabilities. While the specific `MicroBatchDataLoader` implementation details are covered in [Data Loading System](#3.2), the core architecture establishes the foundation for gradient accumulation and distributed data handling.

**Data Flow Architecture**

```mermaid
graph LR
    subgraph "Input Data Sources"
        DATASET["HuggingFace Dataset<br/>TinyStories"]
        RAW_TEXT["Raw Text Strings<br/>Story Content"]
    end
    
    subgraph "Tokenization Layer"
        TOKENIZER["AutoTokenizer<br/>Text to Token Conversion"]
        ENCODING["encode() method<br/>String to List[int]"]
    end
    
    subgraph "Batch Formation"
        CHUNKING["Text Chunking<br/>seq_len + 1 Tokens"]
        INPUT_IDS["input_ids<br/>First seq_len Tokens"]
        TARGET_IDS["target_ids<br/>Last seq_len Tokens"]
    end
    
    subgraph "Distributed Sampling"
        DIST_SAMPLER["DistributedSampler<br/>Data Sharding"]
        RANK_SUBSET["Per-Rank Data<br/>Non-Overlapping Subsets"]
    end
    
    subgraph "Model Input"
        BATCHED_INPUT["Batched Tensors<br/>Shape: [batch_size, seq_len]"]
        MODEL_FORWARD["model.forward()<br/>Logits Generation"]
    end
    
    DATASET --> RAW_TEXT
    RAW_TEXT --> TOKENIZER
    TOKENIZER --> ENCODING
    ENCODING --> CHUNKING
    CHUNKING --> INPUT_IDS
    CHUNKING --> TARGET_IDS
    
    INPUT_IDS --> DIST_SAMPLER
    TARGET_IDS --> DIST_SAMPLER
    DIST_SAMPLER --> RANK_SUBSET
    RANK_SUBSET --> BATCHED_INPUT
    BATCHED_INPUT --> MODEL_FORWARD
```

Sources: [step3_dataloader/utils.py:1-40]()

## Process Group Management

The `ProcessGroupManager` coordinates distributed training operations across multiple parallelism dimensions. This component establishes the communication topology for tensor parallelism, data parallelism, and pipeline parallelism groups. The detailed implementation is covered in [Process Group Management](#3.3).

**Distributed Coordination Architecture**

```mermaid
graph TB
    subgraph "Process Group Hierarchy"
        WORLD_GROUP["WORLD Group<br/>All Processes"]
        TP_GROUP["Tensor Parallel Groups<br/>Model Sharding"]
        DP_GROUP["Data Parallel Groups<br/>Gradient Synchronization"]
        PP_GROUP["Pipeline Parallel Groups<br/>Stage Communication"]
    end
    
    subgraph "Communication Patterns"
        ALL_REDUCE["All-Reduce Operations<br/>Gradient Aggregation"]
        P2P_COMM["Point-to-Point Communication<br/>Pipeline Stage Transfer"]
        BROADCAST["Broadcast Operations<br/>Parameter Synchronization"]
    end
    
    subgraph "Parallelism Integration"
        MODEL_SHARDING["Model Parameter Sharding<br/>Across TP Ranks"]
        DATA_SHARDING["Data Batch Sharding<br/>Across DP Ranks"]
        STAGE_SHARDING["Layer Stage Sharding<br/>Across PP Ranks"]
    end
    
    WORLD_GROUP --> TP_GROUP
    WORLD_GROUP --> DP_GROUP
    WORLD_GROUP --> PP_GROUP
    
    TP_GROUP --> ALL_REDUCE
    DP_GROUP --> ALL_REDUCE
    PP_GROUP --> P2P_COMM
    
    TP_GROUP -.->|"Manages"| MODEL_SHARDING
    DP_GROUP -.->|"Manages"| DATA_SHARDING
    PP_GROUP -.->|"Manages"| STAGE_SHARDING
    
    ALL_REDUCE --> BROADCAST
```

Sources: Referenced from tutorial progression and distributed training patterns

## Component Integration

The three core architectural components work together to enable scalable distributed training. The integration patterns establish how models can be transformed from single-process implementations to sophisticated multi-dimensional parallel configurations.

| Integration Point | Mechanism | Purpose |
|------------------|-----------|---------|
| **Model-Data** | Batch shape coordination | Ensure consistent tensor dimensions across parallelism |
| **Model-ProcessGroup** | Communication group assignment | Map model components to appropriate process groups |
| **Data-ProcessGroup** | Distributed sampling | Coordinate data sharding across data parallel ranks |

The architecture supports progressive enhancement where each tutorial step adds new capabilities while maintaining compatibility with existing components. This design enables users to understand the impact of each parallelism strategy independently before combining them into full 3D parallelism configurations.

For detailed implementation of specific components, see:
- [LLaMA Model Implementation](#3.1) for transformer architecture details
- [Data Loading System](#3.2) for data pipeline implementation  
- [Process Group Management](#3.3) for distributed coordination mechanisms

Sources: [step1_modeling/model.py:1-148](), [step3_dataloader/model.py:1-148](), [step3_dataloader/utils.py:1-40]()

---

