> 来源: [https://deepwiki.com/deepseek-ai/DeepGEMM/2-python-api-reference](https://deepwiki.com/deepseek-ai/DeepGEMM/2-python-api-reference)
> DeepWiki deepseek-ai/DeepGEMM

# Python API Reference

  Relevant source files 
 - [csrc/python_api.cpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp)
 - [csrc/utils/exception.hpp](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/utils/exception.hpp)
 - [deep_gemm/__init__.py](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py)
 
  This document provides comprehensive reference documentation for all Python functions and interfaces exposed by the DeepGEMM library. The Python API serves as the primary interface for performing optimized GEMM, attention, and einsum operations on NVIDIA GPUs with FP8, FP4, and BF16 data types.

 All functions are exposed through the `deep_gemm` Python package and are implemented as bindings to optimized CUDA kernels. The API is organized into functional categories based on operation type.

 For detailed documentation of specific operation categories, see:

 
 - [GEMM Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.1-gemm-operations) — Standard and grouped matrix multiplication.
 - [Attention Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.2-attention-operations) — Multi-query attention logits kernels.
 - [Einsum Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.3-einsum-operations) — Einstein summation operations.
 - [Hyperconnection Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.4-hyperconnection-operations) — Specialized kernels for DeepSeek hyperconnections.
 - [Mega MoE Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.5-mega-moe-operations) — Fused kernels for multi-GPU MoE inference.
 - [Layout and Utility Functions](https://deepwiki.com/deepseek-ai/DeepGEMM/2.6-layout-and-utility-functions) — Tensor transformations and memory utilities.
 - [Configuration and Environment Variables](https://deepwiki.com/deepseek-ai/DeepGEMM/2.7-configuration-and-environment-variables) — Runtime configuration and JIT control.
 
 For architecture-specific implementation details, see page 4. For build and installation procedures, see page 5.

 Sources: [deep_gemm/__init__.py1-126](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L1-L126)

 
## API Organization

 The DeepGEMM Python API is organized into functional categories based on operation type. All functions are exposed through the `deep_gemm` package and implemented as C++ extensions.

 
### Complete API Surface Overview

 DeepGEMM exposes a variety of high-performance kernels tailored for Large Language Model (LLM) workloads.

 Title: DeepGEMM Functional API Taxonomy

 
```

```

 **Module Initialization**: The `deep_gemm._C` module is initialized with the library root directory and CUDA home path via `_C.init()` at import time. This sets up the kernel cache and device runtime.

 Sources: [deep_gemm/__init__.py121-124](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L121-L124) [csrc/python_api.cpp17-28](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp#L17-L28)

 
### Python to C++ API Mapping

 The Python API provides direct bindings to C++ implementation functions. All operations are JIT-compiled and cached for efficient reuse.

 Title: DeepGEMM Python to C++ Binding Map

 
```

```

 **Import Behavior**: DeepGEMM kernel functions are conditionally imported. If the CUDA version is below 12.1, the import silently fails and only basic cuBLASLt functions remain available.

 Sources: [deep_gemm/__init__.py34-81](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L34-L81) [csrc/python_api.cpp21-27](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/csrc/python_api.cpp#L21-L27)

 
## Operation Categories Summary

 The following tables provide a high-level summary of all available operations.

 
### GEMM Operations Overview

 GEMM operations perform matrix multiplication with optional accumulation: `D = C + op(A) @ op(B)`.

 **Standard GEMM Functions** - Detailed in [GEMM Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.1-gemm-operations)

 
| Function Pattern | Supported Data Types | Layouts | Architecture |
|---|---|---|---|
| fp8_gemm_* | FP8 E4M3 + scaling factors | NT, NN, TN, TT | SM90, SM100 |
| fp8_fp4_gemm_* | FP8 + FP4 mixed precision | NT, NN, TN, TT | SM100 only |
| bf16_gemm_* | BFloat16 | NT, NN, TN, TT | SM90, SM100 |

 **Grouped GEMM Functions** - Detailed in [GEMM Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.1-gemm-operations)

 
| Function Pattern | Operation Type | Primary Use Case |
|---|---|---|
| m_grouped_*_contiguous | M-dimension grouped | MoE training/prefill |
| m_grouped_*_masked | M-dimension masked | MoE inference/decoding |
| k_grouped_*_contiguous | K-dimension grouped | MoE weight gradient (dWeight) |

 Sources: [deep_gemm/__init__.py36-58](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L36-L58)

 
### Attention Operations Overview

 Attention operations compute Multi-Query Attention (MQA) logits. Detailed in [Attention Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.2-attention-operations).

 
| Function | Operation | Key Features |
|---|---|---|
| fp8_mqa_logits | Standard MQA logits | Fused Q@K.T for prefill |
| fp8_fp4_mqa_logits | Mixed precision MQA | SM100 optimized Q(FP8)@K(FP4) |
| fp8_paged_mqa_logits | Paged KV cache MQA | Supports paged memory for decoding |
| fp8_fp4_paged_mqa_logits | Mixed paged MQA | SM100 optimized paged KV |

 Sources: [deep_gemm/__init__.py63-68](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L63-L68)

 
### Mega MoE Operations Overview

 The Mega MoE API provides fused kernels for multi-GPU MoE inference, combining Expert Parallelism (EP) dispatch, linear layers, and activation. Detailed in [Mega MoE Operations](https://deepwiki.com/deepseek-ai/DeepGEMM/2.5-mega-moe-operations).

 
| Function/Class | Purpose |
|---|---|
| fp8_fp4_mega_moe | Main fused kernel for SM100 |
| bf16_mega_moe | Main fused kernel for BF16 |
| SymmBuffer | Symmetric memory buffer for EP communication |
| get_symm_buffer_for_mega_moe | Allocates symmetric memory across GPUs |
| transform_weights_for_mega_moe | Preprocesses weights for fused execution |

 Sources: [deep_gemm/__init__.py84-92](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L84-L92)

 
### Configuration Operations Overview

 Configuration functions control runtime behavior and resource allocation. Detailed in [Configuration and Environment Variables](https://deepwiki.com/deepseek-ai/DeepGEMM/2.7-configuration-and-environment-variables).

 
| Function | Purpose |
|---|---|
| set_num_sms | Limit maximum SM count for the device |
| set_tc_util | Set tensor core utilization ratio |
| set_pdl | Enable/Disable Predictable Data Loading (PDL) |
| set_ignore_compile_dims | Ignore specific dimensions for JIT caching |
| set_block_size_multiple_of | Set constraints for JIT block size selection |

 Sources: [deep_gemm/__init__.py17-26](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L17-L26)

 
## Common Parameter Patterns

 DeepGEMM functions follow consistent parameter conventions.

 
### Tensor Input Parameters

 
| Parameter | Type | Description |
|---|---|---|
| a | torch.Tensor or tuple | Input A. For FP8/FP4: tuple of (tensor, scaling_factor) |
| b | torch.Tensor or tuple | Input B. For FP8/FP4: tuple of (tensor, scaling_factor) |
| c | Optional[torch.Tensor] | Optional accumulator matrix for fused add |
| d | torch.Tensor | Output result tensor |

 **Scaling Factor Layout**: Scaling factors must be transformed using `transform_sf_into_required_layout()` before passing to GEMM functions. SM90 uses FP32 scales, while SM100 requires packed format (e.g., UE8M0 for certain ops).

 Sources: [deep_gemm/__init__.py72](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L72-L72) [deep_gemm/__init__.py36-54](https://github.com/deepseek-ai/DeepGEMM/blob/559d79fb/deep_gemm/__init__.py#L36-L54)
