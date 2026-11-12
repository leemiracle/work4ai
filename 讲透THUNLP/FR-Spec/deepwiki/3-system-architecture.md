<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/FR-Spec · page 3 System Architecture · fetched 2026-11-02 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [llamacu/llama.py](llamacu/llama.py)
- [src/entry.cu](src/entry.cu)
- [src/flash_attn/flash_api.hpp](src/flash_attn/flash_api.hpp)

</details>



## Purpose and Scope

This document describes the overall architecture of FR-Spec, explaining how the Python interface, PyBind11 bridge, and C++/CUDA backend work together to provide accelerated LLM inference with frequency-ranked speculative sampling. The architecture follows a three-tier design where high-level Python APIs invoke optimized CUDA kernels through a thin C++ bridge layer.

For detailed information about specific subsystems:
- Python-CUDA bridging mechanisms: see [Python to CUDA Bridge](#3.1)
- Memory allocation and KV cache management: see [Memory Management](#3.2)
- Base transformer implementation: see [ModelImpl: Base Transformer](#4.1)
- Speculative decoding details: see [Speculative Decoding](#5)

**Sources:** [README.md:1-140](), [src/entry.cu:1-184](), [llamacu/llama.py:1-198]()

---

## Three-Tier Architecture

FR-Spec implements a layered architecture that separates concerns between user-facing APIs, language interoperability, and high-performance computation:

```mermaid
graph TB
    subgraph Python["Python Layer (llamacu/)"]
        LLM["LLM class<br/>llamacu/llama.py"]
        LLM_Eagle["LLM_with_eagle"]
        LLM_Medusa["LLM_with_medusa"]
        Config["AutoConfig<br/>HuggingFace integration"]
        Tokenizer["AutoTokenizer"]
    end
    
    subgraph Bridge["PyBind11 Bridge (src/entry.cu)"]
        Module["C module<br/>PYBIND11_MODULE"]
        InitBase["init_base_model()"]
        InitEagle["init_eagle_model()"]
        InitMedusa["init_medusa_model()"]
        Prefill["prefill()"]
        Decode["decode()"]
        Draft["draft()"]
        Verify["verify_and_fix()"]
    end
    
    subgraph CUDA["C++/CUDA Backend (src/model/)"]
        ModelPtr["Model* model<br/>global pointer"]
        ModelImpl["ModelImpl<elem_type>"]
        EagleImpl["EagleImpl<elem_type>"]
        MedusaImpl["MedusaImpl<elem_type>"]
        Layer["Layer"]
        Attention["Attention"]
        FFN["GatedFFN"]
        Cache["KVCacheManager"]
    end
    
    subgraph Kernels["CUDA Kernels (src/)"]
        FlashAttn["mha_fwd_kvcache()<br/>flash_attn/"]
        ElemOps["batched_add<br/>RMSNorm"]
        TopK["bitonic_topk"]
        TreeBuild["build_dynamic_tree"]
    end
    
    LLM --> Module
    LLM_Eagle --> Module
    LLM_Medusa --> Module
    Config --> LLM
    Tokenizer --> LLM
    
    Module --> InitBase
    Module --> InitEagle
    Module --> InitMedusa
    Module --> Prefill
    Module --> Decode
    Module --> Draft
    Module --> Verify
    
    InitBase --> ModelPtr
    InitEagle --> ModelPtr
    InitMedusa --> ModelPtr
    
    ModelPtr --> ModelImpl
    ModelPtr --> EagleImpl
    ModelPtr --> MedusaImpl
    
    ModelImpl --> Layer
    EagleImpl --> ModelImpl
    MedusaImpl --> ModelImpl
    
    Layer --> Attention
    Layer --> FFN
    Attention --> Cache
    
    Attention --> FlashAttn
    FFN --> ElemOps
    EagleImpl --> TopK
    EagleImpl --> TreeBuild
```

**Diagram 1: Three-Tier Architecture and Component Hierarchy**

The architecture consists of:

1. **Python Layer**: Provides high-level APIs compatible with HuggingFace transformers
2. **PyBind11 Bridge**: Marshals data between Python and C++, manages type conversions
3. **C++/CUDA Backend**: Implements core inference logic with optimized CUDA kernels

**Sources:** [src/entry.cu:1-184](), [llamacu/llama.py:20-198]()

---

## Python Layer Components

The Python layer in `llamacu/` provides user-facing classes that integrate with the PyTorch and HuggingFace ecosystems:

### LLM Class

The `LLM` class [llamacu/llama.py:20-198]() serves as the base interface for model inference:

| Component | Type | Purpose |
|-----------|------|---------|
| `tokenizer` | `AutoTokenizer` | Converts text to token IDs |
| `config` | `AutoConfig` | Stores model hyperparameters |
| `memory_pool` | `torch.nn.Parameter` | Pre-allocated GPU memory buffer |
| `logits` | `torch.Tensor` | Output buffer for model predictions |
| `dtype` | `torch.dtype` | Computation precision (FP16/BF16) |

Key methods:
- `__init__()`: Initializes model configuration and calls `C.init_base_model()` [llamacu/llama.py:45-59]()
- `init_storage()`: Allocates memory pools via `C.init_storage()` [llamacu/llama.py:63-64]()
- `load_from_hf()`: Loads weights from HuggingFace checkpoint [llamacu/llama.py:125-138]()
- `prefill()`: Processes initial prompt [llamacu/llama.py:140-150]()
- `decode()`: Generates next tokens [llamacu/llama.py:152-172]()
- `generate()`: End-to-end text generation loop [llamacu/llama.py:174-197]()

### Memory Pool Initialization

The Python layer allocates a contiguous GPU memory buffer representing 80% of available GPU memory [llamacu/llama.py:37-38]():

```python
self.memory_limit = int(torch.cuda.get_device_properties(0).total_memory * memory_limit)
self.memory_pool = torch.nn.Parameter(torch.empty(self.memory_limit, dtype=torch.uint8, device="cuda"))
```

This pointer is passed to C++ for internal memory management (detailed in [Memory Management](#3.2)).

**Sources:** [llamacu/llama.py:20-198]()

---

## PyBind11 Bridge Interface

The file `src/entry.cu` defines the Python-C++ interface using PyBind11. It exposes a module named `C` that Python code imports [src/entry.cu:174-184]().

### Module Definition

```mermaid
graph LR
    Python["Python: import C"] --> Module["PYBIND11_MODULE(C, m)"]
    Module --> Funcs["Exposed Functions"]
    
    Funcs --> F1["init_base_model"]
    Funcs --> F2["init_medusa_model"]
    Funcs --> F3["init_eagle_model"]
    Funcs --> F4["init_storage"]
    Funcs --> F5["load_model"]
    Funcs --> F6["prefill"]
    Funcs --> F7["decode"]
    Funcs --> F8["draft"]
    Funcs --> F9["verify_and_fix"]
```

**Diagram 2: PyBind11 Module Interface**

### Global Model Pointer

A global pointer tracks the currently active model instance [src/entry.cu:32]():

```cpp
Model* model;
```

This pointer is polymorphic and can point to:
- `ModelImpl<elem_type, has_attention_bias>`: Base transformer
- `EagleImpl<elem_type, has_attention_bias>`: EAGLE speculative decoder (wraps ModelImpl)
- `MedusaImpl<elem_type, has_attention_bias>`: Medusa speculative decoder (wraps ModelImpl)

### Type-Generic Initialization

The bridge uses C++ template metaprogramming to support multiple data types and configurations:

```mermaid
graph TD
    InitCall["init_base_model(..., torch_dtype, attention_bias)"]
    InitCall --> BoolSwitch["BOOL_SWITCH(attention_bias)"]
    BoolSwitch --> DtypeSwitch["DTYPE_SWITCH(torch_dtype)"]
    
    DtypeSwitch --> FP16["elem_type = __half"]
    DtypeSwitch --> BF16["elem_type = __nv_bfloat16"]
    
    FP16 --> Create["new ModelImpl<elem_type, has_attention_bias>"]
    BF16 --> Create
    
    Create --> Assign["model = ..."]
```

**Diagram 3: Type-Parameterized Initialization Flow**

The macros `DTYPE_SWITCH` [src/entry.cu:10-19]() and `BOOL_SWITCH` [src/entry.cu:21-30]() enable compile-time specialization for:
- Data type: FP16 (`__half`) or BF16 (`__nv_bfloat16`)
- Attention bias: Present (Qwen2) or absent (LLaMA)

### Function Signatures

| Function | Parameters | Return | Purpose |
|----------|------------|--------|---------|
| `init_base_model` | memory_limit, memory_pool, vocab_size, num_layers, hidden_size, ... | void | Creates `ModelImpl` instance |
| `init_eagle_model` | num_layers, intermediate_size, num_iter, topk_per_iter, V, ... | void | Wraps ModelImpl with EagleImpl |
| `init_medusa_model` | num_heads, num_layers, topk_per_head, tree_size, V, ... | void | Wraps ModelImpl with MedusaImpl |
| `init_storage` | none | int | Allocates internal buffers, returns max sequence length |
| `load_model` | name, param | void | Copies weight tensor to GPU storage |
| `prefill` | input_length, history_length, input, position_ids, output | void | Processes prompt tokens |
| `decode` | input_length, padded_length, input, position_ids, cache_length, mask_2d, output, cuda_graph | void | Generates next tokens |
| `draft` | tree_draft_ids, tree_position_ids, cache_length, attn_mask, tree_parent | void | Generates speculative token candidates |
| `verify_and_fix` | num_tokens, pred, gt, position_ids, cache_length, attn_mask, tree_parent | int | Validates predictions, returns acceptance count |

All pointer parameters use `std::uintptr_t` for cross-language compatibility [src/entry.cu:34-172]().

### CUDA Graph Support

The `decode` function supports CUDA graph capture for reduced kernel launch overhead [src/entry.cu:142-164]():

- First call with `cuda_graph=true`: Captures kernel sequence into `graph`
- Subsequent calls: Replays captured graph via `cudaGraphLaunch`
- Graph is recreated if input dimensions change

**Sources:** [src/entry.cu:1-184]()

---

## C++/CUDA Backend Organization

The C++/CUDA backend implements three main model classes:

```mermaid
classDiagram
    class Model {
        <<interface>>
        +init_storage() int
        +load_to_storage(name, param)
        +prefill(...)
        +decode(...)
        +draft(...)
        +verify(...)
    }
    
    class ModelImpl {
        +vocab_size: int
        +num_hidden_layers: int
        +hidden_size: int
        +layers: Layer*
        +embed_tokens: void*
        +lm_head: void*
        +kv_cache_manager: KVCacheManager
        +prefill(...)
        +decode(...)
    }
    
    class EagleImpl {
        +base_model: ModelImpl*
        +num_iter: int
        +topk_per_iter: int
        +tree_size: int
        +V: int (reduced vocab size)
        +eagle_layers: Layer*
        +token_id_remap: int32_t*
        +draft(...)
        +verify(...)
    }
    
    class MedusaImpl {
        +base_model: ModelImpl*
        +num_heads: int
        +medusa_heads: void*
        +tree_indices: int32_t*
        +draft(...)
        +verify(...)
    }
    
    Model <|-- ModelImpl
    Model <|-- EagleImpl
    Model <|-- MedusaImpl
    EagleImpl o-- ModelImpl : wraps
    MedusaImpl o-- ModelImpl : wraps
```

**Diagram 4: C++ Model Class Hierarchy**

### ModelImpl: Base Transformer

`ModelImpl<elem_type, has_attention_bias>` implements a standard decoder-only transformer:
- Embedding layer: Token ID → hidden states
- N transformer layers: Self-attention + FFN
- LM-Head: Hidden states → vocabulary logits
- RoPE (Rotary Position Embeddings): Position encoding
- KV Cache: Stores past attention keys/values

See [ModelImpl: Base Transformer](#4.1) for detailed documentation.

### EagleImpl: Speculative Decoder

`EagleImpl<elem_type, has_attention_bias>` [src/entry.cu:97-128]() extends ModelImpl with speculative decoding:
- **Drafting**: Generates K candidates per iteration using Eagle layers
- **Tree Building**: Constructs prediction tree from candidates
- **Verification**: Base model validates predictions in parallel
- **FR-Spec Optimization**: Reduces vocabulary from full size to V (8K-64K tokens)

Key parameters passed during initialization [src/entry.cu:97-128]():
- `num_layers`: Number of Eagle layers
- `num_iter`: Iterations per draft phase
- `topk_per_iter`: Candidates selected per iteration
- `tree_size`: Maximum positions in prediction tree
- `V`: Reduced vocabulary size for LM-Head

See [EAGLE Implementation](#5.1) for detailed documentation.

### MedusaImpl: Alternative Speculative Decoder

`MedusaImpl<elem_type, has_attention_bias>` [src/entry.cu:70-95]() uses multiple prediction heads:
- Each head predicts next token at different future positions
- Uses pre-computed tree structure
- Alternative to EAGLE with different accuracy/speed tradeoffs

See [Medusa Implementation](#5.2) for detailed documentation.

**Sources:** [src/entry.cu:32-128]()

---

## Data Flow Through the System

The following diagram shows how a text generation request flows through all three layers:

```mermaid
sequenceDiagram
    participant User
    participant LLM as LLM.generate()
    participant C as C module (PyBind11)
    participant ModelImpl as ModelImpl
    participant Attention as Attention
    participant FlashAttn as mha_fwd_kvcache
    
    User->>LLM: generate(input_ids)
    
    Note over LLM: Phase 1: Prefill
    LLM->>LLM: Convert text to token IDs
    loop chunks of chunk_length
        LLM->>C: prefill(chunk, position_ids)
        C->>ModelImpl: prefill()
        ModelImpl->>ModelImpl: embed_tokens lookup
        loop num_hidden_layers
            ModelImpl->>Attention: forward()
            Attention->>FlashAttn: mha_fwd_kvcache()
            FlashAttn-->>Attention: attention output
            Attention-->>ModelImpl: layer output
        end
        ModelImpl->>ModelImpl: lm_head projection
        ModelImpl-->>C: logits
        C-->>LLM: logits tensor
    end
    
    Note over LLM: Phase 2: Decode
    loop generation_length
        LLM->>C: decode(token, position_ids, cache_length)
        C->>ModelImpl: decode()
        ModelImpl->>ModelImpl: embed_tokens lookup
        loop num_hidden_layers
            ModelImpl->>Attention: forward()
            Note over Attention: Reads from KV cache
            Attention->>FlashAttn: mha_fwd_kvcache()
            FlashAttn-->>Attention: attention output
            Attention-->>ModelImpl: layer output
        end
        ModelImpl->>ModelImpl: lm_head projection
        ModelImpl-->>C: logits
        C-->>LLM: logits tensor
        LLM->>LLM: Sample next token from logits
    end
    
    LLM-->>User: Generated text
```

**Diagram 5: End-to-End Generation Data Flow**

### Prefill Phase

1. **Python**: `LLM.prefill()` tokenizes input and chunks it [llamacu/llama.py:140-150]()
2. **Bridge**: `prefill()` converts Python tensors to raw pointers [src/entry.cu:138-140]()
3. **C++**: `ModelImpl.prefill()` processes all tokens in parallel, populating KV cache
4. **CUDA**: Flash Attention computes attention efficiently [src/flash_attn/flash_api.hpp:207-304]()
5. **Return**: Final token logits returned to Python

### Decode Phase

1. **Python**: `LLM.decode()` passes single token and updated cache length [llamacu/llama.py:152-172]()
2. **Bridge**: `decode()` optionally uses CUDA graph for replay [src/entry.cu:142-164]()
3. **C++**: `ModelImpl.decode()` processes token with cached keys/values
4. **CUDA**: Flash Attention reads from KV cache for efficient computation
5. **Return**: Next token logits returned to Python

### Speculative Decode Phase (EAGLE)

When using `LLM_with_eagle`, the decode phase is replaced by draft-verify loop:

1. **Draft**: `C.draft()` generates prediction tree using Eagle layers
2. **Verify**: Base model processes all tree positions in parallel via `C.decode()`
3. **Accept**: `C.verify_and_fix()` compares predictions with ground truth
4. **Return**: Multiple accepted tokens (speedup!)

See [Draft-Verify Pipeline](#5.3) for detailed documentation.

**Sources:** [llamacu/llama.py:140-197](), [src/entry.cu:138-172]()

---

## Memory and Computation Resources

### Memory Allocation Strategy

```mermaid
graph TB
    GPU["GPU Memory"]
    Pool["Memory Pool<br/>80% of GPU memory<br/>Pre-allocated uint8 array"]
    
    GPU --> Pool
    
    Pool --> Weights["Model Weights<br/>Fixed size"]
    Pool --> KVBase["Base Model KV Cache<br/>Sized by layer ratio"]
    Pool --> KVEagle["Eagle KV Cache<br/>Remaining budget"]
    Pool --> Buffers["Intermediate Buffers<br/>Attention, FFN outputs"]
    
    Weights --> Embed["embed_tokens"]
    Weights --> Layers["layer weights"]
    Weights --> LMHead["lm_head"]
    
    KVBase --> Keys["K cache per layer"]
    KVBase --> Values["V cache per layer"]
    
    Buffers --> AttnOut["softmax_lse, oaccum"]
    Buffers --> FFNOut["gated_up buffer"]
    Buffers --> DraftBuf["tree masks, positions"]
```

**Diagram 6: GPU Memory Layout**

The Python layer allocates a large contiguous buffer [llamacu/llama.py:37-38](), which C++ subdivides:

1. **Fixed Allocations**: Model weights loaded from checkpoint
2. **KV Cache**: Split between base and Eagle models proportionally by layer count
3. **Dynamic Buffers**: Attention outputs, FFN intermediates, draft tree structures

The `init_storage()` function [src/entry.cu:130-132]() computes maximum sequence length based on available memory after weight allocation.

### Compute Resources

- **CUDA Streams**: Single `calc_stream` for all operations [src/entry.cu:142-164]()
- **Tensor Cores**: Used automatically by CUTLASS for FP16/BF16 matrix operations
- **Flash Attention**: Memory-efficient attention with optimal memory access patterns [src/flash_attn/flash_api.hpp:207-304]()
- **Kernel Fusion**: Element-wise operations fused to reduce memory bandwidth

**Sources:** [llamacu/llama.py:37-38](), [src/entry.cu:130-132](), [src/flash_attn/flash_api.hpp:1-304]()

---

## Configuration and Initialization Sequence

### Initialization Order

```mermaid
sequenceDiagram
    participant Script as User Script
    participant LLM as LLM.__init__
    participant C as C.init_base_model
    participant Storage as C.init_storage
    participant Load as LLM.load_from_hf
    
    Script->>LLM: LLM(path, memory_limit, dtype)
    LLM->>LLM: Load tokenizer and config
    LLM->>LLM: Allocate memory pool
    LLM->>C: init_base_model(config params)
    Note over C: Creates ModelImpl instance<br/>Registers memory pool
    
    Script->>Storage: init_storage()
    Note over Storage: Subdivides memory pool<br/>Allocates KV cache
    Storage-->>Script: max_total_length
    
    Script->>Load: load_from_hf()
    loop For each weight tensor
        Load->>C: load_model(name, param)
        Note over C: Copies to GPU storage
    end
    Load->>C: load_model("rotary_emb.inv_freq", ...)
    
    Note over Script: Model ready for inference
```

**Diagram 7: Model Initialization Sequence**

### Configuration Parameters

The `LLM` class reads model architecture from HuggingFace config [llamacu/llama.py:32]():

| Parameter | Example (Llama3-8B) | Purpose |
|-----------|---------------------|---------|
| `vocab_size` | 128256 | Token vocabulary size |
| `num_hidden_layers` | 32 | Number of transformer blocks |
| `hidden_size` | 4096 | Hidden dimension |
| `intermediate_size` | 14336 | FFN intermediate dimension |
| `num_attention_heads` | 32 | Query heads |
| `num_key_value_heads` | 8 | Key/Value heads (GQA) |
| `head_dim` | 128 | Dimension per head |
| `rms_norm_eps` | 1e-5 | RMSNorm epsilon |
| `rope_theta` | 500000.0 | RoPE base frequency |

These parameters are passed to `C.init_base_model()` [llamacu/llama.py:45-59]() which constructs the appropriate `ModelImpl` template instantiation.

### Architecture Detection

FR-Spec detects model architecture to apply architecture-specific optimizations [llamacu/llama.py:44]():

- **LLaMA models**: No attention bias (`has_attention_bias = false`)
- **Qwen2 models**: QKV projection has bias (`has_attention_bias = true`)

This is encoded at compile-time via template parameters for zero-overhead specialization.

**Sources:** [llamacu/llama.py:20-59](), [src/entry.cu:34-68]()

---

## Summary

FR-Spec's three-tier architecture provides:

1. **Python Layer**: Easy-to-use APIs compatible with HuggingFace ecosystem
2. **PyBind11 Bridge**: Efficient marshaling with type-generic C++ templates
3. **C++/CUDA Backend**: Optimized kernels with template specialization

Key design principles:
- **Single memory pool**: Reduces allocation overhead and fragmentation
- **Polymorphic model pointer**: Enables seamless switching between base/Eagle/Medusa
- **Template metaprogramming**: Compile-time specialization for data types and configurations
- **CUDA graph support**: Reduces CPU overhead during decode
- **Modular design**: Clean separation between base model and speculative extensions

For implementation details of each subsystem, refer to the child pages under System Architecture.

**Sources:** [README.md:1-140](), [src/entry.cu:1-184](), [llamacu/llama.py:1-198](), [src/flash_attn/flash_api.hpp:1-304]()

---

