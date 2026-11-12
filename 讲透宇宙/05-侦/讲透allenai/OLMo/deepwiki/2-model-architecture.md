<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMo · page 2 Model Architecture · fetched 2026-10-26 -->

# Model Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [olmo/beam_search.py](olmo/beam_search.py)
- [olmo/checkpoint.py](olmo/checkpoint.py)
- [olmo/config.py](olmo/config.py)
- [olmo/initialization.py](olmo/initialization.py)
- [olmo/model.py](olmo/model.py)
- [olmo/optim.py](olmo/optim.py)
- [olmo/torch_util.py](olmo/torch_util.py)
- [olmo/train.py](olmo/train.py)
- [olmo/util.py](olmo/util.py)
- [scripts/train.py](scripts/train.py)
- [tests/config_test.py](tests/config_test.py)
- [tests/grad_norm_test.py](tests/grad_norm_test.py)
- [tests/initialization_test.py](tests/initialization_test.py)
- [tests/model_test.py](tests/model_test.py)
- [tests/optim_test.py](tests/optim_test.py)

</details>



This page documents the neural network architecture of OLMo (Open Language Model), a decoder-only transformer language model. It covers the core model components, their interactions, and the configurable aspects of the architecture. For information about training the model, see [Training Pipeline](#3).

## Overview

OLMo is a decoder-only transformer language model that builds on recent advances in transformer architecture design. It supports various architectural choices, including different block types, attention mechanisms, and activation functions. The model architecture is highly configurable, allowing for experimentation with different design choices.

```mermaid
flowchart TD
    subgraph "OLMo Model"
        InputIds["Input Token IDs"] --> Embeddings["Token Embeddings"]
        Embeddings --> EmbeddingLN["Embedding LayerNorm (optional)"]
        EmbeddingLN --> EmbeddingDropout["Embedding Dropout"]
        
        EmbeddingDropout --> Transformer["Transformer Blocks"]
        
        Transformer --> FinalLN["Final LayerNorm"]
        FinalLN --> OutputProjection["Output Projection (tied to embeddings by default)"]
        OutputProjection --> Logits["Output Logits"]
    end
```

Sources: [olmo/model.py:4740-4996](). The main `OLMo` class implementation contains the high-level architecture.

## Components in Detail

### Transformer Block Architecture

OLMo implements two main transformer block types:

1. **Sequential Block** (`OLMoSequentialBlock`): A standard transformer block with a sequence of attention and feed-forward layers.
2. **Llama Block** (`OLMoLlamaBlock`): A block similar to the Sequential Block but with implementation differences to match the behavior of Llama models.

```mermaid
flowchart TD
    subgraph "OLMoSequentialBlock"
        direction TB
        input1["Input"] --> |"1"| normA1["LayerNorm (if !norm_after)"]
        normA1 --> qkvProj1["QKV Projection"]
        qkvProj1 --> attention1["Multi-Head Attention"]
        attention1 --> attnProj1["Attention Out Projection"]
        attnProj1 --> |"2"| normA2["LayerNorm (if norm_after)"]
        normA2 --> add1["+ (Add Input)"]
        add1 --> |"3"| normB1["LayerNorm (if !norm_after)"]
        normB1 --> ffProj1["FF Projection"]
        ffProj1 --> activation1["Activation"]
        activation1 --> ffOut1["FF Out Projection"]
        ffOut1 --> |"4"| normB2["LayerNorm (if norm_after)"]
        normB2 --> add2["+ (Add Intermediate)"]
        add2 --> output1["Output"]
    end

    subgraph "OLMoLlamaBlock"
        direction TB
        input2["Input"] --> |"1"| normA3["LayerNorm"]
        normA3 --> separate["Separate Q,K,V Projections"]
        separate --> attention2["Multi-Head Attention"]
        attention2 --> attnProj2["Attention Out Projection"]
        attnProj2 --> add3["+ (Add Input)"]
        add3 --> |"3"| normB3["LayerNorm"]
        normB3 --> ffProj2["FF Projection"]
        ffProj2 --> activation2["Activation"]
        activation2 --> ffOut2["FF Out Projection"]
        ffOut2 --> add4["+ (Add Intermediate)"]
        add4 --> output2["Output"]
    end
```

Sources: 
- Sequential Block: [olmo/model.py:678-823]()
- Llama Block: [olmo/model.py:826-1058]()

### Attention Mechanism

OLMo supports several attention variations:

1. **Multi-Head Attention (MHA)**: Standard multi-head attention where number of key-value heads equals number of query heads.
2. **Multi-Query Attention (MQA)**: A variation where all query heads share a single key-value head.
3. **Grouped-Query Attention (GQA)**: A middle ground where groups of query heads share key-value heads.

The attention mechanism is implemented in the `attention` method of the `OLMoBlock` class:

```mermaid
flowchart TD
    subgraph "Attention Mechanism"
        direction TB
        qkv["Q, K, V"] --> |"Optional"| qkNorm["Q/K Layer Norm"]
        qkNorm --> reshape["Reshape for Heads"]
        reshape --> |"Optional"| pos["Positional Encoding (RoPE/ALiBi)"]
        pos --> sdpa["Scaled Dot-Product Attention"]
        sdpa --> |"If Flash Attention Available"| flashAtt["Flash Attention"]
        sdpa --> |"If not Flash Attention"| vanillaAtt["Regular Attention"]
        flashAtt --> combine["Combine Heads"]
        vanillaAtt --> combine
        combine --> proj["Output Projection"]
    end
```

Sources: [olmo/model.py:588-654]()

### Positional Encodings

OLMo supports two types of positional encodings:

1. **Rotary Position Embeddings (RoPE)**: Applies rotation to the keys and queries based on their positions.
2. **ALiBi**: Adds a bias to the attention scores based on the relative positions of tokens.

```mermaid
flowchart TD
    subgraph "Positional Encodings"
        direction TB
        subgraph "RoPE"
            qr["Query"] --> rotate["Apply Rotation"]
            kr["Key"] --> rotate
            rotate --> qkr["Encoded Q & K"]
        end
        
        subgraph "ALiBi"
            qa["Query"] --> attBias["Compute Attention Bias"]
            ka["Key"] --> attBias
            attBias --> addBias["Add Bias to Attention Scores"]
            addBias --> attScores["Biased Attention Scores"]
        end
    end
```

Sources: 
- RoPE: [olmo/model.py:258-306]()
- ALiBi: [olmo/model.py:396-408]()

### Feed-Forward Network

The feed-forward network consists of:
1. A projection to a higher dimension
2. An activation function
3. A projection back to the model dimension

OLMo supports several activation functions:
- GELU
- ReLU
- SwiGLU (Swish-Gated Linear Unit)

```mermaid
flowchart LR
    input["Input"] --> upProj["Up Projection"]
    upProj --> act["Activation (GELU/ReLU/SwiGLU)"]
    act --> downProj["Down Projection"]
    downProj --> output["Output"]
```

Sources:
- Activation functions: [olmo/model.py:327-372]()
- Implementation in blocks: [olmo/model.py:699-822]() for Sequential Block, [olmo/model.py:834-1057]() for Llama Block

## Layer Normalization Variants

OLMo implements multiple layer normalization variants:

1. **Default LayerNorm**: Standard implementation equivalent to PyTorch's built-in version
2. **Low Precision LayerNorm**: A variant optimized for lower precision computation
3. **RMSLayerNorm**: A simplified layer norm that only normalizes by the root mean square

```mermaid
flowchart TD
    subgraph "LayerNorm Variants"
        direction TB
        
        subgraph "Default LayerNorm"
            inputN1["Input"] --> meanVar1["Compute Mean & Variance"]
            meanVar1 --> norm1["Normalize"]
            norm1 --> scale1["Apply Scale & Bias"]
            scale1 --> outputN1["Output"]
        end
        
        subgraph "Low Precision LayerNorm"
            inputN2["Input"] --> cast["Cast to Low Precision"]
            cast --> meanVar2["Compute Mean & Variance"]
            meanVar2 --> norm2["Normalize"]
            norm2 --> scale2["Apply Scale & Bias"]
            scale2 --> outputN2["Output"]
        end
        
        subgraph "RMSLayerNorm"
            inputN3["Input"] --> var["Compute Variance"]
            var --> normRMS["Normalize by RMS"]
            normRMS --> scale3["Apply Scale & Bias"]
            scale3 --> outputN3["Output"]
        end
    end
```

Sources: [olmo/model.py:139-255]()

## OLMo Model

The main `OLMo` class ties all components together:

```mermaid
classDiagram
    class OLMo {
        +ModelConfig config
        +Embedding wte
        +ModuleList transformer.blocks
        +LayerNorm ln_f
        +Linear output_projection
        +forward(input_ids, attention_mask, layer_past, use_cache)
        +reset_parameters()
        +generate(prompt_ids, generation_config)
    }
    
    class OLMoBlock {
        <<abstract>>
        +attention(q, k, v)
        +forward(x, attention_bias, layer_past, use_cache)
    }
    
    class OLMoSequentialBlock {
        +Linear att_proj
        +Linear ff_proj
        +LayerNorm attn_norm
        +LayerNorm ff_norm
        +forward(x, attention_bias, layer_past, use_cache)
    }
    
    class OLMoLlamaBlock {
        +Linear q_proj
        +Linear k_proj
        +Linear v_proj
        +Linear ff_proj
        +LayerNorm attn_norm
        +LayerNorm ff_norm
        +forward(x, attention_bias, layer_past, use_cache)
    }
    
    OLMo *-- OLMoBlock : contains
    OLMoBlock <|-- OLMoSequentialBlock : extends
    OLMoBlock <|-- OLMoLlamaBlock : extends
```

Sources: [olmo/model.py:4740-6039]() for the `OLMo` class, [olmo/model.py:411-673]() for the `OLMoBlock` base class, [olmo/model.py:678-823]() for `OLMoSequentialBlock`, and [olmo/model.py:826-1058]() for `OLMoLlamaBlock`.

## Forward Pass

The forward pass through the OLMo model follows these steps:

```mermaid
sequenceDiagram
    participant Input as Input Token IDs
    participant Embed as Embedding Layer
    participant EmbedLN as Embedding LayerNorm
    participant EmbedDrop as Embedding Dropout
    participant Blocks as Transformer Blocks
    participant FinalLN as Final LayerNorm
    participant Output as Output Projection
    
    Input->>Embed: Token IDs to Embeddings
    
    alt embedding_layer_norm is True
        Embed->>EmbedLN: Apply LayerNorm
        EmbedLN->>EmbedDrop: Apply Dropout
    else
        Embed->>EmbedDrop: Apply Dropout
    end
    
    EmbedDrop->>Blocks: Process through Blocks
    
    loop For each Block
        Blocks->>Blocks: Self-attention & FFN
    end
    
    Blocks->>FinalLN: Apply Final LayerNorm
    FinalLN->>Output: Project to Logits
    
    alt scale_logits is True
        Output->>Output: Scale by 1/sqrt(d_model)
    end
```

Sources: [olmo/model.py:4898-4996]()

## Generation Capabilities

OLMo supports text generation with various strategies:

```mermaid
flowchart TD
    subgraph "Generation Methods"
        direction TB
        
        input["Input Context"] --> generate["OLMo.generate()"]
        
        generate --> strategies{"Strategy?"}
        strategies -->|"Greedy"| greedy["Select Maximum Probability Token"]
        strategies -->|"Sampling"| sampling["Sample from Distribution"]
        strategies -->|"Beam Search"| beam["Maintain Multiple Sequences"]
        
        greedy --> next["Append to Generated Text"]
        sampling --> next
        beam --> next
        
        next --> done{"Done?"}
        done -->|"No"| generate
        done -->|"Yes"| output["Final Generated Text"]
    end
```

Sources: [olmo/model.py:5001-5285]()

## Model Initialization

OLMo supports several initialization strategies:

1. **Normal**: All weights are initialized from a normal distribution with a fixed standard deviation.
2. **Mitchell**: Weights are initialized with an adaptive standard deviation that depends on the layer depth.
3. **Full Megatron**: The initialization strategy used in Megatron-LM and Llama 2.

```mermaid
flowchart TD
    subgraph "Initialization Strategies"
        direction TB
        
        init["Initialize Model"] --> strategy{"Strategy?"}
        
        strategy -->|"Normal"| normalInit["Normal(0, init_std)"]
        strategy -->|"Mitchell"| mitchellInit["Normal(0, 1/sqrt(2*d_in*(layer_id+1)))"]
        strategy -->|"Full Megatron"| megatronInit["Normal(0, init_std/sqrt(2*n_layers))"]
        
        normalInit --> truncate{"Apply Truncation?"}
        mitchellInit --> truncate
        megatronInit --> truncate
        
        truncate -->|"Yes"| cutoff["Truncate at ±init_cutoff_factor*std"]
        truncate -->|"No"| done["Initialization Complete"]
        cutoff --> done
    end
```

Sources: [olmo/model.py:482-506]() for transformer block initialization, [olmo/initialization.py:8-23]() for the `init_normal` function.

## Key Configuration Options

OLMo's architecture is highly configurable through the `ModelConfig` class. Here's a table of key architectural parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `d_model` | Hidden size of the model | 768 |
| `n_heads` | Number of attention heads | 12 |
| `n_kv_heads` | Number of key-value heads (for GQA/MQA) | Same as `n_heads` |
| `n_layers` | Number of transformer layers | 12 |
| `mlp_ratio` | Ratio of FFN hidden dim to model dim | 4 |
| `activation_type` | Activation function type | `swiglu` |
| `block_type` | Transformer block type | `sequential` |
| `rope` | Use rotary positional embeddings | `False` |
| `alibi` | Use ALiBi positional embeddings | `False` |
| `flash_attention` | Use Flash Attention if available | `False` |
| `attention_dropout` | Dropout rate in attention | 0.1 |
| `residual_dropout` | Dropout rate in residual connections | 0.1 |
| `embedding_dropout` | Dropout rate for embeddings | 0.1 |
| `layer_norm_type` | Type of layer normalization | `default` |
| `max_sequence_length` | Maximum input sequence length | 1024 |
| `vocab_size` | Size of the vocabulary | 50257 |
| `weight_tying` | Tie embedding and output weights | `True` |
| `init_fn` | Weight initialization strategy | `normal` |

Sources: [olmo/config.py:234-496]()

## Instantiating the Model

The OLMo model is typically instantiated in the training script:

```mermaid
flowchart TD
    config["Load ModelConfig"] --> model["OLMo(config)"]
    model --> checkpointing["Set Activation Checkpointing"]
    checkpointing --> distributed{"Distributed Strategy?"}
    
    distributed -->|"DDP"| ddp["Wrap with DistributedDataParallel"]
    distributed -->|"FSDP"| fsdp["Wrap with FullyShardedDataParallel"]
    distributed -->|"Single"| single["Use SingleAccelerator"]
    
    ddp --> train["Training Loop"]
    fsdp --> train
    single --> train
```

Sources: [scripts/train.py:139-226]()

## Differences Between Block Types

The main differences between the two block types are:

| Feature | OLMoSequentialBlock | OLMoLlamaBlock |
|---------|---------------------|----------------|
| Q,K,V Projection | Single fused projection | Separate projections |
| Layer Norm Position | Configurable (before or after) | Always before |
| Implementation Style | Standard transformer | Mimics Llama architecture |

Sources: [olmo/model.py:678-823]() for `OLMoSequentialBlock`, [olmo/model.py:826-1058]() for `OLMoLlamaBlock`

## Attention Implementation Details

The attention mechanism in OLMo supports various features:

1. **Flash Attention**: For efficient attention computation when available
2. **Attention Layer Norm**: Optional layer normalization for queries and keys
3. **Attention Bias**: Support for causal masking and ALiBi biases
4. **QKV Clipping**: Optional clipping of query, key, and value projections

```mermaid
flowchart TD
    subgraph "Attention Implementation"
        direction TB
        
        input["Input Hidden States"] --> qkvProj["Q,K,V Projections"]
        qkvProj --> |"Optional"| qkvClip["Clip QKV Values"]
        qkvClip --> |"Optional"| qkNorm["Layer Norm Q & K"]
        qkNorm --> reshape["Reshape for Multi-Head"]
        
        reshape --> |"If RoPE"| rope["Apply Rotary Embeddings"]
        rope --> sdpa["Scaled Dot-Product Attention"]
        
        reshape --> |"If not RoPE"| sdpa
        
        attMask["Attention Mask/Bias"] --> sdpa
        
        sdpa --> |"If using Flash Attention"| flash["Flash Attention"]
        sdpa --> |"If not using Flash Attention"| vanilla["Regular Attention"]
        
        flash --> combine["Combine Heads"]
        vanilla --> combine
        
        combine --> outProj["Output Projection"]
    end
```

Sources: [olmo/model.py:588-654]()

---

