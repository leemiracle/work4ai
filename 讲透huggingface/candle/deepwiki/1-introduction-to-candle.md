<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/candle · page 1 Introduction to Candle · fetched 2026-10-26 -->

# Introduction to Candle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [candle-core/Cargo.toml](candle-core/Cargo.toml)
- [candle-datasets/Cargo.toml](candle-datasets/Cargo.toml)
- [candle-examples/Cargo.toml](candle-examples/Cargo.toml)
- [candle-examples/examples/rwkv/README.md](candle-examples/examples/rwkv/README.md)
- [candle-examples/examples/rwkv/main.rs](candle-examples/examples/rwkv/main.rs)
- [candle-flash-attn-v3/Cargo.toml](candle-flash-attn-v3/Cargo.toml)
- [candle-flash-attn/Cargo.toml](candle-flash-attn/Cargo.toml)
- [candle-kernels/Cargo.toml](candle-kernels/Cargo.toml)
- [candle-metal-kernels/Cargo.toml](candle-metal-kernels/Cargo.toml)
- [candle-nn/Cargo.toml](candle-nn/Cargo.toml)
- [candle-onnx/Cargo.toml](candle-onnx/Cargo.toml)
- [candle-pyo3/Cargo.toml](candle-pyo3/Cargo.toml)
- [candle-transformers/Cargo.toml](candle-transformers/Cargo.toml)
- [candle-transformers/src/models/mod.rs](candle-transformers/src/models/mod.rs)
- [candle-transformers/src/models/quantized_rwkv_v6.rs](candle-transformers/src/models/quantized_rwkv_v6.rs)
- [candle-transformers/src/models/rwkv_v6.rs](candle-transformers/src/models/rwkv_v6.rs)
- [candle-transformers/src/models/rwkv_v7.rs](candle-transformers/src/models/rwkv_v7.rs)
- [candle-wasm-examples/llama2-c/Cargo.toml](candle-wasm-examples/llama2-c/Cargo.toml)
- [candle-wasm-examples/quant-qwen3/Cargo.toml](candle-wasm-examples/quant-qwen3/Cargo.toml)
- [candle-wasm-examples/whisper/Cargo.toml](candle-wasm-examples/whisper/Cargo.toml)
- [candle-wasm-examples/yolo/Cargo.toml](candle-wasm-examples/yolo/Cargo.toml)

</details>



## Purpose and Scope

This document provides an introduction to Candle, a minimalist machine learning framework for Rust. It covers the project's design philosophy, workspace organization, core architectural concepts, and entry points for users. For detailed information about specific subsystems, see:

