<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-oss · page 2 Models · fetched 2026-10-26 -->

# Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [awesome-gpt-oss.md](awesome-gpt-oss.md)
- [examples/reinforcement-fine-tuning.ipynb](examples/reinforcement-fine-tuning.ipynb)

</details>



This section covers the two open-weight language model variants in the `gpt-oss` repository: `gpt-oss-120b` and `gpt-oss-20b`. It details their technical specifications, architectural characteristics, quantization schemes, and deployment considerations. For information about inference backends and runtime implementations, see [Inference Backends](#4). For deployment guides and platform-specific setup, see [Getting Started](#3).

## Model Variants

The gpt-oss repository provides two model variants optimized for different use cases and hardware constraints:

```mermaid
graph TB
    subgraph "Model Variants"
        GPT120B["gpt-oss-120b<br/>117B total params<br/>5.1B active params<br/>Single 80GB GPU"]
        GPT20B["gpt-oss-20b<br/>21B total params<br/>3.6B active params<br/>16GB memory"]
    end
    
    subgraph "Use Cases"
        Production["Production<br/>High reasoning<br/>General purpose"]
        Local["Local deployment<br/>Lower latency<br/>Specialized tasks"]
    end
    
    subgraph "Hardware Targets"
        H100["NVIDIA H100<br/>AMD MI300X<br/>80GB VRAM"]
        Consumer["Consumer GPUs<br/>Local hardware<br/>16GB+ RAM"]
    end
    
    GPT120B --> Production
    GPT120B --> H100
    GPT20B --> Local
    GPT20B --> Consumer
    
    subgraph "Storage Formats"
        HF["Hugging Face<br/>SafeTensors"]
        Original["original/<br/>Native format"]
        Metal["metal/<br/>Apple Silicon"]
    end
    
    GPT120B --> HF
    GPT120B --> Original
    GPT120B --> Metal
    GPT20B --> HF
    GPT20B --> Original
    GPT20B --> Metal
```

Sources: [README.md:16-19](), [README.md:175-183](), [README.md:246-251]()

## Technical Specifications

| Specification | gpt-oss-120b | gpt-oss-20b |
|---------------|--------------|-------------|
| **Total Parameters** | 117B | 21B |
| **Active Parameters** | 5.1B | 3.6B |
| **Architecture** | Mixture of Experts (MoE) | Mixture of Experts (MoE) |
| **Quantization** | MXFP4 (MoE weights) | MXFP4 (MoE weights) |
| **Base Precision** | BF16 | BF16 |
| **Memory Requirement** | Single 80GB GPU | 16GB |
| **Target Hardware** | H100, MI300X | Consumer GPUs (e.g. T4, RTX) |
| **License** | Apache 2.0 | Apache 2.0 |
| **Response Format** | Harmony (required) | Harmony (required) |

Sources: [README.md:18-19](), [README.md:45](), [README.md:40](), [README.md:21](), [examples/reinforcement-fine-tuning.ipynb:63-65]()

## Architecture and Implementation

The models are implemented across multiple backends with different optimization strategies. The repository provides reference code for PyTorch, Triton, and Metal.

```mermaid
graph TD
    subgraph "Model Implementations"
        TorchImpl["gpt_oss.torch.model<br/>PyTorch reference<br/>4xH100 required"]
        TritonImpl["triton backend<br/>Single GPU optimized<br/>MXFP4 MoE kernel"]
        MetalImpl["gpt_oss.metal<br/>Apple Silicon<br/>Metal Performance Shaders"]
        TransformersImpl["Transformers<br/>HuggingFace integration<br/>Chat template"]
    end
    
    subgraph "Model Files"
        SafeTensors["SafeTensors format<br/>original/ directory"]
        HFFormat["Hugging Face format<br/>Root directory"]
        MetalBin["model.bin<br/>metal/ directory"]
    end
    
    subgraph "Core Components"
        MoELayer["MoE Linear Projections<br/>MXFP4 quantized"]
        Attention["Attention Mechanism<br/>BF16 precision"]
        Embedding["Token Embeddings<br/>BF16 precision"]
    end
    
    TorchImpl --> SafeTensors
    TritonImpl --> SafeTensors
    MetalImpl --> MetalBin
    TransformersImpl --> HFFormat
    
    SafeTensors --> MoELayer
    SafeTensors --> Attention
    SafeTensors --> Embedding
    
    HFFormat --> MoELayer
    HFFormat --> Attention
    HFFormat --> Embedding
```

Sources: [README.md:185-187](), [README.md:204](), [README.md:232](), [README.md:51]()

## Quantization Format

The models use MXFP4 quantization specifically for Mixture of Experts (MoE) weights. This allows the 120B model to fit on a single 80GB GPU. Other weights like attention and embeddings remain in higher precision (BF16).

```mermaid
graph TB
    subgraph "Tensor Storage Format"
        MoETensor["MoE Linear Projection Weight"]
        Blocks["tensor.blocks<br/>FP4 values packed<br/>2 values per uint8"]
        Scales["tensor.scales<br/>Block scale values<br/>Last dimension scaling"]
        OtherTensors["Other Weights<br/>BF16 format<br/>No quantization"]
    end
    
    subgraph "Precision Recommendations"
        SamplingParams["temperature=1.0<br/>top_p=1.0"]
        ActivationPrec["BF16 activations<br/>Recommended"]
    end
    
    MoETensor --> Blocks
    MoETensor --> Scales
    
    subgraph "Implementation Support"
        TritonKernel["triton MoE kernel<br/>MXFP4 support"]
        PyTorchFallback["PyTorch upcast<br/>BF16 computation"]
    end
    
    Blocks --> TritonKernel
    Scales --> TritonKernel
    OtherTensors --> PyTorchFallback
```

Sources: [README.md:45](), [README.md:485-490](), [README.md:494](), [README.md:204]()

## Model Distribution and Access

The models are available through multiple distribution channels with different format requirements. The "original" format is used for the native PyTorch and Triton backends, while the root directory format is compatible with Hugging Face Transformers and vLLM.

```mermaid
graph LR
    subgraph "Distribution Sources"
        HFHub["Hugging Face Hub<br/>openai/gpt-oss-120b<br/>openai/gpt-oss-20b"]
        PyPI["PyPI Package<br/>gpt-oss"]
    end
    
    subgraph "Download Methods"
        HFDownload["hf download<br/>--include original/*<br/>--include metal/*"]
        PipInstall["pip install gpt-oss<br/>--extra torch/triton/metal"]
    end
    
    subgraph "Directory Structure"
        Original["gpt-oss-120b/original/<br/>SafeTensors format<br/>torch/triton backends"]
        Root["gpt-oss-120b/<br/>HF format<br/>transformers/vllm"]
        MetalDir["gpt-oss-120b/metal/<br/>model.bin<br/>metal backend"]
    end
    
    HFHub --> HFDownload
    PyPI --> PipInstall
    
    HFDownload --> Original
    HFDownload --> Root
    HFDownload --> MetalDir
```

Sources: [README.md:175-183](), [README.md:246-251](), [README.md:155-171]()

## Sampling and Configuration

Both models require specific configuration for optimal performance. They are trained with the [Harmony Response Format](#5.1) and will not function correctly without it.

| Parameter | Recommended Value | Purpose |
|-----------|------------------|---------|
| `temperature` | 1.0 | Sampling randomness |
| `top_p` | 1.0 | Nucleus sampling |
| `reasoning_effort` | low/medium/high | Configurable reasoning depth |
| `max_context` | 8192 (default) | Context window size |
| `precision` | BF16 | Activation precision |

The models support configurable reasoning effort levels, allowing users to trade between response quality and latency.

Sources: [README.md:494](), [README.md:41](), [README.md:21](), [README.md:272-294]()

## Child Pages

- [gpt-oss-120b](#2.1) — Detailed specifications for the 117B parameter MoE model.
- [gpt-oss-20b](#2.2) — Detailed specifications for the 21B parameter model optimized for latency.

---

