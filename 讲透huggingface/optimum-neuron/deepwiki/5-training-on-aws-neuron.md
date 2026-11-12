<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-neuron · page 5 Training on AWS Neuron · fetched 2026-10-26 -->

# Training on AWS Neuron

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/training_tutorials/finetune_llama.mdx](docs/source/training_tutorials/finetune_llama.mdx)
- [docs/source/training_tutorials/finetune_qwen3.mdx](docs/source/training_tutorials/finetune_qwen3.mdx)
- [examples/training/llama/finetune_llama.py](examples/training/llama/finetune_llama.py)
- [examples/training/qwen3/finetune_qwen3.py](examples/training/qwen3/finetune_qwen3.py)
- [optimum/neuron/accelerate/accelerator.py](optimum/neuron/accelerate/accelerator.py)
- [optimum/neuron/accelerate/state.py](optimum/neuron/accelerate/state.py)
- [optimum/neuron/accelerate/utils/dataclasses.py](optimum/neuron/accelerate/utils/dataclasses.py)
- [optimum/neuron/trainers/sft_config.py](optimum/neuron/trainers/sft_config.py)
- [optimum/neuron/trainers/sft_trainer.py](optimum/neuron/trainers/sft_trainer.py)
- [optimum/neuron/trainers/training_args.py](optimum/neuron/trainers/training_args.py)
- [optimum/neuron/trainers/transformers.py](optimum/neuron/trainers/transformers.py)
- [optimum/neuron/trainers/trl_utils.py](optimum/neuron/trainers/trl_utils.py)
- [pyproject.toml](pyproject.toml)
- [tests/training/test_neuron_sft_trainer.py](tests/training/test_neuron_sft_trainer.py)

</details>



## Purpose and Scope

This page provides an overview of the training system in `optimum-neuron`, which enables distributed training of large language models and other deep learning models on AWS Trainium accelerators. The training system extends HuggingFace Accelerate with Neuron-specific optimizations and distributed training strategies.

