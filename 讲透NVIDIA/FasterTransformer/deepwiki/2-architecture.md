<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/FasterTransformer · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/fastertransformer/kernels/decoder_masked_multihead_attention.cu](src/fastertransformer/kernels/decoder_masked_multihead_attention.cu)
- [src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_112.cu](src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_112.cu)
- [src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_48.cu](src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_48.cu)
- [src/fastertransformer/kernels/gpt_kernels.cu](src/fastertransformer/kernels/gpt_kernels.cu)
- [src/fastertransformer/kernels/gpt_kernels.h](src/fastertransformer/kernels/gpt_kernels.h)
- [src/fastertransformer/kernels/stop_criteria_kernels.cu](src/fastertransformer/kernels/stop_criteria_kernels.cu)
- [src/fastertransformer/layers/attention_layers/DecoderCrossAttentionLayer.cu](src/fastertransformer/layers/attention_layers/DecoderCrossAttentionLayer.cu)
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc](src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc)
- [src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h](src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h)
- [src/fastertransformer/th_op/common/GptOps.cc](src/fastertransformer/th_op/common/GptOps.cc)
- [src/fastertransformer/utils/CMakeLists.txt](src/fastertransformer/utils/CMakeLists.txt)
- [tests/decoding/tf_fused_self_multihead_attention_unit_test.py](tests/decoding/tf_fused_self_multihead_attention_unit_test.py)
- [tests/unittests/test_gpt_kernels.cu](tests/unittests/test_gpt_kernels.cu)

</details>



This document describes the core architecture of FasterTransformer, a library for accelerated transformer model inference. It covers the main components, their interactions, and optimization strategies employed throughout the system. For information about specific model implementations, please see [Models](#3), and for details on performance optimization techniques, see [Optimization Techniques](#5).

## Core Components and Design

FasterTransformer is architected around high-performance CUDA implementations of transformer components with a focus on inference optimization. The library provides specialized implementations for various transformer architectures such as GPT, BERT, T5, and others, while maintaining a unified framework for common operations.

```mermaid
graph TB
    subgraph "Core Components"
        direction LR
        BaseLayer["BaseLayer<T>"]
        
        subgraph "Models"
            ParallelGpt["ParallelGpt<T>"]
            Bert["Bert<T>"]
            T5["T5<T>"]
            DecoderBase["DecoderBase<T>"]
        end
        
        subgraph "Attention Layers"
            Attn["Attention Layer"]
            SelfAttn["DecoderSelfAttentionLayer<T>"]
            CrossAttn["DecoderCrossAttentionLayer<T>"]
        end
        
        subgraph "CUDA Kernels"
            MaskedMHA["Masked Multihead Attention"]
            FusedQKV["Fused QKV Computation"]
            StopCriteria["Stop Criteria Kernels"]
        end
        
        subgraph "Memory Management"
            MemoryUtils["Memory Utilities"]
            TensorClass["Tensor Class"]
        end
        
        subgraph "Framework Integration"
            TensorRT["TensorRT Plugins"]
            PyTorch["PyTorch Ops"]
            TensorFlow["TensorFlow Ops"]
            Triton["Triton Backend"]
        end
        
        BaseLayer --> ParallelGpt
        BaseLayer --> Bert
        BaseLayer --> T5
        BaseLayer --> DecoderBase
        
        ParallelGpt --> SelfAttn
        DecoderBase --> SelfAttn
        DecoderBase --> CrossAttn
        
        SelfAttn --> MaskedMHA
        CrossAttn --> MaskedMHA
        SelfAttn --> FusedQKV
        
        ParallelGpt --> StopCriteria
        
        ParallelGpt --> MemoryUtils
        Bert --> MemoryUtils
        T5 --> MemoryUtils
        MemoryUtils --> TensorClass
        
        ParallelGpt --> PyTorch
        ParallelGpt --> TensorFlow
        ParallelGpt --> TensorRT
        ParallelGpt --> Triton
    end
```

Sources: 
- [README.md:82-97]()
- [src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h:32-247]()
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc:17-22]()
- [src/fastertransformer/utils/CMakeLists.txt:17-105]()

### Class Hierarchy

FasterTransformer organizes its components in a hierarchical structure with `BaseLayer` as the foundation. All model implementations and layer components inherit from this base class, which provides common functionality like memory management.

