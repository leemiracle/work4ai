> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/5-kt-sft:-fine-tuning-framework](https://deepwiki.com/kvcache-ai/ktransformers/5-kt-sft:-fine-tuning-framework)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# kt-sft: Fine-Tuning Framework

  Relevant source files 
 - [README_ZH.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README_ZH.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1)
 - [doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md?plain=1)
 - [doc/en/SFT/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/README.md?plain=1)
 - [doc/en/SFT/injection_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1)
 - [doc/en/kt-kernel/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/README.md?plain=1)
 - [doc/en/kt-kernel/kt-cli.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/kt-cli.md?plain=1)
 - [doc/en/kt-kernel/kt-kernel_intro.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/kt-kernel/kt-kernel_intro.md?plain=1)
 
  
## Purpose and Scope

 The `kt-sft` module is KTransformers' fine-tuning framework that enables efficient LoRA-based training of ultra-large MoE models on consumer hardware. It acts as a pluggable backend for LLaMA-Factory, implementing heterogeneous CPU-GPU training strategies to fine-tune models like DeepSeek-V3 (671B parameters) using only 2-4 RTX 4090 GPUs [doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md18-24](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md?plain=1#L18-L24)

 This page provides an architectural overview of the fine-tuning system. For specific implementation details, see:

 
 - **Architecture details and design patterns**: [Architecture Overview](https://deepwiki.com/kvcache-ai/ktransformers/5.1-architecture-overview)
 - **LLaMA-Factory integration mechanics**: [LLaMA-Factory Integration](https://deepwiki.com/kvcache-ai/ktransformers/5.2-llama-factory-integration)
 - **YAML configuration and optimization rules**: [Training Configuration](https://deepwiki.com/kvcache-ai/ktransformers/5.3-training-configuration)
 - **LoRA Adapter Management**: [LoRA Adapter Management](https://deepwiki.com/kvcache-ai/ktransformers/5.4-lora-adapter-management)
 - **DPO Training workflow**: [DPO Training](https://deepwiki.com/kvcache-ai/ktransformers/5.5-dpo-training)
 
 For inference-related features, see [kt-kernel: Inference Engine](https://deepwiki.com/kvcache-ai/ktransformers/4-kt-kernel:-inference-engine). For operator injection mechanisms shared between training and inference, see [Optimization Rules (YAML)](https://deepwiki.com/kvcache-ai/ktransformers/10.1-optimization-rules-(yaml)).

 
---

 
## System Architecture

 The `kt-sft` framework is designed as a backend module that integrates with LLaMA-Factory's training orchestration. LLaMA-Factory handles high-level concerns (data processing, training loops, configuration management), while `kt-sft` provides the low-level operator implementations that enable heterogeneous execution [doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md24-26](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md?plain=1#L24-L26)

 **Diagram 1: kt-sft Integration with LLaMA-Factory**

 
```

```

 **Sources:** [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md45-50](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L45-L50) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md66-77](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L66-L77)

 
---

 
## Core Components

 
### KTrainer: Custom Training Orchestrator

 The `KTrainer` class extends `transformers.Trainer` to implement explicit layer placement instead of standard DataParallel. When `USE_KT=1` is set, it [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md81-88](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L81-L88):

 
 - **Prevents automatic model-to-device transfer**: Blocks the default `.to(device)` call that would copy the entire model to a single GPU.
 - **Applies YAML-based placement rules**: Uses the `kt_optimize_rule` file to assign each layer to a specific device (`cuda:0`, `cuda:1`, or `cpu`).
 - **Manages construction**: Layers are constructed directly on the target device to avoid extra copies [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md87-88](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L87-L88)
 
 
### LoRA Integration for Attention Layers

 **Diagram 2: KTransformersLinearLora Class Hierarchy**

 
```

```

 **Sources:** [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md51-62](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L51-L62) [doc/en/SFT/injection_tutorial.md61-68](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L61-L68)

 The `KTransformersLinearLora` class achieves dual inheritance to combine KTransformers optimizations (prefill/generate kernels) with LoRA trainability (low-rank matrices A and B) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md53-56](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L53-L56)

 
### MoE Operator Encapsulation

 MoE layers are wrapped as a differentiable black-box node (`KSFTExpertsCPU`) in PyTorch's computation graph using a custom Autograd Function [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md68-71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L68-L71)

 
 - **Upstream**: The MoE layer behaves like a standard `nn.Module` with gradients.
 - **Downstream**: Calls C++ extensions for forward/backward passes.
 - **Backward Optimizations**: Pre-computes weight transposes ($W^\top$) and caches intermediate activations (e.g., expert projections) to reduce recomputation during the backward pass [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md76-79](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L76-L79)
 
 
---

 
## Training Workflow

 **Diagram 3: End-to-End Training Data Flow**

 
```

```

 **Sources:** [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md81-88](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L81-L88) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md76-79](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L76-L79) [README_ZH.md107-111](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README_ZH.md?plain=1#L107-L111)

 
---

 
## Performance Characteristics

 
| Model | Backend | Throughput | GPU Memory |
|---|---|---|---|
| DeepSeek-V2-Lite 14B | HuggingFace | 303.58 token/s | 32.12 GB |
| DeepSeek-V2-Lite 14B | Unsloth | 455.37 token/s | 9.64 GB |
| DeepSeek-V2-Lite 14B | KTransformers | 530.38 token/s | 6.08 GB |
| DeepSeek-V3 671B | KTransformers | 40.35 token/s | 70 GB (Total) |

 **Sources:** [doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md30-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_User-Guide.md?plain=1#L30-L35) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md30-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L30-L35)

 
---

 
## Configuration Summary

 Training is controlled through YAML configuration. Key parameters include:

 
| Parameter | Purpose | Example Value |
|---|---|---|
| use_kt | Enable KTransformers backend | true |
| kt_optimize_rule | Path to placement strategy YAML | qwen3_5moe_lora_sft_kt.yaml |
| backend | CPU computation backend | AMXBF16, llamafile |
| finetuning_type | Training method | lora |

 **Sources:** [doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md112-115](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Quick-Start.md?plain=1#L112-L115) [doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/KTransformers-Fine-Tuning_Developer-Technical-Notes.md?plain=1#L71-L71) [doc/en/SFT/injection_tutorial.md20-31](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/SFT/injection_tutorial.md?plain=1#L20-L31)

 For details on installation and environment setup, see [Installation](https://deepwiki.com/kvcache-ai/ktransformers/2.1-installation).
