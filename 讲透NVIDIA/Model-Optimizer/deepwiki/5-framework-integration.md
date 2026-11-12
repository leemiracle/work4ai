<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Model-Optimizer · page 5 Framework Integration · fetched 2026-10-26 -->

# Framework Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py](modelopt/torch/opt/plugins/mcore_dist_checkpointing.py)
- [modelopt/torch/quantization/_auto_quantize_cost.py](modelopt/torch/quantization/_auto_quantize_cost.py)
- [modelopt/torch/quantization/algorithms.py](modelopt/torch/quantization/algorithms.py)
- [modelopt/torch/quantization/conversion.py](modelopt/torch/quantization/conversion.py)
- [modelopt/torch/quantization/model_quant.py](modelopt/torch/quantization/model_quant.py)
- [modelopt/torch/quantization/nn/__init__.py](modelopt/torch/quantization/nn/__init__.py)
- [modelopt/torch/quantization/nn/modules/quant_linear.py](modelopt/torch/quantization/nn/modules/quant_linear.py)
- [modelopt/torch/quantization/nn/modules/quant_module.py](modelopt/torch/quantization/nn/modules/quant_module.py)
- [modelopt/torch/quantization/plugins/custom.py](modelopt/torch/quantization/plugins/custom.py)
- [modelopt/torch/quantization/plugins/transformer_engine.py](modelopt/torch/quantization/plugins/transformer_engine.py)
- [modelopt/torch/utils/plugins/megatron_calibration.py](modelopt/torch/utils/plugins/megatron_calibration.py)
- [tests/gpu_megatron/torch/quantization/plugins/test_transformer_engine.py](tests/gpu_megatron/torch/quantization/plugins/test_transformer_engine.py)
- [tests/unit/torch/quantization/plugins/test_huggingface.py](tests/unit/torch/quantization/plugins/test_huggingface.py)
- [tests/unit/torch/quantization/test_autoquant.py](tests/unit/torch/quantization/test_autoquant.py)
- [tests/unit/torch/quantization/test_calib.py](tests/unit/torch/quantization/test_calib.py)
- [tests/unit/torch/quantization/test_tensor_quant_cpu.py](tests/unit/torch/quantization/test_tensor_quant_cpu.py)

</details>



This page provides a high-level overview of NVIDIA Model Optimizer's framework-specific integrations and plugin system. ModelOpt bridges multiple deep learning frameworks, training paradigms, and inference engines through dedicated adapter modules and registration registries. For detailed technical guides and deep dives into specific frameworks, see the child pages: [Hugging Face Models](#5.1), [Megatron-Core and NeMo](#5.2), [PyTorch FSDP and Distributed Support](#5.3), and [vLLM and SGLang Integration](#5.4).

Sources: [modelopt/torch/quantization/nn/modules/quant_module.py:36-48](), [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:16-17]()

## Overview

ModelOpt provides a unified optimization interface across multiple deep learning frameworks and training paradigms. The framework integration layer handles:

- **Model architecture adaptation**: Replacing framework-specific model layers (such as `nn.Linear` or `te.pytorch.Linear`) with ModelOpt optimization modules via `QuantModuleRegistry` [modelopt/torch/quantization/nn/modules/quant_module.py:36-37]().
- **Distributed training compatibility**: Supporting tensor parallelism (TP), pipeline parallelism (PP), data parallelism (DP/FSDP), and expert parallelism (EP) via `ParallelState` [modelopt/torch/quantization/nn/modules/quant_module.py:48]().
- **Checkpoint format management**: Saving and loading optimized models in distributed checkpointing formats using specialized sharded state dict hooks [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:67-85]().
- **Export path coordination**: Generating deployment-ready checkpoints for TensorRT-LLM, vLLM, and SGLang.

Sources: [modelopt/torch/quantization/nn/modules/quant_module.py:36-48](), [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:67-85]()

## Supported Frameworks and Features

ModelOpt supports a wide range of frameworks through dedicated plugins and registries.

| Framework / Ecosystem | Key Features | Plugin / Code Entity |
|-----------------------|--------------|----------------------|
| **Hugging Face** | Transformers (LLMs), Diffusers (VLMs), PEFT/LoRA integration | `modelopt.torch.quantization.plugins.huggingface` |
| **Megatron-Core** | Distributed Quantization, Minitron Pruning, MoE support | `modelopt.torch.quantization.plugins.megatron` |
| **Transformer Engine** | FP8 training conflict resolution, Grouped Linear support | `modelopt.torch.quantization.plugins.transformer_engine` [modelopt/torch/quantization/plugins/transformer_engine.py:16-17]() |
| **PyTorch FSDP** | FSDP2 weight access, distributed checkpointing | `modelopt.torch.opt.plugins.mcore_dist_checkpointing` [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:16-17]() |
| **Inference Engines** | Native vLLM and SGLang quantization support | `modelopt.torch.quantization.plugins.vllm` |

Sources: [modelopt/torch/quantization/plugins/transformer_engine.py:16-17](), [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:16-17]()

## Integration Architecture

