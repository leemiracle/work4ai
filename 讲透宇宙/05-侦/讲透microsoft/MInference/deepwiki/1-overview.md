<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/MInference · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minference/version.py](minference/version.py)

</details>



This document provides a comprehensive introduction to the MInference repository, which contains two primary components designed to accelerate and evaluate large language models (LLMs) with long contexts.

## Purpose and Scope

MInference is a framework that significantly accelerates inference for large language models, particularly when processing long contexts (up to 1 million tokens). It achieves this through dynamic sparse attention patterns and KV cache optimization techniques. This overview explains the system architecture, key components, and how they interact to provide up to 10x faster processing while maintaining accuracy.

For more detailed information about usage examples, see [Usage Examples](#6). For instructions on contributing to the project, see [Contributing and Development](#7).

## System Architecture

The MInference repository consists of two main components: the MInference framework (the acceleration system) and SCBench (the evaluation benchmark).

### High-Level Architecture

```mermaid
graph TD
    subgraph "MInference Repository"
        A["MInference Framework"] --- B["SCBench Benchmark"]
    end
    
    subgraph "MInference Components"
        A --> C["Model Patching System"]
        A --> D["Sparse Attention Kernels"]
        A --> E["KV Cache Optimizations"]
    end
    
    subgraph "SCBench Components"
        B --> F["GreedySearch (Multi-Turn)"]
        B --> G["GreedySearch_vllm (Multi-Request)"]
        B --> H["Task Datasets"]
    end
    
    C --> C1["patch_hf() for HuggingFace"]
    C --> C2["patch_vllm() for vLLM"]
    
    D --> D1["vertical_slash_sparse_attention()"]
    D --> D2["block_sparse_attention()"]
    D --> D3["a_shape_kernel()"]
    D --> D4["flexprefill_forward()"]
    
    E --> E1["SnapKVCache"]
    E --> E2["PyramidKVCache"]
    E --> E3["KiviCache"]
    E --> E4["QuestCache"]
    E --> E5["RetrAttnCache"]
    
    H --> H1["scbench_kv (String Retrieval)"]
    H --> H2["scbench_repoqa (Semantic Retrieval)"]
    H --> H3["scbench_summary (Global Processing)"]
    H --> H4["scbench_mf (Multi-Tasking)"]
```

Sources: [README.md:40-55]()

## MInference Framework

The core of the repository is the MInference framework, which leverages dynamic sparse attention patterns to accelerate LLM inference. The framework identifies that attention in LLMs naturally exhibits sparse patterns and exploits this characteristic to reduce computation while maintaining model accuracy.

### MInference Workflow

```mermaid
flowchart LR
    UserCode(["User Application"]) --> MInferenceClass
    
    subgraph "MInference System"
        MInferenceClass["MInference Class"] --> MInferenceConfig["MInferenceConfig"]
        MInferenceConfig --> PatternSearch["Pattern Search"]
        PatternSearch --> PatternConfig[("Sparsity Pattern Config")]
        
        MInferenceClass --> ModelPatcher["Model Patching System"]
        ModelPatcher --> |"attn_type parameter"| AttentionTypes
        ModelPatcher --> |"kv_type parameter"| KVTypes
        
        AttentionTypes --> |"minference"| MinferenceAttn["minference_forward()"]
        AttentionTypes --> |"a_shape"| AShape["a_shape_kernel()"]
        AttentionTypes --> |"tri_shape"| TriShape["tri_shape_kernel()"]
        AttentionTypes --> |"flexprefill"| FlexPrefill["flexprefill_forward()"]
        
        KVTypes --> |"dense"| DenseKV["Standard KV Cache"]
        KVTypes --> |"snapkv"| SnapKV["SnapKVCache"]
        KVTypes --> |"pyramidkv"| PyramidKV["PyramidKVCache"]
        KVTypes --> |"kivi"| KIVI["KiviCache"]
        KVTypes --> |"quest"| Quest["QuestCache"]
        KVTypes --> |"retr_attn"| RetrAttn["RetrAttnCache"]
    end
    
    ModelPatcher --> PatchedModel["Patched Model"]
    PatchedModel --> Output(["Accelerated Inference"])
```

Sources: [README.md:110-168]()

The workflow diagram illustrates how MInference integrates with existing models:

1. Users initialize MInference with specific attention and KV cache types
2. MInference patches the model architecture with the optimized modules
3. The patched model performs accelerated inference with the selected optimizations

### Dynamic Sparse Attention Mechanism

```mermaid
flowchart TD
    subgraph "Dynamic Sparse Attention Pipeline"
        A["Input Query/Key/Value"] --> B["Sparsity Pattern Selection"]
        B --> |"Offline Analysis"| C["Pattern from Pre-computed Config"]
        B --> |"Dynamic Search"| C2["Runtime Pattern Search"]
        
        C --> D["Apply Sparse Pattern"]
        C2 --> D
        
        D --> E["Vertical/Slash Pattern"]
        D --> F["Block Sparse Pattern"]
        D --> G["A-Shape Pattern"]
        D --> H["Tri-Shape Pattern"]
        
        E --> V["vertical_slash_sparse_attention()"]
        F --> BS["block_sparse_attention()"]
        G --> AS["a_shape_kernel()"]
        H --> TS["tri_shape_kernel()"]
        
        V --> Output["Optimized Attention Output"]
        BS --> Output
        AS --> Output
        TS --> Output
    end
```

Sources: [README.md:80-87]()

MInference's primary innovation is its approach to sparse attention:

1. **Offline Analysis**: Pre-determines which sparse pattern each attention head belongs to
2. **Dynamic Computation**: Approximates sparse indices at runtime
3. **Optimized Kernels**: Uses custom kernels for each pattern type to maximize efficiency

## KV Cache Lifecycle

A key concept in MInference is the KV cache lifecycle, which consists of four stages:

```mermaid
flowchart TD
    subgraph "KV Cache Lifecycle"
        A["① Generation"] --> B["② Compression"]
        B --> C["③ Retrieval"]
        C --> D["④ Loading"]
    end
    
    subgraph "MInference Methods"
        A --> A1["MInference"]
        A --> A2["FlexPrefill"]
        A --> A3["A-shape/Tri-shape"]
        
        B --> B1["SnapKV"]
        B --> B2["PyramidKV"]
        B --> B3["KIVI"]
        B --> B4["StreamingLLM"]
        
        C --> C1["CacheBlend"]
        
        D --> D1["Quest"]
        D --> D2["RetrievalAttention"]
    end
```

Sources: [README.md:80-87]()

MInference provides optimizations for each stage:

1. **Generation**: Creating KV cache during initial processing (using dynamic sparse attention)
2. **Compression**: Reducing the size of KV cache for efficiency
3. **Retrieval**: Selecting relevant KV cache entries
4. **Loading**: Utilizing retrieved KV cache for inference

## SCBench Benchmark Suite

SCBench (SharedContextBench) is a benchmark suite specifically designed to evaluate long-context methods from a KV cache-centric perspective. It provides a comprehensive framework for assessing the performance of different optimization techniques.

### Evaluation Modes

SCBench implements two primary evaluation modes:

1. **Multi-Turn Mode**: Simulates conversations where context builds up over multiple interactions
2. **Multi-Request Mode**: Evaluates handling of shared context across multiple separate requests

### Task Categories

SCBench includes tasks across four categories of long-context capabilities:

| Category | Description | Example Dataset |
|----------|-------------|-----------------|
| String Retrieval | Finding exact matches in long contexts | scbench_kv |
| Semantic Retrieval | Finding conceptually related information | scbench_repoqa |
| Global Processing | Understanding information across the entire context | scbench_summary |
| Multi-Tasking | Handling multiple tasks with the same context | scbench_mf |

Sources: [README.md:191-217]()

## Supported Features

### Supported Models

MInference supports a wide range of LLMs, including:

| Model Family | Supported Variants |
|--------------|-------------------|
| Qwen2.5 | 7B, 32B, 72B, and 1M versions |
| LLaMA-3.1 | 8B, 70B |
| LLaMA-3 | 8B, 70B with various context lengths |
| GLM-4 | 9B with 1M context |
| Yi | 9B with 200K context |
| Phi-3 | mini with 128K context |
| Qwen2 | 7B |

Sources: [README.md:101-109]()

### Efficient Methods

MInference supports various efficient methods categorized by KV cache lifecycle stage:

| Lifecycle Stage | Supported Methods |
|-----------------|-------------------|
| KV Cache Generation | MInference, FlexPrefill, A-shape, Tri-shape, MInference w/ static, Dilated, Strided |
| KV Cache Compression | StreamingLLM, SnapKV, PyramidKV, KIVI |
| KV Cache Retrieval | CacheBlend |
| KV Cache Loading | Quest, RetrievalAttention |

Sources: [README.md:80-87]()

## Integration Architecture

```mermaid
graph TD
    subgraph "External Frameworks"
        HF["HuggingFace Transformers"]
        VLLM["vLLM"]
    end
    
    subgraph "MInference Components"
        Patch["MInference Model Patching"]
        Config["MInferenceConfig"]
        
        Forward["Forward Pass Modules"]
        Forward --> MinFwd["minference_forward()"]
        Forward --> FlexFwd["flexprefill_forward()"]
        Forward --> AShapeFwd["a_shape_kernel()"]
        Forward --> TriShapeFwd["tri_shape_kernel()"]
        
        KVCache["KV Cache Modules"]
        KVCache --> SnapKV["SnapKVCache"]
        KVCache --> PyramidKV["PyramidKVCache"]
        KVCache --> KiviCache["KiviCache"]
        KVCache --> QuestCache["QuestCache"]
        KVCache --> RetrAttnCache["RetrAttnCache"]
        
        Kernels["Custom Attention Kernels"]
        Kernels --> VerticalSlash["vertical_slash_sparse_attention()"]
        Kernels --> BlockSparse["block_sparse_attention()"]
        Kernels --> Streaming["streaming_forward()"]
    end
    
    HF --> |"patch_hf()"| Patch
    VLLM --> |"patch_vllm()"| Patch
    
    Patch --> |"Uses"| Config
    Patch --> |"Modifies"| Forward
    Patch --> |"Configures"| KVCache
    Forward --> |"Uses"| Kernels
```

Sources: [README.md:110-168]()

This diagram illustrates how MInference integrates with external LLM frameworks:

1. MInference provides patching methods for both HuggingFace and vLLM frameworks
2. The patching system modifies the model's forward pass and KV cache implementations
3. Custom attention kernels provide the core optimization functionality

## Current Version

MInference is currently at version 0.1.6 as indicated in the version file.

Sources: [minference/version.py:4-14]()

---

