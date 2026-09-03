# Distributed Execution

> 来源: https://deepwiki.com/vllm-project/vllm/9-distributed-execution 抓取日期: 2026-09-02
> 章节: 第 9 章 分布式执行

---

Relevant source files

  * [tests/distributed/eplb_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/eplb_utils.py)
  * [tests/distributed/test_eplb_algo.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_algo.py)
  * [tests/distributed/test_eplb_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_execute.py)
  * [tests/distributed/test_eplb_fused_moe_layer.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_eplb_fused_moe_layer.py)
  * [tests/distributed/test_multiproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_multiproc_executor.py)
  * [tests/distributed/test_ray_v2_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/distributed/test_ray_v2_executor.py)
  * [tests/kernels/moe/test_routed_experts_capture_monolithic.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/kernels/moe/test_routed_experts_capture_monolithic.py)
  * [tests/model_executor/model_loader/tensorizer_loader/conftest.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/model_executor/model_loader/tensorizer_loader/conftest.py)
  * [tests/v1/executor/test_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/executor/test_executor.py)
  * [tests/v1/executor/test_ray_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/executor/test_ray_utils.py)
  * [tests/v1/kv_connector/unit/test_output_aggregator.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/v1/kv_connector/unit/test_output_aggregator.py)
  * [vllm/config/parallel.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py)
  * [vllm/distributed/elastic_ep/elastic_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/elastic_ep/elastic_execute.py)
  * [vllm/distributed/elastic_ep/elastic_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/elastic_ep/elastic_state.py)
  * [vllm/distributed/eplb/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/__init__.py)
  * [vllm/distributed/eplb/async_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/async_worker.py)
  * [vllm/distributed/eplb/eplb_communicator.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_communicator.py)
  * [vllm/distributed/eplb/eplb_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_state.py)
  * [vllm/distributed/eplb/eplb_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_utils.py)
  * [vllm/distributed/eplb/policy/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/__init__.py)
  * [vllm/distributed/eplb/policy/abstract.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/abstract.py)
  * [vllm/distributed/eplb/policy/default.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/policy/default.py)
  * [vllm/distributed/eplb/rebalance_execute.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/rebalance_execute.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/__init__.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/stats.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/stats.py)
  * [vllm/distributed/kv_transfer/kv_connector/v1/nixl/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/kv_transfer/kv_connector/v1/nixl/utils.py)
  * [vllm/distributed/nixl_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/nixl_utils.py)
  * [vllm/distributed/parallel_state.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py)
  * [vllm/distributed/utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/utils.py)
  * [vllm/utils/__init__.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/utils/__init__.py)
  * [vllm/v1/executor/abstract.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/abstract.py)
  * [vllm/v1/executor/multiproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py)
  * [vllm/v1/executor/ray_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor.py)
  * [vllm/v1/executor/ray_executor_v2.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor_v2.py)
  * [vllm/v1/executor/ray_utils.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_utils.py)
  * [vllm/v1/executor/uniproc_executor.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/uniproc_executor.py)
  * [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py)
  * [vllm/v1/worker/worker_base.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/worker_base.py)

This document describes vLLM's distributed execution capabilities, covering parallelism strategies (Tensor, Pipeline, Data, Expert, Context), communication infrastructure, and multi-process engine management. For model loading and weight distribution, see [Model Support and Registration](/vllm-project/vllm/5-model-support-and-registration). For attention-specific distributed features like disaggregated serving, see [KV Cache Transfer and Disaggregated Serving](/vllm-project/vllm/9.4-kv-cache-transfer-and-disaggregated-serving).

* * *

## Parallelism Strategies Overview

vLLM supports several primary parallelism strategies that can be combined to scale inference across multiple GPUs and nodes. These are configured via the `ParallelConfig` object [vllm/config/parallel.py119-120](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L119-L120)

Strategy| Abbreviation| Purpose| Configuration| Typical Use Case  
---|---|---|---|---  
**Tensor Parallelism**|  TP| Shard model weights across GPUs| `tensor_parallel_size`| Models too large for single GPU  
**Pipeline Parallelism**|  PP| Distribute layers across GPUs| `pipeline_parallel_size`| Very deep models, reduce memory per GPU  
**Data Parallelism**|  DP| Replicate model across instances| `data_parallel_size`| Increase throughput with independent batches  
**Expert Parallelism**|  EP| Distribute MoE experts| `enable_expert_parallel`| Mixture-of-Experts models  
**Context Parallelism**|  CP| Split long sequences| `prefill_context_parallel_size`| Long context windows  
  
The total world size for model execution is generally `TP × PP × PCP` (where PCP is Prefill Context Parallelism) [vllm/v1/executor/multiproc_executor.py125-131](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L125-L131) vLLM also introduces specialized parallelisms like `prefill_context_parallel_size` for scaling long-context prefill [vllm/config/parallel.py126-128](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L126-L128) Data parallelism can be further categorized into global or local configurations, with support for hybrid and external load balancing [vllm/config/parallel.py129-162](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L129-L162)

For details, see [Parallelism Strategies](/vllm-project/vllm/9.1-parallelism-strategies).

