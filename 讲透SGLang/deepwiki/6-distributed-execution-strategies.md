> 来源: [https://deepwiki.com/sgl-project/sglang/6-distributed-execution-strategies](https://deepwiki.com/sgl-project/sglang/6-distributed-execution-strategies)
> DeepWiki sgl-project/sglang | Last indexed: 27 Aug 2026 (94183a)

# Distributed Execution Strategies

  Relevant source files 
 - [benchmark/kernels/all_reduce/benchmark_fused_ar_rms_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/kernels/all_reduce/benchmark_fused_ar_rms_amd.py)
 - [benchmark/kernels/all_reduce/benchmark_fused_ar_rms_quant_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/benchmark/kernels/all_reduce/benchmark_fused_ar_rms_quant_amd.py)
 - [python/sglang/srt/disaggregation/base/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/base/conn.py)
 - [python/sglang/srt/disaggregation/common/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/conn.py)
 - [python/sglang/srt/disaggregation/common/staging_buffer.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/staging_buffer.py)
 - [python/sglang/srt/disaggregation/common/staging_handler.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/staging_handler.py)
 - [python/sglang/srt/disaggregation/decode.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py)
 - [python/sglang/srt/disaggregation/fake/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/fake/conn.py)
 - [python/sglang/srt/disaggregation/mooncake/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mooncake/conn.py)
 - [python/sglang/srt/disaggregation/mori/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mori/conn.py)
 - [python/sglang/srt/disaggregation/nixl/conn.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/nixl/conn.py)
 - [python/sglang/srt/disaggregation/prefill.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/prefill.py)
 - [python/sglang/srt/disaggregation/utils.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/utils.py)
 - [python/sglang/srt/distributed/communication_op.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/communication_op.py)
 - [python/sglang/srt/distributed/device_communicators/pynccl.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/device_communicators/pynccl.py)
 - [python/sglang/srt/distributed/device_communicators/pynccl_wrapper.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/device_communicators/pynccl_wrapper.py)
 - [python/sglang/srt/distributed/parallel_state.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py)
 - [python/sglang/srt/layers/communicator.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py)
 - [python/sglang/srt/layers/dp_attention.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py)
 - [python/sglang/srt/layers/flashinfer_comm_fusion.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/flashinfer_comm_fusion.py)
 - [python/sglang/srt/layers/layernorm.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/layernorm.py)
 - [python/sglang/srt/managers/scheduler_pp_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py)
 - [python/sglang/srt/multiplex/multiplexing_mixin.py](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multiplex/multiplexing_mixin.py)
 - [test/registered/amd/disaggregation/test_mori_transfer_engine_e2e.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/disaggregation/test_mori_transfer_engine_e2e.py)
 - [test/registered/amd/perf/mi35x/test_qwen35_fp8_ar_fusion_mi35x.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/amd/perf/mi35x/test_qwen35_fp8_ar_fusion_mi35x.py)
 - [test/registered/disaggregation/test_disaggregation_different_tp.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/disaggregation/test_disaggregation_different_tp.py)
 - [test/registered/ops/test_aiter_allreduce_fusion_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/ops/test_aiter_allreduce_fusion_amd.py)
 - [test/registered/ops/test_aiter_greedy_sample_amd.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/ops/test_aiter_greedy_sample_amd.py)
 - [test/registered/unit/disaggregation/test_nixl_backend_basic.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_nixl_backend_basic.py)
 - [test/registered/unit/disaggregation/test_receiver_connection_pool.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/disaggregation/test_receiver_connection_pool.py)
 - [test/registered/unit/layers/test_flashinfer_comm_fusion.py](https://github.com/sgl-project/sglang/blob/94183a8d/test/registered/unit/layers/test_flashinfer_comm_fusion.py)
 
  This page provides a high-level overview of the distributed execution strategies in SGLang, encompassing all supported parallelism methods for scaling large language and vision-language models across GPUs and nodes. It covers Tensor Parallelism (TP), Pipeline Parallelism (PP), Expert Parallelism (EP), Data Parallelism (DP), Prefill-Decode disaggregation, and advanced features such as PD-Multiplexing and Elastic EP.

 For details on model configuration parameters that influence these strategies, see [Model Configuration and Loading](https://deepwiki.com/sgl-project/sglang/7-model-configuration-and-loading). For core scheduling and memory management principles that interplay with these distributed strategies, see [Memory Management and KV Cache](https://deepwiki.com/sgl-project/sglang/5-memory-management-and-kv-cache).

 
---

 
## Overview of Parallelism Dimensions

 SGLang supports multiple orthogonal parallelism dimensions to leverage computational resources effectively. These can be combined according to deployment and model requirements.

 
```

```

 The `ServerArgs` package defines these dimensions and controls their interaction. The effective global world size (total number of processes) is typically the product of TP, PP, DP, and CP sizes. MoE-related parallelism (EP and MoE DP) are additional dimensions constrained by TP size.

 **Sources:** [python/sglang/srt/server_args.py365-442](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/server_args.py#L365-L442) [python/sglang/srt/layers/dp_attention.py13-34](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L13-L34) [python/sglang/srt/runtime_context.py75-110](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/runtime_context.py#L75-L110)

 
---

 
## Distributed Execution Initialization and Rank Management

 SGLang initializes the distributed environment during model runner setup. It defines multiple communication groups corresponding to parallelism dimensions, enabling efficient collective communication.

 
### Key Points:

 
 - Initialization occurs in `parallel_state.py` with `init_distributed_environment()` and model parallel setup methods [python/sglang/srt/distributed/parallel_state.py9-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L9-L25)
 - Process groups are created for TP, PP, DP, and attention CP.
 - Each rank is assigned multiple identifiers: global rank, `tp_rank`, `pp_rank`, `dp_rank`, `attn_cp_rank`, `attn_tp_rank`, and `attn_dp_rank`.
 - The `ParallelContext` provides a structured accessor for these live topology facts [python/sglang/srt/runtime_context.py113-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/runtime_context.py#L113-L156)
 
 
```

```

 
### Rank Identifier Summary

 
| Rank | Purpose | Source Location |
|---|---|---|
| rank | Global process rank | torch.distributed.get_rank() |
| tp_rank | Tensor parallel rank | get_tensor_model_parallel_rank() python/sglang/srt/distributed/parallel_state.py180-186 |
| pp_rank | Pipeline stage rank | get_pipeline_model_parallel_rank() python/sglang/srt/distributed/parallel_state.py188-190 |
| attn_cp_rank | Attention context parallel rank | get_attn_cp_group().rank() python/sglang/srt/layers/dp_attention.py15 |
| attn_dp_rank | Attention data parallel rank | get_attention_dp_rank() python/sglang/srt/layers/dp_attention.py36-38 |

 **Sources:** [python/sglang/srt/distributed/parallel_state.py9-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L9-L25) [python/sglang/srt/layers/dp_attention.py13-47](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L13-L47) [python/sglang/srt/disaggregation/common/conn.py167-183](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/conn.py#L167-L183) [python/sglang/srt/runtime_context.py171-200](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/runtime_context.py#L171-L200)

 
---

 
## Tensor Parallelism (TP)

 Tensor Parallelism shards model tensors across GPUs, dividing weights and activations along their feature dimensions.

 
 - Custom operators `inplace_all_reduce` and `outplace_all_reduce` manage effective synchronization of shards [python/sglang/srt/distributed/parallel_state.py167-185](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L167-L185)
 - Linear layers support column and row sharding strategies with classes like `ColumnParallelLinear` and `RowParallelLinear` [python/sglang/srt/layers/communicator.py10-29](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L10-L29)
 - **FlashInfer Allreduce Fusion**: Optimizes communication performance by fusing multiple all-reduce operations (e.g., `flashinfer_allreduce`) [python/sglang/srt/distributed/parallel_state.py189-201](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L189-L201)
 - **Two-Batch Overlap (TBO)**: Advanced optimization to overlap compute and communication between two micro-batches [python/sglang/srt/batch_overlap/two_batch_overlap.py23-28](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/batch_overlap/two_batch_overlap.py#L23-L28)
 
 **Sources:** [python/sglang/srt/distributed/parallel_state.py167-201](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L167-L201) [python/sglang/srt/layers/communicator.py165-179](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L165-L179) [python/sglang/srt/batch_overlap/two_batch_overlap.py12-28](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/batch_overlap/two_batch_overlap.py#L12-L28) For details, see [Tensor and Pipeline Parallelism](https://deepwiki.com/sgl-project/sglang/6.1-tensor-and-pipeline-parallelism).

 
---

 
## Pipeline Parallelism (PP)

 Pipeline Parallelism partitions model layers over a sequence of stages (processes), with efficient forwarding of activations between them.

 
 - The `SchedulerPPMixin` defines the core event loop (`event_loop_pp`) managing scheduling, communication, and overlapping compute and communication [python/sglang/srt/managers/scheduler_pp_mixin.py74-97](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py#L74-L97)
 - The event loop handles batched requests, pipelined communication, and proxy tensors via `PPProxyTensors` [python/sglang/srt/managers/scheduler_pp_mixin.py34-38](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py#L34-L38) [python/sglang/srt/managers/scheduler_pp_mixin.py122-132](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py#L122-L132)
 - **Communication Overlap**: Uses asynchronous sends (`_pp_send_pyobj_to_next_stage`) and synchronous receives to coordinate data passing [python/sglang/srt/managers/scheduler_pp_mixin.py101-115](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py#L101-L115)
 
 **Sources:** [python/sglang/srt/managers/scheduler_pp_mixin.py72-160](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/managers/scheduler_pp_mixin.py#L72-L160) For details, see [Tensor and Pipeline Parallelism](https://deepwiki.com/sgl-project/sglang/6.1-tensor-and-pipeline-parallelism).

 
---

 
## Expert Parallelism (EP) for Mixture-of-Experts (MoE) Models

 Expert Parallelism assigns different experts in MoE layers to separate devices.

 
### Supported Backends for Token Dispatch and KV Transfer

 
 - **DeepEP**: Optimized for NVIDIA and NPU platforms; supports HCCL options for MoE groups [python/sglang/srt/distributed/parallel_state.py89-104](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L89-L104)
 - **Mooncake**: Utilizes RDMA and ZeroMQ messaging with `MooncakeKVManager` [python/sglang/srt/disaggregation/mooncake/conn.py198-209](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mooncake/conn.py#L198-L209)
 - **NIXL**: RDMA-based KV transfer backend supporting multi-node deployments via `NixlKVManager` [python/sglang/srt/disaggregation/nixl/conn.py204-230](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/nixl/conn.py#L204-L230)
 - **MORI**: Designed for ROCm-based AMD GPUs with `MoriKVManager` [python/sglang/srt/disaggregation/mori/conn.py29-47](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mori/conn.py#L29-L47)
 
 **Sources:** [python/sglang/srt/distributed/parallel_state.py89-104](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L89-L104) [python/sglang/srt/disaggregation/mooncake/conn.py198-209](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/mooncake/conn.py#L198-L209) [python/sglang/srt/disaggregation/nixl/conn.py204-230](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/nixl/conn.py#L204-L230) For details, see [Expert Parallelism for MoE Models](https://deepwiki.com/sgl-project/sglang/6.2-expert-parallelism-for-moe-models).

 
---

 
## Data Parallelism (DP) and DP Attention

 SGLang introduces **DP Attention** to shard tokens rather than full sequences, improving performance during long-context inference.

 
### DP Attention Features:

 
 - **Padding Modes**: `MAX_LEN` and `SUM_LEN` determine how tokens are gathered across DP ranks [python/sglang/srt/layers/dp_attention.py76-92](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L76-L92)
 - **Buffer Management**: `_DpGatheredBufferWrapper` class manages DP attention token buffers and allocation metadata [python/sglang/srt/layers/dp_attention.py134-156](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L134-L156)
 - **Global Coordination**: `dp_reduce_scatter_tensor` and `dp_gather_partial` handle token synchronization [python/sglang/srt/layers/communicator.py39-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L39-L55)
 
 **Sources:** [python/sglang/srt/layers/dp_attention.py76-180](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L76-L180) [python/sglang/srt/layers/communicator.py39-55](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/communicator.py#L39-L55) For details, see [Data Parallelism and DP Attention](https://deepwiki.com/sgl-project/sglang/6.3-data-parallelism-and-dp-attention).

 
---

 
## Prefill-Decode Disaggregation

 This strategy decouples the expensive Prefill phase from the low-latency Decode phase by specialization on different nodes.

 
### Architecture Overview

 
```

```

 
### Request Lifecycle

 
 - **Decode Server**: Requests flow through `PreallocQueue`, `TransferQueue`, `WaitingQueue`, and `RunningBatch` [python/sglang/srt/disaggregation/decode.py1-19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py#L1-L19)
 - **Prefill Server**: Requests flow through `Bootstrap Queue`, `Waiting Queue`, and `Inflight Queue` [python/sglang/srt/disaggregation/prefill.py1-18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/prefill.py#L1-L18)
 - **Memory Management**: `DecodeReqToTokenPool` subscribes memory for pre-allocated requests to unblock prefill [python/sglang/srt/disaggregation/decode.py123-152](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py#L123-L152)
 
 **Sources:** [python/sglang/srt/disaggregation/decode.py1-19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py#L1-L19) [python/sglang/srt/disaggregation/prefill.py1-18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/prefill.py#L1-L18) [python/sglang/srt/disaggregation/common/conn.py146-193](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/common/conn.py#L146-L193) For details, see [Prefill-Decode Disaggregation](https://deepwiki.com/sgl-project/sglang/6.4-prefill-decode-disaggregation).

 
---

 
## Advanced Distributed Features

 
### PD-Multiplexing

 PD-Multiplexing allows a single engine to dynamically adapt roles during runtime based on load, implemented via `MultiplexingMixin` [python/sglang/srt/multiplex/multiplexing_mixin.py1-20](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/multiplex/multiplexing_mixin.py#L1-L20)

 
### Elastic EP

 Elastic EP provides the ability to elastically scale expert parallel groups according to runtime load, integrated with `update_dp_attention_post_scale` [python/sglang/srt/layers/dp_attention.py60-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L60-L70)

 
---

 
## Child Pages for Detailed Design and Usage

 
 - [Tensor and Pipeline Parallelism](https://deepwiki.com/sgl-project/sglang/6.1-tensor-and-pipeline-parallelism) — TP/PP implementation and NCCL communication.
 - [Expert Parallelism for MoE Models](https://deepwiki.com/sgl-project/sglang/6.2-expert-parallelism-for-moe-models) — Token dispatch backends and load balancing.
 - [Data Parallelism and DP Attention](https://deepwiki.com/sgl-project/sglang/6.3-data-parallelism-and-dp-attention) — DataParallelController and DP attention communication.
 - [Prefill-Decode Disaggregation](https://deepwiki.com/sgl-project/sglang/6.4-prefill-decode-disaggregation) — Disaggregation architecture and KV cache transfer.
 
 **Sources:** [python/sglang/srt/distributed/parallel_state.py1-25](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/distributed/parallel_state.py#L1-L25) [python/sglang/srt/layers/dp_attention.py1-70](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/layers/dp_attention.py#L1-L70) [python/sglang/srt/disaggregation/decode.py1-19](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/decode.py#L1-L19) [python/sglang/srt/disaggregation/prefill.py1-18](https://github.com/sgl-project/sglang/blob/94183a8d/python/sglang/srt/disaggregation/prefill.py#L1-L18)
