> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/2-getting-started](https://deepwiki.com/kvcache-ai/ktransformers/2-getting-started)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Getting Started

  Relevant source files 
 - [doc/en/balance-serve.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1)
 - [doc/en/fp8_kernel.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1)
 - [doc/en/install.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1)
 - [doc/en/llama4.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1)
 - [doc/zh/DeepseekR1_V3_tutorial_zh.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1)
 - [install.sh](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/install.sh)
 - [ktransformers.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/ktransformers.py)
 - [pyproject.toml](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/pyproject.toml)
 - [setup.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py)
 
  This document provides an overview of how to begin using KTransformers for either inference or fine-tuning of large language models. It covers the prerequisites, basic concepts, deployment options, and points you to detailed instructions for each use case.

 For detailed installation instructions, see [Installation](https://deepwiki.com/kvcache-ai/ktransformers/2.1-installation). For minimal working examples, see [Quick Start Guide](https://deepwiki.com/kvcache-ai/ktransformers/2.2-quick-start-guide). For containerized deployment, see [Docker Deployment](https://deepwiki.com/kvcache-ai/ktransformers/2.3-docker-deployment).

 
## Prerequisites

 Before starting with KTransformers, ensure your system meets these minimum requirements:

 
| Component | Minimum Requirement | Recommended |
|---|---|---|
| CPU | Intel Xeon (4th Gen+) or AMD EPYC with AVX2 | Intel Sapphire Rapids (AMX support) or dual-socket Xeon |
| RAM | 136GB for DeepSeek-V2 | 382GB+ for DeepSeek-V3/R1 |
| GPU | 11GB VRAM (single GPU) | 24GB VRAM (NVIDIA RTX 4090 or better) |
| OS | Linux (Ubuntu 22.04+) | Linux with NUMA support |
| Python | 3.11 | 3.11 |

 **Optional but recommended:**

 
 - **Multi-GPU setup**: For better performance with larger models [doc/zh/DeepseekR1_V3_tutorial_zh.md29-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L29-L30)
 - **Dual-socket CPU**: For NUMA-aware parallel expert computation [doc/en/install.md108-115](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L108-L115)
 - **Intel AMX support**: For significant acceleration on Sapphire Rapids or newer [doc/zh/DeepseekR1_V3_tutorial_zh.md43-49](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L43-L49)
 
 Sources: [doc/en/install.md41-63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L41-L63) [doc/zh/DeepseekR1_V3_tutorial_zh.md51-58](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L51-L58) [doc/en/balance-serve.md107-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L107-L125)

 
## Architecture Overview

 KTransformers consists of two primary modules that can be used separately or together:

 
```

```

 **Diagram: Module and Entry Point Mapping**

 Sources: [setup.py1-29](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py#L1-L29) [ktransformers.py1-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/ktransformers.py#L1-L35) [doc/en/balance-serve.md20-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L20-L30)

 
## Module Selection Guide

 
### kt-kernel: High-Performance Inference

 Use `kt-kernel` when you need to:

 
 - Run inference on large MoE models like DeepSeek-R1, V3, or LLaMA 4 [doc/en/install.md3-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L3-L16) [doc/en/llama4.md1-5](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L1-L5)
 - Deploy production serving with heterogeneous CPU-GPU computation [doc/en/balance-serve.md13-25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L13-L25)
 - Leverage Intel AMX instructions for optimized MoE kernels [doc/zh/DeepseekR1_V3_tutorial_zh.md109-114](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L109-L114)
 
 **Key Entry Point**: `ktransformers.server.main` or `ktransformers.local_chat` [doc/en/install.md155](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L155-L155) [doc/en/balance-serve.md114-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L125)

 
### kt-sft: Fine-Tuning Framework

 Use `kt-sft` when you need to:

 
 - Fine-tune ultra-large models with limited GPU memory via heterogeneous acceleration [setup.py20-24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py#L20-L24)
 - Integrate with LLaMA-Factory workflows by installing the `sft` extra [setup.py21-24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py#L21-L24)
 - Use optimized `transformers-kt` and `accelerate-kt` components [setup.py22-23](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py#L22-L23)
 
 Sources: [setup.py1-29](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/setup.py#L1-L29) [ktransformers.py27-32](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/ktransformers.py#L27-L32) [doc/en/install.md134-160](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L134-L160)

 
## Inference Deployment Options

 KTransformers provides multiple inference serving modes, optimized for different hardware and concurrency needs:

 
```

```

 **Diagram: Inference Deployment Architecture**

 
### Mode Comparison

 
| Mode | Concurrency | Key Feature | Command Entry Point |
|---|---|---|---|
| local_chat.py | Single | Simple testing tool for GGUF/Safetensor models | python -m ktransformers.local_chat doc/en/install.md155 |
| balance_serve | Multi (v0.2.4+) | Continuous batching, chunked prefill, C++ scheduling | python ktransformers/server/main.py --backend_type balance_serve doc/en/balance-serve.md114-125 |
| SGLang | Multi | Production-grade high-throughput serving | sglang-kt setup.py25-27 |

 Sources: [doc/en/balance-serve.md5-30](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L5-L30) [doc/en/install.md134-165](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L134-L165)

 
## Getting Started Workflow

 
 - **Environment Setup**: Create a Conda environment with Python 3.11 and install `libstdcxx-ng` (GLIBCXX_3.4.32+) [doc/en/install.md48-57](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L48-L57)
 - **Installation**: Clone the repository and run `bash install.sh`. For multi-concurrency support, use `USE_BALANCE_SERVE=1` [doc/en/install.md96-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L96-L125)
 - **Model Preparation**: Obtain model configuration files (HF `config.json`) and quantized weights (GGUF or FP8 Safetensors) [doc/en/install.md146-150](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L146-L150) [doc/en/fp8_kernel.md17-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L17-L35)
 - **Configuration**: Select an optimization rule from `ktransformers/optimize/optimize_rules/` matching your model and hardware [doc/en/balance-serve.md118](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L118-L118)
 - **Execution**: Start the inference server or local chat script [doc/en/balance-serve.md114-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L114-L125)
 
 Sources: [doc/en/install.md91-132](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L91-L132) [doc/en/balance-serve.md62-105](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L62-L105)

 
## Hardware Configuration Considerations

 
### CPU Instruction Sets

 KTransformers leverages different CPU features based on hardware availability:

 
 - **AMX**: Recommended for Intel Sapphire Rapids+ (Xeon 4th Gen) for maximum prefill and decode performance [doc/zh/DeepseekR1_V3_tutorial_zh.md43-49](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L43-L49)
 - **AVX512**: Standard acceleration for modern server CPUs, used in standard Docker images [doc/en/balance-serve.md45-48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L45-L48)
 - **AVX2**: Fallback for older CPUs; pre-compiled wheels are often provided for this variant [doc/en/install.md89](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L89-L89)
 
 
### NUMA and Memory

 For dual-socket systems, set `USE_NUMA=1` during installation to enable memory pinning and prevent performance degradation from cross-socket traffic [doc/en/install.md108-115](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L108-L115) Systems with 1TB+ RAM are recommended for full-parameter MoE models like DeepSeek-V3 [doc/en/install.md108-111](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L108-L111)

 
### FP8 Acceleration

 For GPUs supporting FP8 (e.g., NVIDIA H100, 4090), KTransformers supports hybrid quantization where Attention/Shared-Experts use FP8 while MoE experts use GGML (GGUF) on the CPU [doc/en/fp8_kernel.md1-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L1-L15)

 Sources: [doc/en/install.md108-125](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L108-L125) [doc/zh/DeepseekR1_V3_tutorial_zh.md109-114](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/zh/DeepseekR1_V3_tutorial_zh.md?plain=1#L109-L114) [doc/en/fp8_kernel.md1-10](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/fp8_kernel.md?plain=1#L1-L10)

 
## Next Steps

 
 - **[Installation](https://deepwiki.com/kvcache-ai/ktransformers/2.1-installation)**: Detailed setup for Linux/WSL, system dependencies, and build flags.
 - **[Quick Start Guide](https://deepwiki.com/kvcache-ai/ktransformers/2.2-quick-start-guide)**: Minimal commands to run DeepSeek-R1, V3, and LLaMA 4.
 - **[Docker Deployment](https://deepwiki.com/kvcache-ai/ktransformers/2.3-docker-deployment)**: Deploy using pre-built images with specialized CPU support.
 
 Sources: [doc/en/install.md1-160](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/install.md?plain=1#L1-L160) [doc/en/balance-serve.md44-52](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/balance-serve.md?plain=1#L44-L52) [doc/en/llama4.md1-127](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/llama4.md?plain=1#L1-L127)