*   **Project Structure and Crates**: Detailed breakdown of the workspace and crate dependencies. [Project Structure and Crates](#1.1)
*   **Build System and Feature Flags**: Hardware backend configuration and kernel compilation. [Build System and Feature Flags](#1.2)
*   **Core Tensor System**: Tensor abstraction, operations, and autograd. [Core Tensor System](#2)
*   **Device Abstraction and Backends**: CPU, CUDA, and Metal implementations. [Device Abstraction and Backends](#3)
*   **Neural Network Building Blocks**: Layers, optimizers, and variable management. [Neural Network Building Blocks](#5)
*   **Model Implementations**: Large Language Models (LLMs), Whisper, and Vision models. [Model Implementations and Examples](#6)

**Sources:** [README.md:1-40](), [Cargo.toml:24-31]()

## Design Philosophy and Goals

Candle is designed as a minimalist ML framework with three primary goals:

1.  **Serverless Inference**: Enable lightweight binary deployments by avoiding the large runtime overhead of frameworks like PyTorch. Full ML frameworks can be hundreds of megabytes, making serverless cold starts slow.
2.  **Python-Free Production**: Remove Python from production workloads to eliminate Global Interpreter Lock (GIL) contention and interpreter overhead, enabling better performance and simpler deployment pipelines.
3.  **Performance with Simplicity**: Provide GPU acceleration (CUDA, Metal) and optimized CPU execution (MKL, Accelerate) while maintaining a simple, PyTorch-like API that Rust developers can understand.

The framework achieves these goals through a modular crate structure, compile-time feature flags for optional dependencies, and a clear separation between core tensor operations and higher-level abstractions.

**Sources:** [README.md:8-15](), [Cargo.toml:26-27]()

## Workspace Organization

Candle is organized as a Cargo workspace with multiple specialized crates. The following diagram shows the workspace structure and inter-crate dependencies:

**Candle Workspace Structure**

```mermaid
graph TB
    subgraph "CoreFoundation" ["Core Foundation"]
        ["candle-core"]
    end
    
    subgraph "HardwareBackends" ["Hardware Backends"]
        ["candle-kernels<br/>(CUDA PTX)"]
        ["candle-metal-kernels<br/>(Metal MSL)"]
        ["candle-flash-attn<br/>(v1/v2)"]
        ["candle-flash-attn-v3<br/>(v3)"]
    end
    
    subgraph "HighLevelAbstractions" ["High-Level Abstractions"]
        ["candle-nn<br/>(layers, optimizers)"]
        ["candle-transformers<br/>(50+ models)"]
        ["candle-datasets<br/>(data loaders)"]
        ["candle-ug<br/>(Unified Kernel Gen)"]
    end
    
    subgraph "ExternalInterfaces" ["External Interfaces"]
        ["candle-pyo3<br/>(Python)"]
        ["candle-onnx<br/>(ONNX)"]
        ["candle-wasm-examples/*<br/>(browser)"]
    end
    
    subgraph "Applications" ["Applications"]
        ["candle-examples<br/>(CLI)"]
        ["tensor-tools<br/>(CLI)"]
    end
    
    ["candle-nn"] --> ["candle-core"]
    ["candle-transformers"] --> ["candle-core"]
    ["candle-transformers"] --> ["candle-nn"]
    ["candle-datasets"] --> ["candle-core"]
    
    ["candle-pyo3"] --> ["candle-core"]
    ["candle-pyo3"] --> ["candle-nn"]
    ["candle-onnx"] --> ["candle-core"]
    ["candle-onnx"] --> ["candle-nn"]
    
    ["candle-examples"] --> ["candle-core"]
    ["candle-examples"] --> ["candle-nn"]
    ["candle-examples"] --> ["candle-transformers"]
    
    ["candle-wasm-examples/*"] --> ["candle-core"]
    ["candle-wasm-examples/*"] --> ["candle-transformers"]
    
    ["candle-core"] -.optional.-> ["candle-kernels"]
    ["candle-core"] -.optional.-> ["candle-metal-kernels"]
    ["candle-transformers"] -.optional.-> ["candle-flash-attn"]
    ["candle-transformers"] -.optional.-> ["candle-flash-attn-v3"]
```

The workspace members fall into distinct categories:

| Crate | Purpose | Key Dependencies |
| :--- | :--- | :--- |
| `candle-core` | Tensor operations, autograd, device abstraction | `rayon`, `safetensors`, `gemm`, `half` |
| `candle-nn` | Neural network layers (Linear, Conv2d, RmsNorm, etc.) | `candle-core`, `safetensors` |
| `candle-transformers` | Pre-implemented models (Llama, Whisper, YOLO, etc.) | `candle-core`, `candle-nn` |
| `candle-kernels` | Custom CUDA kernels (PTX) | `cudaforge` |
| `candle-metal-kernels` | Metal compute shaders | `objc2-metal` |
| `candle-flash-attn` | Flash Attention v1/v2 integration | `candle-core`, `cudaforge` |
| `candle-flash-attn-v3` | Flash Attention v3 (Hopper) integration | `candle-core`, `cudaforge` |
| `candle-pyo3` | Python API via PyO3 | `candle-core`, `pyo3` |
| `candle-onnx` | ONNX model execution | `candle-core`, `prost` |
| `candle-ug` | Unified kernel generation for CPU/CUDA/Metal | `ug`, `ug-cuda`, `ug-metal` |

For a deep dive into the crate relationships and project layout, see **[Project Structure and Crates](#1.1)**.

**Sources:** [Cargo.toml:1-21](), [candle-flash-attn/Cargo.toml:14-18](), [candle-onnx/Cargo.toml:13-18](), [Cargo.toml:47-101]()

## Core Architecture Layers

Candle's architecture consists of five distinct layers, bridging high-level model code to low-level hardware kernels:

**Candle Five-Layer Architecture**

```mermaid
graph TB
    subgraph ApplicationLayer ["Application Layer"]
        ["candle-examples/*<br/>main.rs"]
        ["candle-pyo3<br/>lib.rs"]
        ["candle-wasm-examples/*<br/>lib.rs"]
    end
    
    subgraph ModelLayer ["Model & Algorithm Layer"]
        ["candle_transformers::models<br/>llama.rs, whisper.rs, etc."]
        ["candle_nn<br/>linear.rs, conv.rs, norm.rs"]
        ["candle_datasets<br/>mnist.rs"]
    end
    
    subgraph CoreLayer ["Core Computation Layer"]
        ["candle_core::Tensor"]
        ["candle_core::Device"]
        ["candle_nn::VarBuilder"]
        ["candle_core::quantized::QTensor"]
    end
    
    subgraph BackendLayer ["Hardware Acceleration Layer"]
        ["candle_core::backend::BackendDevice::Cpu"]
        ["candle_core::backend::BackendDevice::Cuda"]
        ["candle_core::backend::BackendDevice::Metal"]
    end
    
    subgraph KernelLayer ["Kernel Layer"]
        ["CPU: Rayon / MKL / Accelerate"]
        ["CUDA: candle-kernels / cuBLAS / cuDNN"]
        ["Metal: candle-metal-kernels"]
        ["Flash: candle-flash-attn-v3"]
    end
    
    ApplicationLayer --> ModelLayer
    ModelLayer --> CoreLayer
    CoreLayer --> BackendLayer
    BackendLayer --> KernelLayer
```

### Layer Responsibilities

*   **Core Computation Layer**: Defines the `Tensor` struct (shape, `DType`, storage) and the `Device` enum which routes operations [README.md:24-35]().
*   **Hardware Acceleration Layer**: Implements the `BackendDevice` and `BackendStorage` traits for specific hardware (CPU, CUDA, Metal).
*   **Model & Algorithm Layer**: Provides `candle_nn` for reusable layers and `candle_transformers` for state-of-the-art model architectures like `Llama`, `Phi3`, and `Whisper` [candle-transformers/src/models/mod.rs:1-15]().
*   **Kernel Layer**: Contains the actual compute code, ranging from Rust parallel iterators to hand-written CUDA PTX and Metal MSL [candle-kernels/Cargo.toml:6-7]().

**Sources:** [candle-transformers/src/models/mod.rs:1-15](), [README.md:24-35](), [candle-kernels/Cargo.toml:6-7]()

## Quick Start Example

The following demonstrates the minimal API for tensor operations and device selection:

```rust
use candle_core::{Device, Tensor};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Device selection: CPU or GPU
    let device = Device::Cpu;
    // let device = Device::new_cuda(0)?;  // For CUDA GPU
    
    // Tensor creation
    let a = Tensor::randn(0f32, 1., (2, 3), &device)?;
    let b = Tensor::randn(0f32, 1., (3, 4), &device)?;
    
    // Matrix multiplication
    let c = a.matmul(&b)?;
    println!("{c}");  // Prints: Tensor[[2, 4], f32]
    Ok(())
}
```

**Sources:** [README.md:21-46]()

## Build System and Feature Flags

Candle uses Cargo feature flags to control backend inclusion and optimization levels. This allows developers to build specialized binaries for specific hardware.

| Feature | Crate | Effect |
| :--- | :--- | :--- |
| `cuda` | `candle-core` | Enables CUDA backend and `cudarc` integration [candle-core/Cargo.toml:51](). |
| `metal` | `candle-core` | Enables Metal backend for macOS/iOS [candle-core/Cargo.toml:56-61](). |
| `mkl` | `candle-core` | Links Intel MKL for optimized CPU linear algebra [candle-core/Cargo.toml:54](). |
| `accelerate` | `candle-core` | Links Apple's Accelerate framework [candle-core/Cargo.toml:55](). |
| `flash-attn` | `candle-transformers` | Enables Flash Attention v2 kernels [candle-transformers/Cargo.toml:33](). |

For a comprehensive guide on configuring the build environment and managing GPU kernels, see **[Build System and Feature Flags](#1.2)**.

**Sources:** [candle-core/Cargo.toml:51-61](), [candle-transformers/Cargo.toml:33](), [Cargo.toml:35-79]()

## Model Ecosystem

Candle provides production-ready implementations of a wide range of models in `candle-transformers`:

*   **LLMs**: `Llama` (v1-v3), `Mistral`, `Mixtral`, `Phi-3`, `Qwen` (v2, v3, MoE), `Gemma` (v1-v4), `RWKV` (v5-v7) [candle-transformers/src/models/mod.rs:17-138]().
*   **Audio**: `Whisper` (speech-to-text), `MetaVoice` (TTS), `EnCodec`, `Mimi`, `SNAC`, `Parler-TTS` [candle-transformers/src/models/mod.rs:9-10]().
*   **Vision**: `YOLO` (v3/v8), `DINOv2`, `Segment Anything` (SAM), `DepthAnythingV2` [candle-transformers/src/models/mod.rs:34-35]().
*   **Multimodal**: `Stable Diffusion` (v1.5, v2.1, XL, SD3/Flux), `BLIP`, `Moondream`, `PaliGemma`, `Pixtral`, `Qwen3-VL` [candle-transformers/src/models/mod.rs:125-136]().

**Sources:** [candle-transformers/src/models/mod.rs:1-138](), [candle-transformers/src/models/rwkv_v5.rs:1-14](), [candle-transformers/src/models/rwkv_v7.rs:1-20]()

---

