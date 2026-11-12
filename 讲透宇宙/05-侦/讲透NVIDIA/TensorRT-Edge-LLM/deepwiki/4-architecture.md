<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-Edge-LLM · page 4 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [cpp/CMakeLists.txt](cpp/CMakeLists.txt)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the TensorRT-Edge-LLM system architecture, describing the major components and their interactions. The architecture spans from Python-based model preparation through C++ runtime execution on edge devices, optimized for NVIDIA platforms such as Jetson and DRIVE.

For detailed information on specific components:
- Python-to-C++ deployment flow: see [System Overview](#4.1)
- C++ library internals (edgellmCore, edgellmKernels, etc.): see [C++ Core Libraries](#4.2)
- Runtime execution, memory management, and KV cache: see [Runtime Components](#4.3)
- Custom TensorRT layers (Attention, Mamba, MoE): see [TensorRT Plugins](#4.4)
- Experimental loader and server: see [Experimental LLM Loader](#4.5)

---

## Architectural Overview

The TensorRT-Edge-LLM system follows a two-stage deployment architecture: **offline model preparation** and **online inference execution**.

### Deployment Pipeline

```mermaid
graph TB
    subgraph Python["Python Layer (Model Preparation)"]
        HF["HuggingFace Models<br/>transformers library"]
        QUANT["tensorrt-edgellm-quantize-llm<br/>Quantization CLI"]
        EXPORT["tensorrt-edgellm-export-llm<br/>ONNX Export CLI"]
        ONNX["ONNX Model Files<br/>.onnx"]
        LLM_LOADER["experimental/llm_loader<br/>AutoModel/Registry"]
    end
    
    subgraph CPP["C++ Build Layer (Engine Generation)"]
        BUILDER_LIB["edgellmBuilder<br/>Static Library"]
        CORE_LIB["edgellmCore<br/>Static Library"]
        KERNELS_LIB["edgellmKernels<br/>Static Library"]
        TOKENIZER_LIB["edgellmTokenizer<br/>Static Library"]
        PLUGIN_LIB["NvInfer_edgellm_plugin.so<br/>Shared Library"]
    end
    
    subgraph Apps["Executables"]
        BUILD_EXE["llm_build<br/>Engine Builder"]
        INFER_EXE["llm_inference<br/>Inference Runner"]
    end
    
    subgraph Runtime["Runtime Artifacts"]
        ENGINE["TensorRT Engine<br/>.engine files"]
        JSON_IN["Input JSON<br/>requests.json"]
        JSON_OUT["Output JSON<br/>responses.json"]
    end
    
    HF --> QUANT
    QUANT --> EXPORT
    EXPORT --> ONNX
    HF --> LLM_LOADER
    LLM_LOADER --> ONNX
    
    ONNX --> BUILD_EXE
    BUILDER_LIB --> BUILD_EXE
    PLUGIN_LIB --> BUILD_EXE
    
    BUILD_EXE --> ENGINE
    
    ENGINE --> INFER_EXE
    JSON_IN --> INFER_EXE
    CORE_LIB --> INFER_EXE
    TOKENIZER_LIB --> INFER_EXE
    PLUGIN_LIB --> INFER_EXE
    KERNELS_LIB --> INFER_EXE
    
    INFER_EXE --> JSON_OUT
```

**Sources:** [cpp/common/trtUtils.h:60-92](), [cpp/common/version.h:28-34](), [cpp/CMakeLists.txt:62-120]()

The pipeline separates **model preparation** (flexible Python environment) from **inference execution** (optimized C++ runtime). This design enables model conversion on development hosts while inference runs on resource-constrained edge devices.

---

## Component Layers

The system is organized into distinct layers, each with specific responsibilities.

### Layer Architecture

```mermaid
graph TB
    subgraph Layer1["Layer 1: Model Preparation (Python)"]
        PY_QUANT["quantize_llm.py<br/>Quantization logic"]
        PY_EXPORT["export_llm.py<br/>ONNX export logic"]
        LLM_LOADER["llm_loader/auto_model.py<br/>AutoModel class"]
    end
    
    subgraph Layer2["Layer 2: Build Infrastructure (C++)"]
        BUILDER["builder/builder.cpp<br/>LLMBuilder class"]
        ONNX_PARSER["nvonnxparser<br/>TensorRT ONNX Parser"]
        TRT_BUILDER["nvinfer<br/>IBuilder"]
    end
    
    subgraph Layer3["Layer 3: Runtime Execution (C++)"]
        DECODER["runtime/decoder.cpp<br/>Decoder class"]
        SAMPLER["sampler/sampler.cu<br/>Sampling kernels"]
        TENSOR["common/tensor.h<br/>Tensor class"]
        MULTIMODAL["multimodal/runner.cpp<br/>MultimodalRunner"]
    end
    
    subgraph Shared["Shared Components"]
        PLUGIN["plugins/attentionPlugin.cpp<br/>AttentionPlugin"]
        KERNELS["kernels/<br/>CUDA kernel implementations"]
        TOKENIZER["tokenizer/llamaTokenizer.cpp<br/>qwenTokenizer.cpp"]
    end
    
    PY_EXPORT -.ONNX files.-> BUILDER
    LLM_LOADER -.ONNX files.-> BUILDER
    
    BUILDER --> ONNX_PARSER
    BUILDER --> TRT_BUILDER
    
    BUILDER -.engine files.-> DECODER
    
    DECODER --> SAMPLER
    DECODER --> TENSOR
    MULTIMODAL --> DECODER
    
    PLUGIN --> BUILDER
    PLUGIN --> DECODER
    KERNELS --> PLUGIN
    KERNELS --> SAMPLER
    TOKENIZER --> DECODER
```

**Sources:** [cpp/common/trtUtils.h:96-97](), [cpp/common/trtUtils.h:181-182](), [cpp/CMakeLists.txt:101-106]()

---

## C++ Library Dependencies

The C++ codebase is organized into four static libraries and one shared library to manage dependencies and visibility.

### Library Dependency Graph

```mermaid
graph TD
    subgraph External["External Dependencies"]
        CUDA["CUDA Runtime<br/>cudart"]
        TRT["TensorRT<br/>nvinfer"]
        ONNX["ONNX Parser<br/>nvonnxparser"]
        JSON["nlohmann::json"]
    end
    
    subgraph Static["Static Libraries"]
        KERNELS["edgellmKernels<br/>kernels/*.cu + common/*.cpp"]
        TOKENIZER["edgellmTokenizer<br/>tokenizer/*.cpp"]
        BUILDER["edgellmBuilder<br/>builder/*.cpp"]
        CORE["edgellmCore<br/>runtime/* + sampler/* + multimodal/*"]
    end
    
    subgraph Shared["Shared Library"]
        PLUGIN["NvInfer_edgellm_plugin.so<br/>plugins/*.cpp"]
    end
    
    CUDA --> KERNELS
    CUDA --> CORE
    TRT --> BUILDER
    TRT --> PLUGIN
    ONNX --> BUILDER
    JSON --> CORE
    JSON --> BUILDER
    
    KERNELS --> CORE
    KERNELS --> PLUGIN
    TOKENIZER --> CORE
    
    BUILDER --> CORE
    PLUGIN --> CORE
```

**Sources:** [cpp/common/trtUtils.h:20-30](), [cpp/common/trtUtils.cpp:18-34](), [cpp/CMakeLists.txt:62-120]()

### Library Composition

| Library | Purpose | Key Symbols |
|---------|---------|-------------|
| `edgellmKernels` | Low-level CUDA kernels (FMHA, MoE, Mamba) and base utilities. | `captureTRTCudaGraph` [cpp/common/trtUtils.h:96](), `cudaUtils.h` |
| `edgellmTokenizer` | Text tokenization for supported model families (Llama, Qwen). | `llamaTokenizer.cpp`, `qwenTokenizer.cpp` |
| `edgellmBuilder` | Engine building logic using `nvonnxparser`. | `deserializeCudaEngineFromFile` [cpp/common/trtUtils.h:181]() |
| `edgellmCore` | High-level runtime orchestration, including samplers and multimodal runners. | `AuxStreamSet` [cpp/common/trtUtils.h:102](), `version::checkVersion` [cpp/common/version.h:34]() |
| `NvInfer_edgellm_plugin` | Shared library for custom TensorRT layers required by the engine. | `initEdgellmPlugins` [cpp/common/trtUtils.h:85](), `DlDeleter` [cpp/common/trtUtils.h:39]() |

**Sources:** [cpp/CMakeLists.txt:62-120]()

---

## Key Design Patterns

### Runtime Resource Management

The system utilizes specialized RAII classes to manage complex TensorRT and CUDA resources, ensuring safe lifecycle management on edge devices.

```mermaid
graph LR
    subgraph RAII["RAII Resource Managers"]
        AUX["AuxStreamSet<br/>trtUtils.h"]
        DL["DlDeleter<br/>trtUtils.h"]
        BUF["PinnedHostBuffer<br/>trtUtils.cpp"]
    end
    
    subgraph TRT_Context["TRT Context"]
        CTX["IExecutionContext"]
        ENG["ICudaEngine"]
    end
    
    AUX -->|"manages"| CTX
    DL -->|"manages"| ENG
    BUF -->|"accelerates"| ENG
```

**Sources:** [cpp/common/trtUtils.h:39-50](), [cpp/common/trtUtils.h:102-157](), [cpp/common/trtUtils.cpp:56-153]()

- **`DlDeleter`**: Handles proper cleanup of dynamically loaded plugin libraries using `dlclose` with `RTLD_NODELETE` to avoid teardown crashes [cpp/common/trtUtils.h:74-76]().
- **`AuxStreamSet`**: Manages non-blocking auxiliary streams for `IExecutionContext::setAuxStreams()`, ensuring they outlive the context [cpp/common/trtUtils.h:99-102]().
- **`PinnedHostBuffer`**: Facilitates efficient engine deserialization by managing pinned memory and CUDA events for asynchronous transfers [cpp/common/trtUtils.cpp:59-81]().

### Optimized Engine Loading

The `FileStreamReaderV2` implementation enables deserializing TensorRT engine plans from disk without mapping the entire plan into process memory, which is critical for memory-constrained edge devices [cpp/common/trtUtils.h:181-182](). It uses a chunked transfer mechanism via `PinnedHostBuffer` to stream data to the device [cpp/common/trtUtils.cpp:160-162]().

---

## Execution Flow

### Inference Pipeline

The execution flow starts from engine deserialization and moves through tokenization to the autoregressive generation loop.

```mermaid
graph TB
    subgraph Init["Initialization"]
        PLUGIN_LOAD["loadEdgellmPluginLib()<br/>trtUtils.h"]
        ENGINE_LOAD["deserializeCudaEngineFromFile()<br/>trtUtils.h"]
        VERSION_CHECK["version::checkVersion()<br/>version.h"]
    end
    
    subgraph Loop["Generation Loop"]
        EXEC["IExecutionContext::enqueueV3()"]
        SAMPLE["Sampler::sample()"]
        GRAPH["captureTRTCudaGraph()<br/>(Optional optimization)"]
    end
    
    PLUGIN_LOAD --> ENGINE_LOAD
    ENGINE_LOAD --> VERSION_CHECK
    VERSION_CHECK --> EXEC
    EXEC --> SAMPLE
    SAMPLE --> EXEC
    EXEC -.-> GRAPH
```

**Sources:** [cpp/common/trtUtils.h:60-97](), [cpp/common/version.h:34]()

For details on how these components interact in specific scenarios, see the child pages:
- [System Overview](#4.1)
- [C++ Core Libraries](#4.2)
- [Runtime Components](#4.3)
- [TensorRT Plugins](#4.4)
- [Experimental LLM Loader](#4.5)

---

