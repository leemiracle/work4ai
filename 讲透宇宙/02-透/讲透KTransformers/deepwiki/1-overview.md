> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/1-overview](https://deepwiki.com/kvcache-ai/ktransformers/1-overview)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Overview

  Relevant source files 
 - [README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1)
 - [README_ZH.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README_ZH.md?plain=1)
 - [doc/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1)
 - [doc/SUMMARY.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/SUMMARY.md?plain=1)
 - [doc/en/DeepseekR1_V3_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1)
 - [doc/en/FAQ.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/FAQ.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1)
 - [doc/en/SFT/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/README.md?plain=1)
 - [doc/en/kt-kernel/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/README.md?plain=1)
 - [doc/en/kt-kernel/kt-cli.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/kt-cli.md?plain=1)
 
  This document provides a high-level introduction to the KTransformers framework, its architecture, core modules, and capabilities. For detailed installation instructions, see **Installation**. For model-specific deployment guides, see **Model Deployment Guides**.

 
## What is KTransformers

 KTransformers is a research framework for efficient large language model (LLM) inference and fine-tuning through CPU-GPU heterogeneous computing. The project addresses the challenge of running ultra-large mixture-of-experts (MoE) models (e.g., DeepSeek-V3 with 671B parameters) on consumer hardware by strategically offloading computation between GPU and CPU based on arithmetic intensity. [README.md14-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L16) [doc/en/DeepseekR1_V3_tutorial.md39-59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L39-L59)

 The framework has evolved into **two independently usable core modules**:

 
 - **kt-kernel**: High-performance CPU-optimized inference kernels with AMX/AVX acceleration. [README.md55-57](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L55-L57) [doc/README.md57-59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1#L57-L59)
 - **kt-sft**: Fine-tuning framework integrated with LLaMA-Factory for heterogeneous training. [README.md89-91](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L89-L91) [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md5-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L5-L15)
 
 Sources: [README.md14-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L16) [doc/README.md14-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1#L14-L16) [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md1-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L1-L15)

 
## Core Architecture

 
### Dual-Module Design

 
```

```

 **Diagram: KTransformers Module Organization**

 The framework is structured around two independent modules that share the low-level `kt_kernel_ext` extension. The `kt-kernel` module provides CPU-optimized operators for inference, while `kt-sft` leverages these operators for memory-efficient fine-tuning via `ktransformers[sft]`. [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md63-73](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L63-L73) The serving layer offers deployment modes including `local_chat.py`, `balance_serve` for multi-request concurrency, and SGLang for production serving via `sglang-kt`. [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md149-153](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L149-L153)

 Sources: [README.md14-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L16) [README.md55-86](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L55-L86) [README.md89-116](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L89-L116) [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md147-156](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L147-L156)

 
### Heterogeneous Computing Model

 
```

```

 **Diagram: Heterogeneous Inference Pipeline with Code Entities**

 The heterogeneous pipeline operates by routing tokens through the `Expert Router`. High arithmetic-intensity operations (`KDeepseekV2Attention`, shared experts, hot experts) execute on GPU using classes like `KExpertsMarlin`. [doc/en/DeepseekR1_V3_tutorial.md71-72](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L71-L72) Low arithmetic-intensity operations (cold experts in `KExpertsCPU`) offload to CPU with quantized kernels (`AMX_MOE_BASE`, `llamafile`). [README.md65-67](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L65-L67) The `ktransformers.optimize` module injects these optimized operators based on YAML rules. [README.md48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L48-L48)

 Sources: [doc/en/DeepseekR1_V3_tutorial.md39-59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L39-L59) [README.md55-86](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L55-L86)

 
## Core Modules

 
### kt-kernel: CPU-Optimized Inference

 The `kt-kernel` module provides high-performance CPU kernels for MoE inference:

 
| Component | Description | Implementation |
|---|---|---|
| AMX Kernels | Intel AMX INT4/INT8 optimized matrix operations | AMX_MOE_BASE in C++ extension README.md65 |
| AVX512 Kernels | AVX512_BF16, AVX512_VNNI, AVX512_VBMI variants | Multi-variant build system README.md65 |
| Llamafile Backend | GGUF format support with iqk_mul_mat | Submodule integration README.md49 |
| CPUInfer | Thread pool with NUMA-aware allocation | kt-kernel core README.md66 |
| Python API | Wrapper classes for model integration | KTMoEWrapper doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md93 |

 Sources: [README.md55-86](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L55-L86) [doc/README.md57-88](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1#L57-L88)

 
### kt-sft: Fine-Tuning Framework

 The `kt-sft` module enables memory-efficient fine-tuning of ultra-large models:

 
| Feature | Description | Usage |
|---|---|---|
| LLaMA-Factory Integration | Backend for LLaMA-Factory training | ktransformers[sft] entry point doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md73 |
| LoRA Support | Low-rank adapter training with heterogeneous offload | use_kt: true in YAML config doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md145 |
| Resource Efficiency | DeepSeek-V3 671B on limited GPU memory | Layer-wise offloading to CPU README.md99-101 |
| DPO Training | Direct Preference Optimization support | DPO_tutorial.md README.md27 |

 Sources: [README.md89-116](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L89-L116) [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md5-15](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L5-L15)

 
## Supported Models

 KTransformers supports major MoE model families with varying resource requirements:

 
| Model | Parameters | VRAM | DRAM | Quantization | Status |
|---|---|---|---|---|---|
| DeepSeek-R1 | 671B | 14GB | 382GB | Q4_K_M / FP8 | ✅ Stable doc/en/DeepseekR1_V3_tutorial.md39 |
| DeepSeek-V3 | 671B | 14GB | 382GB | Q4_K_M / FP8 | ✅ Stable doc/en/DeepseekR1_V3_tutorial.md39 |
| DeepSeek-V2 | 236B | 11GB | - | - | ✅ Stable README.md47 |
| Kimi-K2-Thinking | - | 14GB | - | RAWINT4 | ✅ Stable README.md28 |
| Kimi-K2.5 | - | - | - | RAWINT4/INT8 | ✅ Day-0 Support README.md24 |
| Qwen3-Next | - | - | - | - | ✅ Stable README.md33 |
| LLaMA 4 | - | - | - | Q4_K_M | ⚠️ Experimental README.md40 |
| MiniMax-M2.5 | - | - | - | - | ✅ Day-0 Support README.md22 |

 Sources: [README.md20-48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L20-L48) [doc/en/DeepseekR1_V3_tutorial.md39-59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L39-L59)

 
## Key Features

 
### CPU Instruction Set Support

 KTransformers includes a build system that supports multiple CPU variants for hardware compatibility:

 
 - **AMX**: Intel Sapphire Rapids (2023+) and newer. [README.md39](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L39-L39)
 - **AVX512**: Variants including BF16, VNNI, and VBMI. [README.md65](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L65-L65)
 - **AVX2**: Support for older or non-AVX512 CPUs. [README.md21](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L21-L21)
 
 
### Multi-Concurrency Serving

 The `balance_serve` backend implements high-performance concurrent scheduling:

 
 - **Continuous Batching**: Support for multiple simultaneous requests. [README.md41](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L41-L41)
 - **3-Layer KV Cache**: GPU-CPU-Disk hierarchy for context reuse. [README.md37](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L37-L37)
 - **SGLang Integration**: Production-ready serving layer. [README.md32](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L32-L32)
 
 
### Weight Quantization Pipeline

 KTransformers supports multiple weight formats through specialized loaders:

 
 - **GGUF**: Support for various GGML quantization levels (Q4_K_M, IQ1_S, etc.). [README.md43-50](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L43-L50)
 - **FP8**: GPU-side kernels for DeepSeek-V3 and R1. [README.md44](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L44-L44)
 - **Native Precision**: BF16 and FP8 per-channel precision. [README.md25](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L25-L25)
 
 Sources: [README.md20-51](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L20-L51) [doc/en/DeepseekR1_V3_tutorial.md97-117](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L97-L117)

 
## Getting Started

 
### Basic Inference Setup

 
```

```

 [README.md72-74](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L72-L74)

 
### Fine-Tuning Setup

 
```

```

 [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md52-55](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L52-L55)

 Sources: [README.md70-74](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L70-L74) [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md17-55](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L17-L55)
