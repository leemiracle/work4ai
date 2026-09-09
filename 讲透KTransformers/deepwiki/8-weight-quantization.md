> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/8-weight-quantization](https://deepwiki.com/kvcache-ai/ktransformers/8-weight-quantization)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Weight Quantization

  Relevant source files 
 - [kt-kernel/ext_bindings.cpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp)
 - [kt-kernel/operators/common.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/common.hpp)
 - [kt-kernel/operators/moe_kernel/moe.hpp](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/moe_kernel/moe.hpp)
 - [kt-kernel/python/experts.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py)
 - [kt-kernel/python/utils/amx.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py)
 - [kt-kernel/python/utils/loader.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py)
 - [kt-kernel/scripts/convert_cpu_weights.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py)
 
  Weight quantization is the process of reducing the precision of model parameters from higher-bit representations (FP16, BF16, FP32) to lower-bit formats (INT4, INT8, FP8) to reduce memory footprint and accelerate inference. KTransformers supports multiple quantization methods optimized for different CPU instruction sets and use cases, particularly focusing on heterogeneous expert placement where "hot" experts reside on GPU and "cold" experts on CPU.

 **Scope**: This document covers quantization methods, weight formats, conversion tools, and backend-specific requirements.

 
 - For details on supported methods, see [Quantization Overview](https://deepwiki.com/kvcache-ai/ktransformers/8.1-quantization-overview).
 - For using conversion tools, see [CPU Weight Conversion](https://deepwiki.com/kvcache-ai/ktransformers/8.2-cpu-weight-conversion).
 - For format technicalities, see [Supported Weight Formats](https://deepwiki.com/kvcache-ai/ktransformers/8.3-supported-weight-formats).
 - For the loading mechanism, see [Weight Loading Pipeline](https://deepwiki.com/kvcache-ai/ktransformers/8.4-weight-loading-pipeline).
 
 
---

 
## Supported Quantization Methods

 KTransformers supports multiple quantization schemes, each optimized for different hardware backends (AMX, AVX512, AVX2) and accuracy requirements. The framework provides specialized wrappers like `AMXMoEWrapper`, `LlamafileMoEWrapper`, and `GeneralMoEWrapper` to handle these methods [kt-kernel/python/experts.py28-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L28-L30)

 
| Method | Precision | Backend | Use Case | Memory Savings |
|---|---|---|---|---|
| AMXINT4 | 4-bit integer | Intel AMX | Maximum memory efficiency on Sapphire Rapids+ kt-kernel/python/utils/amx.py18-31 | ~8x vs BF16 |
| AMXINT8 | 8-bit integer | Intel AMX | Balanced compression and accuracy kt-kernel/python/utils/amx.py19-32 | ~4x vs BF16 |
| FP8 | 8-bit float | AVX512/AMX | High accuracy with compression kt-kernel/python/utils/amx.py21-34 | ~4x vs BF16 |
| RAWINT4 | 4-bit integer | AVX512/AVX2 | Native INT4 weights (e.g., Kimi-K2) kt-kernel/python/utils/amx.py20-33 | ~8x vs BF16 |
| GGUF | Various | LLAMAFILE | Universal CPU compatibility (AVX2+) kt-kernel/python/utils/loader.py19-50 | 4-8x vs BF16 |
| GPTQ_INT4 | 4-bit integer | AVX-VNNI/AVX2 | Optimized for standard x86 CPUs kt-kernel/python/utils/amx.py26-39 | ~8x vs BF16 |

 
### Quantization Decision Flow

 The following diagram illustrates how quantization methods map to specific code entities and hardware:

 
```

```

 **Sources**: [kt-kernel/python/utils/amx.py18-42](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L18-L42) [kt-kernel/python/experts.py34-47](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L34-L47) [kt-kernel/python/utils/loader.py19-50](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L19-L50)

 
---

 
## Weight Conversion Pipeline

 KTransformers provides tools for preparing weights for heterogeneous inference. The primary tool for CPU-optimized weights is `convert_cpu_weights.py` [kt-kernel/scripts/convert_cpu_weights.py1-19](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L1-L19)

 
### CPU Weight Conversion (`convert_cpu_weights.py`)

 This tool converts weights to formats optimized for AMX and AVX inference. It supports input formats like FP8, FP16, and BF16 [kt-kernel/scripts/convert_cpu_weights.py58-67](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L58-L67) For FP8 inputs, it uses a Triton-based dequantization kernel to handle block-wise scaling before re-quantizing for the CPU backend [kt-kernel/scripts/convert_cpu_weights.py34-55](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L34-L55)

 **Key Features**:

 
 - **AWQ Interleaving Reversal**: Handles AWQ-specific weight interleaving to restore original row-major order for CPU kernels [kt-kernel/scripts/convert_cpu_weights.py166-188](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L166-L188)
 - **Packing/Unpacking**: Provides utilities to pack 4-bit integers into 32-bit storage formats for efficient memory transfer [kt-kernel/scripts/convert_cpu_weights.py122-141](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L122-L141)
 - **Config Validation**: Automatically detects model parameters like `num_experts` and `moe_intermediate_size` from `config.json` [kt-kernel/scripts/convert_cpu_weights.py81-86](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L81-L86)
 
 For details, see [CPU Weight Conversion](https://deepwiki.com/kvcache-ai/ktransformers/8.2-cpu-weight-conversion).

 **Sources**: [kt-kernel/scripts/convert_cpu_weights.py24-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L24-L30) [kt-kernel/scripts/convert_cpu_weights.py122-141](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L122-L141) [kt-kernel/scripts/convert_cpu_weights.py178-203](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/scripts/convert_cpu_weights.py#L178-L203)

 
---

 
## Supported Weight Formats

 KTransformers identifies and loads weights through a hierarchy of loaders defined in `loader.py` and `amx.py`.

 
### Format Mapping to Code Entities

 The system uses specific loader classes to handle different file structures and quantization schemes:

 
```

```

 
| Format | Code Implementation | Description |
|---|---|---|
| SafeTensor | SafeTensorLoader | Standard format for AMX/Native quantized weights kt-kernel/python/utils/loader.py102-107 |
| GGUF | GGUFReader | Used by LlamafileMoEWrapper for GGML-style quantization kt-kernel/python/utils/loader.py16-17 |
| CompressedSafeTensor | CompressedSafeTensorLoader | Specialized loader for RAWINT4 and K-Group layouts kt-kernel/python/utils/amx.py10 |
| FP8SafeTensor | FP8SafeTensorLoader | Loader for FP8 weights with block-wise or per-channel scales kt-kernel/python/utils/amx.py11 |
| GPTQSafeTensor | GPTQSafeTensorLoader | Loader for GPTQ-style 4-bit quantized weights kt-kernel/python/utils/amx.py13 |

 For details, see [Supported Weight Formats](https://deepwiki.com/kvcache-ai/ktransformers/8.3-supported-weight-formats).

 **Sources**: [kt-kernel/python/utils/loader.py102-107](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L102-L107) [kt-kernel/python/utils/amx.py8-14](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L8-L14) [kt-kernel/python/experts.py21-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L21-L30)

 
---

 
## Weight Loading Pipeline

 The loading pipeline is managed by the `KTMoEWrapper` factory, which instantiates the correct backend wrapper based on the `method` parameter [kt-kernel/python/experts.py118-145](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L118-L145)

 
### Execution Flow

 
 - **Initialization**: `KTMoEWrapper` selects a backend (e.g., `AMXMoEWrapper` or `LlamafileMoEWrapper`) [kt-kernel/python/experts.py186-210](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L186-L210)
 - **Loader Binding**: The backend initializes a specific loader (e.g., `SafeTensorLoader`) as a singleton or instance [kt-kernel/python/utils/amx.py145-147](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L145-L147)
 - **Expert Loading**: `load_experts` (or `load_weights`) is called to fetch weights and scales for specific layers and NUMA nodes [kt-kernel/python/utils/loader.py175-189](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/loader.py#L175-L189)
 - **C++ Binding**: Weights are passed to the C++ backend (e.g., `TP_MOE<T>::load_weights`) via `pybind11` bindings [kt-kernel/ext_bindings.cpp190-201](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L190-L201)
 
 For details, see [Weight Loading Pipeline](https://deepwiki.com/kvcache-ai/ktransformers/8.4-weight-loading-pipeline).

 **Sources**: [kt-kernel/python/experts.py68-116](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/experts.py#L68-L116) [kt-kernel/python/utils/amx.py139-163](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/utils/amx.py#L139-L163) [kt-kernel/ext_bindings.cpp190-201](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/ext_bindings.cpp#L190-L201) [kt-kernel/operators/moe_kernel/moe.hpp87-112](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/operators/moe_kernel/moe.hpp#L87-L112)