The following diagram bridges natural language framework concepts to concrete code entities in ModelOpt, illustrating how framework-specific models are ingested, optimized, and exported.

### System Flow: From Framework to Deployment Architecture
```mermaid
graph TB
    subgraph ["Input Frameworks (Natural Language Space)"]
        HF["Hugging Face Transformers/Diffusers"]
        MCORE["NVIDIA Megatron-Core Layers"]
        TE["Transformer Engine te.pytorch.Linear"]
        FSDP["PyTorch FSDP2 / Distributed"]
    end
    
    subgraph ["Code Entity Space (modelopt/torch)"]
        REG["QuantModuleRegistry<br/>modelopt.torch.quantization.nn"]
        QUAL["_QuantTELinear / _QuantLinear<br/>modelopt.torch.quantization.plugins"]
        MGR["ModeloptStateManager<br/>modelopt.torch.opt.conversion"]
        DIS_CP["save_sharded_modelopt_state<br/>modelopt.torch.opt.plugins.mcore_dist_checkpointing"]
    end
    
    subgraph ["Export & Deployment"]
        EXP["convert_to_quantized_model<br/>modelopt.torch.quantization.conversion"]
        VLLM_ENG["vLLM / SGLang Quantization Engine"]
        TRT["TensorRT-LLM Checkpoint Exporter"]
    end
    
    HF --> REG
    MCORE --> REG
    TE --> QUAL
    FSDP --> DIS_CP
    
    REG --> EXP
    QUAL --> EXP
    EXP --> MGR
    MGR --> DIS_CP
    
    DIS_CP --> VLLM_ENG
    DIS_CP --> TRT
```

Sources: [modelopt/torch/quantization/nn/modules/quant_module.py:36-37](), [modelopt/torch/quantization/plugins/transformer_engine.py:61-63](), [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:112-117]()

## Hugging Face Models

ModelOpt provides deep integration with the Hugging Face ecosystem, supporting `transformers`, `diffusers`, and `peft`. Transformers and diffusers models are automatically instrumented using `QuantModuleRegistry` entries designed for HF architectures, enabling seamless Post-Training Quantization (PTQ) and Quantization-Aware Training (QAT).

For details, see [Hugging Face Models](#5.1).

Sources: [tests/unit/torch/quantization/plugins/test_huggingface.py:37-42]()

## Megatron-Core and NeMo

Integration with Megatron-Core (MCore) and NeMo 2.0 enables distributed optimization of large language models across multi-GPU clusters. This includes specialized support for Transformer Engine layers (`_QuantTELinear`) [modelopt/torch/quantization/plugins/transformer_engine.py:61-63]() and grouped linear modules for Mixture of Experts (MoE) (`_QuantTEGroupedLinear`) [modelopt/torch/quantization/plugins/transformer_engine.py:116-118]().

For details, see [Megatron-Core and NeMo](#5.2).

Sources: [modelopt/torch/quantization/plugins/transformer_engine.py:61-63](), [modelopt/torch/quantization/plugins/transformer_engine.py:116-118]()

## PyTorch FSDP and Distributed Support

ModelOpt handles the complexities of optimizing models wrapped in Fully Sharded Data Parallel (FSDP) and distributed parallelism. Distributed checkpointing plugins like `save_sharded_modelopt_state` and `restore_modelopt_state` ensure that optimization metadata and quantizer states (`modelopt_state`) are correctly sharded and aligned with pipeline and expert parallelism [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:67-110]().

### Distributed Checkpointing Flow
```mermaid
graph LR
    subgraph ["Distributed Context (Code Entities)"]
        MOD["torch.nn.Module (Optimized)"]
        MTO_STATE["ModeloptStateManager<br/>modelopt.torch.opt.conversion"]
        DIST_CP["dist_checkpointing<br/>megatron.core.dist_checkpointing"]
    end

    subgraph ["Checkpoint Operations"]
        SAVE_STATE["save_sharded_modelopt_state<br/>mcore_dist_checkpointing.py"]
        RESTORE_STATE["restore_modelopt_state<br/>mcore_dist_checkpointing.py"]
        LOAD_EXTRA["_load_extra_state_from_sharded_checkpoint<br/>mcore_dist_checkpointing.py"]
    end

    MOD --> MTO_STATE
    MTO_STATE --> SAVE_STATE
    SAVE_STATE --> DIST_CP
    DIST_CP --> RESTORE_STATE
    RESTORE_STATE --> LOAD_EXTRA
    LOAD_EXTRA --> MOD
```

For details, see [PyTorch FSDP and Distributed Support](#5.3).

Sources: [modelopt/torch/opt/plugins/mcore_dist_checkpointing.py:67-174]()

## vLLM and SGLang Integration

ModelOpt acts as a native quantization provider for high-throughput inference engines like vLLM and SGLang. Models optimized and converted via `convert_to_quantized_model` [modelopt/torch/quantization/conversion.py:63-74]() can export fake-quantized weights, scaling factors, and block-wise quantization descriptors that are recognized directly by inference engine runtimes.

For details, see [vLLM and SGLang Integration](#5.4).

Sources: [modelopt/torch/quantization/conversion.py:63-74]()

---

