<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/torchscale · page 2 Architecture Overview · fetched 2026-10-26 -->

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [torchscale/architecture/decoder.py](torchscale/architecture/decoder.py)
- [torchscale/architecture/encoder.py](torchscale/architecture/encoder.py)
- [torchscale/architecture/retnet.py](torchscale/architecture/retnet.py)
- [torchscale/component/multiscale_retention.py](torchscale/component/multiscale_retention.py)
- [torchscale/component/xpos_relative_position.py](torchscale/component/xpos_relative_position.py)

</details>



This page provides a high-level overview of the different architecture implementations available in TorchScale. We'll examine the core model architectures, how they relate to each other, and their key characteristics. For specific implementation details of individual architectures, see the dedicated pages for [Encoder Architecture](#2.1), [Decoder Architecture](#2.2), [RetNet Architecture](#2.3), and [LongNet Architecture](#2.4).

## Core Architecture Overview

TorchScale provides several foundational architectures that can be used as building blocks for various natural language processing and multimodal tasks:

1. **Encoder** - A bidirectional transformer encoder architecture (BERT-like)
2. **Decoder** - An autoregressive transformer decoder architecture (GPT-like)
3. **EncoderDecoder** - A combined encoder-decoder architecture (T5-like)
4. **RetNet** - A retention-based alternative to transformers
5. **LongNet** - A transformer variant for extremely long sequences

These architectures share common components while introducing specialized innovations for specific use cases.

```mermaid
graph TD
    subgraph "TorchScale Architecture Overview"
        A["TorchScale Models"] --> B["Encoder"]
        A --> C["Decoder"]
        A --> D["EncoderDecoder"]
        A --> E["RetNet"]
        A --> F["LongNet"]
        
        subgraph "Core Components"
            G["MultiheadAttention"]
            H["FeedForwardNetwork"]
            I["Mixture of Experts (MoE)"]
            J["MultiScaleRetention"]
            K["Positional Embeddings"]
            L["Layer Normalization"]
        end
        
        B --> G
        B --> H
        B --> I
        B --> K
        B --> L
        
        C --> G
        C --> H
        C --> I
        C --> K
        C --> L
        
        D --> B
        D --> C
        
        E --> J
        E --> H
        E --> I
        E --> L
        
        F --> G
        F --> H
        F --> I
        F --> K
        F --> L
    end
```

Sources: [README.md:56-85](), [torchscale/architecture/encoder.py:165-400](), [torchscale/architecture/decoder.py:210-482](), [torchscale/architecture/retnet.py:199-392]()

## Model Architecture Variations

TorchScale supports multiple variations of each architecture through a flexible configuration system, providing options for different model sizes, normalization techniques, and architectural enhancements.

```mermaid
graph TD
    subgraph "Architecture Variants"
        A["Base Transformer"] --> B["DeepNorm Transformer"]
        A --> C["SubLN Transformer"]
        A --> D["X-MoE Transformer"]
        A --> E["Multiway Transformer"]
        
        F["RetNet"] --> F1["Parallel Mode"]
        F --> F2["Recurrent Mode"]
        F --> F3["Chunkwise Mode"]
        
        G["LongNet"] --> G1["Dilated Attention"]
        
        A -.-> F
        A -.-> G
    end
```

Sources: [README.md:115-147](), [torchscale/architecture/retnet.py:166-196]()

### Key Architecture Features

| Feature | Description | Enabled By |
|---------|-------------|------------|
| DeepNorm | Improves training stability of Post-LayerNorm Transformers | `deepnorm=True` |
| SubLN | Introduces another LayerNorm to each sublayer for stability and generality | `subln=True` (default) |
| X-MoE | Replaces FFN with Mixture of Experts for efficiency and scalability | `use_xmoe=True` |
| Multiway | Provides a pool of parameters for different modalities | `multiway=True` |
| XPOS | Extrapolatable position embedding | `xpos_rel_pos=True` |
| Relative Position Bias | Alternative positional encoding | Adjusting `rel_pos_buckets` and `max_rel_pos` |

Sources: [README.md:115-147]()

## Encoder Architecture

The Encoder architecture implements a bidirectional transformer encoder that processes all inputs simultaneously. It consists of multiple EncoderLayer instances stacked together.

