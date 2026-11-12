> 来源: [https://deepwiki.com/sgl-project/sglang/11-sgl-kernel-library](https://deepwiki.com/sgl-project/sglang/11-sgl-kernel-library)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# sgl-kernel Library

  Relevant source files 
 - [python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh)
 - [python/sglang/kernels/jit/csrc/kimi_k3/situ_and_mul.cuh](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/kimi_k3/situ_and_mul.cuh)
 - [python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh)
 - [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py)
 - [python/sglang/kernels/ops/kimi_k3/activation.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/kimi_k3/activation.py)
 - [python/sglang/kernels/ops/moe/moe_route_quant_fused.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/moe/moe_route_quant_fused.py)
 - [python/sglang/kernels/ops/quantization/per_token_group_quant.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/per_token_group_quant.py)
 - [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py)
 - [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py)
 - [test/manual/dsv4/test_wo_a_fp8_sm90.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/manual/dsv4/test_wo_a_fp8_sm90.py)
 - [test/registered/kernels/benchmark/quantization/bench_per_token_group_quant.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/kernels/benchmark/quantization/bench_per_token_group_quant.py)
 - [test/registered/kernels/ops/gemm/test_cutedsl_bf16_gemm.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/kernels/ops/gemm/test_cutedsl_bf16_gemm.py)
 - [test/registered/kernels/ops/quantization/test_per_token_group_quant.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/kernels/ops/quantization/test_per_token_group_quant.py)
 
  
## Purpose and Scope

 The `sgl-kernel` library is SGLang's custom kernel package that provides optimized CUDA, HIP, and CPU compute primitives for LLM and multimodal serving. It is distributed as an independent Python package with a dedicated build system and versioning separate from the main `sglang` package [.github/workflows/release-whl-kernel.yml8-25](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L8-L25) The library includes a mixture of hand-written CUDA kernels, CUTLASS templated kernels, JIT-compiled templates, and platform-optimized kernels supporting NVIDIA (SM80+ including SM90 and SM100 architectures), AMD ROCm, Intel AMX/XPU, and Moore Threads (MUSA) [.github/workflows/release-whl-kernel.yml18-22](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L18-L22) [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py27-36](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L27-L36)

 This page provides a high-level overview of the kernel library, its build system, kernel categories, and ecosystem integration. Deeper technical details are covered in the child pages:

 
 - [Build System and Multi-Architecture Support](https://deepwiki.com/sgl-project/sglang/11.1-build-system-and-multi-architecture-support) — Explain CMake configuration, multi-architecture compilation (SM90/SM100), ROCm build, and platform-specific builds.
 - [Kernel Categories and Implementations](https://deepwiki.com/sgl-project/sglang/11.2-kernel-categories-and-implementations) — Document kernel organization (attention, GEMM, MoE, elementwise, etc.) and PyTorch binding architecture.
 - [Quantization Kernels](https://deepwiki.com/sgl-project/sglang/11.3-quantization-kernels) — Detail quantization kernel implementations (per_token_quant, scaled_mm, FP8, NVFP4, INT8, AWQ).
 - [MoE Fused Kernels](https://deepwiki.com/sgl-project/sglang/11.4-moe-fused-kernels) — Explain moe_fused_gate, hierarchical expert selection, grouped GEMM kernels, and moe_align kernels.
 - [Third-Party Library Integration](https://deepwiki.com/sgl-project/sglang/11.5-third-party-library-integration) — Document integration with CUTLASS, DeepGEMM, FlashInfer, Flash-Attention, and other libraries.
 - [CPU and JIT Kernel Support](https://deepwiki.com/sgl-project/sglang/11.6-cpu-and-jit-kernel-support) — Document CPU kernel implementations (AMX, NUMA), JIT kernel infrastructure, and platform-specific optimizations.
 
 **Sources:** [.github/workflows/release-whl-kernel.yml1-39](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L1-L39) [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py11-36](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L11-L36) [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py41-45](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py#L41-L45)

 
---

 
## Package Structure and Build System

 
### High-Level Build Architecture

 
```

```

 The build system manages multiple CUDA versions and architectures, including specific support for Blackwell (SM100) and Hopper (SM90) [.github/workflows/release-whl-kernel.yml47-48](https://github.com/sgl-project/sglang/blob/94183a8d/.github/workflows/release-whl-kernel.yml#L47-L48) For DeepSeek-V3/V4 models, the library utilizes `DeepGEMM` and specialized JIT templates to handle varied expert and batch shapes [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py108-115](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L108-L115)

 
### Architecture-Specific Compilation and Features

 
| Target Platform | Toolchain / Build Method | Primary Features |
|---|---|---|
| NVIDIA SM90 | build.sh / nvcc | DeepGEMM, FP8 Grouped GEMM python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py49-59 |
| NVIDIA SM100 | build.sh / nvcc | Blackwell CuTe DSL, NVFP4, TMA-aligned scales python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py10-25 |
| AMD ROCm | build.sh / hipcc | Aiter integration, MI35x support python/sglang/kernels/jit/csrc/kimi_k3/situ_and_mul.cuh23-28 |
| CPU | setuptools | AMX support, JIT compilation for elementwise python/sglang/kernels/ops/kimi_k3/activation.py35-44 |

 Detailed configuration is covered in [Build System and Multi-Architecture Support](https://deepwiki.com/sgl-project/sglang/11.1-build-system-and-multi-architecture-support).

 **Sources:** [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py102-109](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L102-L109) [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py41-43](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py#L41-L43) [python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh25-31](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh#L25-L31)

 
---

 
## Kernel Categories and Implementations

 
### MoE and DeepSeek Kernels

 SGLang provides a comprehensive suite of kernels for Mixture-of-Experts, particularly for DeepSeek architectures:

 
 - **DeepGEMM Integration:** Used for grouped GEMM operations with masked layouts to optimize DeepSeek-V3/V4 performance [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py83-99](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py#L83-L99)
 - **Fused Routing and Quantization:** Fused kernels that perform radix routing and per-token quantization in a single GPU launch to reduce overhead at decode batch sizes [python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh1-6](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh#L1-L6)
 - **SoftCap-GLU (SiTU):** Optimized fused activation kernels for Kimi K3 and similar architectures, including softcap tanh and sigmoid operations [python/sglang/kernels/jit/csrc/kimi_k3/situ_and_mul.cuh47-53](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/kimi_k3/situ_and_mul.cuh#L47-L53)
 
 **Sources:** [python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh45-61](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/moe/route_quant_fused.cuh#L45-L61) [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py111-120](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py#L111-L120) [python/sglang/kernels/ops/kimi_k3/activation.py47-58](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/kimi_k3/activation.py#L47-L58)

 
### Quantization Kernels

 The library supports various quantization schemes:

 
 - **Per-Token Group Quantization:** Optimized kernels for `per_token_group_quant` supporting both float32 and `ue8m0` (Blackwell-specific) scale layouts [python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh106-118](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh#L106-L118)
 - **TMA-Aligned Tensor Support:** Specialized handling for Blackwell TMA (Tensor Memory Accelerator) layouts, ensuring correct memory alignment for high-performance FP8/FP4 operations [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py25-42](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py#L25-L42)
 
 See child page [Quantization Kernels](https://deepwiki.com/sgl-project/sglang/11.3-quantization-kernels) for implementation details.

 **Sources:** [python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh59-75](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh#L59-L75) [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py196-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py#L196-L200) [python/sglang/kernels/ops/quantization/per_token_group_quant.py162-174](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/per_token_group_quant.py#L162-L174)

 
---

 
## CPU and JIT Kernel Support

 SGLang utilizes a JIT (Just-In-Time) infrastructure to handle kernels that require specific model parameters or hardware alignments:

 
 - **JIT Infrastructure:** The `sglang.kernels.jit` namespace contains C++ templates compiled at runtime using a caching system (`load_jit`) to match specific dtypes and group sizes [python/sglang/kernels/ops/quantization/per_token_group_quant.py24-35](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/per_token_group_quant.py#L24-L35)
 - **Dynamic DeepGEMM Compilation:** SGLang implements a pre-compilation system for DeepGEMM kernels, covering a wide range of batch sizes (M) to avoid latency spikes during serving [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py61-87](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L61-L87)
 - **Blackwell CuTe DSL:** Python-based JIT for SM100 using the NVIDIA CuTe DSL, allowing for low-latency GEMM kernels with customized warp specialization [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py103-123](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py#L103-L123)
 
 For details, see [CPU and JIT Kernel Support](https://deepwiki.com/sgl-project/sglang/11.6-cpu-and-jit-kernel-support).

 **Sources:** [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py144-159](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L144-L159) [python/sglang/kernels/ops/quantization/per_token_group_quant.py54-61](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/per_token_group_quant.py#L54-L61) [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py172-180](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py#L172-L180)

 
---

 
## Bridging Natural Language Concepts to Code Entities

 
### Diagram: DeepSeek Execution Path Selection

 
```

```

 
### Diagram: Quantization Kernel System

 
```

```

 
---

 
## Summary

 The `sgl-kernel` library provides the performance foundation for SGLang, bridging high-level model definitions to hardware-optimized execution. By combining AOT-compiled C++/CUDA kernels with a flexible JIT system and multi-platform support (NVIDIA, AMD, MUSA, CPU), it ensures that SGLang can leverage the full capabilities of modern AI accelerators.

 **Sources:** [python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py1-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py#L1-L100) [python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh1-150](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/jit/csrc/gemm/per_token_group_quant.cuh#L1-L150) [python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py1-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/gemm/cutedsl_bf16_gemm.py#L1-L100) [python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py1-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/deep_gemm_wrapper/entrypoint.py#L1-L100) [python/sglang/kernels/ops/quantization/per_token_group_quant.py1-100](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/kernels/ops/quantization/per_token_group_quant.py#L1-L100)
