<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-habana · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [README.md](README.md)
- [docs/source/_toctree.yml](docs/source/_toctree.yml)
- [docs/source/index.mdx](docs/source/index.mdx)
- [docs/source/quickstart.mdx](docs/source/quickstart.mdx)
- [optimum/habana/__init__.py](optimum/habana/__init__.py)
- [optimum/habana/transformers/generation/utils.py](optimum/habana/transformers/generation/utils.py)
- [optimum/habana/transformers/modeling_utils.py](optimum/habana/transformers/modeling_utils.py)
- [optimum/habana/transformers/models/__init__.py](optimum/habana/transformers/models/__init__.py)
- [optimum/habana/version.py](optimum/habana/version.py)
- [tests/test_text_generation_example.py](tests/test_text_generation_example.py)

</details>



## Purpose and Scope

Optimum Habana is a comprehensive optimization library that serves as the interface between Hugging Face libraries (Transformers, Diffusers, Accelerate) and Intel Gaudi AI Accelerators (HPUs). The library enables efficient model loading, training, and inference on single and multi-HPU configurations through hardware-specific optimizations, static shape management, and specialized model implementations.

This document covers the high-level architecture and core systems of optimum-habana. For specific training configurations, see [Gaudi Trainer](#2.2). For generation-specific optimizations, see [Generation System](#2.1). For application examples, see [Applications and Examples](#3).

## System Architecture

### High-Level Component Overview

```mermaid
graph TB
    subgraph "User Applications"
        TEXT_GEN["Text Generation<br/>run_generation.py"]
        TRAINING["Training Examples<br/>run_clm.py, run_lora_clm.py"]
        DIFFUSION["Diffusion Pipelines<br/>GaudiStableDiffusionPipeline"]
        INFERENCE["Model Inference<br/>GaudiGenerationMixin"]
    end
    
    subgraph "Optimum Habana Core"
        ADAPT["adapt_transformers_to_gaudi()"]
        GAUDI_CONFIG["GaudiConfig"]
        GAUDI_TRAINER["GaudiTrainer"]
        GAUDI_ARGS["GaudiTrainingArguments"]
    end
    
    subgraph "Model Optimizations"
        MODEL_IMPLS["Gaudi Model Implementations<br/>GaudiLlamaForCausalLM<br/>GaudiFalconForCausalLM<br/>GaudiMistralForCausalLM"]
        GENERATION_MIXIN["GaudiGenerationMixin"]
        ATTENTION_OPT["Optimized Attention Layers<br/>GaudiLlamaAttention<br/>GaudiFalconAttention"]
    end
    
    subgraph "Hardware Integration"
        HPU_GRAPHS["HPU Graph Compilation"]
        LAZY_MODE["Lazy Mode Execution"]
        FUSED_OPS["Fused Operations<br/>FusedSDPA, FusedRMSNorm"]
        STATIC_SHAPES["Static Shape Management"]
    end
    
    subgraph "External Libraries"
        HF_TRANSFORMERS["🤗 Transformers"]
        HF_DIFFUSERS["🤗 Diffusers"] 
        DEEPSPEED["DeepSpeed"]
        ACCELERATE["Accelerate"]
    end
    
    %% Core connections
    ADAPT --> HF_TRANSFORMERS
    TEXT_GEN --> GENERATION_MIXIN
    TRAINING --> GAUDI_TRAINER
    DIFFUSION --> HF_DIFFUSERS
    INFERENCE --> GENERATION_MIXIN
    
    %% Model optimization connections
    GENERATION_MIXIN --> MODEL_IMPLS
    GENERATION_MIXIN --> ATTENTION_OPT
    GAUDI_TRAINER --> MODEL_IMPLS
    
    %% Hardware integration
    MODEL_IMPLS --> HPU_GRAPHS
    MODEL_IMPLS --> LAZY_MODE
    ATTENTION_OPT --> FUSED_OPS
    GENERATION_MIXIN --> STATIC_SHAPES
    
    %% External integrations
    GAUDI_TRAINER --> DEEPSPEED
    GAUDI_TRAINER --> ACCELERATE
```

**Sources:** [README.md:26-32](), [optimum/habana/transformers/modeling_utils.py:304-308](), [optimum/habana/transformers/generation/utils.py:178-184]()

### Core Adaptation System

```mermaid
graph LR
    subgraph "Hugging Face Transformers"
        HF_GEN_MIXIN["GenerationMixin"]
        HF_MODELS["Standard Model Classes"]
        HF_ATTENTION["Standard Attention"]
        HF_TRAINER["Trainer"]
    end
    
    subgraph "Adaptation Layer"
        ADAPT_FUNC["adapt_transformers_to_gaudi()"]
        REPLACE_OPS["Method Replacement<br/>Lines 310-600+"]
    end
    
    subgraph "Gaudi Optimized Components"
        GAUDI_GEN_MIXIN["GaudiGenerationMixin"]
        GAUDI_MODELS["GaudiLlamaForCausalLM<br/>GaudiFalconForCausalLM<br/>GaudiMistralForCausalLM"]
        GAUDI_ATTENTION["GaudiLlamaAttention<br/>GaudiFalconAttention<br/>GaudiMistralAttention"]
        GAUDI_TRAINER_CLASS["GaudiTrainer"]
    end
    
    ADAPT_FUNC --> REPLACE_OPS
    REPLACE_OPS -.->|"replaces"| HF_GEN_MIXIN
    REPLACE_OPS -.->|"replaces"| HF_MODELS
    REPLACE_OPS -.->|"replaces"| HF_ATTENTION
    REPLACE_OPS -.->|"replaces"| HF_TRAINER
    
    REPLACE_OPS --> GAUDI_GEN_MIXIN
    REPLACE_OPS --> GAUDI_MODELS
    REPLACE_OPS --> GAUDI_ATTENTION
    REPLACE_OPS --> GAUDI_TRAINER_CLASS
```

**Sources:** [optimum/habana/transformers/modeling_utils.py:304-700](), [optimum/habana/transformers/models/__init__.py:1-353]()

## Core System Components

### Generation System

The generation system centers around `GaudiGenerationMixin`, which replaces the standard Transformers `GenerationMixin` with HPU-optimized implementations. Key optimizations include:

- **Static Shape Management**: The `incrementor()` function [optimum/habana/transformers/generation/utils.py:144-167]() manages dynamic shape bucketing to maintain static shapes during generation
- **KV Cache Optimization**: Methods like `_pad_past_key_values()` [optimum/habana/transformers/generation/utils.py:511-543]() handle efficient key-value cache management
- **HPU Graph Integration**: `_get_hpu_graphs_kwargs()` [optimum/habana/transformers/generation/utils.py:340-347]() controls graph compilation for performance

### Training System

The training infrastructure builds on `GaudiTrainer` and `GaudiTrainingArguments` classes that extend Transformers' training capabilities:

- **Multi-Device Support**: Integration with `gaudi_spawn.py` for distributed training
- **DeepSpeed Integration**: Native support for DeepSpeed on HPUs
- **Mixed Precision**: FP8 and BF16 support through `GaudiConfig`

### Model Implementations

The library provides HPU-optimized implementations for major model architectures:

| Model Family | Implementation Class | Key Optimizations |
|--------------|---------------------|-------------------|
| Llama | `GaudiLlamaForCausalLM` | Fused RMSNorm, optimized attention |
| Falcon | `GaudiFalconForCausalLM` | Flash attention, linear layer optimization |
| Mistral | `GaudiMistralForCausalLM` | Sliding window attention optimization |
| Gemma | `GaudiGemmaForCausalLM` | RoPE optimization, attention scaling |

**Sources:** [optimum/habana/transformers/models/__init__.py:163-196]()

## Hardware Integration

### HPU-Specific Optimizations

```mermaid
graph TB
    subgraph "Intel Gaudi Hardware Stack"
        GAUDI_HW["Gaudi 1/2/3 HPUs"]
        SYNAPSE["Synapse AI Software"]
        HABANA_FRAMEWORKS["habana_frameworks.torch"]
    end
    
    subgraph "Optimum Habana Features"
        LAZY_EXEC["Lazy Mode Execution<br/>PT_HPU_LAZY_MODE=1"]
        HPU_GRAPHS["HPU Graph Compilation<br/>use_hpu_graphs"]
        FUSED_KERNELS["Fused Kernels<br/>FusedSDPA<br/>FusedRMSNorm<br/>FusedRoPE"]
        STATIC_SHAPES["Static Shape Management<br/>incrementor()<br/>bucket_size"]
    end
    
    subgraph "Performance Features"
        BUCKETING["Dynamic Shape Bucketing<br/>bucket_internal"]
        KV_CACHE["KV Cache Optimization<br/>_pad_past_key_values()"]
        MIXED_PRECISION["Mixed Precision<br/>FP8, BF16"]
        REUSE_CACHE["Cache Reuse<br/>reuse_cache"]
    end
    
    GAUDI_HW --> SYNAPSE
    SYNAPSE --> HABANA_FRAMEWORKS
    HABANA_FRAMEWORKS --> LAZY_EXEC
    HABANA_FRAMEWORKS --> HPU_GRAPHS
    HABANA_FRAMEWORKS --> FUSED_KERNELS
    
    LAZY_EXEC --> BUCKETING
    HPU_GRAPHS --> KV_CACHE
    FUSED_KERNELS --> MIXED_PRECISION
    STATIC_SHAPES --> REUSE_CACHE
```

**Sources:** [README.md:196-211](), [optimum/habana/transformers/generation/utils.py:92-136]()

### Supported Model List

The library maintains a curated list of models optimized for static shapes in `MODELS_OPTIMIZED_WITH_STATIC_SHAPES` [optimum/habana/transformers/generation/utils.py:92-136](), including:

- **Language Models**: `llama`, `falcon`, `mistral`, `mixtral`, `gemma`, `qwen2`
- **Code Models**: `gpt_bigcode`, `starcoder2`, `codegen`
- **Multimodal**: `llava`, `paligemma`, `idefics2`, `mllama`
- **Audio**: `whisper`, `seamless_m4t`

## Application Examples

### Text Generation Workflow

1. **Model Loading**: Use `adapt_transformers_to_gaudi()` to replace standard components
2. **Configuration**: Apply `GaudiConfig` for hardware-specific settings
3. **Generation**: Leverage `GaudiGenerationMixin` methods for optimized inference
4. **Bucketing**: Employ static shape management for consistent performance

### Training Workflow

1. **Script Adaptation**: Replace `Trainer` with `GaudiTrainer`
2. **Arguments Setup**: Use `GaudiTrainingArguments` with HPU-specific flags
3. **Distributed Setup**: Utilize `gaudi_spawn.py` for multi-device training
4. **Optimization**: Apply lazy mode and HPU graphs for acceleration

### Diffusion Workflow

1. **Pipeline Setup**: Use `GaudiStableDiffusionPipeline` instead of standard pipeline
2. **Scheduler**: Apply `GaudiDDIMScheduler` for HPU optimization
3. **Configuration**: Set `use_habana=True` and `use_hpu_graphs=True`
4. **Batching**: Optimize batch sizes for HPU memory characteristics

**Sources:** [README.md:107-193](), [docs/source/quickstart.mdx:91-289](), [tests/test_text_generation_example.py:156-392]()

---