```mermaid
graph TD
    Input["Input Tokens"] --> Embed["Token Embedding"]
    Embed --> PosEmbed["Positional Embedding"]
    PosEmbed --> LNEmbed["LayerNorm Embedding (optional)"]
    LNEmbed --> Dropout["Dropout"]
    
    Dropout --> EncoderStack["Encoder Layer Stack"]
    
    subgraph "EncoderLayer"
        SA["Self-Attention"] --> SALN["Layer Norm"]
        SALN --> FFN["FeedForward Network/MoE"]
        FFN --> FFNLN["Layer Norm"]
    end
    
    EncoderStack --> FinalLN["Final Layer Norm (optional)"]
    FinalLN --> Output["Output Representations"]
```

The encoder architecture is defined in [torchscale/architecture/encoder.py:165-400](), with the core layer implementation in [torchscale/architecture/encoder.py:25-162]().

Sources: [torchscale/architecture/encoder.py:165-400]()

## Decoder Architecture

The Decoder architecture implements an autoregressive transformer decoder that processes inputs sequentially. It consists of multiple DecoderLayer instances stacked together.

```mermaid
graph TD
    Input["Input Tokens"] --> Embed["Token Embedding"]
    Embed --> PosEmbed["Positional Embedding"]
    PosEmbed --> LNEmbed["LayerNorm Embedding (optional)"]
    LNEmbed --> Dropout["Dropout"]
    
    Dropout --> DecoderStack["Decoder Layer Stack"]
    
    subgraph "DecoderLayer"
        SA["Self-Attention"] --> SALN["Self Attention Layer Norm"]
        SALN --> CA["Cross-Attention (if encoder-decoder)"]
        CA --> CALN["Cross Attention Layer Norm"]
        CALN --> FFN["FeedForward Network/MoE"]
        FFN --> FFNLN["Final Layer Norm"]
    end
    
    DecoderStack --> FinalLN["Final Layer Norm (optional)"]
    FinalLN --> Output["Output Predictions"]
```

The decoder architecture is defined in [torchscale/architecture/decoder.py:210-482](), with the core layer implementation in [torchscale/architecture/decoder.py:23-208]().

Sources: [torchscale/architecture/decoder.py:210-482]()

## RetNet Architecture

RetNet (Retention Network) is a novel architecture proposed as a successor to Transformers for large language models. It replaces the attention mechanism with a Multi-Scale Retention mechanism.

```mermaid
graph TD
    Input["Input Tokens"] --> Embed["Token Embedding"]
    Embed --> LNEmbed["LayerNorm Embedding (optional)"]
    LNEmbed --> Dropout["Dropout"]
    
    Dropout --> RetNetStack["RetNet Layer Stack"]
    
    subgraph "RetNetLayer"
        RetPos["RetNetRelPos"] --> MSR["MultiScaleRetention"]
        MSR --> MSRLN["RMSNorm"]
        MSRLN --> FFN["FeedForward Network/MoE"]
        FFN --> FFNLN["RMSNorm"]
    end
    
    RetNetStack --> FinalLN["Final Layer Norm (optional)"]
    FinalLN --> Output["Output Predictions"]
    
    subgraph "MultiScaleRetention"
        Q["Q Projection"] --> QR["Rotated Q"]
        K["K Projection"] --> KR["Rotated K"]
        V["V Projection"]
        G["Gate Projection"]
        
        QR --> Mode["Processing Mode"]
        KR --> Mode
        V --> Mode
        
        Mode --> P["Parallel Forward"]
        Mode --> R["Recurrent Forward"]
        Mode --> C["Chunk Recurrent Forward"]
        
        P --> GN["Group Norm"]
        R --> GN
        C --> GN
        
        GN --> Gate["Gate Function"]
        G --> Gate
    end
```

RetNet's key innovation is the MultiScaleRetention mechanism, which offers three processing modes:

1. **Parallel Mode** - Similar to attention but with O(n²) complexity
2. **Recurrent Mode** - Linear complexity O(n) for inference
3. **Chunkwise Recurrent Mode** - Balances between parallel and recurrent

The RetNet architecture is defined in [torchscale/architecture/retnet.py:199-392](), with the MultiScaleRetention implementation in [torchscale/component/multiscale_retention.py:39-204]().

Sources: [torchscale/architecture/retnet.py:199-392](), [torchscale/component/multiscale_retention.py:39-204]()

## LongNet Architecture

