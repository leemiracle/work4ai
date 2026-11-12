<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/apex_plus · page 6 Model Support · fetched 2026-10-26 -->

# Model Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apex_plus/models/bloom.py](apex_plus/models/bloom.py)
- [apex_plus/models/gpt2.py](apex_plus/models/gpt2.py)
- [apex_plus/models/llama.py](apex_plus/models/llama.py)
- [apex_plus/models/llama3.py](apex_plus/models/llama3.py)

</details>



This document covers APEX+'s support for large language models and the conversion process from external model configurations to the APEX+ intermediate representation (IR). It explains the model abstraction layer, supported model architectures, and how Hugging Face configurations are transformed into executable IR components.

For detailed information about the IR components that models are converted to, see [IR Components Reference](#5). For information about how the generated IR is used in execution planning, see [Execution Planning](#3.3).

## Model Conversion Architecture

APEX+ provides a unified interface for converting various language model architectures into its intermediate representation. The conversion process follows a standardized pattern where external model configurations are first loaded into APEX+ model objects, then converted to IR components.

### Model Conversion Pipeline

```mermaid
graph LR
    subgraph "External Configs"
        HFConfig["Hugging Face Config<br/>GPT2Config, LlamaConfig, BloomConfig"]
        JSONConfig["JSON Config Files<br/>Custom configurations"]
    end
    
    subgraph "APEX+ Models"
        GPT2Model["GPT2<br/>ApexModel"]
        BloomModel["Bloom<br/>ApexModel"] 
        LLaMAModel["LLaMA<br/>ApexModel"]
        LLaMA3Model["LLaMA3<br/>ApexModel"]
    end
    
    subgraph "IR Components"
        TransformerIR["Transformer<br/>IR"]
        BlockIR["Block<br/>Container"]
        CellIR["Cells<br/>MHA, MQA, MLP, GLU, SwiGLU"]
    end
    
    HFConfig --> GPT2Model
    HFConfig --> BloomModel
    HFConfig --> LLaMAModel  
    HFConfig --> LLaMA3Model
    JSONConfig --> LLaMAModel
    JSONConfig --> LLaMA3Model
    
    GPT2Model --> TransformerIR
    BloomModel --> TransformerIR
    LLaMAModel --> TransformerIR
    LLaMA3Model --> TransformerIR
    
    TransformerIR --> BlockIR
    BlockIR --> CellIR
```

**Sources:** [apex_plus/models/gpt2.py:1-66](), [apex_plus/models/bloom.py:1-66](), [apex_plus/models/llama.py:1-64](), [apex_plus/models/llama3.py:1-70]()

### Model Interface Pattern

All APEX+ models implement a consistent interface through the `ApexModel` base class:

```mermaid
graph TB
    subgraph "ApexModel Interface"
        ApexModel["ApexModel<br/>Base Class"]
        FromHF["from_hf(config)<br/>@classmethod"]
        ToIR["to_ir()<br/>→ Transformer"]
    end
    
    subgraph "Model Implementations"
        GPT2["GPT2"]
        Bloom["Bloom"] 
        LLaMA["LLaMA"]
        LLaMA3["LLaMA3"]
    end
    
    ApexModel --> GPT2
    ApexModel --> Bloom
    ApexModel --> LLaMA
    ApexModel --> LLaMA3
    
    FromHF --> GPT2
    FromHF --> Bloom
    FromHF --> LLaMA
    FromHF --> LLaMA3
    
    ToIR --> GPT2
    ToIR --> Bloom
    ToIR --> LLaMA
    ToIR --> LLaMA3
```

**Sources:** [apex_plus/models/gpt2.py:7](), [apex_plus/models/bloom.py:9](), [apex_plus/models/llama.py:7](), [apex_plus/models/llama3.py:7]()

## Supported Model Architectures

APEX+ supports several major language model architectures, each with distinct computational patterns and IR mappings.

### Architecture to IR Component Mapping

| Model Family | Attention Mechanism | Feed-Forward | IR Components Used |
|--------------|-------------------|--------------|-------------------|
| GPT-2 | Multi-Head Attention | Standard MLP | `MHA` + `MLP` |
| Bloom | Multi-Head Attention | Standard MLP | `MHA` + `MLP` |
| LLaMA | Multi-Head Attention | Gated Linear Unit | `MHA` + `GLU` |
| LLaMA3 | Multi-Query Attention | SwiGLU | `MQA` + `SwiGLU` |

**Sources:** [apex_plus/models/gpt2.py:44-46](), [apex_plus/models/bloom.py:46-47](), [apex_plus/models/llama.py:44-45](), [apex_plus/models/llama3.py:49-50]()

### Model Parameter Processing

Each model processes standard transformer parameters with architecture-specific variations:

```mermaid
graph TD
    subgraph "Common Parameters"
        VocabSize["vocab_size<br/>Vocabulary size"]
        NumLayers["num_layers<br/>Number of transformer blocks"]
        NumHeads["num_heads<br/>Attention heads"]
        HiddenSize["hidden_size<br/>Model dimension"]
        IntermediateSize["intermediate_size<br/>FFN dimension"]
    end
    
    subgraph "LLaMA3 Specific"
        NumKVHeads["num_kv_heads<br/>Key-value heads for MQA"]
    end
    
    subgraph "Validation"
        HeadSizeCheck["hidden_size % num_heads == 0<br/>Head size validation"]
    end
    
    VocabSize --> HeadSizeCheck
    NumHeads --> HeadSizeCheck
    HiddenSize --> HeadSizeCheck
    NumKVHeads --> HeadSizeCheck
```

**Sources:** [apex_plus/models/gpt2.py:26-31](), [apex_plus/models/bloom.py:28-33](), [apex_plus/models/llama.py:26-31](), [apex_plus/models/llama3.py:28-33]()

## Configuration Processing

### Hugging Face Integration

APEX+ models integrate with Hugging Face transformers library through the `from_hf()` classmethod pattern:

```mermaid
graph LR
    subgraph "Hugging Face Configs"
        GPT2Config["GPT2Config"]
        BloomConfig["BloomConfig"] 
        LlamaConfig["LlamaConfig"]
    end
    
    subgraph "Parameter Mapping"
        VocabMapping["vocab_size"]
        LayerMapping["num_hidden_layers → num_layers"]
        HeadMapping["num_attention_heads → num_heads"]
        HiddenMapping["hidden_size"]
        IntermediateMapping["intermediate_size"]
        KVHeadMapping["num_key_value_heads → num_kv_heads"]
    end
    
    subgraph "APEX+ Models"
        GPT2Instance["GPT2()"]
        BloomInstance["Bloom()"]
        LLaMAInstance["LLaMA()"] 
        LLaMA3Instance["LLaMA3()"]
    end
    
    GPT2Config --> VocabMapping
    GPT2Config --> LayerMapping
    GPT2Config --> HeadMapping
    GPT2Config --> HiddenMapping
    
    BloomConfig --> VocabMapping
    BloomConfig --> LayerMapping
    BloomConfig --> HeadMapping
    BloomConfig --> HiddenMapping
    
    LlamaConfig --> VocabMapping
    LlamaConfig --> LayerMapping
    LlamaConfig --> HeadMapping
    LlamaConfig --> HiddenMapping
    LlamaConfig --> IntermediateMapping
    LlamaConfig --> KVHeadMapping
    
    VocabMapping --> GPT2Instance
    LayerMapping --> GPT2Instance
    HeadMapping --> GPT2Instance
    HiddenMapping --> GPT2Instance
    
    VocabMapping --> BloomInstance
    LayerMapping --> BloomInstance
    HeadMapping --> BloomInstance
    HiddenMapping --> BloomInstance
    
    VocabMapping --> LLaMAInstance
    LayerMapping --> LLaMAInstance
    HeadMapping --> LLaMAInstance
    HiddenMapping --> LLaMAInstance
    IntermediateMapping --> LLaMAInstance
    
    VocabMapping --> LLaMA3Instance
    LayerMapping --> LLaMA3Instance
    HeadMapping --> LLaMA3Instance
    HiddenMapping --> LLaMA3Instance
    IntermediateMapping --> LLaMA3Instance
    KVHeadMapping --> LLaMA3Instance
```

**Sources:** [apex_plus/models/gpt2.py:34-41](), [apex_plus/models/bloom.py:36-43](), [apex_plus/models/llama.py:34-41](), [apex_plus/models/llama3.py:36-44]()

### Architecture-Specific Configuration Handling

Different model families handle intermediate size calculation differently:

- **GPT-2 and Bloom**: Calculate `intermediate_size` as `4 * hidden_size` [apex_plus/models/gpt2.py:40](), [apex_plus/models/bloom.py:42]()
- **LLaMA and LLaMA3**: Use `intermediate_size` directly from config [apex_plus/models/llama.py:40](), [apex_plus/models/llama3.py:43]()

## IR Generation Process

### Block Construction Pattern

All supported models follow a consistent pattern for generating IR blocks:

```mermaid
graph TD
    subgraph "IR Generation Flow"
        ModelParams["Model Parameters<br/>num_heads, hidden_size, etc."]
        AttentionCell["Attention Cell<br/>MHA, MQA"]
        FFNCell["FFN Cell<br/>MLP, GLU, SwiGLU"]
        Block["Block([attention_cell, ffn_cell])"]
        Transformer["Transformer.from_blocks()"]
    end
    
    ModelParams --> AttentionCell
    ModelParams --> FFNCell
    AttentionCell --> Block
    FFNCell --> Block
    Block --> Transformer
    
    subgraph "Model-Specific Variations"
        GPT2Cells["GPT2: MHA + MLP"]
        BloomCells["Bloom: MHA + MLP"]
        LLaMACells["LLaMA: MHA + GLU"] 
        LLaMA3Cells["LLaMA3: MQA + SwiGLU"]
    end
    
    GPT2Cells --> Block
    BloomCells --> Block
    LLaMACells --> Block
    LLaMA3Cells --> Block
```

**Sources:** [apex_plus/models/gpt2.py:43-54](), [apex_plus/models/bloom.py:45-56](), [apex_plus/models/llama.py:43-54](), [apex_plus/models/llama3.py:46-59]()

### Transformer IR Construction

All models use the same `Transformer.from_blocks()` factory method with decoder-only configuration:

| Parameter | Value |
|-----------|-------|
| `vocab_size` | From model config |
| `hidden_size` | From model config |
| `num_encoder_blocks` | `0` (decoder-only) |
| `encoder_block` | `None` (decoder-only) |
| `num_decoder_blocks` | `num_layers` from config |
| `decoder_block` | Generated block with model-specific cells |

**Sources:** [apex_plus/models/gpt2.py:47-54](), [apex_plus/models/bloom.py:49-56](), [apex_plus/models/llama.py:47-54](), [apex_plus/models/llama3.py:52-59]()

### Cell-Level Architecture Differences

The key architectural differences between models are captured at the cell level:

```mermaid
graph TB
    subgraph "Attention Architectures"
        MHA["MHA<br/>Multi-Head Attention<br/>Used by: GPT-2, Bloom, LLaMA"]
        MQA["MQA<br/>Multi-Query Attention<br/>Used by: LLaMA3"]
    end
    
    subgraph "Feed-Forward Architectures"
        MLP["MLP<br/>Standard MLP<br/>Used by: GPT-2, Bloom"]
        GLU["GLU<br/>Gated Linear Unit<br/>Used by: LLaMA"]
        SwiGLU["SwiGLU<br/>Swish GLU<br/>Used by: LLaMA3"]
    end
    
    subgraph "Block Combinations"
        GPT2Block["GPT-2/Bloom Block<br/>MHA + MLP"]
        LLaMABlock["LLaMA Block<br/>MHA + GLU"]
        LLaMA3Block["LLaMA3 Block<br/>MQA + SwiGLU"]
    end
    
    MHA --> GPT2Block
    MLP --> GPT2Block
    
    MHA --> LLaMABlock
    GLU --> LLaMABlock
    
    MQA --> LLaMA3Block
    SwiGLU --> LLaMA3Block
```

**Sources:** [apex_plus/models/gpt2.py:44-46](), [apex_plus/models/bloom.py:46-47](), [apex_plus/models/llama.py:44-45](), [apex_plus/models/llama3.py:49-50]()

---

