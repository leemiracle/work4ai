> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/9-model-deployment-guides](https://deepwiki.com/kvcache-ai/ktransformers/9-model-deployment-guides)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Model Deployment Guides

  Relevant source files 
 - [README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1)
 - [doc/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1)
 - [doc/SUMMARY.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/SUMMARY.md?plain=1)
 - [doc/en/DeepseekR1_V3_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1)
 - [doc/en/FAQ.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/FAQ.md?plain=1)
 - [doc/en/Kimi-K2.5.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1)
 - [doc/en/MiniMax-M2.5.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/MiniMax-M2.5.md?plain=1)
 - [doc/en/Qwen3.5.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Qwen3.5.md?plain=1)
 - [doc/en/SFT_Installation_Guide_KimiK2.5.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT_Installation_Guide_KimiK2.5.md?plain=1)
 - [doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md?plain=1)
 
  This document provides a high-level overview of deploying large language models with KTransformers. It covers the general deployment workflow, configuration patterns, and key concepts that apply across all supported models. For model-specific deployment instructions, see the child pages for [DeepSeek R1, V3, and V3.2](https://deepwiki.com/kvcache-ai/ktransformers/9.1-deepseek-r1-v3-and-v3.2), [Kimi-K2 and Kimi-K2-Thinking](https://deepwiki.com/kvcache-ai/ktransformers/9.2-kimi-k2-and-kimi-k2-thinking), [Kimi-K2.5](https://deepwiki.com/kvcache-ai/ktransformers/9.3-kimi-k2.5), [FP8 Hybrid Quantization Models](https://deepwiki.com/kvcache-ai/ktransformers/9.4-fp8-hybrid-quantization-models), [Qwen Models (Qwen3MoE, Qwen3-Next, Qwen3.5, Qwen3-Coder-Next)](https://deepwiki.com/kvcache-ai/ktransformers/9.5-qwen-models-(qwen3moe-qwen3-next-qwen3.5-qwen3-coder-next)), [GLM Models (GLM-4-MoE, GLM-5, GLM-5.1)](https://deepwiki.com/kvcache-ai/ktransformers/9.6-glm-models-(glm-4-moe-glm-5-glm-5.1)), [MiniMax Models (M2, M2.1, M2.5)](https://deepwiki.com/kvcache-ai/ktransformers/9.7-minimax-models-(m2-m2.1-m2.5)), and [LLaMA 4 (Experimental)](https://deepwiki.com/kvcache-ai/ktransformers/9.8-llama-4-(experimental)).

 
## Deployment Workflow Overview

 Deploying a model with KTransformers involves three main stages: weight acquisition, configuration (including optional quantization), and server initialization. The framework supports heterogeneous deployment where different model components run on different hardware (GPU/CPU) based on arithmetic intensity [README.md14-16](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L16)

 
### Deployment Pipeline Diagram

 
```

```

 **Sources:** [README.md14-51](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L14-L51) [doc/en/DeepseekR1_V3_tutorial.md20-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L20-L35) [doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md63-83](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md?plain=1#L63-L83)

 
## Supported Models and Hardware Requirements

 KTransformers supports multiple model families with varying hardware requirements. The table below summarizes minimum configurations for inference:

 
| Model Family | Parameters | Min GPU VRAM | Min CPU RAM | Quantization | Example Backend |
|---|---|---|---|---|---|
| DeepSeek-V3/R1 | 671B | 14GB | 382GB | Q4_K_M / FP8 | local_chat.py |
| Kimi-K2.5 | Large | 48GB (2x4090) | 600GB | RAWINT4 | SGLang + sglang-kt |
| GLM-5 | Large | Varies | 200GB+ | BF16 / FP8 | SGLang + kt-kernel |
| MiniMax-M2.5 | Large | 48GB (2x4090) | 200GB | FP8 | SGLang + kt-kernel |
| Qwen3.5 | 400B | 96GB (4x4090) | 800GB | BF16 | SGLang + sglang-kt |

 **Sources:** [README.md81-108](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L81-L108) [doc/en/DeepseekR1_V3_tutorial.md73-117](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L73-L117) [doc/en/Kimi-K2.5.md13-20](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1#L13-L20) [doc/en/MiniMax-M2.5.md13-19](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/MiniMax-M2.5.md?plain=1#L13-L19) [doc/en/Qwen3.5.md18-24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Qwen3.5.md?plain=1#L18-L24)

 
## Core Deployment Components

 
### 1. YAML Configuration System

 YAML optimization rules control module injection and device placement. Each rule consists of `match` patterns and `replace` specifications. The framework uses `InjectRules.apply` to iterate through the model and replace standard layers with optimized KTransformers operators.

 **Common Operators:**

 
 - `KDeepseekV2Attention`: Optimized MLA attention for GPU.
 - `KTransformersExperts`: Expert offloading to CPU using optimized AMX/AVX kernels [README.md64-68](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L64-L68)
 - `KTransformersLinear`: Quantized linear kernels like Marlin or llamafile backends [README.md49-51](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L49-L51)
 
 
### 2. Weight Conversion and Quantization

 For models like DeepSeek V3.2 or Kimi-K2.5, weights often need conversion or quantization for optimal CPU inference.

 
 - `convert_cpu_weights.py`: Used to convert FP8/BF16 weights to INT4/INT8 for CPU offloading [doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md74-82](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/deepseek-v3.2-sglang-tutorial.md?plain=1#L74-L82)
 - `convert_lora.py`: Used to convert LoRA adapters for SGLang serving [doc/en/SFT_Installation_Guide_KimiK2.5.md179-184](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT_Installation_Guide_KimiK2.5.md?plain=1#L179-L184)
 
 
### 3. SGLang Integration

 The preferred production serving path is via the `sglang-kt` integration, which uses specific `--kt-*` flags to manage the heterogeneous backend [doc/en/Kimi-K2.5.md76-96](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1#L76-L96)

 
## Deployment Integration Diagram

 This diagram bridges the high-level deployment concepts to the specific code entities used in the KTransformers framework.

 
```

```

 **Sources:** [README.md57-87](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L57-L87) [doc/en/Kimi-K2.5.md76-96](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1#L76-L96) [doc/en/SFT_Installation_Guide_KimiK2.5.md147-152](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT_Installation_Guide_KimiK2.5.md?plain=1#L147-L152)

 
## Model-Specific Guide Links

 For detailed step-by-step guides, refer to the following sub-pages:

 
 - **[DeepSeek R1, V3, and V3.2](https://deepwiki.com/kvcache-ai/ktransformers/9.1-deepseek-r1-v3-and-v3.2)**: Deploying the 671B MoE models with various quantization levels and AMX-accelerated kernels [doc/en/DeepseekR1_V3_tutorial.md52-61](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L61) For details, see [DeepSeek R1, V3, and V3.2](https://deepwiki.com/kvcache-ai/ktransformers/9.1-deepseek-r1-v3-and-v3.2).
 - **[Kimi-K2 and Kimi-K2-Thinking](https://deepwiki.com/kvcache-ai/ktransformers/9.2-kimi-k2-and-kimi-k2-thinking)**: Deployment of Kimi-K2 using RAWINT4 weights and SGLang [README.md28-36](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L28-L36) For details, see [Kimi-K2 and Kimi-K2-Thinking](https://deepwiki.com/kvcache-ai/ktransformers/9.2-kimi-k2-and-kimi-k2-thinking).
 - **[Kimi-K2.5](https://deepwiki.com/kvcache-ai/ktransformers/9.3-kimi-k2.5)**: Deployment of Kimi-K2.5 with LoRA serving support and RAWINT4 weights [doc/en/Kimi-K2.5.md1-11](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1#L1-L11) For details, see [Kimi-K2.5](https://deepwiki.com/kvcache-ai/ktransformers/9.3-kimi-k2.5).
 - **[FP8 Hybrid Quantization Models](https://deepwiki.com/kvcache-ai/ktransformers/9.4-fp8-hybrid-quantization-models)**: Advanced usage of FP8 kernels for DeepSeek models [README.md43-44](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L43-L44) For details, see [FP8 Hybrid Quantization Models](https://deepwiki.com/kvcache-ai/ktransformers/9.4-fp8-hybrid-quantization-models).
 - **[Qwen Models (Qwen3MoE, Qwen3-Next, Qwen3.5, Qwen3-Coder-Next)](https://deepwiki.com/kvcache-ai/ktransformers/9.5-qwen-models-(qwen3moe-qwen3-next-qwen3.5-qwen3-coder-next))**: Optimizing Qwen3.5-MoE-400B and Qwen3MoE families [doc/en/Qwen3.5.md1-11](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Qwen3.5.md?plain=1#L1-L11) For details, see [Qwen Models (Qwen3MoE, Qwen3-Next, Qwen3.5, Qwen3-Coder-Next)](https://deepwiki.com/kvcache-ai/ktransformers/9.5-qwen-models-(qwen3moe-qwen3-next-qwen3.5-qwen3-coder-next)).
 - **[GLM Models (GLM-4-MoE, GLM-5, GLM-5.1)](https://deepwiki.com/kvcache-ai/ktransformers/9.6-glm-models-(glm-4-moe-glm-5-glm-5.1))**: Deploying GLM-5 and GLM-4-MoE with native precision [README.md23-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L23-L35) For details, see [GLM Models (GLM-4-MoE, GLM-5, GLM-5.1)](https://deepwiki.com/kvcache-ai/ktransformers/9.6-glm-models-(glm-4-moe-glm-5-glm-5.1)).
 - **[MiniMax Models (M2, M2.1, M2.5)](https://deepwiki.com/kvcache-ai/ktransformers/9.7-minimax-models-(m2-m2.1-m2.5))**: Deployment of MiniMax-M2.1 and M2.5 with native FP8 support [README.md22-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L22-L26) For details, see [MiniMax Models (M2, M2.1, M2.5)](https://deepwiki.com/kvcache-ai/ktransformers/9.7-minimax-models-(m2-m2.1-m2.5)).
 - **[LLaMA 4 (Experimental)](https://deepwiki.com/kvcache-ai/ktransformers/9.8-llama-4-(experimental))**: Early support for Meta LLaMA 4 models [README.md40](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L40-L40) For details, see [LLaMA 4 (Experimental)](https://deepwiki.com/kvcache-ai/ktransformers/9.8-llama-4-(experimental)).
 
 **Sources:** [README.md19-48](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L19-L48) [doc/en/DeepseekR1_V3_tutorial.md1-63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L1-L63) [doc/en/Kimi-K2.5.md1-11](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Kimi-K2.5.md?plain=1#L1-L11) [doc/en/MiniMax-M2.5.md1-11](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/MiniMax-M2.5.md?plain=1#L1-L11) [doc/en/Qwen3.5.md1-11](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/Qwen3.5.md?plain=1#L1-L11)
