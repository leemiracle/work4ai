<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/open-infra-index · extra page FlashMLA · fetched 2026-10-30 -->

# FlashMLA

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

FlashMLA is an efficient Multi-Layer Attention (MLA) decoding kernel specifically optimized for NVIDIA Hopper GPUs. This component serves as a critical compute optimization layer within DeepSeek's inference system, handling attention computations for variable-length sequences in production environments. FlashMLA is designed to maximize both memory bandwidth utilization and computational throughput for the MLA architecture used in DeepSeek V3 and R1 models.

For information about general matrix operations optimization, see [DeepGEMM](#2.1.2). For distributed communication patterns in MoE architectures, see [DeepEP](#2.2.1). For the complete inference system architecture, see [Inference System Architecture](#3.1).

## Architecture Overview

### System Integration

```mermaid
graph TB
    subgraph "DeepSeek Inference Pipeline"
        CLIENT["Client Request"]
        NGINX["Nginx Load Balancer"]
        INFERENCE["Inference Service<br/>(vLLM Fork)"]
        FLASHMLA["FlashMLA Kernel<br/>MLA Attention Decoding"]
        KV_CACHE["Paged KV Cache<br/>Block Size 64"]
        GPU_MEM["H800 GPU Memory<br/>HBM3"]
    end
    
    subgraph "Model Processing"
        V3_MODEL["DeepSeek-V3 Model<br/>MoE Architecture"]
        R1_MODEL["DeepSeek-R1 Model"]
        ATTENTION_LAYERS["MLA Attention Layers"]
    end
    
    subgraph "Compute Resources"
        H800["NVIDIA H800 GPU<br/>Hopper Architecture"]
        BF16_UNITS["BF16 Tensor Cores"]
        MEMORY_BW["3000 GB/s Memory BW"]
    end
    
    CLIENT --> NGINX
    NGINX --> INFERENCE
    INFERENCE --> FLASHMLA
    FLASHMLA --> KV_CACHE
    FLASHMLA --> V3_MODEL
    FLASHMLA --> R1_MODEL
    V3_MODEL --> ATTENTION_LAYERS
    R1_MODEL --> ATTENTION_LAYERS
    ATTENTION_LAYERS --> FLASHMLA
    
    FLASHMLA --> H800
    H800 --> BF16_UNITS
    H800 --> MEMORY_BW
    KV_CACHE --> GPU_MEM
```

Sources: [README.md:32-41]()

### FlashMLA Core Components

```mermaid
graph TB
    subgraph "FlashMLA Kernel Architecture"
        INPUT_TOKENS["Input Token Sequence<br/>Variable Length"]
        MLA_KERNEL["FlashMLA Kernel"]
        
        subgraph "Memory Management"
            PAGED_KV["Paged KV Cache<br/>Block Size: 64"]
            CACHE_BLOCKS["Cache Block Pool"]
            MEMORY_ALLOCATOR["GPU Memory Allocator"]
        end
        
        subgraph "Compute Pipeline"
            ATTENTION_COMP["Attention Computation<br/>BF16 Precision"]
            TENSOR_CORES["H800 Tensor Cores<br/>580 TFLOPS BF16"]
            MEMORY_OPS["Memory Operations<br/>3000 GB/s Bandwidth"]
        end
        
        OUTPUT_TOKENS["Decoded Output Tokens"]
    end
    
    subgraph "Performance Optimization"
        VARIABLE_SEQ["Variable Sequence<br/>Length Optimization"]
        PRODUCTION_TESTED["Production Battle-tested<br/>Optimizations"]
    end
    
    INPUT_TOKENS --> MLA_KERNEL
    MLA_KERNEL --> PAGED_KV
    PAGED_KV --> CACHE_BLOCKS
    CACHE_BLOCKS --> MEMORY_ALLOCATOR
    
    MLA_KERNEL --> ATTENTION_COMP
    ATTENTION_COMP --> TENSOR_CORES
    TENSOR_CORES --> MEMORY_OPS
    
    ATTENTION_COMP --> OUTPUT_TOKENS
    VARIABLE_SEQ --> MLA_KERNEL
    PRODUCTION_TESTED --> MLA_KERNEL
```

Sources: [README.md:32-41]()

## Performance Characteristics

### Computational Performance

FlashMLA achieves dual performance optimization modes depending on the computational characteristics of the workload:

| Performance Mode | Throughput | Hardware Utilization | Use Case |
|------------------|------------|---------------------|----------|
| Memory-bound | 3000 GB/s | Memory bandwidth limited | Large sequence lengths, sparse attention patterns |
| Compute-bound | 580 TFLOPS BF16 | Tensor core utilization | Dense attention computations, shorter sequences |

### Hardware Optimization

```mermaid
graph TB
    subgraph "NVIDIA H800 Hopper Architecture"
        HOPPER["H800 GPU"]
        
        subgraph "Compute Units"
            TENSOR_CORES["4th Gen Tensor Cores<br/>BF16 Support"]
            SM_UNITS["Streaming Multiprocessors"]
            COMPUTE_580["580 TFLOPS BF16<br/>Peak Performance"]
        end
        
        subgraph "Memory Subsystem"
            HBM3["HBM3 Memory"]
            MEMORY_BW_3000["3000 GB/s<br/>Memory Bandwidth"]
            L2_CACHE["L2 Cache"]
        end
        
        subgraph "FlashMLA Optimizations"
            BF16_OPS["BF16 Operations<br/>Native Support"]
            PAGED_ACCESS["Paged Memory Access<br/>Block Size 64"]
            VAR_LENGTH["Variable Length<br/>Sequence Handling"]
        end
    end
    
    HOPPER --> TENSOR_CORES
    HOPPER --> SM_UNITS
    TENSOR_CORES --> COMPUTE_580
    
    HOPPER --> HBM3
    HBM3 --> MEMORY_BW_3000
    HBM3 --> L2_CACHE
    
    BF16_OPS --> TENSOR_CORES
    PAGED_ACCESS --> HBM3
    VAR_LENGTH --> SM_UNITS
```

Sources: [README.md:38-40]()

## Technical Implementation

### Paged KV Cache Architecture

FlashMLA implements a paged KV cache system with a fixed block size of 64 tokens. This design enables efficient memory utilization for variable-length sequences while maintaining high-performance access patterns optimized for the Hopper architecture.

| Cache Parameter | Value | Purpose |
|-----------------|-------|---------|
| Block Size | 64 tokens | Optimal memory alignment for H800 |
| Precision | BF16 | Balance between precision and performance |
| Access Pattern | Paged | Efficient variable-length sequence handling |

### Integration with Inference System

```mermaid
graph TB
    subgraph "Inference Request Flow"
        BATCH_REQUESTS["Batched Inference Requests"]
        PREFILL_PHASE["Prefill Phase Processing"]
        DECODE_PHASE["Decode Phase Processing"]
    end
    
    subgraph "FlashMLA Processing"
        MLA_PREFILL["FlashMLA Prefill<br/>Initial KV Cache Population"]
        MLA_DECODE["FlashMLA Decode<br/>Incremental Token Generation"]
        
        subgraph "Cache Management"
            KV_ALLOCATION["KV Cache Block<br/>Allocation"]
            KV_LOOKUP["KV Cache Block<br/>Lookup & Update"]
            BLOCK_POOL["Memory Block Pool<br/>Size 64 Management"]
        end
    end
    
    subgraph "Performance Modes"
        MEMORY_BOUND_MODE["Memory-bound Mode<br/>3000 GB/s"]
        COMPUTE_BOUND_MODE["Compute-bound Mode<br/>580 TFLOPS BF16"]
    end
    
    BATCH_REQUESTS --> PREFILL_PHASE
    BATCH_REQUESTS --> DECODE_PHASE
    
    PREFILL_PHASE --> MLA_PREFILL
    DECODE_PHASE --> MLA_DECODE
    
    MLA_PREFILL --> KV_ALLOCATION
    MLA_DECODE --> KV_LOOKUP
    KV_ALLOCATION --> BLOCK_POOL
    KV_LOOKUP --> BLOCK_POOL
    
    MLA_PREFILL --> MEMORY_BOUND_MODE
    MLA_DECODE --> COMPUTE_BOUND_MODE
```

Sources: [README.md:32-41]()

## Production Deployment

FlashMLA has been battle-tested in DeepSeek's production inference environment, serving as a core component for both DeepSeek V3 and R1 model inference. The kernel's optimization for variable-length sequences makes it particularly well-suited for real-world inference workloads where sequence lengths vary significantly across requests.

### Key Production Features

- **BF16 Native Support**: Full support for BF16 precision across all operations
- **Paged KV Cache**: Block-based cache management with 64-token blocks
- **Variable Sequence Optimization**: Efficient handling of varying input sequence lengths
- **Hopper Architecture Tuning**: Specifically optimized for NVIDIA H800 GPUs

The component integrates seamlessly with DeepSeek's broader inference infrastructure, working in conjunction with expert parallelism systems and load balancing mechanisms to deliver high-throughput, low-latency inference for production workloads.

Sources: [README.md:32-41]()

---