```mermaid
classDiagram
    BaseLayer <|-- AttentionLayer
    BaseLayer <|-- ModelClass
    AttentionLayer <|-- DecoderSelfAttentionLayer
    AttentionLayer <|-- DecoderCrossAttentionLayer
    ModelClass <|-- ParallelGpt
    ModelClass <|-- Bert
    ModelClass <|-- T5
    
    class BaseLayer {
        +allocator_
        +stream_
        +cublas_wrapper_
        +allocateBuffer()
        +freeBuffer()
    }
    
    class AttentionLayer {
        +computeAttention()
        +prepareAttentionMask()
    }
    
    class DecoderSelfAttentionLayer {
        +forward()
        +fusedQKV_masked_attention_dispatch()
    }
    
    class DecoderCrossAttentionLayer {
        +forward()
        +cross_attention_dispatch()
    }
    
    class ModelClass {
        +forward()
        +initialize()
    }
    
    class ParallelGpt {
        +gpt_decoder_
        +gpt_context_decoder_
        +dynamic_decode_layer_
        +forward()
    }
```

Sources:
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc:192-456]()
- [src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h:32-85]()

## Memory Management

FasterTransformer implements custom memory management to optimize GPU memory utilization for transformer models.

### Memory Allocation Strategy

The library uses a custom allocator system that efficiently handles the allocation and reuse of GPU memory. Each component has `allocateBuffer()` and `freeBuffer()` methods that manage the memory required for operations.

```mermaid
sequenceDiagram
    participant Model as "Model (e.g., ParallelGpt)"
    participant Layer as "Layer Components"
    participant Allocator as "IAllocator"
    participant GPU as "GPU Memory"
    
    Model->>Allocator: initialize
    
    Model->>Layer: forward()
    Layer->>Allocator: allocateBuffer(size)
    Allocator->>GPU: cudaMalloc()
    GPU-->>Allocator: device_ptr
    Allocator-->>Layer: return buffer_ptr
    
    Layer-->>Model: return results
    
    alt is_free_buffer_after_forward
        Model->>Layer: freeBuffer()
        Layer->>Allocator: free(buffer_ptr)
        Allocator->>GPU: cudaFree()
    end
```

Sources:
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc:192-236]()
- [src/fastertransformer/utils/CMakeLists.txt:51-54]()

## Attention Mechanisms

Attention mechanisms are core to transformer models, and FasterTransformer provides highly optimized implementations for both self-attention and cross-attention.

### Self-Attention

The self-attention mechanism allows a model to attend to different positions within its own input sequence. FasterTransformer implements optimized self-attention for decoder models.

```mermaid
flowchart TB
    subgraph "DecoderSelfAttentionLayer"
        QKV["QKV Computation"]
        MHA["Masked Multi-head Attention"]
        Proj["Projection"]
    end
    
    Input["Input Query"] --> QKV
    QKV --> MHA
    KeyCache["Key Cache"] --> MHA
    ValueCache["Value Cache"] --> MHA
    MHA --> Proj
    Proj --> Output["Attention Output"]
    MHA --> KeyCacheOut["Updated Key Cache"]
    MHA --> ValueCacheOut["Updated Value Cache"]
```

Sources:
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc:459-615]()
- [src/fastertransformer/kernels/decoder_masked_multihead_attention.cu:16-139]()

### Cross-Attention

Cross-attention allows the decoder to attend to the encoder's output sequence. It's essential for encoder-decoder architectures like T5 and BART.

```mermaid
flowchart TB
    subgraph "DecoderCrossAttentionLayer"
        Q["Query Computation"]
        KV["Key-Value Cache"]
        CA["Cross Attention"]
        Proj["Projection"]
    end
    
    InputQuery["Decoder Hidden State"] --> Q
    MemoryK["Encoder Memory Keys"] --> KV
    MemoryV["Encoder Memory Values"] --> KV
    Q --> CA
    KV --> CA
    CA --> Proj
    Proj --> Output["Cross-Attention Output"]
```

Sources:
- [src/fastertransformer/layers/attention_layers/DecoderCrossAttentionLayer.cu:33-546]()

### Attention Optimizations

FasterTransformer implements several optimizations for attention computation:

1. **Fused QKV Computation**: Computing query, key, and value projections in a single GEMM operation.
2. **Specialized kernels** for different head dimensions (e.g., 48, 64, 80, 128, etc.).
3. **Cache-optimized attention**: Efficiently using K/V caches for auto-regressive decoding.

