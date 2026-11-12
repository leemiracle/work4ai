<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RetrievalAttention · page 2 Attention Mechanisms · fetched 2026-10-26 -->

# Attention Mechanisms

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [attn_hub/__init__.py](attn_hub/__init__.py)

</details>



## Purpose and Scope

This document provides an overview of the attention mechanisms implemented in the RetroInfer system. The attention hub serves as the central coordination layer that provides different attention implementations for long-context LLM inference. This page covers the high-level architecture and integration of attention mechanisms, while detailed implementation specifics are covered in [Flash Attention](#2.1) and [RetroInfer Attention](#2.2).

For information about the broader system architecture that these attention mechanisms support, see [System Architecture](#1.1). For performance benchmarking of these attention implementations, see [Benchmarking and Evaluation](#3).

## Attention Hub Architecture

The attention hub provides a unified interface for different attention implementations, supporting both prefill and decode phases of inference. The system is designed to allow seamless switching between attention mechanisms while maintaining consistent interfaces.

### Attention Hub Structure

```mermaid
graph TB
    subgraph "attn_hub Module"
        INIT["__init__.py<br/>Entry Point"]
        FLASH_MOD["flash_attn.py<br/>Flash Attention Implementation"]
        RETRO_MOD["retroinfer_attn.py<br/>RetroInfer Implementation"]
    end
    
    subgraph "Exported Functions"
        FLASH_PREFILL["prefill_full_flash_attn()"]
        FLASH_DECODE["decode_full_flash_attn()"]
        RETRO_PREFILL["retroinfer_prefill_attn()"]
        RETRO_DECODE["retroinfer_decode_attn()"]
    end
    
    subgraph "Inference Phases"
        PREFILL["Prefill Phase<br/>Parallel Processing"]
        DECODE["Decode Phase<br/>Sequential Generation"]
    end
    
    INIT --> FLASH_PREFILL
    INIT --> FLASH_DECODE
    INIT --> RETRO_PREFILL
    INIT --> RETRO_DECODE
    
    FLASH_MOD --> FLASH_PREFILL
    FLASH_MOD --> FLASH_DECODE
    RETRO_MOD --> RETRO_PREFILL
    RETRO_MOD --> RETRO_DECODE
    
    FLASH_PREFILL --> PREFILL
    RETRO_PREFILL --> PREFILL
    FLASH_DECODE --> DECODE
    RETRO_DECODE --> DECODE
```

Sources: [attn_hub/__init__.py:1-3]()

## Attention Implementation Types

The RetroInfer system provides two primary attention implementations, each optimized for different use cases and performance characteristics.

### Implementation Comparison

| Aspect | Flash Attention | RetroInfer Attention |
|--------|----------------|---------------------|
| Purpose | Baseline/Full attention | Sparse attention with caching |
| Memory Usage | Higher (full attention) | Lower (selective attention) |
| Throughput | Standard | 4.5x-10.5x improvement |
| Accuracy | Full precision | Minimal degradation |
| Implementation | `flash_attn` module | `retroinfer_attn` module |

### Function Interface Pattern

Both attention implementations follow a consistent interface pattern with separate functions for prefill and decode phases:

```mermaid
graph LR
    subgraph "Flash Attention Functions"
        FLASH_PREFILL_FUNC["prefill_full_flash_attn"]
        FLASH_DECODE_FUNC["decode_full_flash_attn"]
    end
    
    subgraph "RetroInfer Attention Functions"
        RETRO_PREFILL_FUNC["retroinfer_prefill_attn"]
        RETRO_DECODE_FUNC["retroinfer_decode_attn"]
    end
    
    subgraph "Common Interface"
        PREFILL_INTERFACE["Prefill Interface<br/>Parallel token processing"]
        DECODE_INTERFACE["Decode Interface<br/>Sequential generation"]
    end
    
    FLASH_PREFILL_FUNC --> PREFILL_INTERFACE
    RETRO_PREFILL_FUNC --> PREFILL_INTERFACE
    FLASH_DECODE_FUNC --> DECODE_INTERFACE
    RETRO_DECODE_FUNC --> DECODE_INTERFACE
```

Sources: [attn_hub/__init__.py:2-3]()

## Integration with Model Processing

The attention hub integrates with the broader RetroInfer system to provide attention computation for different model architectures and processing phases.

### System Integration Flow

```mermaid
graph TB
    subgraph "Model Layer"
        LLAMA["LlamaModel"]
        QWEN["QwenModel"]
    end
    
    subgraph "Attention Hub"
        ATTN_HUB["attn_hub"]
        FLASH_ATTN["flash_attn"]
        RETRO_ATTN["retroinfer_attn"]
    end
    
    subgraph "Core Components"
        WAVE_INDEX["Wave Index<br/>Sparse attention selection"]
        WAVE_BUFFER["Wave Buffer<br/>GPU-CPU coordination"]
        KV_CACHE["KV Cache<br/>Vector storage"]
    end
    
    subgraph "Hardware Layer"
        GPU["GPU Computation"]
        CPU["CPU Storage"]
    end
    
    LLAMA --> ATTN_HUB
    QWEN --> ATTN_HUB
    
    ATTN_HUB --> FLASH_ATTN
    ATTN_HUB --> RETRO_ATTN
    
    RETRO_ATTN --> WAVE_INDEX
    RETRO_ATTN --> WAVE_BUFFER
    RETRO_ATTN --> KV_CACHE
    
    WAVE_BUFFER --> GPU
    WAVE_BUFFER --> CPU
    
    FLASH_ATTN --> GPU
```

Sources: [attn_hub/__init__.py:1-3]()

## Usage Patterns

The attention hub is designed to support different usage patterns depending on the performance requirements and accuracy needs of the application.

### Selection Criteria

The choice between attention implementations depends on several factors:

- **Full Flash Attention**: Used for baseline comparisons and when maximum accuracy is required
- **RetroInfer Attention**: Used for production inference where throughput optimization is critical

### Configuration Integration

The attention mechanisms integrate with the broader configuration system to support different model and dataset combinations. Configuration parameters such as `budget_ratio` and `estimate_ratio` control the behavior of the RetroInfer attention implementation.

Sources: [attn_hub/__init__.py:1-3]()

---

