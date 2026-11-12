<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/torchscale · page 4 Core Components · fetched 2026-10-26 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [torchscale/component/feedforward_network.py](torchscale/component/feedforward_network.py)
- [torchscale/component/multihead_attention.py](torchscale/component/multihead_attention.py)
- [torchscale/component/xmoe/moe_layer.py](torchscale/component/xmoe/moe_layer.py)
- [torchscale/component/xpos_relative_position.py](torchscale/component/xpos_relative_position.py)

</details>



This page provides an overview of the fundamental building blocks that power TorchScale's model architectures. These components serve as the critical internal machinery that enables the library's advanced transformer variants, including Encoders, Decoders, RetNet, and LongNet architectures.

For information about how these components are combined to form complete architectures, see [Architecture Overview](#2).

## Component Architecture Overview

The TorchScale library is built around a set of reusable neural network components that can be composed to create various transformer-based architectures. These components are designed to be highly configurable and support features like DeepNorm, SubLN, X-MoE, and various positional embedding schemes.

```mermaid
flowchart TD
    subgraph "Core Components"
        MHA["MultiheadAttention"]
        FFN["FeedForwardNetwork"]
        MOE["Mixture of Experts (MoE)"]
        FA["Flash Attention"]
        PE["Positional Embeddings"]
        MW["Multiway Network"]
    end

    subgraph "Positional Embedding Types"
        PE --> XPOS["XPOS"]
        PE --> RPB["RelativePositionBias"]
    end

    subgraph "Attention Optimizations"
        MHA --> FA
    end

    subgraph "FFN Variants"
        FFN --> Regular["Regular FFN"]
        FFN --> MOE
    end

    subgraph "Architecture Integration"
        MHA --> Encoder["Used in Encoder"]
        MHA --> Decoder["Used in Decoder"]
        MHA --> RetNet["Used in RetNet"]
        MHA --> LongNet["Used in LongNet"]
        
        FFN --> Encoder
        FFN --> Decoder
        FFN --> RetNet
        FFN --> LongNet
        
        PE --> Encoder
        PE --> Decoder
        PE --> RetNet
        
        MW --> Multimodal["Used in Multimodal Models"]
    end
```

Sources: [README.md:117-139]()

## MultiheadAttention

The `MultiheadAttention` module is a critical component in transformer architectures that enables the model to focus on different parts of the input sequence simultaneously. TorchScale's implementation supports both self-attention and encoder-decoder cross-attention, with additional features like XPOS relative positional embeddings and flash attention optimizations.

```mermaid
classDiagram
    class MultiheadAttention {
        +embed_dim: int
        +num_heads: int
        +head_dim: int
        +scaling: float
        +dropout: float
        +self_attention: bool
        +encoder_decoder_attention: bool
        +k_proj: Linear
        +v_proj: Linear
        +q_proj: Linear
        +out_proj: Linear
        +inner_attn_ln: LayerNorm
        +xpos: XPOS
        +forward(query, key, value, incremental_state, key_padding_mask, attn_mask, rel_pos, is_first_step, is_causal)
        +attention_ops(q, k, v, key_padding_mask, attn_mask, rel_pos, is_causal)
        +reset_parameters()
    }
```

Key features of the `MultiheadAttention` implementation:

1. **Query, Key, Value Projections**: Linear transformations that project the input embeddings into query, key, and value representations.
2. **Multiway Wrapper Support**: All projection layers are wrapped with `MultiwayWrapper` for multi-modal model support.
3. **SubLN Support**: Optional inner attention layer normalization for better training stability.
4. **XPOS Integration**: Optional extrapolatable positional embeddings.
5. **Flash Attention**: Optional high-performance attention implementation for faster training and inference.

The attention computation can follow either the standard attention algorithm or use the optimized flash attention implementation when available:

```mermaid
flowchart TD
    Input["Input Tensors\n(query, key, value)"] --> Projections["Apply Q, K, V\nProjections"]
    Projections --> AttentionType{"Flash Attention\nAvailable?"}
    
    AttentionType -->|"Yes"| FlashAttn["Use Flash Attention\nImplementation"]
    AttentionType -->|"No"| StandardAttn["Standard Attention\nComputation"]
    
    StandardAttn --> Scale["Scale Query"]
    Scale --> MatMul["Q·K^T"]
    MatMul --> Mask["Apply Attention Masks"]
    Mask --> RelPos["Add Relative Position\nBias (if used)"]
    RelPos --> Softmax["Softmax"]
    Softmax --> Dropout["Apply Dropout"]
    Dropout --> WeightedSum["Weighted Sum with Values"]
    
    FlashAttn --> OptimizedComp["Optimized Attention\nComputation"]
    
    WeightedSum --> Merge["Reshape and Merge\nAttention Heads"]
    OptimizedComp --> Merge
    
    Merge --> OutProj["Output Projection"]
    OutProj --> Output["Output Tensor"]
```

Sources: [torchscale/component/multihead_attention.py:20-171]()

## FeedForwardNetwork

The `FeedForwardNetwork` module implements the position-wise feed-forward networks used in transformer models. This component transforms each position's representation independently using two linear transformations with an activation function in between.

```mermaid
classDiagram
    class FeedForwardNetwork {
        +embed_dim: int
        +activation_fn: function
        +activation_dropout_module: Dropout
        +dropout_module: Dropout
        +fc1: Linear
        +fc2: Linear
        +ffn_layernorm: LayerNorm
        +forward(x)
        +reset_parameters()
    }
```

Key features of the `FeedForwardNetwork` implementation:

1. **Configurable Activation**: Supports multiple activation functions including ReLU, GELU, and SwiGLU.
2. **SubLN Support**: Optional layer normalization between the two linear transformations.
3. **Dropout**: Applied after both the activation function and the second linear transformation.

The feed-forward computation flow is:

```mermaid
flowchart LR
    Input["Input\nTensor"] --> FC1["First Linear\nTransformation"]
    FC1 --> Activation["Activation\nFunction"]
    Activation --> ActDropout["Activation\nDropout"]
    ActDropout --> Conditional{"SubLN\nEnabled?"}
    Conditional -->|"Yes"| LN["Layer\nNormalization"]
    Conditional -->|"No"| FC2["Second Linear\nTransformation"]
    LN --> FC2
    FC2 --> Dropout["Output\nDropout"]
    Dropout --> Output["Output\nTensor"]
```

Sources: [torchscale/component/feedforward_network.py:105-142]()

## Mixture of Experts (MoE)

TorchScale implements the X-MoE (Mixture of Experts) system, which allows for efficient scaling of transformer models by conditionally routing tokens to different expert networks. This approach enhances model capacity without significantly increasing computation for each token.

```mermaid
classDiagram
    class MOELayer {
        +gate: Module
        +experts: ModuleList
        +expert_group: ProcessGroup
        +all2all_group: ProcessGroup
        +world_size: int
        +all2all_size: int
        +num_local_experts: int
        +forward(input, input_padding_mask)
        +prepare_for_inference_()
        +all_to_all_wrapper(input)
        +record_all_to_all_stats()
    }
```

The MoE mechanism works as follows:

```mermaid
flowchart TD
    Input["Input Tokens"] --> Gate["Token Routing Gate"]
    Gate --> TokenDispatching["Token Dispatching\nto Experts"]
    
    subgraph "Distributed Experts"
        Expert1["Expert 1\n(FeedForwardNetwork)"]
        Expert2["Expert 2\n(FeedForwardNetwork)"]
        ExpertN["Expert N\n(FeedForwardNetwork)"]
    end
    
    TokenDispatching --> AllToAll["All-to-All\nCommunication"]
    AllToAll --> Expert1
    AllToAll --> Expert2
    AllToAll --> ExpertN
    
    Expert1 --> Collect["Collect Expert\nOutputs"]
    Expert2 --> Collect
    ExpertN --> Collect
    
    Collect --> AllToAll2["All-to-All\nCommunication"]
    AllToAll2 --> Combine["Combine Expert\nOutputs"]
    Combine --> Output["Output Tokens"]
```

Key features of the X-MoE implementation:

1. **Token Routing**: Uses a gating mechanism to determine which expert should process each token.
2. **Load Balancing**: Ensures that experts receive a balanced number of tokens.
3. **Distributed Processing**: Supports distributed training with experts distributed across multiple GPUs.
4. **Performance Optimizations**: Includes optional Tutel MoE optimizations for improved efficiency.

Sources: [torchscale/component/xmoe/moe_layer.py:68-308](), [torchscale/component/feedforward_network.py:43-91]()

## Positional Embeddings

TorchScale supports several types of positional embeddings, with a particular focus on extrapolatable position embeddings (XPOS) and relative position bias for improved handling of sequences of varying lengths.

### XPOS (Extrapolatable Position Embeddings)

XPOS is designed to help models generalize to longer sequences than seen during training:

```mermaid
classDiagram
    class XPOS {
        +head_dim: int
        +scale_base: int
        +scale: Buffer
        +forward(x, offset, downscale)
    }
```

The XPOS mechanism applies a rotary position encoding with a carefully designed scaling scheme:

```mermaid
flowchart LR
    Input["Input\nTensor"] --> CalculateScale["Calculate Position\nScaling Factors"]
    CalculateScale --> GenerateSinCos["Generate Sin/Cos\nBase Embeddings"]
    GenerateSinCos --> ApplyScaling["Apply Position-Dependent\nScaling"]
    ApplyScaling --> RotateVectors["Apply Rotary\nTransformation"]
    RotateVectors --> Output["Positionally-Encoded\nTensor"]
```

Sources: [torchscale/component/xpos_relative_position.py:38-66]()

## Flash Attention

Flash Attention is an optimization technique that significantly speeds up the attention computation by reducing memory I/O operations. TorchScale integrates Flash Attention as an optional component that can be enabled for models running on compatible hardware.

```mermaid
flowchart LR
    Query["Query\nTensor"] --> FlashAttn["flash_attn_func()"]
    Key["Key\nTensor"] --> FlashAttn
    Value["Value\nTensor"] --> FlashAttn
    
    FlashAttn --> Output["Attention\nOutput"]
    FlashAttn --> LSE["Log-Sum-Exp\n(for gradients)"]
```

Key benefits of Flash Attention:

1. **Memory Efficiency**: Reduces memory usage during attention computation
2. **Computation Speed**: Faster attention computation, especially for longer sequences
3. **Scalability**: Enables handling of longer sequences without quadratic memory growth

Flash Attention is particularly important for models like LongNet, which are designed to process extremely long sequences.

Sources: [torchscale/component/multihead_attention.py:97-105](), [README.md:43-44]()

## Multiway Network

The Multiway architecture is designed for multi-modal models, allowing different sets of parameters to be used for processing different modalities within the same model architecture.

```mermaid
flowchart TD
    Input["Input\n(from different modalities)"] --> MultiwayWrapper["MultiwayWrapper"]
    
    subgraph "Parameter Sets"
        TextParams["Text Parameters"]
        ImageParams["Image Parameters"]
        AudioParams["Audio Parameters"]
    end
    
    MultiwayWrapper --> ModalityDetection["Modality Detection"]
    ModalityDetection --> TextParams
    ModalityDetection --> ImageParams
    ModalityDetection --> AudioParams
    
    TextParams --> Output["Processed Output"]
    ImageParams --> Output
    AudioParams --> Output
```

The Multiway feature wraps standard modules like Linear layers and LayerNorm, allowing them to use different parameters depending on which modality is being processed. This creates a more flexible architecture that can handle diverse input types while maintaining shared knowledge across modalities.

Sources: [torchscale/component/multihead_attention.py:43-52](), [README.md:131-132]()

## Component Integration

These core components are assembled to build the various model architectures in TorchScale. Here's how they typically integrate in a transformer layer:

```mermaid
flowchart TD
    Input["Layer Input"] --> Choice{"Layer Type"}
    
    Choice -->|"Standard Layer"| Attention["MultiheadAttention"]
    Choice -->|"MoE Layer"| Attention2["MultiheadAttention"]
    
    Attention --> ResidualA["Residual Connection\n+ LayerNorm"]
    Attention2 --> ResidualA2["Residual Connection\n+ LayerNorm"]
    
    ResidualA --> FFN["FeedForwardNetwork"]
    ResidualA2 --> MOE["MoE Layer"]
    
    FFN --> ResidualF["Residual Connection\n+ LayerNorm"]
    MOE --> ResidualM["Residual Connection\n+ LayerNorm"]
    
    ResidualF --> Output["Layer Output"]
    ResidualM --> Output
```

Different architectures (Encoder, Decoder, RetNet, LongNet) use these components in different configurations, but the core building blocks remain the same across all model types.

Sources: [README.md:54-63](), [README.md:87-100]()

---