Sources:
- [src/fastertransformer/kernels/decoder_masked_multihead_attention.cu:28-135]()
- [src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_112.cu:27-101]()
- [src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_48.cu:27-100]()

## Parallelism Strategies

FasterTransformer supports different parallelism strategies to distribute computation across multiple GPUs for large models.

### Tensor Parallelism

Tensor parallelism splits individual tensors across multiple GPUs, allowing larger model sizes to fit in GPU memory.

```mermaid
graph LR
    subgraph "Tensor Parallelism"
        direction TB
        subgraph "GPU 0"
            A0["Attention (First Half)"]
            F0["FFN (First Half)"]
        end
        subgraph "GPU 1"
            A1["Attention (Second Half)"]
            F1["FFN (Second Half)"]
        end
        
        Input0["Input"] --> A0
        Input0 --> A1
        A0 --> |AllReduce| MidPoint0["Hidden State"]
        A1 --> |AllReduce| MidPoint0
        MidPoint0 --> F0
        MidPoint0 --> F1
        F0 --> |AllReduce| Output0["Output"]
        F1 --> |AllReduce| Output0
    end
```

Sources:
- [src/fastertransformer/utils/CMakeLists.txt:63-68]()
- [src/fastertransformer/utils/CMakeLists.txt:83-86]()

### Pipeline Parallelism

Pipeline parallelism distributes transformer layers across multiple GPUs, with each GPU handling a subset of the layers.

```mermaid
graph LR
    subgraph "Pipeline Parallelism"
        direction TB
        subgraph "GPU 0"
            L0["Layers 0-3"]
        end
        subgraph "GPU 1"
            L1["Layers 4-7"]
        end
        subgraph "GPU 2"
            L2["Layers 8-11"]
        end
        
        Input1["Input"] --> L0
        L0 --> L1
        L1 --> L2
        L2 --> Output1["Output"]
    end
```

Sources:
- [src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h:62-63]()

## Data Flows and Components

The following diagram illustrates the data flow in a GPT model implemented in FasterTransformer:

```mermaid
flowchart TB
    Input["Input Ids"] --> Embedding["Embedding Layer"]
    Embedding --> ContextDecoder["Context Decoder\nParallelGptContextDecoder"]
    ContextDecoder --> DecoderInput["Decoder Input"]
    DecoderInput --> Decoder["Auto-regressive Decoder\nParallelGptDecoder"]
    
    subgraph "ParallelGptDecoder"
        SelfAttn["Self Attention\nDecoderSelfAttentionLayer"] --> FFN["Feed Forward Network"]
        KeyCache["Key Cache"] <--> SelfAttn
        ValueCache["Value Cache"] <--> SelfAttn
    end
    
    Decoder --> HiddenStates["Hidden States"]
    HiddenStates --> DynamicDecode["Dynamic Decode Layer"]
    
    subgraph "DynamicDecodeLayer"
        Logits["Compute Logits"] --> Sampling["Sampling/Beam Search"]
        StopCriteria["Stop Criteria"] --> Sampling
    end
    
    DynamicDecode --> NextToken["Next Token"]
    NextToken --> Decoder
    NextToken --> Output["Output Sequence"]
```

Sources:
- [src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.h:84-176]()
- [src/fastertransformer/kernels/gpt_kernels.cu:29-188]()
- [src/fastertransformer/kernels/stop_criteria_kernels.cu:24-157]()

## CUDA Kernels

FasterTransformer extensively uses custom CUDA kernels to maximize performance for transformer operations:

| Kernel Category | Purpose | Key Functions |
|-----------------|---------|--------------|
| Attention Kernels | Computing self and cross attention | `masked_multihead_attention_kernel`, `cross_attention_kernel` |
| Embedding Kernels | Input embedding and position encoding | `invokeInputIdsEmbeddingLookupPosEncoding` |
| Stop Criteria Kernels | Determining when to stop generation | `invokeStopWordsCriterion`, `invokeLengthCriterion` |
| Memory Optimization | Managing shared contexts, deduplication | `invokeFindContextDups`, `invokeCompactInputs` |
| Transformation Kernels | Data layout transformations | `invokeTransposeAxis01` |

Sources:
- [src/fastertransformer/kernels/decoder_masked_multihead_attention.cu:25-135]()
- [src/fastertransformer/kernels/gpt_kernels.cu:29-103]()
- [src/fastertransformer/kernels/stop_criteria_kernels.cu:24-157]()

