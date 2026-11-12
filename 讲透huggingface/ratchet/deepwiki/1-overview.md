<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/ratchet · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/rust.yml](.github/workflows/rust.yml)
- [crates/ratchet-core/Cargo.toml](crates/ratchet-core/Cargo.toml)
- [crates/ratchet-core/src/lib.rs](crates/ratchet-core/src/lib.rs)
- [crates/ratchet-core/tests/attn_tests.rs](crates/ratchet-core/tests/attn_tests.rs)
- [crates/ratchet-models/Cargo.toml](crates/ratchet-models/Cargo.toml)
- [crates/ratchet-models/src/whisper/mod.rs](crates/ratchet-models/src/whisper/mod.rs)
- [crates/ratchet-models/src/whisper/options.rs](crates/ratchet-models/src/whisper/options.rs)
- [crates/ratchet-models/src/whisper/tokenizer.rs](crates/ratchet-models/src/whisper/tokenizer.rs)
- [justfile](justfile)
- [pnpm-workspace.yaml](pnpm-workspace.yaml)

</details>



## Purpose and Scope

Ratchet is a high-performance tensor computation framework written in Rust, designed for efficient machine learning model inference with a focus on web deployment through WebAssembly. The framework provides:

1. A core tensor system supporting both CPU and GPU execution (via WebGPU)
2. Neural network primitives for building machine learning models
3. Implementations of popular models like Whisper (speech recognition) and Phi (language model)
4. Tools for loading models from standardized formats (GGUF)
5. Deployment options including web browsers (WebAssembly) and command-line interfaces

