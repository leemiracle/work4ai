> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/14-glossary](https://deepwiki.com/kvcache-ai/ktransformers/14-glossary)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Glossary

  Relevant source files 
 - [.github/workflows/release-pypi.yml](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/workflows/release-pypi.yml)
 - [README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1)
 - [doc/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1)
 - [doc/SUMMARY.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/SUMMARY.md?plain=1)
 - [doc/en/DeepseekR1_V3_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1)
 - [doc/en/FAQ.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/FAQ.md?plain=1)
 - [doc/en/kt-kernel/experts-sched-Tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/experts-sched-Tutorial.md?plain=1)
 - [kt-kernel/CMakeLists.txt](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/CMakeLists.txt)
 - [kt-kernel/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1)
 - [kt-kernel/README_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1)
 - [kt-kernel/ext_bindings.cpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp)
 - [kt-kernel/install.sh](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/install.sh)
 - [kt-kernel/python/__init__.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/__init__.py)
 - [kt-kernel/python/cli/__init__.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/__init__.py)
 - [kt-kernel/python/experts.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py)
 - [kt-kernel/python/utils/amx.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py)
 - [kt-kernel/python/utils/loader.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py)
 - [kt-kernel/setup.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py)
 - [version.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/version.py)
 
  This glossary provides definitions and technical details for terms, jargon, and domain-specific concepts used within the KTransformers codebase. It is intended to help onboarding engineers navigate the hybrid CPU-GPU architecture and the specialized high-performance kernels.

 
## Core Concepts & Architecture

 
### MoE (Mixture of Experts)

 A model architecture where only a subset of parameters (experts) are activated for each input token. KTransformers specializes in heterogeneous MoE inference, where "hot" experts are placed on the GPU and "cold" experts are placed on the CPU or Disk [README.md14-17](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L17)

 
### MLA (Multi-head Latent Attention)

 An attention mechanism used in models like DeepSeek-V3/R1 that reduces KV cache memory usage by compressing keys and values into a latent vector. KTransformers integrates Triton-based MLA kernels for efficient processing [doc/en/DeepseekR1_V3_tutorial.md96-97](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L96-L97)

 
### NUMA (Non-Uniform Memory Access)

 A memory design used in multi-socket systems where memory access time depends on the memory location relative to the processor. KTransformers implements NUMA-aware memory management and thread pools to minimize cross-socket latency [kt-kernel/README.md45](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L45-L45) [kt-kernel/ext_bindings.cpp22-23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L22-L23)

 
### GGUF

 A binary file format for storing models for inference with `llama.cpp` and `llamafile`. KTransformers uses GGUF for its universal CPU backend and provides loaders to map GGUF tensors to internal structures [kt-kernel/python/utils/loader.py6-7](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L6-L7) [kt-kernel/README.md32](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L32-L32)

 
### KGroup

 A quantization technique where weights are grouped, and each group has its own scale factor. Specifically used in the `AMXInt4_KGroup_MOE` operator for models like Kimi-K2 [kt-kernel/python/utils/amx.py20-21](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L20-L21)

 
## Module Definitions

 
| Term | Definition |
|---|---|
| kt-kernel | The core C++/CUDA module containing high-performance inference kernels (AMX, AVX, etc.) README.md55-57 |
| kt-sft | The fine-tuning module that integrates with LLaMA-Factory for resource-efficient training README.md89-91 |
| sglang-kt | A specialized build of the SGLang frontend optimized for KTransformers integration README.md30 .github/workflows/release-pypi.yml25-26 |
| balance_serve | A multi-concurrency backend engine supporting continuous batching and chunked prefill README.md41 |
| CPUInfer | The C++ class responsible for managing CPU-side execution threads and task enqueuing kt-kernel/ext_bindings.cpp22 |
| WorkerPool | A thread pool management system, often divided into NUMA-specific subpools for parallel execution kt-kernel/ext_bindings.cpp23 |

 **Sources:** [README.md14-17](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L17) [kt-kernel/README.md55-57](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L55-L57) [kt-kernel/ext_bindings.cpp22-23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L22-L23)

 
## Hardware Acceleration & Kernels

 
### AMX (Advanced Matrix Extensions)

 Intel's hardware acceleration for matrix operations (found in Sapphire Rapids and newer). KTransformers provides several AMX-specific operators:

 
 - **AMXINT4 / AMXINT8**: Quantized integer backends for MoE experts [kt-kernel/python/utils/amx.py18-19](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L18-L19)
 - **AMXBF16**: Native Brain Floating Point 16-bit support [kt-kernel/python/utils/amx.py22](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L22-L22)
 - **RAWINT4**: An AMX-based backend specifically for KGroup-style weights [kt-kernel/python/utils/amx.py31](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L31-L31)
 
 
### llamafile Backend

 A universal CPU backend built on `llamafile` that supports AVX2 and AVX512. It is used as a fallback for non-AMX CPUs or for models provided in GGUF format [kt-kernel/README.md44](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L44-L44) [kt-kernel/ext_bindings.cpp72-75](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L72-L75)

 
### CRTP (Curiously Recurring Template Pattern)

 A C++ design pattern used in the kernel implementation to achieve compile-time polymorphism without the overhead of virtual functions. This is used in the native BF16 MoE implementation [kt-kernel/ext_bindings.cpp46](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L46-L46)

 
### TP_MOE

 The C++ template class representing a Tensor Parallel MoE operator. It handles the logic for distributing expert computation across threads and NUMA nodes [kt-kernel/ext_bindings.cpp179](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L179-L179)

 **Sources:** [kt-kernel/python/utils/amx.py18-31](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L18-L31) [kt-kernel/ext_bindings.cpp46-75](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L46-L75)

 
## System Data Flow & Logic

 
### Physical-to-Logical Map

 A mapping used during weight loading to associate physical expert indices in a file with the logical expert IDs used by the model architecture. This is critical for Tensor Parallelism where different nodes handle different expert subsets [kt-kernel/ext_bindings.cpp201-205](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L201-L205)

 
### Deferred Experts

 An optimization strategy where certain expert computations are delayed or scheduled differently to balance load between CPU and GPU [kt-kernel/python/utils/amx.py160](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L160-L160)

 
### Prefill Strategies

 
 - **Layerwise Prefill**: Processing the prefill stage one layer at a time.
 - **Chunked Prefill**: Breaking large input prompts into smaller "chunks" to prevent OOM and improve scheduling in multi-concurrency scenarios [README.md41](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L41-L41)
 
 
### Continuous Batching

 A scheduling technique implemented in the `balance_serve` backend that allows new requests to be added to a batch as soon as others finish [README.md41](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L41-L41)

 
### System Architecture: Request to Kernel

 The following diagram bridges the high-level serving concepts to the low-level C++ entities.

 **Diagram: Inference Request Lifecycle**

 
```

```

 **Sources:** [README.md41](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L41-L41) [kt-kernel/python/utils/amx.py139-163](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L139-L163) [kt-kernel/ext_bindings.cpp22-23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L22-L23) [kt-kernel/ext_bindings.cpp179](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L179-L179)

 
## Memory & Buffers

 
### KExpertsCPUBuffer

 A Python-side wrapper for managing CPU memory buffers used during MoE inference. It handles allocation and ensures memory is aligned for high-performance kernels.

 
### Injection Rules

 YAML-based configuration files that define how standard PyTorch modules (like `Linear` or `MoE`) should be replaced by KTransformers' optimized kernels during model loading [README.md48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L48-L48)

 
### MTP Weights

 Multi-Token Prediction weights, supported in newer models like GLM-5.1, allowing the model to predict multiple future tokens in a single forward pass [README.md23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L23-L23)

 **Diagram: Weight Loading Pipeline**

 
```

```

 **Sources:** [kt-kernel/python/utils/loader.py102-115](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L102-L115) [kt-kernel/ext_bindings.cpp201-205](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L201-L205)

 
## Quantization Formats

 
| Format | Description |
|---|---|
| FP8 | 8-bit floating point, used for high-performance DeepSeek-V3/R1 inference kt-kernel/python/utils/amx.py21 |
| BF16 | Bfloat16, native precision for many modern LLMs, supported via AVX512-BF16 or AMX kt-kernel/python/utils/amx.py22 |
| INT4 / INT8 | Standard integer quantization, optimized via AMX VNNI instructions kt-kernel/python/utils/amx.py18-19 |
| RAWINT4 | KTransformers-specific format for KGroup weights where scales are handled separately from the 4-bit integer payload kt-kernel/python/utils/amx.py31 |
| GPTQ_INT4 | GPTQ 4-bit integer quantization, supported via AVX2 and AVX-VNNI backends kt-kernel/python/utils/amx.py26-28 |

 **Sources:** [kt-kernel/python/utils/amx.py18-31](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L18-L31) [kt-kernel/README.md30-33](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L30-L33)