## Framework Integration

FasterTransformer provides integration with popular deep learning frameworks through custom operators and plugins.

```mermaid
graph TB
    FT["FasterTransformer Core"]
    
    subgraph "TensorFlow"
        TFOp["Custom TF Ops"]
        TFModel["TF Model with FT Ops"]
    end
    
    subgraph "PyTorch"
        THOp["Custom PyTorch Ops"]
        THModel["PyTorch Model with FT Ops"]
    end
    
    subgraph "Deployment"
        TRT["TensorRT Plugins"]
        Triton["Triton Inference Server"]
    end
    
    FT --> TFOp
    FT --> THOp
    FT --> TRT
    FT --> Triton
    
    TFOp --> TFModel
    THOp --> THModel
    TFModel --> Triton
    THModel --> Triton
    TRT --> Triton
```

Sources:
- [README.md:82-97]()
- [src/fastertransformer/th_op/common/GptOps.cc:16-69]()
- [tests/decoding/tf_fused_self_multihead_attention_unit_test.py:104-171]()

## Performance Optimization Techniques

FasterTransformer implements several optimization techniques to maximize inference performance:

1. **Kernel Fusion**: Combining multiple operations into a single CUDA kernel to reduce memory traffic and kernel launch overhead.
2. **Context Sharing**: Reusing computations for identical input sequences in a batch.
3. **Memory Management**: Custom memory allocators and reuse strategies to minimize allocation overhead.
4. **Quantization Support**: INT8, FP8, and other reduced precision formats for faster computation.

```mermaid
graph TD
    subgraph "Optimization Techniques"
        KF["Kernel Fusion"]
        CS["Context Sharing"]
        MM["Memory Management"]
        QZ["Quantization"]
        TP["Tensor Parallelism"]
        PP["Pipeline Parallelism"]
    end
    
    KF --> |"Reduces Memory Traffic"| Performance["Improved Performance"]
    CS --> |"Reduces Redundant Computation"| Performance
    MM --> |"Reduces Allocation Overhead"| Performance
    QZ --> |"Reduces Computation Cost"| Performance
    TP --> |"Enables Larger Models"| Performance
    PP --> |"Enables Larger Models"| Performance
```

Sources:
- [README.md:28-36]()
- [src/fastertransformer/kernels/gpt_kernels.cu:106-159]()
- [tests/unittests/test_gpt_kernels.cu:42-106]()

## Unique Features

FasterTransformer introduces several unique features for efficient transformer inference:

### Context Deduplication

For batched inference, FasterTransformer can identify and deduplicate identical input contexts to avoid redundant computation.

```mermaid
flowchart LR
    subgraph "Context Deduplication"
        Input["Input Batch\n[B×Seq×H]"] --> FindDups["Find Duplicate Contexts"]
        FindDups --> CompactInputs["Compact Inputs\n[Unique×Seq×H]"]
        CompactInputs --> ProcessUnique["Process Unique Contexts"]
        ProcessUnique --> UncompactOutputs["Uncompact Outputs\n[B×Seq×H]"]
        UncompactOutputs --> Output["Output Batch"]
    end
```

Sources:
- [src/fastertransformer/th_op/common/GptOps.cc:26-62]()
- [tests/unittests/test_gpt_kernels.cu:42-106]()

### Dynamic Shape Support

FasterTransformer supports dynamic shapes for both batch size and sequence length, allowing flexible deployment across various use cases.

```mermaid
flowchart TB
    subgraph "Dynamic Shape Handling"
        CheckBatch["Check Batch Size"]
        ReallocBuffer["Reallocate Buffer if Needed"]
        ProcessInput["Process Input"]
        
        CheckBatch -->|"Batch size changed"| ReallocBuffer
        CheckBatch -->|"Batch size unchanged"| ProcessInput
        ReallocBuffer --> ProcessInput
    end
```

Sources:
- [src/fastertransformer/layers/attention_layers/DecoderSelfAttentionLayer.cc:239-249]()

## Summary

FasterTransformer provides a highly optimized architecture for transformer model inference with a focus on performance and scalability. Its key strengths include:

1. Specialized implementations for different transformer architectures
2. Optimized CUDA kernels for critical operations
3. Support for various parallelism strategies
4. Integration with popular deep learning frameworks
5. Advanced memory management techniques
6. Support for model quantization and other optimizations

These features together make FasterTransformer an efficient solution for deploying transformer models in production environments.

---

