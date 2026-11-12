<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V3 · page 4 Model Architecture · fetched 2026-10-30 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [inference/model.py](inference/model.py)

</details>



This document provides a comprehensive technical overview of the DeepSeek-V3 model architecture implementation, focusing on the core components, attention mechanisms, and distributed processing capabilities. The architecture is implemented primarily in the `Transformer` class and related modules.

For information about the inference pipeline and text generation, see [Inference Pipeline](#4). For configuration options and model parameters, see [Configuration](#6). For model weight structure and quantization details, see [Model Weights](#5).

## Architecture Overview

The DeepSeek-V3 model implements a transformer architecture with Multi-head Latent Attention (MLA) and Mixture of Experts (MoE) components. The model supports distributed processing across multiple GPUs and includes FP8 quantization for memory efficiency.

### Core Architecture Components

```mermaid
graph TB
    subgraph "Transformer Model"
        A[Transformer] --> B[ParallelEmbedding]
        A --> C[Block_0]
        A --> D[Block_1]
        A --> E[Block_n]
        A --> F[RMSNorm]
        A --> G[ColumnParallelLinear]
    end
    
    subgraph "Block Structure"
        C --> H[MLA]
        C --> I[MLP_or_MoE]
        C --> J[RMSNorm_attn]
        C --> K[RMSNorm_ffn]
    end
    
    subgraph "Attention Layer"
        H --> L[wq_projection]
        H --> M[wkv_projection]
        H --> N[rotary_embeddings]
        H --> O[attention_computation]
    end
    
    subgraph "Feed-Forward Layer"
        I --> P[MLP]
        I --> Q[MoE]
        Q --> R[Gate]
        Q --> S[Expert_modules]
        Q --> T[shared_experts]
    end
    
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    
    style A fill:#f9f9f9
    style H fill:#e8f4f8
    style Q fill:#f0f8e8
```

**Sources:** [inference/model.py:735-795]()

The `Transformer` class serves as the main model container, orchestrating embeddings, multiple transformer blocks, normalization, and output projection. Each `Block` contains an MLA attention layer and either an MLP or MoE feed-forward layer depending on the layer position.

### Model Configuration

The architecture is highly configurable through the `ModelArgs` dataclass, which defines key parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_layers` | 27 | Number of transformer blocks |
| `n_dense_layers` | 1 | Number of dense (MLP) layers before MoE |
| `dim` | 2048 | Model dimension |
| `n_heads` | 16 | Number of attention heads |
| `n_routed_experts` | 64 | Total number of MoE experts |
| `n_activated_experts` | 6 | Number of experts activated per token |
| `vocab_size` | 102400 | Vocabulary size |

**Sources:** [inference/model.py:19-85]()

## Multi-head Latent Attention (MLA)

The MLA mechanism implements an efficient attention computation using low-rank projections and compressed key-value representations. This approach reduces memory usage while maintaining attention quality.

### MLA Architecture

```mermaid
graph LR
    subgraph "MLA Forward Pass"
        A[input_x] --> B[wq_projection]
        A --> C[wkv_a_projection]
        
        B --> D[q_nope]
        B --> E[q_pe]
        
        C --> F[kv_compressed]
        C --> G[k_pe]
        
        E --> H[apply_rotary_emb]
        G --> I[apply_rotary_emb]
        
        F --> J[kv_norm]
        J --> K[wkv_b_projection]
        
        K --> L[k_nope]
        K --> M[v_values]
        
        D --> N[attention_scores]
        H --> N
        I --> N
        L --> N
        
        N --> O[softmax]
        O --> P[attention_output]
        M --> P
        
        P --> Q[wo_projection]
        Q --> R[output]
    end
    
    style F fill:#f0f8e8
    style J fill:#e8f4f8
```

**Sources:** [inference/model.py:393-495]()

The MLA implementation includes several key components:

- **Low-rank projections**: Uses `q_lora_rank` and `kv_lora_rank` parameters to reduce computational complexity
- **Rotary embeddings**: Applied to position-dependent components (`q_pe` and `k_pe`)
- **Compressed representations**: Key-value pairs are compressed through the `kv_lora_rank` bottleneck
- **Caching strategies**: Supports both naive and absorb caching implementations via `attn_impl` parameter

### MLA Implementation Details

The `MLA` class handles query, key, and value projections with different strategies based on configuration:

```python
# Query projection (conditional on q_lora_rank)
if self.q_lora_rank == 0:
    self.wq = ColumnParallelLinear(self.dim, self.n_heads * self.qk_head_dim)
else:
    self.wq_a = Linear(self.dim, self.q_lora_rank)
    self.wq_b = ColumnParallelLinear(self.q_lora_rank, self.n_heads * self.qk_head_dim)
```

**Sources:** [inference/model.py:421-426](), [inference/model.py:427-430]()

## Mixture of Experts (MoE)

The MoE architecture activates a subset of experts for each token, enabling the model to scale capacity without proportionally increasing computation. The implementation includes routing mechanisms, expert computation, and load balancing.

### MoE Components

```mermaid
graph TB
    subgraph "MoE Module"
        A[input_x] --> B[Gate]
        A --> C[shared_experts]
        
        B --> D[routing_weights]
        B --> E[expert_indices]
        
        E --> F[Expert_0]
        E --> G[Expert_1]
        E --> H[Expert_n]
        
        F --> I[expert_outputs]
        G --> I
        H --> I
        
        D --> J[weighted_sum]
        I --> J
        
        C --> K[shared_output]
        J --> L[routed_output]
        
        K --> M[final_output]
        L --> M
    end
    
    subgraph "Expert Structure"
        F --> N[w1_linear]
        F --> O[w3_linear]
        F --> P[w2_linear]
        
        N --> Q[silu_activation]
        O --> Q
        Q --> P
    end
    
    subgraph "Gate Mechanism"
        B --> R[expert_scoring]
        R --> S[topk_selection]
        S --> T[weight_normalization]
    end
    
    style B fill:#f0f8e8
    style C fill:#e8f4f8
```

**Sources:** [inference/model.py:633-691](), [inference/model.py:532-596](), [inference/model.py:598-631]()

### Expert Routing

The `Gate` class implements the routing mechanism that determines which experts process each token:

- **Scoring**: Computes scores for all experts using learned parameters
- **Selection**: Uses top-k selection to choose `n_activated_experts` experts
- **Normalization**: Applies softmax or sigmoid normalization based on `score_func`
- **Grouping**: Supports expert grouping for load balancing via `n_expert_groups`

**Sources:** [inference/model.py:563-595]()

Each `Expert` module is a standard MLP with SiLU activation, consisting of three linear layers (`w1`, `w2`, `w3`) configured for the MoE intermediate dimension.

## Distributed Processing

The architecture includes comprehensive support for distributed training and inference across multiple GPUs through specialized linear layers and embedding components.

### Parallel Components

```mermaid
graph TB
    subgraph "Parallel Linear Layers"
        A[Linear] --> B[ColumnParallelLinear]
        A --> C[RowParallelLinear]
        
        B --> D[split_output_features]
        C --> E[split_input_features]
        
        D --> F[local_computation]
        E --> G[local_computation]
        G --> H[all_reduce]
    end
    
    subgraph "Parallel Embedding"
        I[ParallelEmbedding] --> J[vocab_partitioning]
        J --> K[local_embedding]
        K --> L[all_reduce]
    end
    
    subgraph "Distributed Coordination"
        M[world_size] --> N[rank_assignment]
        N --> O[partition_calculation]
        O --> P[communication_patterns]
    end
    
    style B fill:#f0f8e8
    style C fill:#e8f4f8
    style I fill:#f9f9f9
```

**Sources:** [inference/model.py:205-232](), [inference/model.py:234-265](), [inference/model.py:87-127]()

### Distributed Implementation Details

The distributed processing relies on three key patterns:

1. **Column Parallelism**: `ColumnParallelLinear` splits output features across ranks
2. **Row Parallelism**: `RowParallelLinear` splits input features and reduces results
3. **Embedding Parallelism**: `ParallelEmbedding` partitions vocabulary across ranks

Global variables `world_size` and `rank` coordinate distributed operations, automatically set when `torch.distributed` is initialized.

## Quantization Support

The model supports FP8 quantization through custom linear operations and kernel implementations. The quantization strategy reduces memory usage while maintaining computational efficiency.

### Quantization Flow

```mermaid
graph LR
    subgraph "Quantization Pipeline"
        A[input_tensor] --> B[act_quant]
        C[weight_tensor] --> D[weight_dequant]
        
        B --> E[quantized_input]
        D --> F[dequantized_weight]
        
        E --> G[fp8_gemm]
        F --> G
        
        G --> H[output_tensor]
    end
    
    subgraph "Linear Function"
        I[weight_check] --> J[element_size]
        J --> K[gemm_impl_decision]
        K --> L[bf16_path]
        K --> M[fp8_path]
    end
    
    style B fill:#f0f8e8
    style G fill:#e8f4f8
```

**Sources:** [inference/model.py:129-162](), [inference/model.py:10]()

The `linear` function automatically handles quantization based on weight properties and the global `gemm_impl` setting. When weights are quantized (element size = 1), the function either dequantizes for BF16 computation or uses FP8 GEMM operations.

## Block Structure and Layer Composition

Each transformer block combines attention and feed-forward components with residual connections and layer normalization.

### Block Implementation

```mermaid
graph TD
    subgraph "Block Forward Pass"
        A[input_x] --> B[attn_norm]
        A --> C[residual_1]
        
        B --> D[MLA]
        D --> E[attention_output]
        
        E --> F[add_residual_1]
        C --> F
        
        F --> G[ffn_norm]
        F --> H[residual_2]
        
        G --> I[MLP_or_MoE]
        I --> J[ffn_output]
        
        J --> K[add_residual_2]
        H --> K
        
        K --> L[block_output]
    end
    
    subgraph "Layer Selection"
        M[layer_id] --> N[compare_n_dense_layers]
        N --> O[MLP_selection]
        N --> P[MoE_selection]
    end
    
    style D fill:#e8f4f8
    style I fill:#f0f8e8
```

**Sources:** [inference/model.py:693-733]()

The `Block` class determines whether to use MLP or MoE based on the layer position: layers with `layer_id < n_dense_layers` use MLP, while subsequent layers use MoE. This allows for a mixed architecture where early layers use dense computation and later layers use sparse expert routing.

---

