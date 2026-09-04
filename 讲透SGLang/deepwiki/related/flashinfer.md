> 来源: [https://deepwiki.com/flashinfer-ai/flashinfer](https://deepwiki.com/flashinfer-ai/flashinfer)
> 关联理由: SGLang 核心 attention/MoE 内核库依赖（Python API + JIT）

# Overview

  Relevant source files 
 - [.gitignore](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/.gitignore)
 - [README.md](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1)
 - [docs/conf.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/conf.py)
 - [docs/index.rst](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/index.rst)
 - [docs/installation.rst](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/installation.rst)
 - [docs/requirements.txt](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/requirements.txt)
 - [docs/tutorials/recursive_attention.rst](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/tutorials/recursive_attention.rst)
 - [flashinfer/__init__.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/__init__.py)
 - [flashinfer/__main__.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/__main__.py)
 - [flashinfer/aot.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/aot.py)
 - [flashinfer/comm/nvshmem.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/comm/nvshmem.py)
 - [flashinfer/comm/nvshmem_allreduce.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/comm/nvshmem_allreduce.py)
 - [flashinfer/jit/__init__.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/__init__.py)
 - [flashinfer/jit/attention/__init__.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/attention/__init__.py)
 - [flashinfer/jit/core.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/core.py)
 - [flashinfer/jit/cpp_ext.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/cpp_ext.py)
 - [flashinfer/jit/env.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/env.py)
 - [flashinfer/utils.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/utils.py)
 - [scripts/update_whl_index.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/scripts/update_whl_index.py)
 - [tests/utils/test_decorators.py](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/tests/utils/test_decorators.py)
 - [version.txt](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/version.txt)
 
  FlashInfer is a high-performance GPU kernel library and generator for Large Language Model (LLM) inference and serving. It delivers state-of-the-art performance across diverse GPU architectures, from SM 7.5 (Turing) through SM 12.x (Blackwell). The library provides unified APIs for attention, GEMM, and Mixture-of-Experts (MoE) operations, featuring automatic backend selection, dual JIT/AOT compilation strategies, and extensive support for low-precision computation including FP8 and FP4.

 **Scope**: This page provides a high-level system overview of FlashInfer's architecture and organization. For detailed information about specific components and hardware support:

 
 - [Core Components](https://deepwiki.com/flashinfer-ai/flashinfer/1.1-core-components) — Details on attention mechanisms, GEMM, MoE, sampling, and communication.
 - [Hardware and Backend Support](https://deepwiki.com/flashinfer-ai/flashinfer/1.2-hardware-and-backend-support) — Details on supported GPUs (SM 7.5 to 12.x) and backend implementations (FA2/3, CUTLASS, TRT-LLM).
 
 Sources: [README.md1-27](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1#L1-L27) [README.md28-62](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1#L28-L62) [docs/index.rst11-12](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/index.rst#L11-L12) [version.txt1](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/version.txt#L1-L1)

 
## System Architecture

 FlashInfer implements a layered architecture where high-level Python APIs dispatch to specialized backend implementations. The system is designed to separate the user-facing interface from hardware-specific kernel logic, allowing for seamless optimization across different GPU generations.

 
### Primary System Layers

 
```

```

 Sources: [flashinfer/__init__.py25-170](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/__init__.py#L25-L170) [flashinfer/aot.py37-88](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/aot.py#L37-L88) [flashinfer/jit/__init__.py24-105](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/__init__.py#L24-L105) [flashinfer/utils.py148-156](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/utils.py#L148-L156)

 
### Core Operation Categories

 FlashInfer organizes its high-performance kernels into functional categories, exposed via the flashinfer root module:

 
| Category | Key Entities | Primary File |
|---|---|---|
| Attention | BatchPrefillWithPagedKVCacheWrapper, BatchDecodeWithPagedKVCacheWrapper, BatchMLAPagedAttentionWrapper | flashinfer/prefill.py flashinfer/decode.py flashinfer/mla.py |
| GEMM | mm_bf16, mm_fp8, mm_fp4, tgv_gemm_sm100, grouped_mm_bf16 | flashinfer/gemm.py flashinfer/grouped_mm.py |
| MoE | cutlass_fused_moe, trtllm_bf16_moe, cute_dsl_fused_moe_nvfp4 | flashinfer/fused_moe.py |
| Sampling | top_k_sampling, top_p_sampling, chain_speculative_sampling | flashinfer/sampling.py |
| Norm/RoPE | fused_add_rmsnorm, apply_rope, apply_llama31_rope | flashinfer/norm.py flashinfer/rope.py |

 For details on these functional blocks, see [Core Components](https://deepwiki.com/flashinfer-ai/flashinfer/1.1-core-components).

 Sources: [flashinfer/__init__.py31-170](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/__init__.py#L31-L170) [README.md28-62](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1#L28-L62)

 
## Backend Selection and Hardware Support

 FlashInfer provides a unified interface that automatically selects the most efficient backend for the current hardware. This includes support for legacy architectures (Turing SM 7.5) and the latest Blackwell (SM 10.0/12.0) features like FP4 and groupwise scaling.

 
 - **Legacy & Mainstream**: FlashAttention-2 and cuDNN backends for SM 7.5 to 8.9.
 - **Hopper (SM 9.0)**: FlashAttention-3 and CUTLASS-based FP8 kernels.
 - **Blackwell (SM 10.0+)**: TensorRT-LLM and CuTe DSL backends for FP4/FP8 operations, groupwise GEMM (tgv_gemm_sm100), and Key-Driven Attention (recurrent_kda).
 
 For details on architecture-specific logic and backend selection, see [Hardware and Backend Support](https://deepwiki.com/flashinfer-ai/flashinfer/1.2-hardware-and-backend-support).

 Sources: [README.md63-74](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1#L63-L74) [flashinfer/aot.py51-88](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/aot.py#L51-L88) [flashinfer/jit/core.py122-136](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/core.py#L122-L136)

 
## Compilation and Deployment

 FlashInfer employs a dual compilation strategy to balance flexibility and runtime performance.

 
 - **JIT (Just-In-Time)**: Uses Ninja and NVCC to compile specialized kernels on the fly based on runtime parameters (e.g., head_dim, dtype). The system utilizes JitSpec to define compilation requirements and JitSpecRegistry to track them.
 - **AOT (Ahead-Of-Time)**: Provides pre-compiled binaries (flashinfer-cubin) and pre-built caches (flashinfer-jit-cache) to eliminate compilation latency. The aot.py script manages the generation of these modules.
 
 
```

```

 Sources: [README.md94-107](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/README.md?plain=1#L94-L107) [docs/installation.rst32-49](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/installation.rst#L32-L49) [flashinfer/jit/core.py160-201](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/core.py#L160-L201) [flashinfer/aot.py116-213](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/aot.py#L116-L213)

 
## Codebase Organization

 The repository is structured to separate kernel definitions from framework bindings:

 
 - include/: Framework-agnostic CUDA kernel definitions and common utility functions.
 - csrc/: Operator registration to PyTorch, C++ binding code, and Jinja templates for JIT.
 - flashinfer/: Python interface, JIT infrastructure (flashinfer/jit/), and high-level logic.
 - tests/ & docs/: Validation suites and Sphinx documentation configuration.
 
 Sources: [flashinfer/jit/core.py18-20](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/jit/core.py#L18-L20) [docs/conf.py1-42](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/docs/conf.py#L1-L42) [flashinfer/utils.py1-30](https://github.com/flashinfer-ai/flashinfer/blob/2b150b39/flashinfer/utils.py#L1-L30)
