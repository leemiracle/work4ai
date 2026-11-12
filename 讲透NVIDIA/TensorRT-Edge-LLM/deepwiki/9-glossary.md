<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-Edge-LLM · page 9 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [cpp/common/bindingNames.h](cpp/common/bindingNames.h)
- [cpp/common/inputLimits.h](cpp/common/inputLimits.h)
- [cpp/common/pagedKvTypes.h](cpp/common/pagedKvTypes.h)
- [cpp/common/tensor.h](cpp/common/tensor.h)
- [cpp/common/trtUtils.h](cpp/common/trtUtils.h)
- [cpp/common/version.h](cpp/common/version.h)

</details>



This page provides definitions for codebase-specific terminology, domain concepts, and technical jargon used within the TensorRT Edge-LLM project. It serves as a reference for engineers to understand the mapping between high-level LLM concepts and their specific implementations in the C++ and Python source code.

## Core System Concepts

### Engine Building and Inference
The project splits the lifecycle of a model into two distinct phases: **Building** (generating an optimized TensorRT engine) and **Inference** (executing the engine on an edge device).

| Term | Definition | Code Reference |
| :--- | :--- | :--- |
| **LLMBuilder** | The primary C++ class responsible for converting ONNX models into optimized TensorRT engines. | [cpp/builder/llmBuilder.h:148-149]() |
| **LLMBuilderConfig** | A configuration structure containing parameters like `maxBatchSize`, `maxInputLen`, and `maxKVCacheCapacity` used during the build process. | [cpp/builder/llmBuilder.h:37-45]() |
| **Context Phase** | Also known as "Prefill". The phase where the model processes the entire input prompt at once to populate the KV cache. | [cpp/kernels/contextAttentionKernels/contextFMHARunner.h:51-56]() |
| **Generation Phase** | Also known as "Decode". The autoregressive phase where the model generates one token at a time using the KV cache. | [cpp/builder/llmBuilder.h:54-55]() |
| **ONNX-less Builder** | An experimental workflow introduced in 0.10.0 to build engines directly from checkpoints, bypassing ONNX intermediate steps. | [CHANGELOG.md:6-6]() |

**Sources:** [cpp/builder/llmBuilder.h:37-149](), [cpp/kernels/contextAttentionKernels/contextFMHARunner.h:51-56](), [CHANGELOG.md:6-6]()

### Data Management
The runtime uses a custom abstraction for memory management to handle both CPU and GPU allocations efficiently.

*   **Tensor**: A wrapper class for linear layout tensors. It manages memory ownership (owned or reused) and supports reshapes if capacity allows. [cpp/common/tensor.h:221-226]()
*   **Coords**: A utility class to store tensor shapes (up to 8 dimensions). It provides conversion to TensorRT's `nvinfer1::Dims`. [cpp/common/tensor.h:85-118]()
*   **DeviceType**: An enumeration distinguishing between `kCPU` (0) and `kGPU` (1) memory locations. [cpp/common/tensor.h:41-45]()
*   **AuxStreamSet**: An RAII owner for non-blocking auxiliary CUDA streams used by the TensorRT execution context. [cpp/common/trtUtils.h:107-108]()
*   **Binding Names**: Centralized strings for tensor I/O (e.g., `kInputsEmbeds`, `kLogits`) used to ensure consistency between builder and runtime. [cpp/common/bindingNames.h:32-44]()

**Sources:** [cpp/common/tensor.h:41-226](), [cpp/common/trtUtils.h:107-108](), [cpp/common/bindingNames.h:32-44]()

## Specialized Architectures and Decoding

### Speculative Decoding and Non-Autoregressive Strategies
TensorRT Edge-LLM implements advanced decoding strategies to accelerate inference, moving beyond standard autoregressive generation.

*   **Eagle (EagleDecoder)**: A strategy using a smaller draft model to predict multiple candidate tokens, verified by the base model using tree-based attention. [cpp/builder/llmBuilder.h:40-41]()
*   **MTP (Multi-Token Prediction)**: A technique used in models like Gemma 4 and Qwen 3.5 to predict multiple future tokens simultaneously. [CHANGELOG.md:5-5](), [CHANGELOG.md:24-24]()
*   **DFlash**: A speculative decoding strategy utilizing `DDTree` for hybrid models. [CHANGELOG.md:25-25](), [CHANGELOG.md:37-37]()
*   **DSpark**: Speculative decoding using `DDTree` drafting, introduced in 0.10.0. [CHANGELOG.md:10-10]()
*   **BlockDiffusion**: Non-autoregressive decoding for DiffusionGemma models. [CHANGELOG.md:8-8]()

**Sources:** [cpp/builder/llmBuilder.h:40-41](), [CHANGELOG.md:5-37](), [CHANGELOG.md:8-10]()

### Multimodal and Experimental Models
*   **Cosmos3-Edge**: Multimodal reasoning and policy/action-generation support. [CHANGELOG.md:7-7]()
*   **Nemotron-3.5-ASR**: RNN-T based transcription runtime for audio processing. [CHANGELOG.md:9-9]()
*   **Alpamayo 1**: Trajectory prediction model using a flow-matching head for robotics. [CHANGELOG.md:60-60]()

