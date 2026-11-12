<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/MInference · page 3 KV Cache Optimizations · fetched 2026-10-26 -->

# KV Cache Optimizations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minference/modules/kivi.py](minference/modules/kivi.py)
- [minference/modules/kvcompression.py](minference/modules/kvcompression.py)
- [minference/modules/retr_attn.py](minference/modules/retr_attn.py)

</details>



This page provides a comprehensive overview of Key-Value (KV) cache optimization techniques implemented in MInference for accelerating LLM inference with long contexts. KV cache optimizations focus on reducing memory usage and improving computational efficiency during text generation while maintaining model performance.

For detailed information about sparse attention mechanisms that complement these KV cache optimizations, see [Sparse Attention Mechanisms](#2.2).

## Introduction

The KV cache stores previously computed key and value tensors in transformer attention layers, eliminating the need to recompute them for each new token during autoregressive generation. As context lengths increase, KV cache memory requirements grow linearly, becoming a major bottleneck. MInference implements several optimization techniques to address this challenge:

```mermaid
flowchart TD
    subgraph "KV Cache Optimizations in MInference"
        KVCache["Base KV Cache"] --> Compression["Compression Techniques"]
        KVCache --> Quantization["Quantization Techniques"]
        KVCache --> Retrieval["Retrieval-Augmented Techniques"]
        
        Compression --> SnapKV["SnapKV"]
        Compression --> PyramidKV["PyramidKV"]
        Compression --> StreamingLLM["StreamingLLM KV"]
        
        Quantization --> KIVI["KIVI (Kernel Injected Vector Instructions)"]
        
        Retrieval --> RetrAttn["Retrieval Attention (RetrAttn)"]
        
        SnapKV -- "Layer-uniform compression" --> |"Windowing + Pooling"|CompressedKV
        PyramidKV -- "Layer-adaptive compression" --> |"Hierarchical Compression"|CompressedKV
        StreamingLLM -- "Fixed memory streaming" --> |"Sliding Window"|CompressedKV
        
        KIVI -- "Low-bit representation" --> |"Group-wise Quantization"|QuantizedKV
        
        RetrAttn -- "Vector DB storage" --> |"Similarity Search"|RetrievedKV
    end
    
    CompressedKV["Compressed KV Cache"]
    QuantizedKV["Quantized KV Cache"]
    RetrievedKV["Retrieved KV Cache"]
    
    CompressedKV --> ReducedMemory["Reduced Memory Usage"]
    QuantizedKV --> ReducedMemory
    RetrievedKV --> ReducedMemory
    
    ReducedMemory --> LongerContext["Longer Context Processing"]
```

Sources: [minference/modules/kvcompression.py:1-462]()

## Base KV Cache Implementation

MInference's KV cache system is built on a flexible base class that handles storage and retrieval of key-value tensors during inference.

### BaseKVCache

The `BaseKVCache` class serves as the foundation for all KV cache implementations in MInference:

```mermaid
classDiagram
    class Cache {
        <<Transformers>>
        +update(key_states, value_states, layer_idx, cache_kwargs)
        +get_seq_length(layer_idx)
    }
    
    class BaseKVCache {
        +key_cache: List[Tensor]
        +value_cache: List[Tensor]
        +temp_key_cache: List[Tensor]
        +temp_value_cache: List[Tensor]
        +kv_clusters: Dict
        +kv_cluster_granularity: str
        +_seen_tokens: int
        +update(key_states, value_states, layer_idx, cache_kwargs)
        +get_kv_cluster_class(layer_idx, head_idx)
        +compresssed_kv(key_states, query_states, value_states, attention_mask, num_key_value_groups, layer_idx)
        +get_seq_length(layer_idx)
        +to_legacy_cache()
        +from_legacy_cache(past_key_values)
        +clear_temp_kv_cache()
    }
    
    class DynamicCacheWithRepeat {
        +temp_key_cache: List[Tensor]
        +temp_value_cache: List[Tensor]
        +update(key_states, value_states, layer_idx, cache_kwargs)
        +get_seq_length(layer_idx)
        +clear_temp_kv_cache()
    }
    
    Cache <|-- BaseKVCache
    Cache <|-- DynamicCacheWithRepeat
```

The `BaseKVCache` provides essential functionality:

- Storing key-value pairs for each transformer layer
- Tracking the total number of processed tokens
- Supporting both global caching and temporary caching (for multi-turn conversations)
- Handling compression through KV cluster classes
- Converting between different cache formats

Sources: [minference/modules/kvcompression.py:155-309](), [minference/modules/kvcompression.py:369-449]()

### KV Cache Update Flow

The KV cache update process is a critical part of the inference pipeline:

```mermaid
sequenceDiagram
    participant Model as "LLM Forward Pass"
    participant Cache as "KV Cache Implementation"
    participant Cluster as "KV Cluster (Compression)"
    
    Model->>Cache: update(key_states, value_states, layer_idx, cache_kwargs)
    
    alt First update for layer (prefill)
        Cache->>Cluster: get_kv_cluster_class(layer_idx)
        Cache->>Cluster: update_kv(key_states, query_states, value_states, attention_mask, num_key_value_groups)
        Cluster-->>Cache: key_compress, value_compress
        Cache->>Cache: Store in key_cache/value_cache
    else Subsequent update (decode/extension)
        alt update_global_past_kv = True
            Cache->>Cache: Append to key_cache/value_cache
        else update_global_past_kv = False
            Cache->>Cache: Append to temp_key_cache/temp_value_cache
        end
    end
    
    alt Temporary cache exists
        Cache->>Cache: Concatenate main cache with temp cache
    end
    
    Cache-->>Model: Return processed key_states, value_states
```

The system supports two operational modes:
1. **Global Update Mode**: Updates permanent KV cache (for context that should persist)
2. **Temporary Update Mode**: Updates temporary KV cache (for follow-up requests that shouldn't affect the main context)

Sources: [minference/modules/kvcompression.py:208-281]()

## KV Compression Techniques

MInference implements several KV cache compression techniques to reduce memory usage.

### SnapKV

SnapKV implements a window-based compression approach that maintains both recent context and compressed history:

```mermaid
flowchart LR
    subgraph "SnapKV Compression"
        Input["Input KV Sequence\n(length N)"] --> Split["Split Sequence"]
        Split --> Recent["Recent Window\n(length window_size)"]
        Split --> ToCompress["Earlier Context\n(length N-window_size)"]
        
        ToCompress --> Pooling["Pooling Operation\n(kernel_size)"]
        Pooling --> Compressed["Compressed KVs"]
        
        Recent --> Concat["Concatenate"]
        Compressed --> Concat
        
        Concat --> CompressedCache["SnapKV Cache\n(Reduced Size)"]
    end
```

Key parameters:
- `window_size`: Number of recent tokens to retain in full fidelity
- `max_capacity_prompt`: Maximum length of the prompt to handle
- `kernel_size`: Size of the pooling window for compression
- `pooling`: Type of pooling operation (e.g., "avgpool")

Sources: [minference/modules/kvcompression.py:311-328]()

### PyramidKV

PyramidKV extends SnapKV by implementing layer-specific compression rates, forming a pyramid structure:

```mermaid
flowchart TD
    subgraph "PyramidKV Layer-Adaptive Compression"
        Input["Input KV Sequence"] --> L0["Layer 0\n(Highest Compression)"]
        Input --> L1["Layer 1"]
        Input --> L2["Layer 2"]
        Input --> L3["..."]
        Input --> LN["Layer N\n(Lowest Compression)"]
        
        L0 --> C0["Compressed KVs"]
        L1 --> C1["Compressed KVs"]
        L2 --> C2["Compressed KVs"]
        L3 --> C3["..."]
        LN --> CN["Compressed KVs"]
        
        C0 --> Out["Pyramid-Structured KV Cache"]
        C1 --> Out
        C2 --> Out
        C3 --> Out
        CN --> Out
    end
```

PyramidKV applies higher compression rates to early layers and lower compression to later layers, based on the observation that later transformer layers often need more precise context information.

Sources: [minference/modules/kvcompression.py:330-347]()

### StreamingLLM

StreamingLLM KV cache optimization focuses on fixed-memory streaming for very long documents:

```mermaid
flowchart LR
    subgraph "StreamingLLM KV Cache"
        Input["Input Stream"] --> Split["Split Context"]
        Split --> Initial["Initial Context\n(n_init tokens)"]
        Split --> Local["Local Window\n(n_local tokens)"]
        
        Initial --> Store["Store in Cache"]
        Local --> Store
        
        Store --> FixedCache["Fixed-Size KV Cache\n(n_init + n_local tokens)"]
        
        NewToken["New Token"] --> Update["Update Cache"]
        Update --> Evict["Evict Oldest Local Token"]
        Evict --> FixedCache
    end
```

Key parameters:
- `n_local`: Size of the sliding window for recent tokens (default: 3968)
- `n_init`: Size of the initial context to preserve (default: 128)

This approach ensures constant memory usage regardless of the total sequence length.

Sources: [minference/modules/kvcompression.py:350-366]()

## Quantized KV Cache with KIVI

KIVI (Kernel Injected Vector Instructions) implements quantization techniques to reduce KV cache memory usage through low-bit representation.

### KiviCache Operation

```mermaid
flowchart TD
    subgraph "KIVI Quantization Process"
        Input["Input KV Sequence"] --> Split["Split Sequence"]
        Split --> ToQuantize["Portion to Quantize"]
        Split --> ToPreserve["Residual Portion\n(residual_length tokens)"]
        
        ToQuantize --> QuantK["Quantize Keys\n(to k_bits bits)"]
        ToQuantize --> QuantV["Quantize Values\n(to v_bits bits)"]
        
        QuantK --> Scales1["Calculate Scales & Zero Points"]
        QuantV --> Scales2["Calculate Scales & Zero Points"]
        
        Scales1 --> Pack1["Pack Quantized Values"]
        Scales2 --> Pack2["Pack Quantized Values"]
        
        Pack1 --> KCache["Quantized Key Cache"]
        Pack2 --> VCache["Quantized Value Cache"]
        ToPreserve --> FullKV["Full-Precision KV Cache"]
        
        KCache --> Output["Complete KV Cache"]
        VCache --> Output
        FullKV --> Output
    end
```

The quantization process:
1. Divides the sequence into portions for quantization and full-precision preservation
2. Groups values for quantization (controlled by `group_size` parameter)
3. Computes scaling factors and zero points for each group
4. Packs multiple low-bit values into single integers
5. Stores both quantized and full-precision portions for efficient retrieval

Key parameters:
- `bits`: Quantization bit-width (typically 2 or 4)
- `group_size`: Number of values in each quantization group
- `residual_length`: Number of recent tokens to keep in full precision

Sources: [minference/modules/kivi.py:560-952]()

### Matrix Multiplication with Quantized Values

KIVI implements specialized CUDA kernels for efficient matrix multiplication with quantized values:

```mermaid
flowchart LR
    subgraph "KIVI Matrix Multiplication"
        Query["Query Tensor\nfloat16"] --> MatMul1["cuda_bmm_fA_qB_outer()"]
        KQuantized["Quantized Key Tensor\nint2/4/8"] --> MatMul1
        KScales["Key Scales"] --> MatMul1
        KZeros["Key Zero Points"] --> MatMul1
        
        MatMul1 --> QKQuant["Quantized Attention Scores"]
        
        Query --> MatMul2["torch.matmul()"]
        KFull["Full-Precision Key Tensor"] --> MatMul2
        
        MatMul2 --> QKFull["Full-Precision Attention Scores"]
        
        QKQuant --> Combine["Combine & Scale"]
        QKFull --> Combine
        
        Combine --> Softmax["Softmax"]
        
        Softmax --> MatMul3["cuda_bmm_fA_qB_outer()"]
        VQuantized["Quantized Value Tensor\nint2/4/8"] --> MatMul3
        VScales["Value Scales"] --> MatMul3
        VZeros["Value Zero Points"] --> MatMul3
        
        Softmax --> MatMul4["torch.matmul()"]
        VFull["Full-Precision Value Tensor"] --> MatMul4
        
        MatMul3 --> OutQuant["Quantized Output"]
        MatMul4 --> OutFull["Full-Precision Output"]
        
        OutQuant --> Combine2["Combine Outputs"]
        OutFull --> Combine2
        
        Combine2 --> FinalOutput["Final Attention Output"]
    end
```

The specialized CUDA kernels:
- Efficiently unpack quantized values during computation
- Apply scaling and zero-point adjustments on-the-fly
- Enable computation with mixed precision (quantized and full-precision)
- Support batch operations for multiple attention heads simultaneously

Sources: [minference/modules/kivi.py:394-574](), [minference/modules/kivi.py:954-1075]()

## Retrieval-Augmented KV Cache

The Retrieval-Augmented KV cache (RetrAttn) leverages vector databases to store and retrieve KV pairs, enabling efficient processing of extremely long contexts.

### RetrAttn Architecture

```mermaid
flowchart TD
    subgraph "RetrAttn System"
        Input["Input KV Sequence"] --> GPUCache["GPU KV Cache\n(start_size + recent_size tokens)"]
        Input --> VectorDB["Vector Database\n(FAISS/papyfaiss)"]
        
        Query["Query Vector"] --> Retrieve["Vector Similarity Search"]
        VectorDB --> Retrieve
        
        Retrieve --> TopK["Top-k Retrieved KV Pairs"]
        GPUCache --> LocalAttn["Local Attention"]
        
        TopK --> CombineAttn["Combine Attention Outputs"]
        LocalAttn --> CombineAttn
        
        CombineAttn --> Output["Final Attention Output"]
    end
```

The RetrAttn system:
1. Stores KV pairs in both GPU memory and a vector database
2. Uses vector similarity search to retrieve relevant KV pairs
3. Computes attention scores over both local and retrieved KV pairs
4. Combines the results weighted by their respective attention scores

Key components:
- `VectorDB_KV_Cache`: Manages storage and retrieval of KV pairs
- `RetrAttnCache`: Extends the Cache interface for retrieval-augmented operations
- `retr_attn()`: Core function that performs retrieval and attention computation

Sources: [minference/modules/retr_attn.py:24-264](), [minference/modules/retr_attn.py:267-348](), [minference/modules/retr_attn.py:350-442]()

### RetrAttn Operation Flow

```mermaid
sequenceDiagram
    participant Model as "LLM Forward Pass"
    participant Cache as "RetrAttnCache"
    participant VectorDB as "VectorDB_KV_Cache"
    participant FAISS as "FAISS/papyfaiss"
    
    Model->>Cache: update(key_states, value_states, layer_idx, cache_kwargs)
    
    alt Prefill phase
        Cache->>VectorDB: async_update(key_states, value_states, layer_idx, do_strllm_until_layer, core)
        VectorDB->>VectorDB: Split keys/values for GPU and vector DB
        VectorDB-->>FAISS: Store KV pairs (background thread)
        VectorDB-->>Cache: Return processed key_states, value_states
    else Decode phase
        Cache->>VectorDB: sync_key_update(key_states, layer_idx, do_strllm_until_layer, core, insert_db)
        Cache->>VectorDB: sync_value_update(value_states, layer_idx, do_strllm_until_layer, insert_db)
        VectorDB->>FAISS: Search for similar keys
        FAISS-->>VectorDB: Return top-k matches with distances
        VectorDB->>VectorDB: Compute combined attention with GPU cache
        VectorDB-->>Cache: Return processed attention output
    end
    
    Cache-->>Model: Return final output
```

Key parameters:
- `top_k`: Number of KV pairs to retrieve from the vector database
- `from_layer`: Layer from which to start using retrieval (earlier layers may use standard attention)
- `start_size`: Number of initial tokens to retain in GPU memory
- `recent_size`: Number of recent tokens to retain in GPU memory

Sources: [minference/modules/retr_attn.py:350-442](), [minference/modules/retr_attn.py:444-545]()

## Comparison and Usage Guidelines

The following table summarizes the key characteristics of each KV cache optimization technique:

| Technique | Memory Efficiency | Computational Overhead | Context Length | Implementation Complexity | Key Use Cases |
|-----------|-------------------|------------------------|----------------|--------------------------|--------------|
| SnapKV | Medium | Low | Long | Low | General-purpose, balanced approach |
| PyramidKV | High | Low | Very Long | Medium | When layer-specific compression is beneficial |
| StreamingLLM | High (Fixed) | Low | Unlimited | Low | Streaming documents, fixed memory budgets |
| KIVI | Very High | Medium | Very Long | High | Memory-constrained environments |
| RetrAttn | Extremely High | High | Extremely Long | Very High | Document retrieval, semantic search |

### Selection Guidance

1. **For general use cases**:
   - Start with SnapKV as it provides a good balance of memory efficiency and performance

2. **For very long contexts with limited memory**:
   - Consider PyramidKV to efficiently allocate memory across layers

3. **For unbounded streaming contexts**:
   - Use StreamingLLM to maintain fixed memory usage regardless of sequence length

4. **For extreme memory constraints**:
   - Apply KIVI with appropriate quantization bits (2-4) based on acceptable quality loss

5. **For document retrieval and semantic search applications**:
   - Implement RetrAttn to leverage vector similarity search for efficient retrieval

Sources: [minference/modules/kvcompression.py:452-461]()

## Integration with MInference

The KV cache optimizations are integrated with MInference through the patching system:

```mermaid
flowchart TD
    subgraph "MInference Integration"
        Config["MInferenceConfig"] --> KVConfig["KV Cache Configuration"]
        
        KVConfig --> KVType["kv_type Parameter"]
        
        KVType -->|"dense"| DenseKV["Standard KV Cache\n(DynamicCacheWithRepeat)"]
        KVType -->|"snapkv"| SnapKV["SnapKV Compression"]
        KVType -->|"pyramidkv"| PyramidKV["PyramidKV Compression"] 
        KVType -->|"streamingllm"| StreamingLLM["StreamingLLM Cache"]
        KVType -->|"kivi"| KIVI["KIVI Quantization"]
        KVType -->|"retr_attn"| RetrAttn["Retrieval Attention"]
        
        DenseKV --> Patching["Model Patching System"]
        SnapKV --> Patching
        PyramidKV --> Patching
        StreamingLLM --> Patching
        KIVI --> Patching
        RetrAttn --> Patching
        
        Patching --> ModelInference["Optimized Model Inference"]
    end
```

The `method_to_cache_obj` dictionary maps configuration parameters to the appropriate KV cache implementation, making it easy to switch between different optimization techniques.

Sources: [minference/modules/kvcompression.py:452-461](), [minference/modules/kvcompression.py:20-45]()

## Conclusion

KV cache optimization techniques in MInference provide a comprehensive set of tools for efficient LLM inference with long contexts. By selecting the appropriate technique based on your specific requirements, you can significantly reduce memory usage and improve inference performance while maintaining model quality.

---

