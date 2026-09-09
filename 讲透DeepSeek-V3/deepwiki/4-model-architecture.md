> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-V3/4-model-architecture](https://deepwiki.com/deepseek-ai/DeepSeek-V3/4-model-architecture)
> DeepWiki deepseek-ai/DeepSeek-V3

# Model Architecture

  Relevant source files 
 - [inference/model.py](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py)
 
  This document provides a comprehensive technical overview of the DeepSeek-V3 model architecture implementation, focusing on the core components, attention mechanisms, and distributed processing capabilities. The architecture is implemented primarily in the `Transformer` class and related modules.

 For information about the inference pipeline and text generation, see [Inference Pipeline](https://deepwiki.com/deepseek-ai/DeepSeek-V3/4-model-architecture). For configuration options and model parameters, see [Configuration](https://deepwiki.com/deepseek-ai/DeepSeek-V3/6-model-weights). For model weight structure and quantization details, see [Model Weights](https://deepwiki.com/deepseek-ai/DeepSeek-V3/5-inference-pipeline).

 
## Architecture Overview

 The DeepSeek-V3 model implements a transformer architecture with Multi-head Latent Attention (MLA) and Mixture of Experts (MoE) components. The model supports distributed processing across multiple GPUs and includes FP8 quantization for memory efficiency.

 
### Core Architecture Components

 
```

```

 **Sources:** [inference/model.py735-795](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L735-L795)

 The `Transformer` class serves as the main model container, orchestrating embeddings, multiple transformer blocks, normalization, and output projection. Each `Block` contains an MLA attention layer and either an MLP or MoE feed-forward layer depending on the layer position.

 
### Model Configuration

 The architecture is highly configurable through the `ModelArgs` dataclass, which defines key parameters:

 
| Parameter | Default | Description |
|---|---|---|
| n_layers | 27 | Number of transformer blocks |
| n_dense_layers | 1 | Number of dense (MLP) layers before MoE |
| dim | 2048 | Model dimension |
| n_heads | 16 | Number of attention heads |
| n_routed_experts | 64 | Total number of MoE experts |
| n_activated_experts | 6 | Number of experts activated per token |
| vocab_size | 102400 | Vocabulary size |

 **Sources:** [inference/model.py19-85](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L19-L85)

 
## Multi-head Latent Attention (MLA)

 The MLA mechanism implements an efficient attention computation using low-rank projections and compressed key-value representations. This approach reduces memory usage while maintaining attention quality.

 
### MLA Architecture

 
```

```

 **Sources:** [inference/model.py393-495](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L393-L495)

 The MLA implementation includes several key components:

 
 - **Low-rank projections**: Uses `q_lora_rank` and `kv_lora_rank` parameters to reduce computational complexity
 - **Rotary embeddings**: Applied to position-dependent components (`q_pe` and `k_pe`)
 - **Compressed representations**: Key-value pairs are compressed through the `kv_lora_rank` bottleneck
 - **Caching strategies**: Supports both naive and absorb caching implementations via `attn_impl` parameter
 
 
### MLA Implementation Details

 The `MLA` class handles query, key, and value projections with different strategies based on configuration:

 
```

```

 **Sources:** [inference/model.py421-426](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L421-L426) [inference/model.py427-430](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L427-L430)

 
## Mixture of Experts (MoE)

 The MoE architecture activates a subset of experts for each token, enabling the model to scale capacity without proportionally increasing computation. The implementation includes routing mechanisms, expert computation, and load balancing.

 
### MoE Components

 
```

```

 **Sources:** [inference/model.py633-691](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L633-L691) [inference/model.py532-596](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L532-L596) [inference/model.py598-631](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L598-L631)

 
### Expert Routing

 The `Gate` class implements the routing mechanism that determines which experts process each token:

 
 - **Scoring**: Computes scores for all experts using learned parameters
 - **Selection**: Uses top-k selection to choose `n_activated_experts` experts
 - **Normalization**: Applies softmax or sigmoid normalization based on `score_func`
 - **Grouping**: Supports expert grouping for load balancing via `n_expert_groups`
 
 **Sources:** [inference/model.py563-595](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L563-L595)

 Each `Expert` module is a standard MLP with SiLU activation, consisting of three linear layers (`w1`, `w2`, `w3`) configured for the MoE intermediate dimension.

 
## Distributed Processing

 The architecture includes comprehensive support for distributed training and inference across multiple GPUs through specialized linear layers and embedding components.

 
### Parallel Components

 
```

```

 **Sources:** [inference/model.py205-232](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L205-L232) [inference/model.py234-265](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L234-L265) [inference/model.py87-127](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L87-L127)

 
### Distributed Implementation Details

 The distributed processing relies on three key patterns:

 
 - **Column Parallelism**: `ColumnParallelLinear` splits output features across ranks
 - **Row Parallelism**: `RowParallelLinear` splits input features and reduces results
 - **Embedding Parallelism**: `ParallelEmbedding` partitions vocabulary across ranks
 
 Global variables `world_size` and `rank` coordinate distributed operations, automatically set when `torch.distributed` is initialized.

 
## Quantization Support

 The model supports FP8 quantization through custom linear operations and kernel implementations. The quantization strategy reduces memory usage while maintaining computational efficiency.

 
### Quantization Flow

 
```

```

 **Sources:** [inference/model.py129-162](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L129-L162) [inference/model.py10](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L10-L10)

 The `linear` function automatically handles quantization based on weight properties and the global `gemm_impl` setting. When weights are quantized (element size = 1), the function either dequantizes for BF16 computation or uses FP8 GEMM operations.

 
## Block Structure and Layer Composition

 Each transformer block combines attention and feed-forward components with residual connections and layer normalization.

 
### Block Implementation

 
```

```

 **Sources:** [inference/model.py693-733](https://github.com/deepseek-ai/DeepSeek-V3/blob/9b4e9788/inference/model.py#L693-L733)

 The `Block` class determines whether to use MLP or MoE based on the layer position: layers with `layer_id < n_dense_layers` use MLP, while subsequent layers use MoE. This allows for a mixed architecture where early layers use dense computation and later layers use sparse expert routing.