LongNet is designed to process extremely long sequences (up to 1 billion tokens) through a dilated attention pattern that groups tokens into segments with different dilation ratios.

```mermaid
graph TD
    Input["Input Tokens"] --> Embed["Token Embedding"]
    Embed --> PosEmbed["Positional Embedding"]
    PosEmbed --> LNEmbed["LayerNorm Embedding (optional)"]
    LNEmbed --> Dropout["Dropout"]
    
    Dropout --> LongNetStack["LongNet Layer Stack"]
    
    subgraph "LongNetLayer"
        subgraph "Dilated Attention"
            Segments["Token Segments"]
            Segments --> Seg1["Segment 1 (Length=2048, Ratio=1)"]
            Segments --> Seg2["Segment 2 (Length=4096, Ratio=2)"]
            Seg1 --> DilAttn["Dilated Self-Attention"]
            Seg2 --> DilAttn
            DilAttn --> FlashAttn["Flash Attention"]
        end
        
        FlashAttn --> SALN["Layer Norm"]
        SALN --> FFN["FeedForward Network/MoE"]
        FFN --> FFNLN["Layer Norm"]
    end
    
    LongNetStack --> FinalLN["Final Layer Norm (optional)"]
    FinalLN --> Output["Output Representations/Predictions"]
```

LongNet's key features:
- Segmented token representations with different dilation ratios
- Flash Attention for memory-efficient computation
- Support for sequences up to 1 billion tokens

LongNet's approach enables linear complexity relative to sequence length, making it suitable for extremely long context processing.

Sources: [README.md:102-114](), [README.md:144-148]()

## Data Flow Through Models

The following diagram illustrates how data flows through TorchScale models during forward passes:

```mermaid
flowchart TD
    Input["Input Data"] --> Config["Configuration"]
    Config --> ModelType{"Model Type"}
    
    ModelType -->|"Encoder"| Enc["Encoder Model"]
    ModelType -->|"Decoder"| Dec["Decoder Model"]
    ModelType -->|"EncoderDecoder"| EncDec["EncoderDecoder Model"]
    ModelType -->|"RetNet"| Ret["RetNet Model"]
    ModelType -->|"LongNet"| Long["LongNet Model"]
    
    Enc --> EncEmbed["Encoder Embedding"]
    EncEmbed --> EncLayers["Encoder Layers"]
    EncLayers --> EncOut["Encoder Output"]
    
    Dec --> DecEmbed["Decoder Embedding"]
    DecEmbed --> DecLayers["Decoder Layers"]
    DecLayers --> DecOut["Decoder Output"]
    
    EncDec --> EncEmbed2["Encoder Embedding"]
    EncDec --> DecEmbed2["Decoder Embedding"]
    EncEmbed2 --> EncLayers2["Encoder Layers"]
    EncLayers2 --> EncOut2["Encoder Output"]
    EncOut2 --> DecLayers2["Decoder Layers"]
    DecEmbed2 --> DecLayers2
    DecLayers2 --> EncDecOut["EncoderDecoder Output"]
    
    Ret --> RetEmbed["RetNet Embedding"]
    RetEmbed --> RetPos["RetNetRelPos"]
    RetPos --> RetLayers["RetNet Layers"]
    RetLayers --> RetOut["RetNet Output"]
    
    Long --> LongEmbed["LongNet Embedding"]
    LongEmbed --> DilAttn["Dilated Attention Layers"]
    DilAttn --> LongOut["LongNet Output"]
    
    subgraph "Layer Processing Pattern"
        LayerIn["Layer Input"] --> Norm1["Normalization"]
        Norm1 --> Attn["Attention/Retention"]
        Attn --> Drop1["Dropout"]
        Drop1 --> Add1["Residual Connection"]
        Add1 --> Norm2["Normalization"]
        Norm2 --> FFN["FFN/MoE"]
        FFN --> Drop2["Dropout"]
        Drop2 --> Add2["Residual Connection"]
        Add2 --> LayerOut["Layer Output"]
    end
```

Sources: [torchscale/architecture/encoder.py:327-399](), [torchscale/architecture/decoder.py:388-481](), [torchscale/architecture/retnet.py:328-391]()

## Extension and Configuration

TorchScale is designed to be easily configured and extended through its configuration system. Each architecture type has a corresponding configuration class that allows customization of model dimensions, number of layers, attention heads, and other architectural parameters.

