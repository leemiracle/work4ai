<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/xla · page 4 Advanced Features · fetched 2026-10-21 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [test/benchmarks/test_ragged_paged_attention_benchmark.py](test/benchmarks/test_ragged_paged_attention_benchmark.py)
- [test/test_gmm.py](test/test_gmm.py)
- [test/test_multi_queries_paged_attention_kernel.py](test/test_multi_queries_paged_attention_kernel.py)
- [test/test_pallas.py](test/test_pallas.py)
- [test/test_pallas_spmd.py](test/test_pallas_spmd.py)
- [test/test_quantized_matmul_pallas_kernel.py](test/test_quantized_matmul_pallas_kernel.py)
- [test/test_ragged_paged_attention_kernel.py](test/test_ragged_paged_attention_kernel.py)
- [torch_xla/csrc/data_ops.cpp](torch_xla/csrc/data_ops.cpp)
- [torch_xla/csrc/data_ops.h](torch_xla/csrc/data_ops.h)
- [torch_xla/csrc/helpers.cpp](torch_xla/csrc/helpers.cpp)
- [torch_xla/csrc/helpers.h](torch_xla/csrc/helpers.h)
- [torch_xla/csrc/ops/split.cpp](torch_xla/csrc/ops/split.cpp)
- [torch_xla/csrc/ops/split.h](torch_xla/csrc/ops/split.h)
- [torch_xla/csrc/reduction.cpp](torch_xla/csrc/reduction.cpp)
- [torch_xla/csrc/reduction.h](torch_xla/csrc/reduction.h)
- [torch_xla/experimental/custom_kernel.py](torch_xla/experimental/custom_kernel.py)
- [torch_xla/experimental/pallas_kernels/__init__.py](torch_xla/experimental/pallas_kernels/__init__.py)
- [torch_xla/experimental/pallas_kernels/multi_queries_paged_attention_kernel.py](torch_xla/experimental/pallas_kernels/multi_queries_paged_attention_kernel.py)
- [torch_xla/experimental/pallas_kernels/quantized_matmul_kernel.py](torch_xla/experimental/pallas_kernels/quantized_matmul_kernel.py)
- [torch_xla/experimental/pallas_kernels/ragged_paged_attention_kernel.py](torch_xla/experimental/pallas_kernels/ragged_paged_attention_kernel.py)
- [torch_xla/experimental/pallas_kernels/ragged_paged_attention_v2.py](torch_xla/experimental/pallas_kernels/ragged_paged_attention_v2.py)

</details>



This document covers advanced capabilities in PyTorch/XLA that extend beyond standard tensor operations. It focuses on two major areas: (1) Custom kernel integration with JAX/Pallas for high-performance TPU-specific operations, and (2) Dynamic shape support including bounded and unbounded dynamism for variable-sized tensor computations.

