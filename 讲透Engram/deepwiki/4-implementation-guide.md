<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/Engram · page 4 Implementation Guide · fetched 2026-10-30 -->

# Implementation Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [engram_demo_v1.py](engram_demo_v1.py)

</details>



## Purpose and Scope

This guide provides a practical walkthrough of the Engram codebase implementation, focusing on the demonstration code in `engram_demo_v1.py`. It explains how the theoretical concepts from [Core Concepts](#2) are realized in working code, detailing the class hierarchies, data transformations, and component interactions.

For architectural theory and system design principles, see [Architecture](#3). For experimental validation of the implementation's effectiveness, see [Experimental Validation](#5). For step-by-step usage instructions, see [Getting Started](#6).

---

## Code Structure Overview

The demonstration implementation in `engram_demo_v1.py` provides a self-contained illustration of the Engram module's core logic. The file contains approximately 423 lines organized into distinct functional components.

### File Organization

```mermaid
graph TB
    subgraph "Configuration Layer"
        EC["EngramConfig<br/>(lines 38-48)"]
        BC["BackBoneConfig<br/>(lines 50-55)"]
    end
    
    subgraph "Foundation Components"
        CT["CompressedTokenizer<br/>(lines 60-121)"]
        NHM["NgramHashMapping<br/>(lines 188-303)"]
    end
    
    subgraph "Neural Components"
        MHE["MultiHeadEmbedding<br/>(lines 305-324)"]
        SC["ShortConv<br/>(lines 123-179)"]
    end
    
    subgraph "Integration Components"
        ENG["Engram<br/>(lines 326-378)"]
        TB["TransformerBlock<br/>(lines 380-394)"]
    end
    
    subgraph "Entry Point"
        MAIN["__main__<br/>(lines 396-423)"]
    end
    
    EC --> NHM
    EC --> MHE
    EC --> SC
    EC --> ENG
    BC --> SC
    BC --> TB
    
    CT --> NHM
    NHM --> ENG
    MHE --> ENG
    SC --> ENG
    ENG --> TB
    TB --> MAIN
```

**Sources:** [engram_demo_v1.py:1-423]()

### Key Classes and Their Roles

| Class | Lines | Purpose | Key Methods |
|-------|-------|---------|-------------|
| `CompressedTokenizer` | 60-121 | Vocabulary compression via normalization | `__call__`, `_compress`, `_build_lookup_table` |
| `NgramHashMapping` | 188-303 | Deterministic N-gram hashing with layer-specific mixing | `hash`, `_get_ngram_hashes`, `calculate_vocab_size_across_layers` |
| `MultiHeadEmbedding` | 305-324 | Unified embedding table with offset-based indexing | `forward` |
| `ShortConv` | 123-179 | Grouped 1D convolution with per-head normalization | `forward` |
| `Engram` | 326-378 | Main module integrating hashing, embedding, and fusion | `forward` |
| `TransformerBlock` | 380-394 | Conditional integration of Engram into transformer layers | `forward` |

**Sources:** [engram_demo_v1.py:60-394]()

---

## Component Initialization Flow

The following diagram maps the initialization sequence, showing how configuration objects flow through component constructors and what dependencies are established.

```mermaid
sequenceDiagram
    participant Main as "__main__"
    participant EngCfg as "EngramConfig"
    participant BackCfg as "BackBoneConfig"
    participant TB as "TransformerBlock"
    participant Eng as "Engram"
    participant NHM as "NgramHashMapping"
    participant CT as "CompressedTokenizer"
    participant MHE as "MultiHeadEmbedding"
    participant SC as "ShortConv"
    
    Main->>EngCfg: Instantiate (lines 38-48)
    Note over EngCfg: tokenizer_name_or_path<br/>engram_vocab_size<br/>max_ngram_size<br/>layer_ids
    
    Main->>BackCfg: Instantiate (lines 50-55)
    Note over BackCfg: hidden_size<br/>hc_mult<br/>num_layers
    
    Main->>TB: Create for layer_id (line 399)
    
    alt layer_id in engram_cfg.layer_ids
        TB->>Eng: Initialize with layer_id (line 387)
        
        Eng->>NHM: Initialize (lines 330-339)
        NHM->>CT: Create tokenizer (lines 207-209)
        CT->>CT: Build lookup table (line 79)
        Note over CT: Normalize & deduplicate<br/>Returns compressed vocab size
        
        NHM->>NHM: Generate layer multipliers (lines 219-231)
        Note over NHM: Layer-specific random<br/>odd multipliers
        
        NHM->>NHM: Calculate vocab sizes (lines 233-260)
        Note over NHM: Find primes for each<br/>ngram/head combination
        
        Eng->>MHE: Initialize (lines 340-343)
        Note over MHE: Single embedding with<br/>offset-based addressing
        
        Eng->>SC: Initialize (lines 344-349)
        Note over SC: Grouped 1D convolution<br/>with RMSNorm per group
        
        Eng->>Eng: Create projections (lines 350-356)
        Note over Eng: value_proj<br/>key_projs (per hc_mult)<br/>norm1, norm2 (per hc_mult)
    end
```

**Sources:** [engram_demo_v1.py:38-58](), [engram_demo_v1.py:326-356](), [engram_demo_v1.py:380-394]()

---

## Forward Pass Data Flow

This diagram traces the complete data transformation pipeline through an Engram-augmented layer, using actual variable names and method calls from the implementation.

```mermaid
graph TB
    subgraph "Input Stage"
        IDS["input_ids<br/>[B, L]<br/>torch.Tensor"]
        HS_IN["hidden_states<br/>[B, L, HC_MULT, D]<br/>torch.Tensor"]
    end
    
    subgraph "CompressedTokenizer (lines 120-121)"
        COMP["__call__(input_ids)<br/>Returns: np.ndarray"]
        LUT["lookup_table[valid_ids]<br/>Compressed token IDs"]
        COMP --> LUT
    end
    
    subgraph "NgramHashMapping (lines 298-303)"
        HASH_CALL["hash(input_ids)<br/>Returns: dict[layer_id, np.ndarray]"]
        GET_HASH["_get_ngram_hashes(input_ids, layer_id)<br/>[B, L, NUM_HEADS]"]
        SHIFT["shift_k(k) for k in range(max_ngram_size)<br/>Create N-gram contexts"]
        XOR["XOR mixing with multipliers<br/>mix = tokens[0] * mult[0] ^ ..."]
        MOD["mod = head_vocab_sizes[j]<br/>head_hash = mix % mod"]
        
        HASH_CALL --> GET_HASH
        GET_HASH --> SHIFT
        SHIFT --> XOR
        XOR --> MOD
    end
    
    subgraph "MultiHeadEmbedding (lines 320-323)"
        OFFSET["shifted_input_ids = input_ids + offsets<br/>Offset-based addressing"]
        EMB["embedding(shifted_input_ids)<br/>[B, L, NUM_HEADS, D//NUM_HEADS]"]
        FLAT["flatten(start_dim=-2)<br/>[B, L, ENGRAM_HIDDEN]"]
        
        OFFSET --> EMB
        EMB --> FLAT
    end
    
    subgraph "Engram Module (lines 358-378)"
        GATE_GEN["Generate gates per hc_idx<br/>key = key_projs[hc_idx](embeddings)<br/>gate = (normed_key * normed_query).sum()"]
        GATE_ACT["gate.abs().clamp_min(1e-6).sqrt() * gate.sign()<br/>gate.sigmoid()"]
        VAL_PROJ["value = gates * value_proj(embeddings)"]
        CONV_CALL["short_conv(value)<br/>Grouped convolution"]
        OUTPUT["output = value + short_conv(value)<br/>Residual connection"]
        
        GATE_GEN --> GATE_ACT
        GATE_ACT --> VAL_PROJ
        VAL_PROJ --> CONV_CALL
        CONV_CALL --> OUTPUT
    end
    
    subgraph "TransformerBlock (lines 389-394)"
        ENGRAM_ADD["hidden_states = engram(...) + hidden_states"]
        ATTN_ADD["hidden_states = attn(...) + hidden_states"]
        MOE_ADD["hidden_states = moe(...) + hidden_states"]
        
        ENGRAM_ADD --> ATTN_ADD
        ATTN_ADD --> MOE_ADD
    end
    
    IDS --> COMP
    COMP --> HASH_CALL
    HASH_CALL --> OFFSET
    FLAT --> GATE_GEN
    HS_IN --> GATE_GEN
    OUTPUT --> ENGRAM_ADD
    
    style COMP fill:#f9f9f9,stroke:#333
    style HASH_CALL fill:#f9f9f9,stroke:#333
    style GATE_GEN fill:#f9f9f9,stroke:#333
    style OUTPUT fill:#f9f9f9,stroke:#333
```

**Sources:** [engram_demo_v1.py:358-378](), [engram_demo_v1.py:389-394]()

---

## Component Dependency Graph

This graph shows the instantiation dependencies between components, using actual class names and constructor signatures.

```mermaid
graph TB
    subgraph "Configuration Objects"
        EC_INST["engram_cfg: EngramConfig<br/>Line 57"]
        BC_INST["backbone_config: BackBoneConfig<br/>Line 58"]
    end
    
    subgraph "NgramHashMapping Dependencies"
        NHM_INIT["NgramHashMapping.__init__(<br/>engram_vocab_size,<br/>max_ngram_size,<br/>layer_ids,<br/>tokenizer_name_or_path,<br/>pad_id, seed)"]
        
        CT_INIT["CompressedTokenizer.__init__(<br/>tokenizer_name_or_path)"]
        
        NORM["normalizers.Sequence([<br/>NFKC(), NFD(),<br/>StripAccents(),<br/>Lowercase(), ...])"]
        
        LUT_BUILD["_build_lookup_table()<br/>Returns: lookup_table, num_new_token"]
    end
    
    subgraph "Embedding Layer"
        MHE_INIT["MultiHeadEmbedding.__init__(<br/>list_of_N,<br/>D)"]
        
        OFFSET_CALC["Register offsets buffer<br/>offsets = [0, N[0], N[0]+N[1], ...]"]
        
        EMB_LAYER["nn.Embedding(<br/>num_embeddings=sum(list_of_N),<br/>embedding_dim=D)"]
    end
    
    subgraph "Convolution Layer"
        SC_INIT["ShortConv.__init__(<br/>hidden_size,<br/>kernel_size,<br/>dilation,<br/>hc_mult)"]
        
        CONV1D["nn.Conv1d(<br/>in_channels=hidden_size*hc_mult,<br/>groups=hidden_size*hc_mult,<br/>kernel_size=kernel_size)"]
        
        NORMS["nn.ModuleList([<br/>nn.RMSNorm(hidden_size)<br/>for _ in range(hc_mult)])"]
    end
    
    subgraph "Engram Module"
        ENG_INIT["Engram.__init__(layer_id)"]
        
        VAL_PROJ["value_proj:<br/>nn.Linear(engram_hidden_size,<br/>hidden_size)"]
        
        KEY_PROJS["key_projs:<br/>nn.ModuleList([<br/>nn.Linear(engram_hidden, hidden)<br/>for _ in range(hc_mult)])"]
    end
    
    EC_INST --> NHM_INIT
    NHM_INIT --> CT_INIT
    CT_INIT --> NORM
    CT_INIT --> LUT_BUILD
    
    EC_INST --> MHE_INIT
    MHE_INIT --> OFFSET_CALC
    MHE_INIT --> EMB_LAYER
    
    BC_INST --> SC_INIT
    EC_INST --> SC_INIT
    SC_INIT --> CONV1D
    SC_INIT --> NORMS
    
    ENG_INIT --> NHM_INIT
    ENG_INIT --> MHE_INIT
    ENG_INIT --> SC_INIT
    ENG_INIT --> VAL_PROJ
    ENG_INIT --> KEY_PROJS
```

**Sources:** [engram_demo_v1.py:326-356](), [engram_demo_v1.py:188-233](), [engram_demo_v1.py:305-318](), [engram_demo_v1.py:123-154]()

---

## N-gram Hash Computation Pipeline

The hash computation process is central to Engram's O(1) lookup mechanism. This diagram details the algorithmic steps in `NgramHashMapping._get_ngram_hashes`.

### Hashing Algorithm Flow

```mermaid
graph TB
    START["Input: input_ids [B, T]<br/>Layer: layer_id"]
    
    COMPRESS["CompressedTokenizer<br/>x = compressed(input_ids)<br/>[B, T] with reduced vocab"]
    
    MULT["Retrieve layer_multipliers[layer_id]<br/>Random odd multipliers [max_ngram_size]"]
    
    SHIFT["Generate base_shifts<br/>shift_k(k) for k=0 to max_ngram_size-1<br/>Pad with pad_id on left"]
    
    LOOP_START{"For n=2 to max_ngram_size"}
    
    SELECT["Select tokens = base_shifts[:n]<br/>Get first n shifted arrays"]
    
    XOR_MIX["XOR mixing:<br/>mix = tokens[0] * multipliers[0]<br/>for k=1 to n-1:<br/>  mix ^= tokens[k] * multipliers[k]"]
    
    HEAD_LOOP{"For each head j<br/>in range(n_head_per_ngram)"}
    
    MODULO["mod = vocab_size_across_layers[layer_id][n-2][j]<br/>head_hash = mix % mod<br/>[B, T] per head"]
    
    STACK["Stack all head hashes<br/>[B, T, NUM_HEADS]<br/>NUM_HEADS = (max_ngram-1) * n_head_per_ngram"]
    
    START --> COMPRESS
    COMPRESS --> MULT
    MULT --> SHIFT
    SHIFT --> LOOP_START
    LOOP_START -->|Yes| SELECT
    SELECT --> XOR_MIX
    XOR_MIX --> HEAD_LOOP
    HEAD_LOOP -->|Yes| MODULO
    MODULO --> HEAD_LOOP
    HEAD_LOOP -->|No| LOOP_START
    LOOP_START -->|No| STACK
```

**Sources:** [engram_demo_v1.py:262-296]()

### Prime Modulo Collision Reduction

The hash function uses prime numbers as moduli to minimize collisions. The `calculate_vocab_size_across_layers` method ensures each head for each N-gram uses a distinct prime.

```mermaid
graph LR
    subgraph "Prime Selection Process"
        SEARCH_START["Start: vocab_size - 1"]
        FIND_NEXT["find_next_prime(start, seen_primes)"]
        CHECK_PRIME["isprime(candidate)"]
        CHECK_SEEN{"candidate in<br/>seen_primes?"}
        ADD_SEEN["seen_primes.add(candidate)"]
        RETURN["Return prime for this head"]
        
        SEARCH_START --> FIND_NEXT
        FIND_NEXT --> CHECK_PRIME
        CHECK_PRIME --> CHECK_SEEN
        CHECK_SEEN -->|No| ADD_SEEN
        CHECK_SEEN -->|Yes| FIND_NEXT
        ADD_SEEN --> RETURN
    end
    
    subgraph "Example for 2-gram, Head 0"
        V1["vocab_size_per_ngram[0] = 646400"]
        P1["Search from 646399"]
        R1["First prime >= 646399 not in seen"]
        RESULT1["Prime ~= 646411"]
        
        V1 --> P1
        P1 --> R1
        R1 --> RESULT1
    end
```

**Sources:** [engram_demo_v1.py:181-186](), [engram_demo_v1.py:235-260]()

---

## Gating Mechanism Implementation

The Engram module uses an attention-like gating mechanism to fuse static N-gram embeddings with dynamic hidden states. This occurs separately for each hyper-connection index.

```mermaid
sequenceDiagram
    participant Emb as "embeddings<br/>[B, L, ENGRAM_HIDDEN]"
    participant KeyProj as "key_projs[hc_idx]"
    participant Norm1 as "norm1[hc_idx]"
    participant HS as "hidden_states[:,:,hc_idx,:]<br/>[B, L, D]"
    participant Norm2 as "norm2[hc_idx]"
    participant Gate as "gate computation"
    
    rect rgb(250, 250, 250)
        Note over Emb,Norm1: Key Generation
        Emb->>KeyProj: Linear projection
        KeyProj->>Norm1: key [B, L, D]
        Norm1->>Gate: normed_key
    end
    
    rect rgb(250, 250, 250)
        Note over HS,Norm2: Query Generation
        HS->>Norm2: hidden_states slice
        Norm2->>Gate: normed_query [B, L, D]
    end
    
    rect rgb(250, 250, 250)
        Note over Gate: Attention Score
        Gate->>Gate: (normed_key * normed_query).sum(dim=-1)
        Gate->>Gate: / sqrt(hidden_size)
        Note over Gate: [B, L] scores
    end
    
    rect rgb(250, 250, 250)
        Note over Gate: Symmetry Breaking
        Gate->>Gate: abs().clamp_min(1e-6).sqrt()
        Gate->>Gate: * sign()
        Note over Gate: Preserves direction,<br/>dampens magnitude
    end
    
    rect rgb(250, 250, 250)
        Note over Gate: Final Activation
        Gate->>Gate: sigmoid()
        Gate->>Gate: unsqueeze(-1)
        Note over Gate: [B, L, 1] gate
    end
```

**Sources:** [engram_demo_v1.py:365-375]()

### Gate Application and Residual Connection

```mermaid
graph TB
    EMB["embeddings<br/>[B, L, ENGRAM_HIDDEN]"]
    GATES["gates<br/>[B, L, HC_MULT, 1]"]
    
    VAL_PROJ["value_proj(embeddings)<br/>[B, L, D]"]
    UNSQUEEZE["unsqueeze(2)<br/>[B, L, 1, D]"]
    MULTIPLY["gates * value<br/>[B, L, HC_MULT, D]"]
    
    CONV_IN["value<br/>[B, L, HC_MULT, D]"]
    CONV_OUT["short_conv(value)<br/>[B, L, HC_MULT, D]"]
    
    ADD["output = value + short_conv(value)<br/>[B, L, HC_MULT, D]"]
    
    EMB --> VAL_PROJ
    VAL_PROJ --> UNSQUEEZE
    UNSQUEEZE --> MULTIPLY
    GATES --> MULTIPLY
    MULTIPLY --> CONV_IN
    MULTIPLY --> ADD
    CONV_IN --> CONV_OUT
    CONV_OUT --> ADD
```

**Sources:** [engram_demo_v1.py:376-378]()

---

## Configuration Parameters

### EngramConfig

The `EngramConfig` dataclass [engram_demo_v1.py:38-48]() specifies all Engram-specific hyperparameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tokenizer_name_or_path` | `str` | `"deepseek-ai/DeepSeek-V3"` | HuggingFace tokenizer identifier for vocabulary compression |
| `engram_vocab_size` | `List[int]` | `[646400, 646400]` | Vocabulary size per N-gram (length = max_ngram_size - 1) |
| `max_ngram_size` | `int` | `3` | Maximum N-gram order (e.g., 3 means 2-grams and 3-grams) |
| `n_embed_per_ngram` | `int` | `512` | Total embedding dimension per N-gram |
| `n_head_per_ngram` | `int` | `8` | Number of heads per N-gram for multi-head embeddings |
| `layer_ids` | `List[int]` | `[1, 15]` | Transformer layers to augment with Engram |
| `pad_id` | `int` | `2` | Token ID for padding in N-gram contexts |
| `seed` | `int` | `0` | Random seed for hash multiplier generation |
| `kernel_size` | `int` | `4` | Convolution kernel size in ShortConv |

### BackBoneConfig

The `BackBoneConfig` dataclass [engram_demo_v1.py:50-55]() specifies LLM backbone parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hidden_size` | `int` | `1024` | Model hidden dimension |
| `hc_mult` | `int` | `4` | Hyper-connection multiplier (number of parallel streams) |
| `vocab_size` | `int` | `129280` | Original tokenizer vocabulary size |
| `num_layers` | `int` | `30` | Total number of transformer layers |

**Sources:** [engram_demo_v1.py:38-58]()

---

## ShortConv Architecture Details

The `ShortConv` module implements grouped 1D convolution with per-group normalization. This processes the gated N-gram features with local context modeling.

### Internal Structure

```mermaid
graph TB
    INPUT["Input: x<br/>[B, T, HC_MULT, D]"]
    
    NORM_LOOP["For i in range(HC_MULT):<br/>  chunk = x[:,:,i,:]<br/>  normed = norms[i](chunk)"]
    
    CONCAT["Concatenate normed chunks<br/>x_norm: [B, T, HC_MULT * D]"]
    
    TRANSPOSE["Transpose to [B, HC_MULT*D, T]<br/>For Conv1d format"]
    
    CONV["Conv1d(<br/>in_channels=HC_MULT*D,<br/>out_channels=HC_MULT*D,<br/>groups=HC_MULT*D,<br/>kernel_size=4)<br/>Depthwise convolution"]
    
    CROP["Crop to [:, :, :T]<br/>Remove padding"]
    
    ACT["SiLU activation<br/>if activation=True"]
    
    RESHAPE["Transpose and reshape<br/>to [B, T, HC_MULT, D]"]
    
    INPUT --> NORM_LOOP
    NORM_LOOP --> CONCAT
    CONCAT --> TRANSPOSE
    TRANSPOSE --> CONV
    CONV --> CROP
    CROP --> ACT
    ACT --> RESHAPE
```

**Key Implementation Details:**
- **Grouped Convolution**: Each of the `hidden_size * hc_mult` channels has its own convolution kernel (groups = in_channels)
- **Dilation**: Set to `max_ngram_size` to match the N-gram context span [engram_demo_v1.py:347]()
- **Padding**: Calculated as `(kernel_size - 1) * dilation` to enable causal processing [engram_demo_v1.py:144]()
- **Per-Group Normalization**: Separate RMSNorm for each of the `hc_mult` groups [engram_demo_v1.py:148-151]()

**Sources:** [engram_demo_v1.py:123-179]()

---

## Main Execution Flow

The `__main__` block demonstrates end-to-end usage of the Engram-augmented LLM:

```mermaid
sequenceDiagram
    participant Main as "__main__"
    participant LLM as "LLM (list)"
    participant Embed as "nn.Embedding"
    participant TB as "TransformerBlock[i]"
    participant Output as "nn.Linear"
    
    rect rgb(250, 250, 250)
        Note over Main: Model Construction (lines 397-401)
        Main->>LLM: Create embedding layer
        Main->>LLM: Create 30 TransformerBlocks
        Main->>LLM: Create output projection
    end
    
    rect rgb(250, 250, 250)
        Note over Main: Input Processing (lines 403-407)
        Main->>Main: text = "Only Alexander..."
        Main->>Main: tokenizer(text)
        Main->>Main: input_ids [B, L]
    end
    
    rect rgb(250, 250, 250)
        Note over Main: Forward Pass (lines 409-419)
        Main->>Embed: hidden = embedding(input_ids)
        Note over Main: Mock hyper-connection
        Main->>Main: hidden = hidden.unsqueeze(2).expand(..., hc_mult, ...)
        
        loop For each layer (1 to 29)
            Main->>TB: hidden = layer(input_ids, hidden)
            Note over TB: Engram at layers 1, 15<br/>Attention (mocked)<br/>MoE (mocked)
        end
        
        Note over Main: Mock hyper-connection reduction
        Main->>Main: hidden = hidden[:,:,0,:]
        Main->>Output: output = linear(hidden)
    end
    
    rect rgb(250, 250, 250)
        Note over Main: Output (lines 421-422)
        Main->>Main: Print shapes
        Note over Main: input_ids.shape=(1, 11)<br/>output.shape=(1, 11, 129280)
    end
```

**Sources:** [engram_demo_v1.py:396-423]()

---

## Memory and Computation Characteristics

### Memory Layout

The implementation uses the following memory structures:

| Component | Data Structure | Shape | Notes |
|-----------|----------------|-------|-------|
| `CompressedTokenizer.lookup_table` | `np.ndarray` | `[vocab_size]` | Maps original to compressed token IDs |
| `NgramHashMapping.layer_multipliers` | `dict[int, np.ndarray]` | `{layer_id: [max_ngram_size]}` | Layer-specific hash multipliers |
| `MultiHeadEmbedding.offsets` | `torch.Tensor` | `[num_heads]` | Address offsets for unified embedding |
| `MultiHeadEmbedding.embedding.weight` | `nn.Parameter` | `[sum(vocab_sizes), D]` | Massive static memory table |
| `ShortConv.conv.weight` | `nn.Parameter` | `[hidden*hc_mult, 1, kernel_size]` | Depthwise convolution kernels |

### Computational Complexity

**Per-Token Operations in `Engram.forward`:**

1. **Hash Computation**: O(max_ngram_size × n_head_per_ngram) XOR and modulo operations
2. **Embedding Lookup**: O(1) deterministic addressing into embedding table
3. **Gating**: O(hc_mult × hidden_size) for key-query attention scores
4. **Convolution**: O(hc_mult × hidden_size × kernel_size) for local context modeling

Total: O(hc_mult × hidden_size) dominant term, same order as standard transformer operations.

**Sources:** [engram_demo_v1.py:358-378]()

---

## Simplifications and Production Considerations

The demonstration code includes several simplifications noted in the header [engram_demo_v1.py:5-18]():

### Mocked Components

- **Attention**: Replaced with identity function `lambda x: x` [engram_demo_v1.py:383]()
- **MoE**: Replaced with identity function `lambda x: x` [engram_demo_v1.py:384]()
- **Hyper-connections**: Manual expand/reduction operations [engram_demo_v1.py:413](), [engram_demo_v1.py:416]()

### Production Requirements

For deployment, the implementation would require:

1. **Custom CUDA Kernels**: Fused hash computation and embedding lookup
2. **Distributed Training**: All2All communication for N-gram embedding synchronization (see [Training vs Inference Architecture](#3.3))
3. **Memory Offloading**: Host memory management for massive embedding tables (see [Memory Hierarchy and Offloading](#3.4))
4. **Quantization**: Reduced precision for embedding tables to lower memory footprint
5. **Gradient Checkpointing**: For backward pass memory efficiency

**Sources:** [engram_demo_v1.py:5-18]()

---