```mermaid
graph TD
    subgraph "Configuration System"
        BaseConfig["Base Config Parameters"]
        BaseConfig --> EncoderConfig["EncoderConfig"]
        BaseConfig --> DecoderConfig["DecoderConfig"]
        BaseConfig --> EncoderDecoderConfig["EncoderDecoderConfig"]
        BaseConfig --> RetNetConfig["RetNetConfig"]
        
        subgraph "Common Parameters"
            VP1["vocab_size"]
            VP2["max_position_embeddings"]
            VP3["layernorm_eps"]
            VP4["dropout"]
            VP5["attention_dropout"]
            VP6["activation_fn"]
        end
        
        subgraph "Architecture Flags"
            AF1["deepnorm"]
            AF2["subln"]
            AF3["use_xmoe"]
            AF4["multiway"]
            AF5["xpos_rel_pos"]
            AF6["flash_attention"]
        end
    end
```

The configuration system provides a unified interface for creating and customizing different architectures, allowing users to easily experiment with architectural variations.

Sources: [README.md:52-159]()

## Component Relationships

The following diagram illustrates how various components in TorchScale interact with each other:

```mermaid
classDiagram
    class Encoder {
        +embed_tokens
        +embed_positions
        +layernorm_embedding
        +layers[]
        +layer_norm
        +relative_position
        +forward()
    }
    
    class Decoder {
        +embed_tokens
        +embed_positions
        +layernorm_embedding
        +layers[]
        +layer_norm
        +self_attn_relative_position
        +cross_attn_relative_position
        +forward()
    }
    
    class RetNetDecoder {
        +embed_tokens
        +layernorm_embedding
        +layers[]
        +layer_norm
        +retnet_rel_pos
        +forward()
    }
    
    class EncoderLayer {
        +self_attn
        +self_attn_layer_norm
        +ffn/moe_layer
        +final_layer_norm
        +forward()
    }
    
    class DecoderLayer {
        +self_attn
        +self_attn_layer_norm
        +encoder_attn
        +encoder_attn_layer_norm
        +ffn/moe_layer
        +final_layer_norm
        +forward()
    }
    
    class RetNetLayer {
        +retention
        +retention_layer_norm
        +ffn/moe_layer
        +final_layer_norm
        +forward()
    }
    
    class MultiheadAttention {
        +q_proj
        +k_proj
        +v_proj
        +out_proj
        +forward()
    }
    
    class MultiScaleRetention {
        +q_proj
        +k_proj
        +v_proj
        +g_proj
        +out_proj
        +parallel_forward()
        +recurrent_forward()
        +chunk_recurrent_forward()
        +forward()
    }
    
    class FeedForwardNetwork {
        +fc1
        +fc2
        +forward()
    }
    
    class MOELayer {
        +gate
        +experts[]
        +forward()
    }
    
    Encoder --> EncoderLayer
    Decoder --> DecoderLayer
    RetNetDecoder --> RetNetLayer
    
    EncoderLayer --> MultiheadAttention
    EncoderLayer --> FeedForwardNetwork
    EncoderLayer --> MOELayer
    
    DecoderLayer --> MultiheadAttention
    DecoderLayer --> FeedForwardNetwork
    DecoderLayer --> MOELayer
    
    RetNetLayer --> MultiScaleRetention
    RetNetLayer --> FeedForwardNetwork
    RetNetLayer --> MOELayer
```

Sources: [torchscale/architecture/encoder.py:25-400](), [torchscale/architecture/decoder.py:23-482](), [torchscale/architecture/retnet.py:72-392](), [torchscale/component/multiscale_retention.py:39-204]()

## Conclusion

TorchScale provides a comprehensive set of architectures for transformer-based models, with a focus on scalability, efficiency, and innovation. The library includes traditional transformer architectures (Encoder, Decoder, EncoderDecoder) as well as cutting-edge designs like RetNet and LongNet for specialized use cases.

Each architecture is highly configurable through a unified configuration system, allowing researchers and practitioners to easily experiment with different model variations. The shared components across architectures ensure consistency while enabling specific optimizations for different use cases.

For more details on specific architectures, refer to:
- [Encoder Architecture](#2.1)
- [Decoder Architecture](#2.2)
- [RetNet Architecture](#2.3)
- [LongNet Architecture](#2.4)

---