This page introduces the core training components and their architecture. For detailed information on specific topics, see:
- Training API details: [NeuronTrainer and NeuronAccelerator](#5.1)
- Distributed parallelism strategies: [Distributed Training Strategies](#5.2)
- Precision and optimization settings: [Mixed Precision Training](#5.3)
- Neuron-optimized model implementations: [Custom Model Architectures](#5.4)

For inference on Neuron accelerators, see [Inference with Neuron Models](#6).

---

## Overview

The `optimum-neuron` training system is built on three foundational layers:

1. **HuggingFace Accelerate** - Provides the base distributed training abstraction
2. **NeuronAccelerator** - Extends Accelerate with XLA and Neuron-specific functionality
3. **neuronx_distributed** - Provides low-level distributed primitives for model and data parallelism

The training system supports both standard transformers models and custom Neuron-optimized models with tensor parallelism, pipeline parallelism, sequence parallelism, and ZeRO-1 optimizer sharding.

**Sources:** [optimum/neuron/accelerate/accelerator.py:79-597](), [optimum/neuron/accelerate/state.py:85-177]()

---

## Core Training Components

### Component Hierarchy

```mermaid
graph TB
    HFA["accelerate.Accelerator<br/>HuggingFace Accelerate base class"]
    NA["NeuronAccelerator<br/>optimum.neuron.accelerate.accelerator.NeuronAccelerator<br/>XLA and Neuron extensions"]
    NT["NeuronTrainer<br/>optimum.neuron.NeuronTrainer<br/>Training loop implementation"]
    NSFT["NeuronSFTTrainer<br/>optimum.neuron.NeuronSFTTrainer<br/>Supervised fine-tuning"]
    
    NAS["NeuronAcceleratorState<br/>optimum.neuron.accelerate.state.NeuronAcceleratorState<br/>Environment and device state"]
    NPS["NeuronPartialState<br/>optimum.neuron.accelerate.state.NeuronPartialState<br/>Base distributed state"]
    
    TNC["TrainingNeuronConfig<br/>optimum.neuron.models.neuron_config.TrainingNeuronConfig<br/>Parallelism configuration"]
    MPC["MixedPrecisionConfig<br/>optimum.neuron.accelerate.utils.dataclasses.MixedPrecisionConfig<br/>Precision settings"]
    
    HFA --> NA
    NA --> NT
    NT --> NSFT
    
    NA --> NAS
    NAS --> NPS
    
    NA --> TNC
    NA --> MPC
    
    style NA fill:#e1f5ff
    style NT fill:#e1f5ff
    style NAS fill:#fff3cd
```

### NeuronAccelerator

`NeuronAccelerator` is the central class that manages training on Neuron hardware. It extends `accelerate.Accelerator` and provides:

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **XLA Integration** | Manages XLA device and graph execution | [optimum/neuron/accelerate/accelerator.py:79-157]() |
| **Distributed Setup** | Initializes process groups and parallel state | [optimum/neuron/accelerate/state.py:43-83]() |
| **Model Preparation** | Patches models for Neuron, applies mixed precision | [optimum/neuron/accelerate/accelerator.py:338-398]() |
| **Optimizer Wrapping** | Supports ZeRO-1 optimizer sharding | [optimum/neuron/accelerate/accelerator.py:253-306]() |
| **Data Parallel Loading** | Configures distributed data loaders | [optimum/neuron/accelerate/accelerator.py:208-251]() |
| **Checkpointing** | Handles model and optimizer state persistence | [optimum/neuron/accelerate/accelerator.py:436-548]() |

**Key initialization parameters:**

- `trn_config: TrainingNeuronConfig` - Configures tensor/pipeline parallelism
- `zero_1: bool` - Enables ZeRO-1 optimizer state sharding
- `mixed_precision_config: MixedPrecisionConfig` - Controls precision modes
- `gradient_accumulation_steps: int` - Number of microbatches before optimizer step

**Sources:** [optimum/neuron/accelerate/accelerator.py:79-170]()

### NeuronAcceleratorState

`NeuronAcceleratorState` manages the global training environment state, including:

- Distributed backend initialization (XLA/torch.distributed)
- Device assignment and process topology
- Parallel state initialization via `neuronx_distributed.parallel_layers.parallel_state`
- Training configuration (`TrainingNeuronConfig`) storage

The state is a singleton that persists across the training session.

**Sources:** [optimum/neuron/accelerate/state.py:85-177]()

---

## Training System Architecture

### Full System View

```mermaid
graph TB
    subgraph "User API"
        ARGS["NeuronTrainingArguments<br/>Command-line & config parameters"]
        TRAINER["NeuronTrainer<br/>Training loop orchestration"]
    end
    
    subgraph "Acceleration Layer"
        ACCEL["NeuronAccelerator<br/>optimum.neuron.accelerate.accelerator.NeuronAccelerator"]
        STATE["NeuronAcceleratorState<br/>Process groups & device state"]
    end
    
    subgraph "Distributed Backend"
        XLA["torch_xla<br/>XLA graph execution"]
        NXDIST["neuronx_distributed<br/>Distributed primitives"]
        PSTATE["parallel_state<br/>TP/PP process groups"]
    end
    
    subgraph "Model Layer"
        STD["Standard Models<br/>transformers.PreTrainedModel<br/>BERT, RoBERTa, etc."]
        CUSTOM["Custom Models<br/>Llama, Granite, Qwen3<br/>With TP/PP support"]
    end
    
    subgraph "Optimization"
        OPT["Optimizer<br/>torch.optim.Optimizer"]
        ZERO["NeuronZero1Optimizer<br/>neuronx_distributed.optimizer<br/>Sharded optimizer state"]
        SCHED["Scheduler<br/>torch.optim.lr_scheduler"]
    end
    
    subgraph "Data Pipeline"
        DLOAD["DataLoader<br/>torch.utils.data.DataLoader"]
        DSAMP["DistributedSampler<br/>Data parallel sharding"]
        MPDEV["MpDeviceLoader<br/>XLA device transfer"]
    end
    
    ARGS --> TRAINER
    TRAINER --> ACCEL
    ACCEL --> STATE
    
    STATE --> XLA
    STATE --> NXDIST
    NXDIST --> PSTATE
    
    ACCEL --> STD
    ACCEL --> CUSTOM
    
    ACCEL --> OPT
    OPT --> ZERO
    ACCEL --> SCHED
    
    ACCEL --> DLOAD
    DLOAD --> DSAMP
    DLOAD --> MPDEV
    
    STD --> XLA
    CUSTOM --> NXDIST
    
    style ACCEL fill:#e1f5ff
    style STATE fill:#fff3cd
    style ZERO fill:#d4edda
```

**Sources:** [optimum/neuron/accelerate/accelerator.py:79-597](), [optimum/neuron/accelerate/state.py:85-177]()

---

## Distributed Training Support

The training system supports multiple distributed parallelism strategies that can be combined:

### Parallelism Strategies

| Strategy | Purpose | Configuration | Support Level |
|----------|---------|---------------|---------------|
| **Data Parallelism** | Replicate model across devices | Automatic via process count | Standard models |
| **Tensor Parallelism** | Shard model layers across devices | `trn_config.tensor_parallel_size` | Custom models only |
| **Pipeline Parallelism** | Split model stages across devices | `trn_config.pipeline_parallel_size` | Custom models only |
| **Sequence Parallelism** | Shard activation tensors | `trn_config.sequence_parallel_enabled` | Custom models only |
| **ZeRO-1** | Shard optimizer states | `zero_1=True` | All models |

### Process Group Topology

```mermaid
graph LR
    subgraph "World Size = 32"
        subgraph "TP Group 0"
            TP0_0["Worker 0"]
            TP0_1["Worker 1"]
            TP0_2["Worker 2"]
            TP0_3["Worker 3"]
        end
        
        subgraph "TP Group 1"
            TP1_0["Worker 4"]
            TP1_1["Worker 5"]
            TP1_2["Worker 6"]
            TP1_3["Worker 7"]
        end
        
        subgraph "TP Group 2"
            TP2_0["Worker 8"]
            TP2_1["Worker 9"]
            TP2_2["Worker 10"]
            TP2_3["Worker 11"]
        end
        
        DOTS["..."]
    end
    
    TP0_0 -.TP Sync.-> TP0_1
    TP0_1 -.TP Sync.-> TP0_2
    TP0_2 -.TP Sync.-> TP0_3
    
    TP0_0 ==DP Sync==> TP1_0
    TP1_0 ==DP Sync==> TP2_0
    TP2_0 ==DP Sync==> DOTS
```

**Example:** With `tensor_parallel_size=4` and 32 workers, you get 8 data parallel replicas, each containing 4 tensor parallel shards.

The parallel state is initialized by `neuronx_distributed.parallel_layers.parallel_state.initialize_model_parallel()` during `NeuronAcceleratorState` setup.

**Sources:** [optimum/neuron/accelerate/state.py:153-157](), [optimum/neuron/accelerate/accelerator.py:253-300]()

---

## Training Workflow

### Typical Training Loop

```mermaid
sequenceDiagram
    participant User
    participant NeuronTrainer
    participant NeuronAccelerator
    participant Model
    participant Optimizer
    participant XLA
    
    User->>NeuronTrainer: train()
    NeuronTrainer->>NeuronAccelerator: __init__(trn_config, zero_1, mixed_precision)
    NeuronAccelerator->>NeuronAccelerator: Initialize NeuronAcceleratorState
    NeuronAccelerator->>XLA: init_process_group()
    
    NeuronTrainer->>NeuronAccelerator: prepare_model(model)
    NeuronAccelerator->>Model: patch_model_for_neuron()
    NeuronAccelerator->>Model: to(device) / to(bfloat16)
    NeuronAccelerator->>XLA: move_model_to_device()
    
    NeuronTrainer->>NeuronAccelerator: prepare_optimizer(optimizer)
    alt zero_1 enabled
        NeuronAccelerator->>Optimizer: wrap with NeuronZero1Optimizer
    end
    
    NeuronTrainer->>NeuronAccelerator: prepare_data_loader(dataloader)
    NeuronAccelerator->>NeuronAccelerator: wrap with DistributedSampler
    
    loop Training Steps
        NeuronTrainer->>Model: forward(inputs)
        Model-->>NeuronTrainer: loss
        NeuronTrainer->>NeuronAccelerator: backward(loss)
        NeuronAccelerator->>XLA: loss.backward()
        alt gradient_accumulation_steps reached
            NeuronTrainer->>Optimizer: step()
            NeuronTrainer->>XLA: mark_step()
        end
    end
    
    NeuronTrainer->>NeuronAccelerator: save_state(output_dir)
    NeuronAccelerator->>Model: save_pretrained()
    NeuronAccelerator->>Optimizer: save_state_dict()
```

### Model Preparation Pipeline

The `prepare_model()` method performs these steps:

1. **Patching** - Disables incompatible features ([optimum/neuron/accelerate/accelerator.py:312-336]())
   - Sets `config.layerdrop = 0`
   - Disables cache and attention outputs
   - Replaces `save_pretrained` for standard models
   - Adds `no_sync` context manager

2. **Precision Conversion** - Applies mixed precision ([optimum/neuron/accelerate/accelerator.py:361-389]())
   - `FULL_BF16`: Convert entire model to bfloat16
   - `AUTOCAST_BF16`: Enable autocast for selective bf16 operations

3. **Device Placement** - Moves model to Neuron cores ([optimum/neuron/accelerate/accelerator.py:363-391]())
   - Standard models: `move_model_to_device(model, xm.xla_device())`
   - Custom models with PP: `create_nxdpp_model()` and `model.move_model_to_device()`
   - Custom models without PP: `move_model_to_device(model, self.device)`

4. **Weight Tying** - Ensures embeddings are tied ([optimum/neuron/accelerate/accelerator.py:373-391]())

5. **Registration** - Adds to `self._models` list for lifecycle management

**Sources:** [optimum/neuron/accelerate/accelerator.py:338-398]()

---

## Mixed Precision Training

The training system supports three mixed precision modes via `MixedPrecisionConfig`:

| Mode | Description | Use Case |
|------|-------------|----------|
| `NO` | Full FP32 training | Maximum accuracy, slow |
| `FULL_BF16` | All operations in BF16 | Fast training, requires stochastic rounding or master weights |
| `AUTOCAST_BF16` | Selective BF16 with FP32 accumulation | Balanced speed/accuracy |

### MixedPrecisionConfig Options

- `stochastic_rounding: bool` - Enables SR to reduce BF16 quantization error
- `optimizer_use_master_weights: bool` - Maintains FP32 optimizer state
- `optimizer_use_fp32_grad_acc: bool` - Uses FP32 for gradient accumulation
- `optimizer_save_master_weights_in_ckpt: bool` - Saves FP32 weights to checkpoint

The configuration sets environment variables and compiler flags to control precision behavior.

**Sources:** [optimum/neuron/accelerate/utils/dataclasses.py:28-70]()

For detailed information, see [Mixed Precision Training](#5.3).

---

## Custom Model Support

For models requiring tensor or pipeline parallelism, `optimum-neuron` provides custom implementations:

- `LlamaForCausalLM` - Base Llama architecture with parallel layers
- `GraniteForCausalLM` - Extends Llama with Granite-specific modifications  
- `Qwen3ForCausalLM` - Extends Llama with Qwen3 architecture changes

These models use:
- `neuronx_distributed.parallel_layers` - ColumnParallelLinear, RowParallelLinear, ParallelEmbedding
- `GQAQKVColumnParallelLinear` - Fused QKV projection for Grouped Query Attention
- `nki_flash_attn_func` - Flash Attention v2 implementation

The `NeuronModelMixin` provides shared functionality for weight transformations between HuggingFace and Neuron formats.

**Sources:** [optimum/neuron/accelerate/accelerator.py:348-373]()

For detailed information, see [Custom Model Architectures](#5.4).

---

## Environment Initialization

The training system initializes the XLA and Neuron environment through several steps:

1. **Flag Setting** - `set_common_flags()` configures Neuron compiler flags
2. **Process Group** - `init_process_group()` initializes torch.distributed backend
3. **Parallel State** - `parallel_state.initialize_model_parallel()` sets up TP/PP groups
4. **Device Assignment** - Workers receive device ordinal from `xm.xla_device()`

These operations occur during `NeuronAcceleratorState.__init__()` and are performed once per training session.

**Sources:** [optimum/neuron/accelerate/state.py:69-76](), [optimum/neuron/accelerate/state.py:153-157]()

---

## Unsupported Features

The following Accelerate features are **not supported** by `NeuronAccelerator`:

- DeepSpeed plugin - Neuron has native distributed strategies
- FSDP plugin - Use ZeRO-1 instead
- Dynamo backend - XLA graph compilation incompatible
- Megatron-LM plugin - Use neuronx_distributed instead
- Torch distributed tensor parallel - Use custom models with TP

Attempting to use these will raise `NotImplementedError`.

**Sources:** [optimum/neuron/accelerate/accelerator.py:95-129]()

---

## Summary

The `optimum-neuron` training system provides a comprehensive framework for distributed training on AWS Trainium, combining:

- **HuggingFace compatibility** through extended Accelerate APIs
- **Scalable parallelism** via tensor, pipeline, sequence, and data parallelism
- **Optimized execution** using XLA graph compilation
- **Flexible precision** with full BF16, autocast, and master weight options
- **Production-ready checkpointing** with optimizer state sharding support

For hands-on examples, see the training tutorials in the documentation tree at [docs/source/_toctree.yml:29-42]().

---

