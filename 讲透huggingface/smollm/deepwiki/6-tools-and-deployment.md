<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smollm · page 6 Tools and Deployment · fetched 2026-10-26 -->

# Tools and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tools/README.md](tools/README.md)

</details>



This document covers the tools and infrastructure for deploying and running SmolLM models locally across different platforms. It includes local inference tools, deployment strategies, and utility scripts for working with SmolLM3, SmolLM2, and SmolVLM models on various hardware configurations and frameworks.

For training infrastructure and pipelines, see [SmolLM3 Pretraining](#2.2) and [SmolLM2 Fine-tuning](#3.2). For model evaluation frameworks, see [SmolLM3 Evaluation](#2.4).

## Deployment Ecosystem Overview

The SmolLM repository provides multiple deployment paths optimized for different use cases, from edge devices to local development environments. The deployment ecosystem supports CPU-only inference, GPU acceleration, and specialized hardware optimizations.

### Deployment Architecture

```mermaid
graph TB
    subgraph "SmolLM Models"
        SmolLM3["SmolLM3-3B"]
        SmolLM2_135M["SmolLM2-135M"]
        SmolLM2_360M["SmolLM2-360M"] 
        SmolLM2_1_7B["SmolLM2-1.7B"]
        SmolVLM["SmolVLM"]
    end
    
    subgraph "Local Inference Frameworks"
        LlamaCpp["llama.cpp"]
        MLX["MLX"]
        MLC["MLC"]
        TransformersJS["Transformers.js"]
        HFTransformers["HuggingFace Transformers"]
    end
    
    subgraph "Platform Targets"
        MacOS["macOS (Apple Silicon)"]
        Linux["Linux (x86_64)"]
        Windows["Windows"]
        WebBrowser["Web Browser"]
        MobileDevice["Mobile Devices"]
    end
    
    subgraph "Deployment Tools"
        SmolTools["smol-tools"]
        LocalInferenceTools["Local Inference Tools"]
        ConversionScripts["Model Conversion Scripts"]
    end
    
    SmolLM3 --> LlamaCpp
    SmolLM3 --> MLX
    SmolLM3 --> HFTransformers
    
    SmolLM2_135M --> LlamaCpp
    SmolLM2_135M --> TransformersJS
    SmolLM2_135M --> SmolTools
    
    SmolLM2_360M --> LlamaCpp
    SmolLM2_360M --> MLX
    SmolLM2_360M --> MLC
    
    SmolLM2_1_7B --> LlamaCpp
    SmolLM2_1_7B --> MLX
    SmolLM2_1_7B --> MLC
    
    SmolVLM --> MLX
    SmolVLM --> HFTransformers
    
    LlamaCpp --> MacOS
    LlamaCpp --> Linux
    LlamaCpp --> Windows
    
    MLX --> MacOS
    MLC --> MacOS
    MLC --> Linux
    MLC --> MobileDevice
    
    TransformersJS --> WebBrowser
    HFTransformers --> Linux
    HFTransformers --> MacOS
    HFTransformers --> Windows
    
    LocalInferenceTools --> LlamaCpp
    LocalInferenceTools --> MLX
    LocalInferenceTools --> MLC
    LocalInferenceTools --> TransformersJS
    
    SmolTools --> SmolLM2_135M
    ConversionScripts --> LlamaCpp
    ConversionScripts --> MLX
```

Sources: [tools/README.md:1-3]()

## Local Inference Tools

The repository provides a comprehensive set of tools for running SmolLM models locally without requiring cloud infrastructure. These tools are optimized for different hardware configurations and use cases.

### Inference Framework Integration

```mermaid
graph TB
    subgraph "Model Formats"
        HFCheckpoint["HuggingFace Checkpoint"]
        GGUFFormat["GGUF Format"]
        MLXFormat["MLX Format"]
        MLCFormat["MLC Format"]
        OnnxFormat["ONNX Format"]
    end
    
    subgraph "Conversion Pipeline"
        HFToGGUF["convert_hf_to_gguf.py"]
        HFToMLX["mlx_lm.convert"]
        HFToMLC["mlc_llm.convert_weight"]
        HFToOnnx["optimum.exporters.onnx"]
    end
    
    subgraph "Inference Engines"
        LlamaCppMain["llama-cpp-python"]
        MLXGenerate["mlx_lm.generate"]
        MLCChat["mlc_llm.MLCEngine"]
        TransformersJSPipeline["transformers.js Pipeline"]
        HFPipeline["transformers.pipeline"]
    end
    
    subgraph "Hardware Optimization"
        CPUOptimized["CPU Optimized (AVX2/AVX512)"]
        MetalAccelerated["Metal Accelerated (Apple)"]
        CUDAAccelerated["CUDA Accelerated (NVIDIA)"]
        WebGLAccelerated["WebGL Accelerated"]
    end
    
    HFCheckpoint --> HFToGGUF
    HFCheckpoint --> HFToMLX
    HFCheckpoint --> HFToMLC
    HFCheckpoint --> HFToOnnx
    
    HFToGGUF --> GGUFFormat
    HFToMLX --> MLXFormat
    HFToMLC --> MLCFormat
    HFToOnnx --> OnnxFormat
    
    GGUFFormat --> LlamaCppMain
    MLXFormat --> MLXGenerate
    MLCFormat --> MLCChat
    HFCheckpoint --> HFPipeline
    OnnxFormat --> TransformersJSPipeline
    
    LlamaCppMain --> CPUOptimized
    LlamaCppMain --> CUDAAccelerated
    MLXGenerate --> MetalAccelerated
    MLCChat --> MetalAccelerated
    MLCChat --> CUDAAccelerated
    TransformersJSPipeline --> WebGLAccelerated
```

Sources: [tools/README.md:1-3]()

### Framework-Specific Features

| Framework | Model Support | Hardware | Key Features |
|-----------|---------------|----------|--------------|
| `llama.cpp` | SmolLM2, SmolLM3 | CPU, CUDA, Metal | Quantization (Q4_0, Q8_0), fast CPU inference |
| `MLX` | SmolLM2, SmolLM3, SmolVLM | Apple Silicon | Native Metal acceleration, memory efficiency |
| `MLC` | SmolLM2 | Mobile, GPU | Cross-platform, mobile deployment |
| `Transformers.js` | SmolLM2-135M | Browser | WebGL acceleration, no server required |
| `HuggingFace Transformers` | All models | CPU, CUDA | Full Python ecosystem, research-friendly |

## Model Deployment Strategies

The deployment approach varies based on model size, target hardware, and performance requirements. Smaller models like SmolLM2-135M are optimized for edge deployment, while larger models like SmolLM3-3B require more computational resources.

### Resource Requirements Matrix

```mermaid
graph TB
    subgraph "Model Variants"
        SmolLM2_135M_Node["SmolLM2-135M<br/>~270MB RAM"]
        SmolLM2_360M_Node["SmolLM2-360M<br/>~720MB RAM"] 
        SmolLM2_1_7B_Node["SmolLM2-1.7B<br/>~3.4GB RAM"]
        SmolLM3_3B_Node["SmolLM3-3B<br/>~6GB RAM"]
        SmolVLM_Node["SmolVLM<br/>~4GB RAM"]
    end
    
    subgraph "Deployment Targets"
        EdgeDevice["Edge Devices<br/>(4GB RAM)"]
        Laptop["Laptop<br/>(8GB+ RAM)"]
        Workstation["Workstation<br/>(16GB+ RAM)"]
        WebBrowser_Node["Web Browser<br/>(2GB+ available)"]
    end
    
    subgraph "Optimization Techniques"
        Quantization["Model Quantization<br/>(4-bit, 8-bit)"]
        MemoryMapping["Memory Mapping<br/>(mmap)"]
        StreamingInference["Streaming Inference<br/>(chunked processing)"]
    end
    
    SmolLM2_135M_Node --> EdgeDevice
    SmolLM2_135M_Node --> WebBrowser_Node
    SmolLM2_360M_Node --> EdgeDevice
    SmolLM2_360M_Node --> Laptop
    SmolLM2_1_7B_Node --> Laptop
    SmolLM2_1_7B_Node --> Workstation
    SmolLM3_3B_Node --> Workstation
    SmolVLM_Node --> Laptop
    SmolVLM_Node --> Workstation
    
    Quantization --> SmolLM2_360M_Node
    Quantization --> SmolLM2_1_7B_Node
    Quantization --> SmolLM3_3B_Node
    
    MemoryMapping --> SmolLM2_1_7B_Node
    MemoryMapping --> SmolLM3_3B_Node
    MemoryMapping --> SmolVLM_Node
    
    StreamingInference --> SmolVLM_Node
    StreamingInference --> SmolLM3_3B_Node
```

Sources: [tools/README.md:1-3]()

## Platform-Specific Optimizations

### macOS (Apple Silicon)

The MLX framework provides native Metal acceleration for Apple Silicon Macs, offering optimal performance for SmolLM models on M1/M2/M3 processors.

```bash
# MLX installation and usage
pip install mlx-lm
mlx_lm.generate --model HuggingFaceTB/SmolLM2-1.7B-Instruct
```

### Linux/Windows (x86_64)

For x86_64 systems, `llama.cpp` provides highly optimized CPU inference with optional CUDA acceleration for NVIDIA GPUs.

```bash
# llama.cpp compilation with CUDA support
cmake -B build -DLLAMA_CUDA=ON
cmake --build build --config Release
```

### Web Browser Deployment

`Transformers.js` enables running SmolLM2-135M directly in web browsers without server infrastructure.

```javascript
// Browser-based inference
import { pipeline } from '@xenova/transformers';
const generator = await pipeline('text-generation', 'HuggingFaceTB/SmolLM2-135M');
```

### Mobile Deployment

MLC-LLM provides cross-platform mobile deployment for iOS and Android devices, particularly optimized for SmolLM2 models.

Sources: [tools/README.md:1-3]()

## Utility Scripts and Tools

The repository includes utility scripts for model conversion, benchmarking, and deployment automation. These tools streamline the deployment process across different inference frameworks.

### Model Conversion Pipeline

```mermaid
graph LR
    subgraph "Source Models"
        HFHub["HuggingFace Hub<br/>Original Models"]
        LocalCheckpoint["Local Checkpoint<br/>Custom Fine-tuned"]
    end
    
    subgraph "Conversion Scripts"
        ConvertGGUF["convert_to_gguf.py"]
        ConvertMLX["convert_to_mlx.py"] 
        ConvertMLC["convert_to_mlc.py"]
        ConvertONNX["convert_to_onnx.py"]
    end
    
    subgraph "Optimized Formats"
        GGUFOutput["GGUF<br/>(llama.cpp)"]
        MLXOutput["MLX<br/>(Apple Silicon)"]
        MLCOutput["MLC<br/>(Mobile)"]
        ONNXOutput["ONNX<br/>(Web/ONNX Runtime)"]
    end
    
    HFHub --> ConvertGGUF
    HFHub --> ConvertMLX
    HFHub --> ConvertMLC
    HFHub --> ConvertONNX
    
    LocalCheckpoint --> ConvertGGUF
    LocalCheckpoint --> ConvertMLX
    LocalCheckpoint --> ConvertMLC
    LocalCheckpoint --> ConvertONNX
    
    ConvertGGUF --> GGUFOutput
    ConvertMLX --> MLXOutput
    ConvertMLC --> MLCOutput
    ConvertONNX --> ONNXOutput
```

### Benchmarking and Performance Tools

The deployment tools include performance benchmarking utilities to measure inference speed, memory usage, and accuracy across different frameworks.

| Tool | Purpose | Metrics |
|------|---------|---------|
| `benchmark_inference.py` | Framework comparison | Tokens/second, latency |
| `memory_profiler.py` | Memory usage analysis | RAM usage, peak memory |
| `accuracy_validator.py` | Cross-framework validation | Output consistency |
| `deployment_tester.py` | Platform compatibility | Framework availability |

Sources: [tools/README.md:1-3]()

---