**Sources:** [vllm/config/parallel.py119-174](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L119-L174) [vllm/distributed/parallel_state.py8-24](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py#L8-L24) [vllm/v1/executor/multiproc_executor.py125-131](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L125-L131)

* * *

## Configuration and Initialization

### ParallelConfig Structure

The `ParallelConfig` class encapsulates all distributed execution settings. It manages worker counts, rank assignments, and backend selection for data and model parallelism.

Title: "ParallelConfig Attributes to Code Entities"

**Sources:** [vllm/config/parallel.py119-174](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L119-L174)

* * *

## Distributed Communication Infrastructure

vLLM utilizes platform-specific communication backends (NCCL for NVIDIA/AMD, XCCL for Intel, Gloo for CPU) to perform collective operations like `all_reduce`, `all_gather`, and `reduce_scatter`.

### Communication Backend Selection

The system initializes the distributed environment through `init_distributed_environment` [vllm/v1/worker/gpu_worker.py25](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L25-L25) and creates specialized process groups for each parallelism dimension (TP, PP, DP, EP, CP) via `GroupCoordinator` [vllm/distributed/parallel_state.py123-146](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py#L123-L146)

For specialized MoE communication, vLLM supports multiple `all2all` backends including `deepep_v2`, `flashinfer_nvlink_two_sided`, `mori_low_latency`, and `nixl_ep` [vllm/config/parallel.py42-55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L42-L55) The communication state is managed by a variety of group accessors such as `get_tp_group`, `get_pp_group`, and `get_ep_group` [vllm/distributed/parallel_state.py46-48](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py#L46-L48)

Title: "Distributed Group Management and Operations"

For details, see [Communication Infrastructure](/vllm-project/vllm/9.2-communication-infrastructure).

**Sources:** [vllm/v1/worker/gpu_worker.py23-27](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L23-L27) [vllm/config/parallel.py42-55](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L42-L55) [vllm/distributed/parallel_state.py152-197](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/parallel_state.py#L152-L197)

* * *

## Multi-Process Engine Management

In vLLM, the engine manages model execution through specialized executors that coordinate one or more worker processes. The engine can spawn processes locally or manage them across a cluster using Ray.

### Executor Implementations

vLLM provides several executor backends depending on the environment and parallelism requirements:

  * **RayDistributedExecutor** : Orchestrates workers across a cluster using Ray actors. It utilizes `RayWorkerWrapper` to lazily initialize workers [vllm/v1/executor/ray_executor.py64-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor.py#L64-L110)
  * **MultiprocExecutor** : Spawns multiple local processes using `multiprocessing` and manages a `MessageQueue` for broadcasting `SchedulerOutput` via shared memory [vllm/v1/executor/multiproc_executor.py111-167](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L111-L167)
  * **UniProcExecutor** : Single-process execution where the engine and worker share a process [vllm/v1/executor/uniproc_executor.py51-75](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/uniproc_executor.py#L51-L75)

The `ParallelConfig` defines the `distributed_executor_backend` which can be `"ray"`, `"mp"`, `"uni"`, or `"external_launcher"` [vllm/config/parallel.py37](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L37-L37)

For details, see [Multi-Process Engine Management](/vllm-project/vllm/9.3-multi-process-engine-management).

**Sources:** [vllm/config/parallel.py37](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L37-L37) [vllm/v1/executor/multiproc_executor.py111-167](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L111-L167) [vllm/v1/executor/ray_executor.py64-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/ray_executor.py#L64-L110) [vllm/v1/executor/uniproc_executor.py51-75](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/uniproc_executor.py#L51-L75)

* * *

## KV Cache Transfer and Disaggregated Serving

vLLM supports disaggregated serving (prefill-decode separation) by transferring KV cache blocks between different engine instances.

### KVConnector and Transfer Backends

The system supports infrastructure for moving KV cache data using `KVConnector`. This enables "prefill" nodes to compute the cache and "decode" nodes to consume it. The `ensure_kv_transfer_initialized` function sets up the required distributed groups [vllm/v1/worker/gpu_worker.py33-38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L33-L38) `MultiprocExecutor` utilizes `KVOutputAggregator` to manage distributed output collection when connectors are active [vllm/v1/executor/multiproc_executor.py33](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L33-L33)

For details, see [KV Cache Transfer and Disaggregated Serving](/vllm-project/vllm/9.4-kv-cache-transfer-and-disaggregated-serving).

**Sources:** [vllm/v1/worker/gpu_worker.py33-38](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/worker/gpu_worker.py#L33-L38) [vllm/v1/executor/multiproc_executor.py33](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/multiproc_executor.py#L33-L33) [vllm/v1/executor/abstract.py113-114](https://github.com/vllm-project/vllm/blob/185cada3/vllm/v1/executor/abstract.py#L113-L114)

* * *

## Expert Parallelism (EP) and Load Balancing

For Mixture-of-Experts (MoE) models, vLLM supports Expert Parallelism, which shards experts across ranks. To prevent "hot" experts from bottlenecking the system, vLLM includes an Expert Parallelism Load Balancer (EPLB) configured via `EPLBConfig` [vllm/config/parallel.py59-115](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L59-L115)

### EPLB State and Rebalancing

The `EplbModelState` tracks expert load using token counts per expert [vllm/distributed/eplb/eplb_state.py104-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_state.py#L104-L170) Rebalancing involves rearranging physical experts (replicas of logical experts) across devices [vllm/distributed/eplb/eplb_state.py6-27](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_state.py#L6-L27) The actual exchange of expert weights between GPUs is performed by `move_to_buffer` and `rearrange_expert_weights_inplace` using specialized communicators [vllm/distributed/eplb/rebalance_execute.py173-183](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/rebalance_execute.py#L173-L183)

Title: "MoE Expert Parallelism and EPLB"

For details, see [Parallelism Strategies](/vllm-project/vllm/9.1-parallelism-strategies).

**Sources:** [vllm/config/parallel.py59-115](https://github.com/vllm-project/vllm/blob/185cada3/vllm/config/parallel.py#L59-L115) [vllm/distributed/eplb/eplb_state.py6-170](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/eplb_state.py#L6-L170) [vllm/distributed/eplb/rebalance_execute.py3-61](https://github.com/vllm-project/vllm/blob/185cada3/vllm/distributed/eplb/rebalance_execute.py#L3-L61)
