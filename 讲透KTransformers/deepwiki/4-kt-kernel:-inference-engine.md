> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/4-kt-kernel:-inference-engine](https://deepwiki.com/kvcache-ai/ktransformers/4-kt-kernel:-inference-engine)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# kt-kernel: Inference Engine

  Relevant source files 
 - [.github/workflows/release-pypi.yml](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/workflows/release-pypi.yml)
 - [kt-kernel/CMakeLists.txt](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/CMakeLists.txt)
 - [kt-kernel/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1)
 - [kt-kernel/README_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README_zh.md?plain=1)
 - [kt-kernel/ext_bindings.cpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp)
 - [kt-kernel/install.sh](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/install.sh)
 - [kt-kernel/python/experts.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py)
 - [kt-kernel/python/utils/amx.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py)
 - [kt-kernel/python/utils/loader.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py)
 - [kt-kernel/setup.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py)
 
  
## Purpose and Scope

 `kt-kernel` is the high-performance CPU inference engine for KTransformers, providing optimized MoE (Mixture-of-Experts) operator implementations for heterogeneous CPU-GPU inference. It delivers hardware-accelerated matrix operations using Intel AMX, AVX512, AVX2, and vendor-specific libraries (BLIS for AMD, KML for ARM).

 This page provides an overview of kt-kernel's architecture, backend system, and integration points. For detailed information:

 
 - Runtime architecture and dynamic loading: see [Architecture and Design](https://deepwiki.com/kvcache-ai/ktransformers/4.1-architecture-and-design)
 - MoE operator internals and C++ interfaces: see [MoE Operator System](https://deepwiki.com/kvcache-ai/ktransformers/4.2-moe-operator-system)
 - Production serving integration: see [SGLang Integration](https://deepwiki.com/kvcache-ai/ktransformers/4.3-sglang-integration)
 - Python wrapper APIs: see [Python API Reference](https://deepwiki.com/kvcache-ai/ktransformers/4.4-python-api-reference)
 - Command-line tools: see [CLI Tools (kt-cli)](https://deepwiki.com/kvcache-ai/ktransformers/4.5-cli-tools-(kt-cli))
 
 For training-related functionality, see [kt-sft: Fine-Tuning Framework](https://deepwiki.com/kvcache-ai/ktransformers/5-kt-sft:-fine-tuning-framework).

 **Sources:** [kt-kernel/README.md1-47](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L1-L47)

 
---

 
## System Architecture

 kt-kernel employs a three-layer architecture with runtime CPU detection, dynamic backend selection, and hardware-optimized operator implementations.

 
### Architecture Layers

 
```

```

 **Progressive Variant Fallback Chain:** The runtime loader attempts variants in order: `amx` → `avx512_bf16` → `avx512_vbmi` → `avx512_vnni` → `avx512_base` → `avx2`. If a variant's `.so` file is missing, it automatically falls back to the next lower variant.

 **Sources:** [kt-kernel/python/_cpu_detect.py26-164](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/_cpu_detect.py#L26-L164) [kt-kernel/setup.py258-431](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py#L258-L431) [kt-kernel/README.md112-122](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L112-L122)

 
---

 
## Core Components

 
### Python API Layer

 The Python layer provides the main entry points for expert execution and memory management:

 **`KTMoEWrapper`** (`kt-kernel/python/experts.py`) - Factory-based interface:

 
 - **Constructor**: `KTMoEWrapper(layer_idx, num_experts, num_experts_per_tok, hidden_size, moe_intermediate_size, gpu_experts_mask, cpuinfer_threads, threadpool_count, weight_path, chunked_prefill_size, method, ...)` [kt-kernel/python/experts.py118-180](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L118-L180)
 - **Backend Selection**: Automatically selects between `AMXMoEWrapper`, `NativeMoEWrapper`, `LlamafileMoEWrapper`, or `GeneralMoEWrapper` based on the `method` parameter [kt-kernel/python/experts.py186-218](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L186-L218)
 - **SFT Support**: Includes specific logic for Supervised Fine-Tuning modes and LoRA ranks [kt-kernel/python/experts.py221-255](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L221-L255)
 
 **`BaseMoEWrapper`** (`kt-kernel/python/experts_base.py`) - Abstract base class:

 
 - **Core Interface**: Defines the contract for weight loading (`load_weights`) and expert execution.
 - **Asynchronous API**: Supports `submit_forward()` and `sync_forward()` to enable CPU-GPU pipelining.
 - **Buffer Management**: Integrates with `KExpertsCPUBuffer` to manage pinned memory for efficient data transfer.
 
 **Sources:** [kt-kernel/python/experts.py68-255](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L68-L255) [kt-kernel/python/experts_base.py25-300](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts_base.py#L25-L300)

 
---

 
### Runtime CPU Detection

 The package automatically detects hardware capabilities to load the most optimized kernel variant at runtime.

 
```

```

 **Detection Algorithm:** [kt-kernel/python/_cpu_detect.py26-106](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/_cpu_detect.py#L26-L106) The `detect_cpu_features()` function parses `/proc/cpuinfo` flags on Linux to identify support for AMX, AVX512 variants (VNNI, BF16, VBMI), and AVX2.

 **Loader Implementation:** [kt-kernel/python/_cpu_detect.py165-264](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/_cpu_detect.py#L165-L264) The `load_extension(variant)` function handles the dynamic loading of the C++ shared objects and implements a progressive fallback chain if the optimal variant is unavailable.

 **Sources:** [kt-kernel/python/_cpu_detect.py1-295](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/_cpu_detect.py#L1-L295) [kt-kernel/python/__init__.py38-49](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/__init__.py#L38-L49)

 
---

 
### C++ Extension Build System

 The build system produces multiple optimized binaries in a single compilation pass to support the runtime detection system.

 **Build Script Implementation:** The `setup.py` build system implements two modes via `CMakeBuild.build_extension()` [kt-kernel/setup.py:244-256]:

 
 - **Multi-variant mode** (`CPUINFER_BUILD_ALL_VARIANTS=1`): Builds all 6 configurations (AMX, AVX512 variants, AVX2) [kt-kernel/setup.py251-256](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py#L251-L256)
 - **Single-variant mode**: Builds only the NATIVE or specified target variant [kt-kernel/setup.py254-256](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py#L254-L256)
 
 **CMake Integration:**

 
 - **AMX detection**: Auto-enables if `amx_tile`, `amx_int8`, `amx_bf16` are detected [kt-kernel/setup.py182-185](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py#L182-L185)
 - **Architecture flags**: Configured via `ARCH_FLAGS` in [kt-kernel/CMakeLists.txt154-180](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/CMakeLists.txt#L154-L180)
 
 **Sources:** [kt-kernel/setup.py10-48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/setup.py#L10-L48) [kt-kernel/CMakeLists.txt1-180](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/CMakeLists.txt#L1-L180) [kt-kernel/install.sh149-196](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/install.sh#L149-L196)

 
---

 
## Backend Implementations

 kt-kernel supports multiple MoE backends implemented as C++ template specializations.

 
| Backend | Method String | Implementation Class | Hardware | Weight Format |
|---|---|---|---|---|
| AMX KGroup | "RAWINT4" | AMXInt4_KGroup_MOE | Sapphire Rapids+ | RAWINT4 (KGroup) |
| AMX INT4 | "AMXINT4" | AMXInt4_MOE | Sapphire Rapids+ | INT4 Quantized |
| AMX INT8 | "AMXINT8" | AMXInt8_MOE | Sapphire Rapids+ | INT8 Quantized |
| AMX FP8 | "FP8" | AMXFP8_MOE | Ice Lake+ / Zen 4+ | FP8 SafeTensor |
| AMX BF16 | "BF16" | AMXBF16_MOE | Ice Lake+ / Zen 4+ | BF16 SafeTensor |
| llamafile | "LLAMAFILE" | MOE (llamafile) | AVX2+ | GGUF (Q4_K, etc.) |
| General MoE | "MOE_INT8" | Int8_KERNEL_MOE | Universal | INT8 |

 **Backend Selection**: Selection is handled in `KTMoEWrapper` [kt-kernel/python/experts.py186-218](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L186-L218) and exposed via pybind11 in `kt-kernel/ext_bindings.cpp`.

 **Sources:** [kt-kernel/python/experts.py34-65](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L34-L65) [kt-kernel/python/utils/amx.py18-42](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L18-L42) [kt-kernel/ext_bindings.cpp44-63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L44-L63)

 
---

 
## Weight Loading Pipeline

 The engine supports various weight formats and loading mechanisms:

 
 - **SafeTensorLoader**: Primary loader for AMX-quantized weights (INT4/INT8) and native formats (FP8/BF16) [kt-kernel/python/utils/loader.py102-170](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L102-L170)
 - **GGUFLoader**: Specialized loader for llamafile-based GGUF weights [kt-kernel/python/utils/loader.py16-52](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L16-L52)
 - **Online Quantization**: Supported for `GeneralMoEWrapper` via `load_weights_from_tensors()` which quantizes FP16/BF16 tensors to INT4/INT8 at runtime.
 
 **NUMA Sharding**: Weights can be sharded across NUMA nodes for multi-socket systems to maximize memory bandwidth [kt-kernel/python/utils/loader.py175-189](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L175-L189)

 **Sources:** [kt-kernel/python/utils/loader.py1-200](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L1-L200) [kt-kernel/python/utils/amx.py145-146](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L145-L146)

 
---

 
## SGLang Integration

 kt-kernel integrates with SGLang to provide high-performance CPU expert execution for production serving.

 **Key Parameters**:

 
 - `--kt-method`: Selects the backend (e.g., `AMXINT8`, `LLAMAFILE`) [kt-kernel/README.md183](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L183-L183)
 - `--kt-cpuinfer`: Sets the number of CPU inference threads [kt-kernel/README.md185](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L185-L185)
 - `--kt-threadpool-count`: Sets the number of NUMA thread pools [kt-kernel/README.md186](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L186-L186)
 - `--kt-num-gpu-experts`: Configures the number of experts to remain on GPU [kt-kernel/README.md187](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L187-L187)
 - `--kt-max-deferred-experts-per-token`: Configures pipelining depth [kt-kernel/README.md188](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L188-L188)
 
 **Sources:** [kt-kernel/README.md109-191](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/README.md?plain=1#L109-L191)

 
---

 
## CI/CD and Distribution

 
### PyPI Release Pipeline

 The project uses GitHub Actions to build and distribute multi-variant wheels.

 **Workflow Highlights**:

 
 - **Multi-Variant Build**: Builds for Python 3.11 and 3.12 with all CPU variants included in a single wheel [kt-kernel/.github/workflows/release-pypi.yml109-122](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/.github/workflows/release-pypi.yml#L109-L122)
 - **Static CUDA**: Statically links the CUDA runtime so users do not need the CUDA toolkit installed [kt-kernel/.github/workflows/release-pypi.yml113-159](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/.github/workflows/release-pypi.yml#L113-L159)
 - **Verification**: Automates verification of CPU variants and CUDA support before publishing [kt-kernel/.github/workflows/release-pypi.yml124-150](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/.github/workflows/release-pypi.yml#L124-L150)
 
 **Sources:** [.github/workflows/release-pypi.yml76-221](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/.github/workflows/release-pypi.yml#L76-L221)