**Sources:** [CHANGELOG.md:7-60]()

## Kernel and Plugin Terminology

### Attention and Cache Mechanisms
*   **FMHA (Fused Multi-Head Attention)**: Optimized kernels for the prefill phase. The legacy cubin backend was replaced in 0.10.0 with **CuTe DSL FMHA-v2**. [CHANGELOG.md:14-14](), [cpp/kernels/contextAttentionKernels/contextFMHARunner.h:51-56]()
*   **XQA**: Optimized attention kernels for the decode phase, supporting paged KV-cache and sliding-window attention. [CHANGELOG.md:26-26](), [CHANGELOG.md:43-43]()
*   **ContextCacheManager**: A system for paged KV-cache reuse across multi-turn requests and media-aware reuse for VLMs. [CHANGELOG.md:11-11]()
*   **kTOKENS_PER_PAGE**: The fixed page size (128 tokens) for paged KV layouts. [cpp/common/pagedKvTypes.h:27-27]()

**Sources:** [CHANGELOG.md:11-43](), [cpp/kernels/contextAttentionKernels/contextFMHARunner.h:51-56](), [cpp/common/pagedKvTypes.h:27-27]()

### Optimization Techniques
*   **CUDA Graph**: Captured sequences of kernels to reduce CPU overhead. [cpp/common/trtUtils.h:99-102]()
*   **CuTe DSL**: A domain-specific language for generating high-performance CUDA kernels (FMHA, XQA, GEMM, MoE). [CHANGELOG.md:14-14](), [CHANGELOG.md:29-29]()
*   **LoRA (Low-Rank Adaptation)**: Support for dynamic insertion and static merging of adapters. [CHANGELOG.md:69-73]()

**Sources:** [cpp/common/trtUtils.h:99-102](), [CHANGELOG.md:14-73]()

## System Space to Code Entity Mapping

### Inference Request Flow
The following diagram maps the conceptual flow of an inference request to specific code entities.

**Diagram: "Inference_Request_Pipeline"**
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        [UserPrompt] --> ["JSON Request"]
    end

    subgraph "Code_Entity_Space"
        ["llm_inference"] --> ["EngineExecutor"]
        ["EngineExecutor"] --> ["LLMBuilder"]
        ["EngineExecutor"] --> ["ContextCacheManager"]
        ["LLMBuilder"] --> ["trt_edgellm::rt::Tensor"]
        ["trt_edgellm::rt::Tensor"] --> ["ContextFMHARunner"]
    end

    ["JSON Request"] -.-> ["llm_inference"]
```
**Sources:** [cpp/builder/llmBuilder.h:148-149](), [cpp/common/tensor.h:221-226](), [cpp/kernels/contextAttentionKernels/contextFMHARunner.h:57-58](), [CHANGELOG.md:11-11]()

### Model Export and Build Flow
This diagram maps the model conversion steps to specific tooling and the new ONNX-less path.

**Diagram: "Model_Export_Workflow"**
```mermaid
graph LR
    subgraph "Natural_Language_Space"
        [HF_Checkpoint] --> [Quantized_Weights]
    end

    subgraph "Code_Entity_Space"
        [llm_loader] --> [tensorrt_edgellm_quantize_llm]
        [tensorrt_edgellm_quantize_llm] --> [tensorrt_edgellm_export_llm]
        [tensorrt_edgellm_export_llm] --> [LLMBuilder]
        [HF_Checkpoint] -- "ONNX-less Path" --> [tensorrt_edgellm_build]
        [tensorrt_edgellm_build] --> [LLMBuilder]
    end

    [Quantized_Weights] -.-> [tensorrt_edgellm_quantize_llm]
```
**Sources:** [CHANGELOG.md:6-6](), [CHANGELOG.md:121-121](), [cpp/builder/llmBuilder.h:148-149]()

## Abbreviations Table

| Abbreviation | Full Term | Description |
| :--- | :--- | :--- |
| **VLM** | Vision-Language Model | Models processing text and images. |
| **ASR** | Automatic Speech Recognition | Speech-to-text processing (e.g., Nemotron-3.5-ASR). [CHANGELOG.md:9-9]() |
| **TTS** | Text-to-Speech | Text-to-audio generation (e.g., Qwen3-TTS). [CHANGELOG.md:13-13]() |
| **NVFP4** | NVIDIA FP4 | 4-bit floating point format for Blackwell. [CHANGELOG.md:38-42]() |
| **MoE** | Mixture of Experts | Model architecture using sparse conditional computation. [CHANGELOG.md:16-17]() |
| **MTP** | Multi-Token Prediction | Predicting multiple tokens in one forward pass. [CHANGELOG.md:5-5]() |
| **GDN** | Gated Delta Net | Linear attention architecture. [CHANGELOG.md:21-21]() |

**Sources:** [CHANGELOG.md:5-42]()