For detailed information about specific systems, see:
- [Core Tensor System](#2) for tensor operations and device abstractions
- [Model Implementations](#3) for specific model architectures and usage
- [Model Loading](#4) for loading models from file formats
- [Deployment](#5) for running models in different environments

## System Architecture

The diagram below illustrates the layered architecture of Ratchet:

```mermaid
flowchart TD
    subgraph "Core Tensor System [ratchet-core]"
        Tensor["Tensor"] --- LazyOp["LazyOp"]
        Tensor --- Device["Device"]
        Tensor --- Storage["Storage"]
        Tensor --- Shape["Shape"]
        Tensor --- DType["DType"]
        Device --- CPUDevice["CPU Device"]
        Device --- GPUDevice["GPU Device"]
        Storage --- CPUBuffer["CPU Buffer"]
        Storage --- GPUBuffer["GPU Buffer"]
        Operations["Operations"] --- BinaryOps["Binary Ops"]
        Operations --- UnaryOps["Unary Ops"]
        Operations --- MatmulOp["Matrix Multiplication"]
        Operations --- SoftmaxOp["Softmax"]
    end
    
    subgraph "Neural Network Components [ratchet-nn]"
        NNModule["NN Module"] --- Embedding["Embedding"]
        NNModule --- Linear["Linear Layer"]
        NNModule --- Attention["Attention Mechanism"]
        NNModule --- LayerNorm["Layer Normalization"]
        NNModule --- Activation["Activation Functions"]
    end
    
    subgraph "Model Implementations [ratchet-models]"
        Models["Models"] --- Whisper["Whisper"]
        Models --- Phi["Phi"]
        Models --- Moondream["Moondream"]
        Whisper --- WhisperEncoder["Encoder"]
        Whisper --- WhisperDecoder["Decoder"]
        Whisper --- WhisperConfig["Config"]
        Whisper --- Tokenizer["Tokenizer"]
        Whisper --- DecodingOptions["Options"]
    end
    
    subgraph "Loading & Deployment"
        RatchetLoader["ratchet-loader"] --- GGUF["GGUF Format"]
        RatchetWeb["ratchet-web"] --- WasmBindings["WebAssembly Bindings"]
        RatchetHub["ratchet-hub"] --- HFRepo["HuggingFace Integration"]
        RatchetCLI["ratchet-cli"] --- CLI["Command Line Interface"]
    end
    
    CoreTensorSystem["Core Tensor System"] --> NeuralNetworkComponents["Neural Network Components"]
    NeuralNetworkComponents --> ModelImplementations["Model Implementations"]
    ModelImplementations --> LoadingDeployment["Loading & Deployment"]
```

Sources: [crates/ratchet-core/Cargo.toml](), [crates/ratchet-models/Cargo.toml](), [crates/ratchet-core/src/lib.rs]()

## Core Tensor System

The core tensor system provides the foundation for all computations in Ratchet:

```mermaid
classDiagram
    class Tensor {
        +LazyOp op
        +StorageView view
        +Device device
        +Shape shape
        +DType dtype
        +resolve()
        +add(), sub(), mul(), div()
        +matmul(), softmax(), etc.
    }
    
    class LazyOp {
        <<enum>>
        +Const
        +Binary
        +Unary
        +Matmul
        +Reindex
        +Softmax
    }
    
    class Shape {
        +RVec~usize~ dims
        +size()
        +rank()
    }
    
    class DType {
        <<enum>>
        +F32
        +F16
        +I32
        +U32
        +I8
        +U8
        +Q4_0
        +Q8_0
    }
    
    class Device {
        <<enum>>
        +CPU
        +GPU(WgpuDevice)
        +request_device()
    }
    
    class Storage {
        <<enum>>
        +CPU(CPUBuffer)
        +GPU(GPUBuffer)
    }
    
    Tensor o-- LazyOp
    Tensor o-- Shape
    Tensor o-- DType
    Tensor o-- Device
    Tensor o-- Storage
    Storage <|-- CPUBuffer
    Storage <|-- GPUBuffer
```

Key features of the tensor system:

1. **Lazy Evaluation**: Operations on tensors create a computation graph via `LazyOp` that is executed only when `resolve()` is called.
2. **Shape and Data Types**: Support for multiple shapes and data types, including F32, F16, I32, and quantized types.
3. **Device Abstraction**: Computations can be performed on CPU or GPU through the `Device` abstraction.
4. **Memory Management**: Efficient buffer allocation and reuse strategies for both CPU and GPU memory.

Example tensor operations:
```rust
// Create a tensor with specific shape
let input = Tensor::randn::<f32>(shape![1, 128, 256], Device::CPU);

// Matrix multiplication
let output = input.matmul(weights, false, false)?;

// Apply softmax
let output = output.softmax(2)?;

// Resolve to execute computation
let result = output.resolve()?;
```

Sources: [crates/ratchet-core/src/lib.rs](), [crates/ratchet-core/tests/attn_tests.rs:50-66]()

## Model Implementations

### Whisper Speech Recognition Model

The Whisper model is structured as follows:

```mermaid
graph TD
    subgraph "Whisper Model"
        WhisperModel["Whisper"] --> WhisperEncoder["Encoder"]
        WhisperModel --> WhisperDecoder["Decoder"]
        WhisperModel --> Config["Config"]
        WhisperModel --> Spectrogram["Spectrogram"]
        WhisperModel --> Tokenizer["Tokenizer"]
    end
    
    subgraph "Tokenizer"
        TokenizerCore["WhisperTokenizer"] --> Languages["LANGUAGES (100 supported)"]
        TokenizerCore --> SpecialTokens["Special Tokens (SOT, EOT)"]
        TokenizerCore --> InnerTokenizer["tokenizers::Tokenizer"]
    end
    
    subgraph "Decoding Options"
        DecodingOptionsBuilder["DecodingOptionsBuilder"] --> TaskOptions["Task (Transcribe/Translate)"]
        DecodingOptionsBuilder --> LanguageOption["Language Selection"]
        DecodingOptionsBuilder --> SamplingOptions["Sampling Parameters"]
    end
    
    subgraph "Transcription Process"
        AudioInput["Audio Input"] --> SpectrogramGen["Generate Spectrogram"]
        SpectrogramGen --> EncoderProcess["Encoder Processing"]
        EncoderProcess --> AudioFeatures["Audio Features"]
        AudioFeatures --> DecoderProcess["Decoder Processing"]
        DecoderProcess --> TokenOutput["Token Output"]
        TokenOutput --> TextOutput["Text Transcription"]
    end
    
    WhisperModel --> Transcription["Transcription Process"]
    Tokenizer --> TokenOutput
    DecodingOptionsBuilder --> DecodingOptions["DecodingOptions"]
    DecodingOptions --> DecoderProcess
```

The Whisper implementation includes:

- **Model Structure**: Encoder-decoder architecture for audio transcription
- **Tokenizer**: Handles 100 languages with special tokens for tasks and control
- **Decoding Options**: Configurable parameters for inference (language, temperature, etc.)
- **Spectrogram Generation**: Converts raw audio to mel spectrograms
- **Transcription Process**: End-to-end pipeline from audio to text

Configuring Whisper transcription:
```rust
let options = DecodingOptionsBuilder::new()
    .task(Task::Transcribe)
    .language("en")
    .temperature(0.0)
    .build();
```

Sources: [crates/ratchet-models/src/whisper/mod.rs](), [crates/ratchet-models/src/whisper/options.rs](), [crates/ratchet-models/src/whisper/tokenizer.rs]()

### Phi Language Model

```mermaid
graph TD
    subgraph "Phi Model"
        PhiModel["Phi Model"] --> DecoderLayers["Decoder Layers"]
        DecoderLayers --> SelfAttention["Self-Attention"]
        DecoderLayers --> MLP["MLP"]
        SelfAttention --> KVCache["KV Cache"]
    end
    
    subgraph "Text Generation Process"
        TextInput["Text Input"] --> Tokens["Token IDs"]
        Tokens --> AttentionProc["Self-Attention Processing"]
        AttentionProc --> NextToken["Next Token Prediction"]
        NextToken --> GeneratedText["Generated Text"]
    end
    
    SelfAttention --> AttentionProc
```

Sources: [crates/ratchet-models/Cargo.toml]()

## Execution Flow

The execution flow in Ratchet involves several stages:

```mermaid
flowchart TD
    subgraph "Model Loading"
        GGUFFile["GGUF File"] --> HeaderParsing["Parse Header"]
        HeaderParsing --> TensorInfo["Extract Tensor Info"]
        TensorInfo --> WeightLoad["Load Model Weights"]
        WeightLoad --> ModelConstruct["Construct Model"]
    end
    
    subgraph "Tensor Execution"
        InputTensor["Input Tensor"] --> BuildGraph["Build Lazy Op Graph"]
        BuildGraph --> TensorResolve["Tensor.resolve()"]
        TensorResolve --> OpCompile["Compile Operations"]
        OpCompile --> DeviceDispatch["Dispatch to Device"]
        DeviceDispatch --> ExecuteOps["Execute Operations"]
        ExecuteOps --> ResultTensor["Result Tensor"]
    end
    
    subgraph "Whisper Inference"
        AudioData["Audio Data"] --> CreateSpectrogram["Create Spectrogram"]
        CreateSpectrogram --> EncoderForward["Encoder Forward Pass"]
        EncoderForward --> AudioContext["Audio Context"]
        AudioContext --> DecoderForward["Decoder Forward Pass"]
        DecoderForward --> TextTokens["Text Tokens"]
        TextTokens --> Transcription["Transcription Result"]
    end
    
    ModelConstruct --> WhisperModel["Whisper Model"]
    WhisperModel --> AudioData
    TensorResolve --> EncoderForward
    TensorResolve --> DecoderForward
```

The key aspect of Ratchet's execution flow is lazy evaluation. Operations on tensors build a computation graph that is only executed when `resolve()` is called. This allows for optimization of the computation sequence and efficient memory allocation.

Sources: [crates/ratchet-core/tests/attn_tests.rs]()

## Deployment Options

### Web Deployment via WebAssembly

```mermaid
graph TD
    subgraph "Browser Environment"
        WebApp["Web Application"] --> JavaScriptAPI["JavaScript API"]
        JavaScriptAPI --> WasmModule["WebAssembly Module"]
        WasmModule --> RatchetCore["Ratchet Core"]
        RatchetCore --> WebGPU["WebGPU API"]
    end
    
    subgraph "Model Loading"
        ModelFile["Model File"] --> FetchAPI["Fetch API"]
        FetchAPI --> ModelBytes["Model Bytes"]
        ModelBytes --> ModelConstruction["Construct Model"]
    end
    
    JavaScriptAPI --> ModelConstruction
    ModelConstruction --> RatchetCore
```

### Command Line Interface

```mermaid
graph TD
    subgraph "CLI Environment"
        CommandLine["Command Line Arguments"] --> RatchetCLI["ratchet-cli"]
        RatchetCLI --> ModelLoading["Load Model from File"]
        ModelLoading --> RunInference["Run Inference"]
        RunInference --> OutputResults["Output Results"]
    end
```

Sources: [.github/workflows/rust.yml](), [justfile]()

## Project Structure

The codebase is organized into several crates, each with a specific responsibility:

| Crate | Description | Key Components |
|-------|-------------|----------------|
| ratchet-core | Core tensor system | Tensor, LazyOp, Device, Storage, Shape, DType |
| ratchet-nn | Neural network components | Embedding, Linear, Attention, LayerNorm |
| ratchet-models | Model implementations | Whisper, Phi, Moondream |
| ratchet-loader | Model loading utilities | GGUF format parsing, tensor loading |
| ratchet-web | WebAssembly bindings | JavaScript API, WASM exports |
| ratchet-hub | HuggingFace integration | Model repository access |
| ratchet-cli | Command-line interface | Argument parsing, model execution |

This organization allows for a clean separation of concerns, with each crate building upon the functionality provided by lower-level crates.

Sources: [crates/ratchet-core/Cargo.toml](), [crates/ratchet-models/Cargo.toml](), [pnpm-workspace.yaml]()

## Environment Configuration

Ratchet supports various runtime environments and configurations, controlled through environment variables and build features:

```
RUST_LOG: "info"
WGPU_DX12_COMPILER: dxc
RUSTFLAGS: --cfg=web_sys_unstable_apis
RUST_BACKTRACE: 1
RATCHET_FORCE_F32: 1
```

These settings enable debugging, configure GPU backends, and set tensor precision.

Sources: [.github/workflows/rust.yml:9-22]()

## Development and Testing

The project includes a comprehensive test suite, including tests for core tensor operations and model-specific functionality:

```bash
# Run tests
cargo nextest run -j 1 --no-fail-fast --features=ci,pyo3

# Build WebAssembly module
just wasm ratchet-web

# Publish WebAssembly package
just wasm-publish-pr ratchet-web
```

Sources: [.github/workflows/rust.yml:51-73](), [justfile:7-16]()

---

