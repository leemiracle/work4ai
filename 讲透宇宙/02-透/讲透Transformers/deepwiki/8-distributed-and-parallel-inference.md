> 来源: [https://deepwiki.com/huggingface/transformers/8-distributed-and-parallel-inference](https://deepwiki.com/huggingface/transformers/8-distributed-and-parallel-inference)
> DeepWiki huggingface/transformers | Last indexed: 3 September 2026 (8f5420

# Distributed & Parallel Inference

  Relevant source files 
 - [docs/source/en/continuous_batching.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/continuous_batching.md?plain=1)
 - [docs/source/en/continuous_batching_architecture.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/continuous_batching_architecture.md?plain=1)
 - [docs/source/en/expert_parallelism.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/expert_parallelism.md?plain=1)
 - [docs/source/en/experts_interface.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/experts_interface.md?plain=1)
 - [docs/source/en/feature_extractors.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/feature_extractors.md?plain=1)
 - [docs/source/en/main_classes/continuous_batching.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/continuous_batching.md?plain=1)
 - [docs/source/en/main_classes/quantization.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/main_classes/quantization.md?plain=1)
 - [docs/source/en/optimization_overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/optimization_overview.md?plain=1)
 - [docs/source/en/perf_infer_gpu_multi.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/perf_infer_gpu_multi.md?plain=1)
 - [docs/source/en/quantization/finegrained_fp8.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/finegrained_fp8.md?plain=1)
 - [docs/source/en/quantization/overview.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/quantization/overview.md?plain=1)
 - [docs/source/en/tensor_parallelism.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/tensor_parallelism.md?plain=1)
 - [docs/source/en/weightconverter.md](https://github.com/huggingface/transformers/blob/8f542025/docs/source/en/weightconverter.md?plain=1)
 - [src/transformers/conversion_mapping.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py)
 - [src/transformers/core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py)
 - [src/transformers/distributed/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/__init__.py)
 - [src/transformers/distributed/configuration_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/configuration_utils.py)
 - [src/transformers/distributed/fsdp.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/fsdp.py)
 - [src/transformers/distributed/mixin.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/mixin.py)
 - [src/transformers/distributed/pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/pipeline_parallel.py)
 - [src/transformers/distributed/sharding_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/sharding_utils.py)
 - [src/transformers/distributed/tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/tensor_parallel.py)
 - [src/transformers/distributed/utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/utils.py)
 - [src/transformers/integrations/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/__init__.py)
 - [src/transformers/integrations/accelerate.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py)
 - [src/transformers/integrations/deepspeed.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py)
 - [src/transformers/integrations/tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/tensor_parallel.py)
 - [src/transformers/modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py)
 - [src/transformers/quantizers/auto.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/quantizers/auto.py)
 - [src/transformers/testing_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/testing_utils.py)
 - [src/transformers/trainer.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py)
 - [src/transformers/trainer_pt_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_pt_utils.py)
 - [src/transformers/trainer_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer_utils.py)
 - [src/transformers/training_args.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/training_args.py)
 - [src/transformers/utils/__init__.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/__init__.py)
 - [src/transformers/utils/import_utils.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/import_utils.py)
 - [src/transformers/utils/loading_report.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/loading_report.py)
 - [src/transformers/utils/quantization_config.py](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/utils/quantization_config.py)
 - [tests/pipeline_parallel/test_pipeline_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/pipeline_parallel/test_pipeline_parallel.py)
 - [tests/tensor_parallel/test_tensor_parallel.py](https://github.com/huggingface/transformers/blob/8f542025/tests/tensor_parallel/test_tensor_parallel.py)
 - [tests/test_modeling_common.py](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py)
 - [tests/trainer/test_trainer.py](https://github.com/huggingface/transformers/blob/8f542025/tests/trainer/test_trainer.py)
 - [tests/utils/test_core_model_loading.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_core_model_loading.py)
 - [tests/utils/test_distributed_sharding_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_distributed_sharding_utils.py)
 - [tests/utils/test_modeling_utils.py](https://github.com/huggingface/transformers/blob/8f542025/tests/utils/test_modeling_utils.py)
 
  Distributed execution in Transformers allows models to scale across multiple GPUs and nodes by partitioning computation and memory. The library supports several paradigms for high-performance inference and training, ranging from automated device mapping for single-node setups to advanced tensor and expert parallelism for large-scale clusters.

 
## High-Level Parallelism Overview

 Transformers leverages `torch.distributed` and the `accelerate` library to provide several distribution strategies. These strategies can often be combined (e.g., Tensor Parallelism + FSDP) to optimize throughput and memory usage. A critical component in modern loading is the `WeightConverter` and `ConversionOps` system, which handles tensor transformations (like sharding or permuting) during the loading process [src/transformers/core_model_loading.py51-82](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L51-L82)

 
| Strategy | Key Code Entities | Primary Use Case |
|---|---|---|
| Tensor Parallelism (TP) | DistributedMixin, tp_plan, DTensor | Splitting individual layers (e.g., Attention, MLP) across GPUs to reduce latency. |
| Expert Parallelism (EP) | ep_plan, ALL_EXPERTS_FUNCTIONS | Scaling Mixture-of-Experts (MoE) models by distributing experts across devices. |
| FSDP / ZeRO | is_fsdp_enabled, HfDeepSpeedConfig | Sharding model states, gradients, and optimizer states to fit massive models. |
| Device Mapping | device_map='auto', accelerate_dispatch | Vertical model sharding (layer-by-layer) across multiple devices with disk/CPU offload. |

 
### Architecture to Code Mapping: Distributed Orchestration

 The following diagram illustrates how high-level distributed concepts map to specific classes and utilities within the `transformers` codebase.

 
```

```

 **Sources:** [src/transformers/distributed/tensor_parallel.py60](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/tensor_parallel.py#L60-L60) [src/transformers/modeling_utils.py57-59](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L57-L59) [src/transformers/integrations/accelerate.py69-77](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py#L69-L77) [src/transformers/integrations/deepspeed.py78](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/deepspeed.py#L78-L78)

 
---

 
## Tensor & Expert Parallelism (TP/EP)

 Tensor Parallelism shards individual tensors (like linear layer weights) across a `DeviceMesh` using PyTorch `DTensor` abstractions [src/transformers/modeling_utils.py46](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L46-L46) Transformers implements this via a `tp_plan`, a dictionary mapping layer patterns to sharding styles like `colwise` or `rowwise` [src/transformers/distributed/tensor_parallel.py60](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/tensor_parallel.py#L60-L60) During loading, `DtensorShardOperation` handles the transformation of local weights into distributed tensors [src/transformers/core_model_loading.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L33-L33)

 Expert Parallelism is specialized for MoE models, where experts are distributed across GPUs. This is supported through the `ep_plan` and integrated expert functions like `ALL_EXPERTS_FUNCTIONS` [src/transformers/modeling_utils.py85](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L85-L85) The `DistributedMixin` provides the core API for applying these plans during model loading via `from_pretrained` [src/transformers/modeling_utils.py58](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L58-L58)

 For details, see [Tensor Parallelism & Expert Parallelism](https://deepwiki.com/huggingface/transformers/8.1-tensor-parallelism-and-expert-parallelism).

 **Sources:** [src/transformers/modeling_utils.py46-65](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L46-L65) [src/transformers/core_model_loading.py33-34](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L33-L34) [src/transformers/distributed/tensor_parallel.py60](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/distributed/tensor_parallel.py#L60-L60)

 
---

 
## DeepSpeed & FSDP Integration

 Transformers provides deep integration with **DeepSpeed ZeRO** (Stages 1, 2, and 3) and **PyTorch FSDP**. These technologies shard model parameters, gradients, and optimizer states to enable training and inference of models that exceed the memory of a single GPU.

 The `HfDeepSpeedConfig` class [tests/test_modeling_common.py48](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py#L48-L48) handles the translation of configuration into DeepSpeed-compatible environments. FSDP integration is checked via `is_fsdp_enabled` [src/transformers/modeling_utils.py68](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L68-L68) and managed through `FullyShardedDataParallel` wrappers. The `Trainer` class orchestrates these integrations, specifically handling DeepSpeed initialization via `deepspeed_init` [src/transformers/trainer.py63-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L63-L69)

 For details, see [DeepSpeed & FSDP Integration](https://deepwiki.com/huggingface/transformers/8.2-deepspeed-and-fsdp-integration).

 **Sources:** [src/transformers/modeling_utils.py68-78](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L68-L78) [src/transformers/trainer.py58-69](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/trainer.py#L58-L69) [tests/test_modeling_common.py48-54](https://github.com/huggingface/transformers/blob/8f542025/tests/test_modeling_common.py#L48-L54)

 
---

 
## Accelerate & Device Mapping

 For simpler multi-GPU setups, the `device_map='auto'` feature uses the `accelerate` library to automatically calculate a "balanced" distribution of model layers across available GPUs, CPU, and disk [src/transformers/integrations/accelerate.py70-75](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/integrations/accelerate.py#L70-L75)

 The `check_and_set_device_map` function validates the provided mapping and ensures compatibility with the available hardware [src/transformers/modeling_utils.py73](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L73-L73) Unlike TP, which parallelizes computation within layers, device mapping shards the model vertically, often utilizing `accelerate_disk_offload` for models larger than total VRAM [src/transformers/modeling_utils.py71](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L71-L71)

 For details, see [Accelerate & Device Mapping](https://deepwiki.com/huggingface/transformers/8.3-accelerate-and-device-mapping).

 
### Logic Flow: Weight Dispatching

 This diagram shows how weights are processed from the state dict into their final distributed locations, incorporating `ConversionOps` (like `Chunk` or `Concatenate`) and the `DtensorShardOperation` for distributed sharding.

 
```

```

 **Sources:** [src/transformers/core_model_loading.py81-165](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L81-L165) [src/transformers/core_model_loading.py33](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L33-L33) [src/transformers/modeling_utils.py70-73](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L70-L73)

 **Sources:** [src/transformers/modeling_utils.py51-77](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/modeling_utils.py#L51-L77) [src/transformers/core_model_loading.py21-34](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/core_model_loading.py#L21-L34) [src/transformers/conversion_mapping.py21-34](https://github.com/huggingface/transformers/blob/8f542025/src/transformers/conversion_mapping.py#L21-L34)
