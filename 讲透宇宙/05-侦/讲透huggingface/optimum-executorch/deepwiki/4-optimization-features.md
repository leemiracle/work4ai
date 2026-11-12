<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-executorch · page 4 Optimization Features · fetched 2026-10-26 -->

# Optimization Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/executorch/attentions/custom_sdpa.py](optimum/executorch/attentions/custom_sdpa.py)
- [optimum/exporters/executorch/quantization.py](optimum/exporters/executorch/quantization.py)
- [optimum/exporters/executorch/recipes/xnnpack.py](optimum/exporters/executorch/recipes/xnnpack.py)
- [optimum/exporters/executorch/tasks/masked_lm.py](optimum/exporters/executorch/tasks/masked_lm.py)
- [tests/models/test_modeling_bert.py](tests/models/test_modeling_bert.py)

</details>



This document covers the performance optimization features available in optimum-executorch that enhance model inference efficiency. These optimizations include custom attention mechanisms, KV cache management, quantization techniques, and backend-specific optimizations that can significantly improve inference speed and reduce memory usage.

For information about specific model runtime and inference APIs, see [Runtime and Inference](#3). For details on export recipes and backend delegation, see [Recipes and Backend Delegation](#2.4).

## Custom Attention Mechanisms

The library provides custom implementations of scaled dot product attention (SDPA) that offer substantial performance improvements over standard PyTorch attention mechanisms. The custom SDPA implementation can provide up to 3x faster inference compared to standard attention.

### Custom SDPA Implementation

The core custom attention functionality is implemented in the `custom_sdpa_with_start_pos_forward` function, which replaces standard PyTorch SDPA with an optimized ExecuTorch-specific implementation.

```mermaid
graph TB
    subgraph "Standard Attention Flow"
        STD_SDPA["torch.nn.functional.scaled_dot_product_attention"]
        STD_TRANSPOSE["Standard transpose operations"]
        STD_MASK["Standard attention masking"]
    end
    
    subgraph "Custom SDPA Flow"
        CUSTOM_SDPA["custom_sdpa_with_start_pos_forward"]
        ET_CUSTOM_OP["torch.ops.llama.custom_sdpa"]
        START_POS["start_pos calculation"]
        DTYPE_CONV["fp32 conversion optimization"]
        CAUSAL_OPT["Optimized causal attention"]
    end
    
    subgraph "Input Processing"
        QKV_INPUT["query, key, value tensors"]
        ATTN_MASK["attention_mask"]
        SCALING["scaling factor"]
    end
    
    subgraph "Configuration"
        IS_CAUSAL["module.is_causal"]
        IS_SLIDING["is_sliding flag"]
        LAYER_IDX["module.layer_idx"]
    end
    
    QKV_INPUT --> CUSTOM_SDPA
    ATTN_MASK --> START_POS
    SCALING --> ET_CUSTOM_OP
    
    CUSTOM_SDPA --> DTYPE_CONV
    DTYPE_CONV --> ET_CUSTOM_OP
    START_POS --> ET_CUSTOM_OP
    
    IS_CAUSAL --> CAUSAL_OPT
    IS_SLIDING --> START_POS
    LAYER_IDX --> CAUSAL_OPT
    
    ET_CUSTOM_OP --> CAUSAL_OPT
```

**Sources**: [optimum/executorch/attentions/custom_sdpa.py:21-77]()

The custom SDPA implementation includes several key optimizations:

| Optimization | Description | Implementation |
|--------------|-------------|----------------|
| **Start Position Calculation** | Calculates attention start position from mask | `torch.argmin(first_row_mask.to(torch.long)).item() - 1` |
| **Data Type Optimization** | Converts to fp32 for computation, back to original | `query.to(torch.float32)` → `output.to(input_dtype)` |
| **Causal Attention** | Optimized causal masking for autoregressive models | `is_causal=module.is_causal` |
| **Custom Operator** | Uses ExecuTorch's optimized SDPA operator | `torch.ops.llama.custom_sdpa` |

### Sliding Window Attention Integration

For models using sliding window attention, the custom SDPA integrates with ring KV cache through the `get_custom_sdpa_for_ring_kv_cache` function:

```mermaid
graph LR
    subgraph "Ring KV Cache Integration"
        GET_CUSTOM["get_custom_sdpa_for_ring_kv_cache"]
        RING_CACHE["CustomRingKVCache"]
        HYBRID_CACHE["ETCustomHybridCache"]
        CACHE_POS["cache_position"]
    end
    
    subgraph "Sliding Window Logic"
        IS_SLIDING["is_sliding check"]
        LAYER_IDX["layer_idx retrieval"]
        INPUT_POS["input_pos calculation"]
        CAUSAL_MASK["create_causal_mask_for_ring_buffer"]
    end
    
    subgraph "Attention Execution"
        CUSTOM_FORWARD["custom_sdpa_with_start_pos_forward"]
        SLIDING_KWARGS["is_sliding: True"]
    end
    
    GET_CUSTOM --> IS_SLIDING
    IS_SLIDING --> LAYER_IDX
    LAYER_IDX --> HYBRID_CACHE
    HYBRID_CACHE --> RING_CACHE
    RING_CACHE --> INPUT_POS
    INPUT_POS --> CAUSAL_MASK
    CAUSAL_MASK --> SLIDING_KWARGS
    SLIDING_KWARGS --> CUSTOM_FORWARD
```

**Sources**: [optimum/executorch/attentions/custom_sdpa.py:80-144]()

## KV Cache Optimization

The library implements advanced KV cache management strategies to optimize memory usage and inference performance, particularly for long sequence generation and sliding window attention patterns.

### Custom KV Cache Types

The optimization system supports multiple KV cache implementations:

- **Static KV Cache**: Traditional fixed-size cache for standard attention
- **Custom KV Cache**: Enhanced cache with better memory management
- **Ring KV Cache**: Circular buffer cache for sliding window attention

The ring KV cache integration is specifically designed for sliding window attention models and provides efficient memory usage for long sequences:

```mermaid
graph TB
    subgraph "Cache Architecture"
        EXPORTABLE_MODULE["exportable_module.model.cache"]
        HYBRID_CACHE["ETCustomHybridCache"]
        LAYER_CACHE["get_layer_cache(layer_idx)"]
        RING_BUFFER["CustomRingKVCache"]
    end
    
    subgraph "Cache Operations"
        CACHE_POSITION["cache_position[0].item()"]
        INPUT_POS_CALC["input_pos calculation"]
        SEQLEN["query.shape[2]"]
        MASK_CREATION["create_causal_mask_for_ring_buffer"]
    end
    
    subgraph "Attention Integration"
        SLIDING_FLAG["is_sliding: True"]
        CUSTOM_SDPA_CALL["custom_sdpa_with_start_pos_forward"]
    end
    
    EXPORTABLE_MODULE --> HYBRID_CACHE
    HYBRID_CACHE --> LAYER_CACHE
    LAYER_CACHE --> RING_BUFFER
    
    RING_BUFFER --> CACHE_POSITION
    CACHE_POSITION --> INPUT_POS_CALC
    INPUT_POS_CALC --> MASK_CREATION
    SEQLEN --> MASK_CREATION
    
    MASK_CREATION --> SLIDING_FLAG
    SLIDING_FLAG --> CUSTOM_SDPA_CALL
```

**Sources**: [optimum/executorch/attentions/custom_sdpa.py:104-130]()

## Quantization

The quantization system provides comprehensive model compression through weight and activation quantization, supporting various precision levels and granularities.

### Quantization Configuration

The `quantize_model_` function supports two main quantization categories:

```mermaid
graph TB
    subgraph "Quantization Entry Point"
        QUANTIZE_MODEL["quantize_model_(eager_model, qlinear_config, qembedding_config)"]
        TORCHAO_CHECK["torchao >= 0.11.0.dev0 check"]
    end
    
    subgraph "Linear Layer Quantization"
        QLINEAR_CONFIG["qlinear_config"]
        LINEAR_CONFIGS["Linear Configurations"]
        EIGHTDA4W["8da4w: Int8DynamicActivationIntxWeightConfig"]
        FOURW["4w: IntxWeightOnlyConfig(torch.int4)"]
        EIGHTW["8w: IntxWeightOnlyConfig(torch.int8)"]
    end
    
    subgraph "Embedding Layer Quantization"
        QEMBEDDING_CONFIG["qembedding_config"]
        EMBEDDING_CONFIGS["Embedding Configurations"]
        EMB_4W["4w: IntxWeightOnlyConfig(torch.int4, PerGroup(32))"]
        EMB_8W["8w: IntxWeightOnlyConfig(torch.int8, PerAxis(0))"]
    end
    
    subgraph "Granularity Options"
        PERGROUP["PerGroup(32)"]
        PERAXIS["PerAxis(0)"]
    end
    
    subgraph "Final Processing"
        QUANTIZE_CALL["quantize_(eager_model, config)"]
        UNWRAP["unwrap_tensor_subclass(eager_model)"]
    end
    
    QUANTIZE_MODEL --> TORCHAO_CHECK
    TORCHAO_CHECK --> QLINEAR_CONFIG
    TORCHAO_CHECK --> QEMBEDDING_CONFIG
    
    QLINEAR_CONFIG --> LINEAR_CONFIGS
    LINEAR_CONFIGS --> EIGHTDA4W
    LINEAR_CONFIGS --> FOURW
    LINEAR_CONFIGS --> EIGHTW
    
    QEMBEDDING_CONFIG --> EMBEDDING_CONFIGS
    EMBEDDING_CONFIGS --> EMB_4W
    EMBEDDING_CONFIGS --> EMB_8W
    
    FOURW --> PERGROUP
    EMB_4W --> PERGROUP
    EIGHTW --> PERAXIS
    EMB_8W --> PERAXIS
    
    LINEAR_CONFIGS --> QUANTIZE_CALL
    EMBEDDING_CONFIGS --> QUANTIZE_CALL
    QUANTIZE_CALL --> UNWRAP
```

**Sources**: [optimum/exporters/executorch/quantization.py:23-82]()

### Quantization Schemes

The quantization system supports the following schemes:

| Scheme | Target | Weight Dtype | Granularity | Description |
|--------|--------|--------------|-------------|-------------|
| **8da4w** | Linear layers | `torch.int4` | `PerGroup(32)` | 8-bit dynamic activation, 4-bit weights |
| **4w** | Linear/Embedding | `torch.int4` | `PerGroup(32)` | 4-bit weight-only quantization |
| **8w** | Linear/Embedding | `torch.int8` | `PerAxis(0)` | 8-bit weight-only quantization |

### Integration with Export Pipeline

Quantization is integrated into the task-specific model loading pipeline. For example, in the masked language model task:

```python
qlinear_config = kwargs.get("qlinear", None)
qembedding_config = kwargs.get("qembedding", None)
quantize_model_(eager_model, qlinear_config=qlinear_config, qembedding_config=qembedding_config)
```

**Sources**: [optimum/exporters/executorch/tasks/masked_lm.py:44-46]()

## Backend-Specific Optimizations

The XNNPACK backend recipe provides additional optimization features that enhance performance during the export and lowering process.

### XNNPACK Optimization Pipeline

The XNNPACK export recipe implements a comprehensive optimization pipeline:

```mermaid
graph TB
    subgraph "Export Configuration"
        XNNPACK_RECIPE["@register_recipe('xnnpack')"]
        EXPORT_FUNC["export_to_executorch_with_xnnpack"]
        MODEL_EXPORT["model.export()"]
    end
    
    subgraph "Custom SDPA Validation"
        ATTN_CHECK["config._attn_implementation check"]
        CUSTOM_SDPA_IMPL["custom_sdpa"]
        RING_KV_IMPL["custom_sdpa_ring_kv_cache"]
        GRAPH_VALIDATION["custom_sdpa node validation"]
    end
    
    subgraph "Lowering Pipeline"
        LOWER_FUNC["_lower_to_executorch"]
        XNNPACK_PARTITIONER["XnnpackPartitioner()"]
        EDGE_CONFIG["EdgeCompileConfig"]
        TRANSFORM_PASSES["RemovePaddingIdxEmbeddingPass()"]
    end
    
    subgraph "Backend Configuration"
        BACKEND_CONFIG["ExecutorchBackendConfig"]
        EXTRACT_DELEGATES["extract_delegate_segments: True"]
        QUANT_FUSION["do_quant_fusion_and_const_prop: True"]
    end
    
    subgraph "Optimization Passes"
        REMOVE_PADDING["RemovePaddingIdxEmbeddingPass"]
        IR_VALIDITY["_check_ir_validity: False"]
        DIM_ORDER["_skip_dim_order: True"]
    end
    
    XNNPACK_RECIPE --> EXPORT_FUNC
    EXPORT_FUNC --> MODEL_EXPORT
    MODEL_EXPORT --> ATTN_CHECK
    
    ATTN_CHECK --> CUSTOM_SDPA_IMPL
    ATTN_CHECK --> RING_KV_IMPL
    CUSTOM_SDPA_IMPL --> GRAPH_VALIDATION
    RING_KV_IMPL --> GRAPH_VALIDATION
    
    GRAPH_VALIDATION --> LOWER_FUNC
    LOWER_FUNC --> XNNPACK_PARTITIONER
    LOWER_FUNC --> EDGE_CONFIG
    LOWER_FUNC --> TRANSFORM_PASSES
    
    EDGE_CONFIG --> IR_VALIDITY
    EDGE_CONFIG --> DIM_ORDER
    TRANSFORM_PASSES --> REMOVE_PADDING
    
    XNNPACK_PARTITIONER --> BACKEND_CONFIG
    BACKEND_CONFIG --> EXTRACT_DELEGATES
    BACKEND_CONFIG --> QUANT_FUSION
```

**Sources**: [optimum/exporters/executorch/recipes/xnnpack.py:41-112]()

### Optimization Features by ExecuTorch Version

The XNNPACK recipe adapts its optimization features based on the ExecuTorch version:

| Feature | Condition | Implementation |
|---------|-----------|----------------|
| **Quantization Fusion** | ExecuTorch > 0.6.0 | `do_quant_fusion_and_const_prop: True` |
| **Delegate Extraction** | Always enabled | `extract_delegate_segments: True` |
| **Padding Removal** | Always enabled | `RemovePaddingIdxEmbeddingPass()` |
| **IR Validity Skip** | Always enabled | `_check_ir_validity: False` |
| **Dimension Order Skip** | Always enabled | `_skip_dim_order: True` |

### Performance Monitoring

The XNNPACK recipe includes built-in delegation monitoring and debugging capabilities:

```python
delegation_info = get_delegation_info(et_progs[pte_name].exported_program().graph_module)
logging.debug(f"Delegation info Summary for {pte_name}.pte: {delegation_info.get_summary()}")
```

This provides detailed information about which operations are successfully delegated to the XNNPACK backend versus remaining on the portable backend.

**Sources**: [optimum/exporters/executorch/recipes/xnnpack.py:91-95]()

---