For distributed training features like SPMD and collective operations, see [Distributed Training and SPMD](#3). For core tensor operations and the lazy execution model, see [Core Components](#2).

---

## Custom Kernels and Pallas Integration

PyTorch/XLA provides a framework for integrating custom TPU kernels written in JAX/Pallas, enabling users to leverage highly optimized kernels for operations like Flash Attention and quantized matrix multiplication. The integration bridges PyTorch's eager execution model with JAX's compilation pipeline while maintaining compatibility with PyTorch's autograd system.

### Architecture Overview

The custom kernel system operates through several layers:

```mermaid
graph TB
    subgraph "PyTorch User Layer"
        UserCode["User Code<br/>flash_attention(q, k, v)"]
        TorchOps["torch.ops.xla.*<br/>Registered operators"]
    end
    
    subgraph "Custom Kernel Framework"
        CustomOp["@custom_op decorator<br/>fa_custom_forward/backward"]
        FakeImpl["@register_fake<br/>Shape inference"]
        ShardMap["_shard_map<br/>SPMD wrapper"]
    end
    
    subgraph "JAX/Pallas Layer"
        TracePallas["trace_pallas()<br/>JAX tracing"]
        PayloadCache["trace_pallas_arg_to_payload<br/>Dict[hash, payload]"]
        JaxKernel["JAX/Pallas Kernel<br/>_flash_attention_impl"]
        MLIRCompile["JAX MLIR Compilation"]
    end
    
    subgraph "XLA Execution"
        ExtractConfig["_extract_backend_config()<br/>Parse MLIR"]
        CustomCall["_xla_tpu_custom_call<br/>XLA custom call"]
        TPUExec["TPU Kernel Execution"]
    end
    
    UserCode --> TorchOps
    TorchOps --> CustomOp
    CustomOp --> ShardMap
    CustomOp --> FakeImpl
    
    ShardMap --> TracePallas
    TracePallas --> PayloadCache
    PayloadCache --> JaxKernel
    JaxKernel --> MLIRCompile
    
    MLIRCompile --> ExtractConfig
    ExtractConfig --> CustomCall
    CustomCall --> TPUExec
    
    FakeImpl -.-> UserCode
```

**Sources:** [torch_xla/experimental/custom_kernel.py:1-288]()

### Core Integration Mechanisms

#### Payload Extraction and Caching

The `trace_pallas()` function converts JAX/Pallas kernels to executable payloads:

```mermaid
graph LR
    Args["Tensor Arguments"] --> ToJax["to_jax_shape_dtype_struct()"]
    ToJax --> ComputeHash["Compute Cache Key<br/>kernel + args + kwargs"]
    ComputeHash --> CheckCache{"Cache Hit?"}
    CheckCache -->|Yes| ReturnCached["Return Cached Payload"]
    CheckCache -->|No| JaxJit["jax.jit(kernel).lower()"]
    JaxJit --> GetIR["compiler_ir()"]
    GetIR --> Extract["_extract_backend_config()"]
    Extract --> StoreCache["Store in<br/>trace_pallas_arg_to_payload"]
    StoreCache --> ReturnNew["Return Payload"]
```

The payload cache is a global dictionary mapping input signatures to compiled MLIR backend configurations:

- **Key**: `(jax_config, kernel, static_argnums, static_argnames, tuple(jax_args), kwargs)`
- **Value**: Serialized MLIR backend config string

**Sources:** [torch_xla/experimental/custom_kernel.py:207-258]()

#### Custom Operator Registration

PyTorch custom operators are registered using `@custom_op` decorator with fake implementations for shape inference:

| Component | Purpose | Example |
|-----------|---------|---------|
| `@custom_op` | Register forward/backward ops | `fa_custom_forward`, `fa_custom_backward` |
| `@register_fake` | Provide shape inference without execution | Returns empty tensors with correct shapes |
| `mutates_args=()` | Declare no in-place mutations | Required for torch.compile compatibility |

**Sources:** [torch_xla/experimental/custom_kernel.py:403-471](), [torch_xla/experimental/custom_kernel.py:643-706]()

### Flash Attention Implementation

Flash Attention is a memory-efficient attention mechanism that reduces memory usage from O(N²) to O(N) by tiling and recomputation.

#### Forward Pass

```mermaid
graph TB
    Input["q, k, v<br/>[batch, heads, seq, dim]"] --> Reshape["Reshape to 4D<br/>_maybe_reshape_input_output_funcs"]
    Reshape --> Pad["Pad KV to block size<br/>_pad_to_block_size"]
    Pad --> PrepSegment["prepare_segment_ids<br/>Expand to NUM_LANES/NUM_SUBLANES"]
    PrepSegment --> TracePallas["trace_pallas<br/>_flash_attention_impl"]
    
    TracePallas --> CustomCall["_xla_tpu_custom_call"]
    CustomCall --> Output["o, l, m<br/>output + residuals"]
    
    Output --> SaveCtx["Save for backward:<br/>full_q, full_k, full_v, o, l, m"]
    
    style TracePallas fill:#f9f9f9
    style CustomCall fill:#f9f9f9
```

**Key Implementation Details:**

1. **Block Sizes**: Tuned per TPU version (v4/v5/v6):
   - `block_q`: Query block size (typically 512-1024)
   - `block_k_major`: Major K block size (512)
   - `block_k`: Minor K block size (256-512)
   - `block_b`: Batch block size (2)

2. **Residuals**: Forward pass saves `l` (log-sum-exp) and `m` (max values) for backward:
   - Shape: `[batch, heads, seq, MIN_BLOCK_SIZE]` where `MIN_BLOCK_SIZE = 128`
   - Required when any of q, k, v requires gradients

3. **Segment IDs**: For packed sequences, segment IDs mask attention across different sequences:
   - Expanded to `[batch, num_heads, q_seq, NUM_LANES=128]` for queries
   - Expanded to `[batch, NUM_SUBLANES=8, kv_seq]` for keys/values

**Sources:** [torch_xla/experimental/custom_kernel.py:308-400](), [torch_xla/experimental/custom_kernel.py:747-823]()

#### Backward Pass

The backward pass computes gradients with respect to q, k, v using saved residuals:

```mermaid
graph TB
    GradOut["grad_output"] --> ComputeGradI["Compute grad_i<br/>sum(o * grad_output)"]
    SavedTensors["q, k, v, o, l, m"] --> ExpandResiduals["Expand l, m, grad_i<br/>to MIN_BLOCK_SIZE"]
    
    ExpandResiduals --> ComputeDQ{"require_grad_q?"}
    ComputeDQ -->|Yes| TraceDQ["trace_pallas<br/>_flash_attention_bwd_dq"]
    TraceDQ --> CustomCallDQ["_xla_tpu_custom_call"]
    CustomCallDQ --> GradQ["grad_q"]
    
    ExpandResiduals --> ComputeDKV{"require_grad_k<br/>or require_grad_v?"}
    ComputeDKV -->|Yes| TraceDKV["trace_pallas<br/>_flash_attention_bwd_dkv"]
    TraceDKV --> CustomCallDKV["_xla_tpu_custom_call"]
    CustomCallDKV --> GradKV["grad_k, grad_v"]
```

**Sources:** [torch_xla/experimental/custom_kernel.py:495-640](), [torch_xla/experimental/custom_kernel.py:825-851]()

### Ragged Paged Attention

Ragged Paged Attention is optimized for serving workloads with variable-length sequences, storing KV cache in pages to avoid memory fragmentation.

#### Data Layout

```mermaid
graph TB
    subgraph "Input Tensors"
        Q["queries<br/>[max_num_batched_tokens, num_q_heads, head_dim]"]
        KVPages["kv_pages<br/>[total_num_pages, page_size, num_combined_kv_heads, head_dim]"]
        KVLens["kv_lens<br/>[max_num_seqs]<br/>Actual KV length per sequence"]
        PageIdx["page_indices<br/>[max_num_seqs, pages_per_seq]"]
        CuQLens["cu_q_lens<br/>[max_num_seqs + 1]<br/>Cumulative query lengths"]
        NumSeqs["num_seqs<br/>[1]<br/>Actual number of sequences"]
    end
    
    subgraph "Layout Details"
        KVInterleave["KV pages interleaved:<br/>k0, v0, k1, v1, ...<br/>num_combined_kv_heads = 2 * num_kv_heads"]
        PageMap["Page mapping:<br/>page_indices[seq_i, page_j]<br/>→ kv_pages[page_idx]"]
    end
    
    Q --> KVInterleave
    KVPages --> KVInterleave
    PageIdx --> PageMap
    KVPages --> PageMap
```

#### Kernel Configuration

The kernel is highly parameterized with tuned configurations per TPU version:

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `num_q_heads_per_blk` | Query heads per block | 12, 28 (v6) |
| `num_kv_heads_per_blk` | KV heads per block | 2, 4 (v6) |
| `num_kv_pages_per_block` | Pages loaded per iteration | 4, 8, 16 |
| `num_queries_per_block` | Queries processed per iteration | 32, 64 |
| `page_size` | Tokens per page | 16, 32, 64, 128, 256 |

**Tuned Block Sizes**: Over 1000 tuned configurations stored in `TUNED_BLOCK_SIZES` dict keyed by:
- TPU version (v4, v5, v6)
- Data types (q_dtype, kv_dtype)
- Dimensions (num_q_heads_per_blk, num_kv_heads_per_blk, head_dim, page_size)
- Batch constraints (max_num_batched_tokens, max_model_len)

**Sources:** [torch_xla/experimental/pallas_kernels/ragged_paged_attention_v2.py:30-48](), [torch_xla/experimental/custom_kernel.py:871-1053]()

#### Runtime Validation

The kernel performs extensive runtime checks:

```mermaid
graph TD
    Input["Input Tensors"] --> CheckNumSeqs["num_seqs[0] <= max_num_seqs"]
    CheckNumSeqs --> CheckMaxKV["max(kv_lens) computable<br/>with pages_per_seq"]
    CheckMaxKV --> CheckTotalQ["cu_q_lens[num_seqs[0]]<br/><= max_num_batched_tokens"]
    CheckTotalQ --> CheckSeqLen["For each seq:<br/>q_len <= kv_len"]
    CheckSeqLen --> Execute["Execute Kernel"]
    
    CheckNumSeqs -->|Fail| Error["Raise ValueError"]
    CheckMaxKV -->|Fail| Error
    CheckTotalQ -->|Fail| Error
    CheckSeqLen -->|Fail| Error
```

**Sources:** [torch_xla/experimental/custom_kernel.py:873-902]()

### Quantized Matrix Multiplication

The quantized matmul kernel performs INT8 quantization for memory-efficient inference:

#### Quantization Flow

```mermaid
graph LR
    X["Input X<br/>[bs, in_features]"] --> ComputeMax["Compute abs max<br/>per row"]
    ComputeMax --> Quantize["Quantize to INT8<br/>scale = max / 127"]
    Quantize --> XQ["x_q: int8<br/>x_scale: float32"]
    
    W["Weight W (pre-quantized)<br/>[out_features, in_features]<br/>int8 + scale"] --> Matmul["INT32 Matmul<br/>x_q @ w_q.T"]
    XQ --> Matmul
    
    Matmul --> Scale["Multiply by scales<br/>x_scale * w_scale"]
    Scale --> Output["Output<br/>[bs, out_features]"]
```

#### Kernel Parameters

The kernel supports various configurations:

| Mode | `quantize_activation` | `save_acc` | `save_x_q` | Use Case |
|------|----------------------|------------|------------|----------|
| Dynamic Quant | True | False | False | Single-layer inference |
| Cached Quant | True | False | True | Multi-layer (reuse quantized activations) |
| Accumulation | True | True | True | Very large matrices (split computation) |
| No Quant | False | - | False | Weights-only quantization |

**Block Size Tuning**: The kernel selects block sizes based on:
- Input dimensions (batch_size, in_features, out_features)
- Available VMEM (considering double buffering)
- Tensor layouts and alignment requirements

**Sources:** [torch_xla/experimental/pallas_kernels/quantized_matmul_kernel.py:1-274](), [torch_xla/experimental/custom_kernel.py:1634-1792]()

### SPMD Integration with Custom Kernels

Custom kernels can be wrapped with `_shard_map()` for SPMD parallelism:

```mermaid
graph TB
    Input["Sharded Tensors<br/>Global View"] --> EnableManual["xs.enable_manual_sharding<br/>Convert to local view"]
    EnableManual --> Kernel["Execute Kernel<br/>on local shard"]
    Kernel --> DisableManual["xs.disable_manual_sharding<br/>Convert to global view"]
    DisableManual --> Output["Sharded Output<br/>Global View"]
    
    subgraph "Partition Spec Mapping"
        InputSpec["input_specs<br/>e.g., (0, None, None, None)"]
        OutputSpec["output_specs<br/>e.g., (0, None, None, None)"]
    end
    
    InputSpec --> EnableManual
    OutputSpec --> DisableManual
```

**Key Functions:**

- **`_shard_map(func, mesh, input_specs, output_specs)`**: Wraps kernel for SPMD execution
- **`xs.enable_manual_sharding(tensor, spec, mesh)`**: Provides local view of sharded tensor
- **`xs.disable_manual_sharding(tensor, spec, full_shape, mesh)`**: Reconstructs global view

**Example**: Flash Attention with data parallelism on batch dimension:
```python
partition_spec = (0, None, None, None)  # Shard batch
o = flash_attention(q, k, v, partition_spec=partition_spec)
```

**Sources:** [torch_xla/experimental/custom_kernel.py:25-109](), [torch_xla/experimental/custom_kernel.py:431-468]()

### Helper Functions and Utilities

#### Type Conversion

**`convert_torch_dtype_to_jax(dtype)`**: Maps PyTorch dtypes to JAX dtypes:

| PyTorch | JAX | Notes |
|---------|-----|-------|
| `torch.float32` | `jnp.float32` | - |
| `torch.bfloat16` | `jnp.bfloat16` | - |
| `torch.float8_e5m2` | `jnp.float8_e5m2` | FP8 types |
| `torch.float8_e4m3fn` | `jnp.float8_e4m3fn` | FP8 types |
| `torch.int8` | `jnp.int8` | Quantization |

**Sources:** [torch_xla/experimental/custom_kernel.py:161-194]()

#### Payload Extraction

**`_extract_backend_config(module)`**: Extracts serialized kernel from MLIR:

1. Traverses MLIR module operations (2 levels deep)
2. Searches for `stablehlo.custom_call` operation
3. Returns `backend_config.value` containing base64-encoded kernel

**Sources:** [torch_xla/experimental/custom_kernel.py:125-158]()

---

## Dynamic Shapes and Symbolic Integers

PyTorch/XLA supports dynamic shapes to handle variable-sized tensors efficiently. The system provides two modes: (1) bounded dynamism where dimensions have upper bounds, and (2) unbounded dynamism where dimensions can grow arbitrarily.

### Dynamic Reshape System

The core dynamic reshape functionality handles shape transformations while propagating dynamic dimension information.

#### Architecture

```mermaid
graph TB
    subgraph "Input Analysis"
        InputShape["Input xla::Shape<br/>with dynamic dims"]
        CheckDynamic{"Is Dynamic?"}
    end
    
    subgraph "Dynamic Reshape Path"
        GetInfo["SafeGetDynamicReshapeInfo()"]
        CheckSingle["CheckAtMostOneDynamicDimension()"]
        MapDim["GetOutputDynamicDimension()"]
        CreateShape["Create output shape<br/>with dynamic flag"]
    end
    
    subgraph "Static Reshape Path"
        StaticReshape["xla::Reshape()"]
    end
    
    subgraph "Execution"
        BuildReshape["xla::Reshape(input, sizes)"]
        SetDynamic["xla::SetDimensionSize()"]
    end
    
    InputShape --> CheckDynamic
    CheckDynamic -->|Dynamic| GetInfo
    CheckDynamic -->|Static| StaticReshape
    
    GetInfo --> CheckSingle
    CheckSingle --> MapDim
    MapDim --> CreateShape
    CreateShape --> BuildReshape
    BuildReshape --> SetDynamic
    
    StaticReshape --> BuildReshape
```

**Sources:** [torch_xla/csrc/helpers.cpp:533-579](), [torch_xla/csrc/helpers.h:161-201]()

#### Dynamic Dimension Mapping

**`GetOutputDynamicDimension()`** maps the input dynamic dimension to the output:

```mermaid
graph LR
    Input["input_sizes<br/>[2, *4, 8]<br/>dim=1 is dynamic"] --> ComputeProd["Compute product<br/>before dynamic dim:<br/>2 * 1 = 2"]
    
    ComputeProd --> Iterate["Iterate output dims<br/>accumulate product"]
    
    Iterate --> Check1["output_elements<br/><= 2?"]
    Check1 -->|Yes| Continue1["Continue"]
    Continue1 --> Check2["output_elements<br/>>= 2 * 4?"]
    Check2 -->|Yes| Found["Found dynamic dim"]
    
    Found --> Result["Output: dim index<br/>where dynamic maps"]
```

**Example Mapping:**
- Input: `[2, *4, 8]` (32 elements, dim 1 dynamic)
- Output: `[8, *4, 2]` → dim 1 is dynamic (8 elements before, 8*4=32 including)
- Output: `[64]` → dim 0 is dynamic (entire tensor)

**Sources:** [torch_xla/csrc/helpers.cpp:230-273]()

#### Error Handling

The system performs comprehensive validation:

| Error Condition | Check Function | Error Message |
|----------------|----------------|---------------|
| More than 1 dynamic dim | `CheckAtMostOneDynamicDimension()` | "expected shape [...] to have a single dynamic dimension (*)" |
| Unbounded output dims | `CheckNoOutputSizesAreUnbounded()` | "expected output sizes [...] to have no unbounded dynamic dimensions" |
| Dynamic dim split | `CheckDynamicDimensionNotSplit()` | "Expected the number of output elements..." |
| No output dim found | `CheckFoundOutputDynamicDimension()` | "The mapped dynamic dimension of the output was not found" |

**Sources:** [torch_xla/csrc/helpers.cpp:142-224]()

### Unbounded Dynamism

Unbounded dynamism allows dimensions to grow without compile-time upper bounds, using custom calls for shape manipulation.

#### Dynamic Unbounded Reshape

```mermaid
graph TB
    Input["Input with unbounded dim<br/>Shape: [*, d1, d2, ...]"] --> ExtractDim["xla::GetDimensionSize(input, 0)"]
    ExtractDim --> ReshapeDim["xla::Reshape(size, {1})"]
    ReshapeDim --> BuildStatic["Build static dims vector<br/>[d1, d2, ...]"]
    
    BuildStatic --> Concat["xla::ConcatInDim<br/>Concatenate dynamic + static"]
    Concat --> CustomCall["xla::CustomCall<br/>'mhlo.dynamic_reshape'"]
    
    OutputSizes["output_sizes<br/>[*, o1, o2, ...]"] --> BuildShape["Build output shape<br/>Mark dim 0 as unbounded"]
    BuildShape --> CustomCall
    
    CustomCall --> Result["Result with unbounded output shape"]
```

**Key Implementation:**

- **`DynamicUnboundedReshape(input, aux_input, output_sizes)`**: Uses custom call `"mhlo.dynamic_reshape"`
- Preserves unbounded dimension markers: `xla::Shape::kUnboundedSize`
- Broadcasts dimensions from `aux_input` to guide shape inference

**Sources:** [torch_xla/csrc/helpers.cpp:627-694](), [torch_xla/csrc/helpers.h:203-214]()

#### View Operation with Unbounded Dims

The view operation handles unbounded dynamism through custom reshaping:

```mermaid
graph TD
    Check{"Is unbounded<br/>dynamic?"}
    Check -->|Yes| BuildUnbounded["BuildUnboundedDynamicView()"]
    Check -->|No| BuildStandard["BuildView()<br/>DynamicReshape()"]
    
    BuildUnbounded --> ExtractBS["Extract batch size<br/>from input dim 0"]
    ExtractBS --> ConcatDims["Concat with static dims"]
    ConcatDims --> CustomReshape["mhlo.dynamic_reshape<br/>custom call"]
    
    BuildStandard --> DynamicReshape["XlaHelpers::DynamicReshape()"]
```

**Constraints:**
- Only batch size (dim 0) can be unbounded
- Product of non-batch dims must match between input and output
- Uses `mhlo.dynamic_reshape` custom call for runtime shape resolution

**Sources:** [torch_xla/csrc/data_ops.cpp:95-145](), [torch_xla/csrc/data_ops.h:27-32]()

### Helper Functions for Dynamic Operations

#### XlaHelpers Methods

| Method | Purpose | Dynamic Handling |
|--------|---------|------------------|
| `GetDimensionsSize()` | Compute total size of dimensions | Returns `{XlaOp, optional<int64_t>}` |
| `DynamicReshape()` | Reshape with dynamic dims | Propagates dynamic dimension |
| `SafeDynamicReshape()` | Error-checked reshape | Returns `StatusOr<XlaOp>` |
| `DynamicBroadcastInDim()` | Broadcast with dynamic shapes | Uses `xla::SetDimensionSize()` |
| `IsUnboundedDynamic()` | Check if shape has unbounded dims | Tests for `kUnboundedSize` |

**Sources:** [torch_xla/csrc/helpers.h:36-228](), [torch_xla/csrc/helpers.cpp:369-404]()

#### Dimension Size Computation

**`GetDimensionsSize()`** computes dimension sizes handling both static and dynamic cases:

```mermaid
graph LR
    Init["Initialize:<br/>size_scalar = 1<br/>size_op = invalid"] --> Loop["For each dimension"]
    
    Loop --> CheckStatic{"Static<br/>dimension?"}
    CheckStatic -->|Yes| MultScalar["size_scalar *= dim_size"]
    CheckStatic -->|No| CheckValid{"size_op<br/>valid?"}
    
    MultScalar --> Loop
    
    CheckValid -->|No| InitOp["size_op = scalar_value(size_scalar)<br/>size_scalar = -1"]
    CheckValid -->|Yes| Continue
    InitOp --> GetDim["size_op *= GetDimensionSize(input, dim)"]
    Continue --> GetDim
    GetDim --> Loop
    
    Loop --> Return["Return {size_op, optional<size_scalar>}"]
```

**Return Value:**
- `DynamicSize::size`: XlaOp computing the runtime size
- `DynamicSize::scalar_size`: Optional compile-time size (if all static)

**Sources:** [torch_xla/csrc/helpers.cpp:369-404](), [torch_xla/csrc/helpers.h:42-45]()

### Shape Inference and Propagation

#### Reduction Operations

Reduction operations maintain dynamic shape information:

```mermaid
graph TB
    Input["Input Shape<br/>[*, d1, d2]<br/>dim 0 is dynamic"] --> GetInfo["GetReductionInfo()"]
    
    GetInfo --> BuildNewDims["Build new_dimensions:<br/>- Keep dim if not reduced<br/>- Insert 1 if keep_reduced_dimensions"]
    
    BuildNewDims --> ComputeCount["GetDimensionsSize()<br/>Count reduced elements"]
    
    ComputeCount --> Reduce["xla::Reduce()<br/>Apply reduction"]
    
    Reduce --> ReshapeBack{"keep_reduced_<br/>dimensions?"}
    
    ReshapeBack -->|Yes| CheckUnbounded{"Unbounded<br/>dynamic?"}
    CheckUnbounded -->|Yes| UnboundedReshape["DynamicUnboundedReshape()<br/>Preserve * marker"]
    CheckUnbounded -->|No| BoundedReshape["DynamicReshape()"]
    
    UnboundedReshape --> Result["Result with preserved<br/>dynamic dimensions"]
    BoundedReshape --> Result
```

**Example:** Sum over dim 1:
- Input: `[*8, 4, 16]` (dim 0 dynamic)
- Output: `[*8, 16]` (dim 0 still dynamic)
- Output (keep_dims): `[*8, 1, 16]` (dim 0 still dynamic)

**Sources:** [torch_xla/csrc/reduction.cpp:26-140](), [torch_xla/csrc/reduction.h:1-96]()

#### Expansion and Broadcasting

**`BuildExpand()`** handles dynamic shape broadcasting:

1. Adjust input rank: Insert 1s at the beginning if needed
2. Use `DynamicReshape()` to match dimensions
3. Apply `xla::BroadcastInDim()` with correct dimension mapping

For unbounded shapes, implicit broadcasting uses `ImplicitBroadcastWithUnboundedDynamicShapes()` which:
- Identifies unbounded dimensions
- Creates dynamic broadcast using `DynamicUnboundedBroadcast()`
- Ensures proper dimension alignment

**Sources:** [torch_xla/csrc/data_ops.cpp:183-193](), [torch_xla/csrc/helpers.cpp:712-772]()

### SetDimensionSizes API

The `SetDimensionSizes()` function marks dimensions as dynamically sized:

```mermaid
graph LR
    Input["input: XlaOp"] --> Loop["Iterate dynamic_dims"]
    SymbolicSizes["symbolic_output_sizes:<br/>vector of XlaOp"] --> Loop
    DynamicFlags["dynamic_dims:<br/>vector of bool"] --> Loop
    
    Loop --> CheckFlag{"dynamic_dims[i]<br/>== true?"}
    CheckFlag -->|Yes| SetSize["input = SetDimensionSize<br/>(input, symbolic_sizes[idx++], i)"]
    CheckFlag -->|No| Skip["Skip dimension"]
    
    SetSize --> Loop
    Skip --> Loop
    Loop --> Result["Return modified input"]
```

**Usage Example:**
```cpp
// Mark dims 0 and 2 as dynamic
std::vector<bool> dynamic_dims = {true, false, true, false};
std::vector<xla::XlaOp> sizes = {size_dim0, size_dim2};
xla::XlaOp result = SetDimensionSizes(input, sizes, dynamic_dims);
```

**Sources:** [torch_xla/csrc/data_ops.cpp:147-164](), [torch_xla/csrc/data_ops.h:34-37]()

### Environment Control

**`IsUnboundedDynamismEnabled()`**: Feature flag for unbounded dynamism

- Environment variable: `EXPERIMENTAL_XLA_UNBOUNDED_DYNAMISM`
- Default: `false` (bounded dynamism only)
- When enabled: Allows `xla::Shape::kUnboundedSize` dimensions

**Sources:** [torch_xla/csrc/helpers.h:205-208]()

---

**Document Sources:**
- [torch_xla/experimental/custom_kernel.py:1-1800]()
- [torch_xla/csrc/helpers.cpp:1-1500]()
- [torch_xla/csrc/helpers.h:1-500]()
- [torch_xla/csrc/data_ops.cpp:1-1000]()
- [torch_xla/csrc/data_ops.h:1-122]()
- [torch_xla/csrc/reduction.cpp:1-500]()
- [torch_xla/csrc/reduction.h:1-96]()
- [torch_xla/experimental/pallas_kernels/ragged_paged_attention_v2.py:1-1000]()
- [torch_xla/experimental/pallas_kernels/quantized_matmul_kernel.py:1-274]()
- [test/test_pallas.py:1-1500]()

---

