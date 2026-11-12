<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/Engram · page 6 Getting Started · fetched 2026-10-30 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [engram_demo_v1.py](engram_demo_v1.py)

</details>



This document provides a practical guide for users to begin working with the Engram repository. It covers environment setup, dependency installation, running the demonstration implementation, and understanding the demo's output and structure.

For detailed architectural concepts, see [Core Concepts](#2). For production implementation guidance, see [Implementation Guide](#4). For experimental validation details, see [Experimental Validation](#5).

---

## Prerequisites

The Engram demo requires a Python environment with the following specifications:

| Requirement | Specification |
|------------|---------------|
| Python Version | 3.8 or higher (recommended) |
| PyTorch | Latest stable version |
| Operating System | Linux, macOS, or Windows with WSL |
| Hardware | CPU sufficient for demo; GPU not required |
| Memory | Minimum 4GB RAM for small examples |

**Important Notes:**
- The provided demo ([engram_demo_v1.py:1-423]()) is designed for demonstration purposes, not production deployment
- Standard components (Attention, MoE, advanced hyper-connections) are mocked to focus on Engram module logic
- The demo illustrates data flow and core algorithms without requiring distributed training infrastructure

**Sources:** [README.md:80-90](), [engram_demo_v1.py:1-19]()

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/deepseek-ai/Engram.git
cd Engram
```

### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install torch numpy transformers sympy
```

**Dependency Purposes:**

| Package | Purpose | Used By |
|---------|---------|---------|
| `torch` | Neural network implementation | All module components |
| `numpy` | N-gram hash computation | `NgramHashMapping` class |
| `transformers` | Tokenizer loading | `CompressedTokenizer` class |
| `sympy` | Prime number calculations | Hash table sizing logic |

The installation is complete when all dependencies resolve without errors.

**Sources:** [README.md:80-83](), [engram_demo_v1.py:22-36]()

---

## Running the Demo

### Basic Execution

Execute the demo script from the repository root:

```bash
python engram_demo_v1.py
```

### Expected Output

The demo processes a sample text through the Engram-augmented architecture and displays:

```
✅ Forward Complete!
input_ids.shape=torch.Size([1, 13])
output.shape=torch.Size([1, 13, 129280])
```

This output confirms:
- **Input Shape:** `[batch_size, sequence_length]` = `[1, 13]` for the demo text
- **Output Shape:** `[batch_size, sequence_length, vocab_size]` = `[1, 13, 129280]` logits for next-token prediction

**Sources:** [engram_demo_v1.py:396-422]()

---

## Demo Execution Flow

The following diagram traces the execution path from script invocation to output:

```mermaid
graph TB
    START["Script Entry<br/>(engram_demo_v1.py:396)"]
    
    CONFIG["Load Configurations<br/>EngramConfig<br/>BackBoneConfig"]
    
    TOKENIZER["Initialize Tokenizer<br/>AutoTokenizer.from_pretrained<br/>(line 404)"]
    
    TOKENIZE["Tokenize Input Text<br/>'Only Alexander...'<br/>(line 405)"]
    
    BUILD_LLM["Construct Model<br/>List[nn.Module]<br/>(lines 397-401)"]
    
    EMBED["Embedding Layer<br/>nn.Embedding<br/>(line 411)"]
    
    MOCK_HC["Mock Hyper-connection<br/>unsqueeze(2).expand<br/>(line 413)"]
    
    subgraph "Transformer Layers"
        LAYER0["Layer 0<br/>TransformerBlock<br/>(no Engram)"]
        LAYER1["Layer 1<br/>TransformerBlock<br/>(with Engram)"]
        LAYER_MID["Layers 2-14<br/>(standard blocks)"]
        LAYER15["Layer 15<br/>TransformerBlock<br/>(with Engram)"]
        LAYER_END["Layers 16-29<br/>(standard blocks)"]
    end
    
    UNMOCK["Unmock Hyper-connection<br/>hidden_states[:,:,0,:]<br/>(line 416)"]
    
    OUTPUT_PROJ["Output Projection<br/>nn.Linear<br/>(line 417)"]
    
    PRINT["Print Results<br/>(lines 421-422)"]
    
    START --> CONFIG
    CONFIG --> TOKENIZER
    TOKENIZER --> TOKENIZE
    TOKENIZE --> BUILD_LLM
    BUILD_LLM --> EMBED
    EMBED --> MOCK_HC
    MOCK_HC --> LAYER0
    LAYER0 --> LAYER1
    LAYER1 --> LAYER_MID
    LAYER_MID --> LAYER15
    LAYER15 --> LAYER_END
    LAYER_END --> UNMOCK
    UNMOCK --> OUTPUT_PROJ
    OUTPUT_PROJ --> PRINT
```

**Sources:** [engram_demo_v1.py:396-422]()

---

## Understanding the Demo Implementation

### Configuration Architecture

The demo uses two configuration dataclasses that control system behavior:

```mermaid
graph LR
    subgraph "EngramConfig"
        E_TOKENIZER["tokenizer_name_or_path<br/>'deepseek-ai/DeepSeek-V3'"]
        E_VOCAB["engram_vocab_size<br/>[129280*5, 129280*5]"]
        E_NGRAM["max_ngram_size: 3"]
        E_EMBED["n_embed_per_ngram: 512"]
        E_HEAD["n_head_per_ngram: 8"]
        E_LAYERS["layer_ids: [1, 15]"]
        E_PAD["pad_id: 2"]
        E_SEED["seed: 0"]
        E_KERNEL["kernel_size: 4"]
    end
    
    subgraph "BackBoneConfig"
        B_HIDDEN["hidden_size: 1024"]
        B_MULT["hc_mult: 4"]
        B_VOCAB["vocab_size: 129280"]
        B_LAYERS["num_layers: 30"]
    end
    
    E_TOKENIZER -.used by.-> COMP_TOK["CompressedTokenizer"]
    E_VOCAB -.used by.-> HASH["NgramHashMapping"]
    E_LAYERS -.determines.-> INTEGRATION["Engram Integration<br/>Layers 1 and 15"]
    
    B_HIDDEN -.defines.-> DIMS["Hidden State<br/>Dimensions"]
    B_MULT -.defines.-> HC["Hyper-connection<br/>Multiplicity"]
```

**Key Configuration Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `engram_vocab_size` | `[129280*5, 129280*5]` | Hash table sizes for 2-gram and 3-gram embeddings |
| `max_ngram_size` | `3` | Generate up to 3-grams (bigrams and trigrams) |
| `n_embed_per_ngram` | `512` | Embedding dimension per N-gram type |
| `n_head_per_ngram` | `8` | Multi-head configuration for each N-gram type |
| `layer_ids` | `[1, 15]` | Transformer layers with Engram integration |
| `hc_mult` | `4` | Hyper-connection multiplicity (4 parallel paths) |

**Sources:** [engram_demo_v1.py:38-58]()

---

### Component Initialization Sequence

The following diagram maps initialization order to specific code entities:

```mermaid
sequenceDiagram
    participant Main as "Main Block<br/>(line 396)"
    participant LLM as "LLM List<br/>(lines 397-401)"
    participant TBlock as "TransformerBlock<br/>(lines 380-394)"
    participant Engram as "Engram Module<br/>(lines 326-378)"
    participant Hash as "NgramHashMapping<br/>(lines 188-303)"
    participant Tokenizer as "CompressedTokenizer<br/>(lines 60-121)"
    participant Embed as "MultiHeadEmbedding<br/>(lines 305-324)"
    participant Conv as "ShortConv<br/>(lines 123-179)"
    
    Main->>LLM: "Create model list"
    LLM->>TBlock: "for layer_id in range(30)"
    
    alt "layer_id in [1, 15]"
        TBlock->>Engram: "Engram(layer_id)"
        Engram->>Hash: "NgramHashMapping(config)"
        Hash->>Tokenizer: "CompressedTokenizer(path)"
        Tokenizer-->>Hash: "lookup_table, vocab_size"
        Hash->>Hash: "calculate_vocab_size_across_layers()"
        Hash-->>Engram: "hash_mapping instance"
        
        Engram->>Embed: "MultiHeadEmbedding(list_of_N, D)"
        Embed-->>Engram: "embedding instance"
        
        Engram->>Conv: "ShortConv(hidden_size, kernel_size)"
        Conv-->>Engram: "conv instance"
        
        Engram->>Engram: "Initialize projections:<br/>value_proj, key_projs, norms"
        Engram-->>TBlock: "engram instance"
    else "other layers"
        TBlock->>TBlock: "engram = None"
    end
    
    TBlock-->>LLM: "transformer block instance"
    LLM-->>Main: "Complete LLM list"
```

**Sources:** [engram_demo_v1.py:326-378](), [engram_demo_v1.py:380-394](), [engram_demo_v1.py:397-401]()

---

### Forward Pass Data Flow

The demo processes input through three main phases:

**Phase 1: Embedding and Preparation**

```mermaid
graph TB
    INPUT["input_ids<br/>[B, L]<br/>torch.Size([1, 13])"]
    
    EMBED["nn.Embedding<br/>(line 411)<br/>vocab_size=129280<br/>hidden_size=1024"]
    
    HIDDEN1["hidden_states<br/>[B, L, D]<br/>[1, 13, 1024]"]
    
    EXPAND["unsqueeze(2).expand<br/>(line 413)<br/>Mock hyper-connection"]
    
    HIDDEN2["hidden_states<br/>[B, L, HC_MULT, D]<br/>[1, 13, 4, 1024]"]
    
    INPUT --> EMBED
    EMBED --> HIDDEN1
    HIDDEN1 --> EXPAND
    EXPAND --> HIDDEN2
```

**Phase 2: Engram Processing (Layer 1 and Layer 15)**

```mermaid
graph TB
    HIDDEN_IN["hidden_states<br/>[B, L, HC_MULT, D]"]
    INPUT_IDS["input_ids<br/>[B, L]"]
    
    subgraph "Engram.forward (lines 358-378)"
        HASH["hash_mapping.hash<br/>(line 363)<br/>Compute N-gram hashes"]
        
        LOOKUP["multi_head_embedding<br/>(line 364)<br/>Retrieve embeddings"]
        
        FLATTEN["flatten(start_dim=-2)<br/>(line 364)<br/>Merge N-gram heads"]
        
        subgraph "Gate Computation (lines 365-375)"
            KEY_PROJ["key_projs[hc_idx]<br/>Project to hidden_size"]
            QUERY["hidden_states[:,:,hc_idx,:]<br/>Extract query"]
            NORM["norm1, norm2<br/>RMSNorm"]
            DOT["key * query<br/>Attention scoring"]
            GATE["abs().sqrt() * sign()<br/>.sigmoid()<br/>Gating function"]
        end
        
        VALUE["value_proj<br/>(line 376)<br/>Project embeddings"]
        
        SHORTCONV["short_conv<br/>(line 377)<br/>Local context"]
        
        OUTPUT["engram_output<br/>[B, L, HC_MULT, D]"]
    end
    
    RESIDUAL["hidden_states +<br/>engram_output<br/>(line 391)"]
    
    INPUT_IDS --> HASH
    HASH --> LOOKUP
    LOOKUP --> FLATTEN
    FLATTEN --> KEY_PROJ
    HIDDEN_IN --> QUERY
    KEY_PROJ --> NORM
    QUERY --> NORM
    NORM --> DOT
    DOT --> GATE
    FLATTEN --> VALUE
    GATE --> OUTPUT
    VALUE --> OUTPUT
    OUTPUT --> SHORTCONV
    SHORTCONV --> OUTPUT
    OUTPUT --> RESIDUAL
    HIDDEN_IN --> RESIDUAL
```

**Phase 3: Output Projection**

```mermaid
graph TB
    HIDDEN_HC["hidden_states<br/>[B, L, HC_MULT, D]<br/>[1, 13, 4, 1024]"]
    
    SELECT["hidden_states[:,:,0,:]<br/>(line 416)<br/>Select first HC path"]
    
    HIDDEN_2D["hidden_states<br/>[B, L, D]<br/>[1, 13, 1024]"]
    
    PROJ["nn.Linear<br/>(line 417)<br/>hidden_size → vocab_size"]
    
    LOGITS["output<br/>[B, L, vocab_size]<br/>[1, 13, 129280]"]
    
    HIDDEN_HC --> SELECT
    SELECT --> HIDDEN_2D
    HIDDEN_2D --> PROJ
    PROJ --> LOGITS
```

**Sources:** [engram_demo_v1.py:409-419](), [engram_demo_v1.py:358-378](), [engram_demo_v1.py:389-394]()

---

## Demo Text Processing Example

The demo uses a fixed input text to demonstrate the complete pipeline:

### Input Text

```
"Only Alexander the Great could tame the horse Bucephalus."
```

### Tokenization Process

```mermaid
graph LR
    TEXT["Input Text<br/>'Only Alexander...'"]
    
    TOK_RAW["AutoTokenizer<br/>(line 404-405)<br/>DeepSeek-V3 tokenizer"]
    
    RAW_IDS["Raw Token IDs<br/>[B, L]<br/>Uncompressed vocabulary"]
    
    COMPRESS["CompressedTokenizer<br/>(line 299)<br/>Normalize & deduplicate"]
    
    COMP_IDS["Compressed IDs<br/>Reduced vocabulary space"]
    
    HASH["NgramHashMapping<br/>(line 363)<br/>Generate 2-gram, 3-gram hashes"]
    
    HASH_IDS["Hash Addresses<br/>[B, L, num_heads*num_ngrams]"]
    
    TEXT --> TOK_RAW
    TOK_RAW --> RAW_IDS
    RAW_IDS --> COMPRESS
    COMPRESS --> COMP_IDS
    COMP_IDS --> HASH
    HASH --> HASH_IDS
```

**Tokenization Details:**

| Stage | Shape | Vocabulary Size | Purpose |
|-------|-------|-----------------|---------|
| Raw Tokens | `[1, 13]` | 129,280 | Standard DeepSeek-V3 tokenization |
| Compressed Tokens | `[1, 13]` | ~80,000 (typical) | Normalized, deduplicated vocabulary |
| Hash Addresses | `[1, 13, 16]` | 16 heads (8 per N-gram type) | Per-layer N-gram embedding addresses |

**Sources:** [engram_demo_v1.py:403-405](), [engram_demo_v1.py:60-121](), [engram_demo_v1.py:298-303]()

---

## Interpreting Demo Output

### Success Indicators

When the demo runs successfully, you should observe:

1. **No Errors:** Module initialization and forward pass complete without exceptions
2. **Shape Consistency:** Output shape matches expected `[batch_size, sequence_length, vocab_size]`
3. **Completion Message:** `✅ Forward Complete!` printed to console

### Output Tensor Analysis

```mermaid
graph TB
    OUTPUT["output tensor<br/>[1, 13, 129280]"]
    
    subgraph "Dimensions"
        DIM0["Dimension 0: Batch<br/>Size = 1<br/>(single example)"]
        DIM1["Dimension 1: Sequence<br/>Size = 13<br/>(13 tokens)"]
        DIM2["Dimension 2: Vocabulary<br/>Size = 129280<br/>(logit per token)"]
    end
    
    OUTPUT --> DIM0
    OUTPUT --> DIM1
    OUTPUT --> DIM2
    
    DIM2 --> SOFTMAX["Can apply softmax<br/>for probability distribution"]
    SOFTMAX --> NEXT_TOKEN["Predict next token<br/>at each position"]
```

**Key Observations:**

- The output represents **unnormalized logits** for next-token prediction
- Each position in the sequence has a distribution over the entire vocabulary
- For generation tasks, apply `softmax` along dimension 2, then sample or take `argmax`
- The demo does **not** implement autoregressive generation; it performs a single forward pass

**Sources:** [engram_demo_v1.py:421-422]()

---

## Next Steps

After successfully running the demo, consider the following paths:

### Understanding Components

Explore individual components in depth:

- **N-gram Hashing:** See [N-gram Hash Mapping](#4.2) for deterministic addressing details
- **Multi-Head Embeddings:** See [Multi-Head Embedding and ShortConv](#4.4) for embedding architecture
- **Configuration:** See [Configuration Reference](#4.6) for parameter tuning

### Architectural Concepts

Understand the theoretical foundations:

- **Conditional Memory:** See [Conditional Memory vs Conditional Computation](#2.1)
- **Scaling Laws:** See [Sparsity Allocation and U-shaped Scaling Law](#2.3)
- **Memory Hierarchy:** See [Memory Hierarchy and Offloading](#3.4)

### Experimental Results

Review validation evidence:

- **Performance Metrics:** See [Engram-27B Model Results](#5.1)
- **Long Context:** See [Long Context Evaluation](#5.2)
- **Baseline Comparisons:** See [Baseline Comparisons](#5.4)

### Research Foundation

Consult the research paper:

- **PDF Document:** `Engram_paper.pdf` in repository root
- **Paper Summary:** See [Paper Summary](#7.1)
- **Mechanistic Analysis:** See [Mechanistic Analysis](#7.2)

### Modification Guidelines

To experiment with the demo:

1. **Adjust N-gram Size:** Modify `max_ngram_size` in `EngramConfig` (lines 42-43)
2. **Change Integration Layers:** Modify `layer_ids` in `EngramConfig` (line 45)
3. **Alter Hyper-connections:** Modify `hc_mult` in `BackBoneConfig` (line 53)
4. **Test Different Text:** Replace the sample text at line 403

**Important:** The demo is simplified for illustration. Production deployment requires:
- Custom CUDA kernels for efficient N-gram hashing
- Distributed training infrastructure (All2All communication)
- Memory offloading mechanisms for large embedding tables
- Integration with full Attention and MoE implementations

**Sources:** [README.md:78-93](), [engram_demo_v1.py:1-19]()

---

