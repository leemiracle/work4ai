<!-- source: DeepWiki mcp.deepwiki.com · repo RLinf/RLinf · page 9 Advanced Topics · fetched 2026-10-21 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/agent-e2e-tests.yml](.github/workflows/agent-e2e-tests.yml)
- [rlinf/algorithms/losses.py](rlinf/algorithms/losses.py)
- [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py](rlinf/hybrid_engines/fsdp/fsdp_model_manager.py)
- [rlinf/hybrid_engines/fsdp/strategy/base.py](rlinf/hybrid_engines/fsdp/strategy/base.py)
- [rlinf/hybrid_engines/fsdp/strategy/fsdp.py](rlinf/hybrid_engines/fsdp/strategy/fsdp.py)
- [rlinf/hybrid_engines/fsdp/utils.py](rlinf/hybrid_engines/fsdp/utils.py)
- [rlinf/hybrid_engines/megatron/token_dispatcher.py](rlinf/hybrid_engines/megatron/token_dispatcher.py)
- [rlinf/hybrid_engines/megatron/utils.py](rlinf/hybrid_engines/megatron/utils.py)
- [rlinf/models/__init__.py](rlinf/models/__init__.py)
- [rlinf/runners/agentlightning_runner.py](rlinf/runners/agentlightning_runner.py)
- [rlinf/utils/metric_utils.py](rlinf/utils/metric_utils.py)
- [rlinf/workers/actor/async_ppo_fsdp_worker.py](rlinf/workers/actor/async_ppo_fsdp_worker.py)
- [rlinf/workers/actor/ma_megatron_actor_worker.py](rlinf/workers/actor/ma_megatron_actor_worker.py)
- [rlinf/workers/actor/megatron_actor_worker.py](rlinf/workers/actor/megatron_actor_worker.py)
- [rlinf/workers/agent/agentlightning_rollout_worker.py](rlinf/workers/agent/agentlightning_rollout_worker.py)
- [rlinf/workers/critic/megatron_critic_worker.py](rlinf/workers/critic/megatron_critic_worker.py)
- [rlinf/workers/megatron_worker.py](rlinf/workers/megatron_worker.py)
- [tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml](tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml)

</details>



This page covers advanced features and optimizations in RLinf designed for expert users who need fine-grained control over distributed training, memory management, and performance tuning. These techniques enable scaling to production workloads and achieving maximum hardware utilization.

## Model Parallelism Strategies

RLinf supports multiple dimensions of model parallelism that can be combined to train models at arbitrary scales. These strategies are primarily managed through the Megatron and FSDP backends.

### Parallelism Dimensions

| Dimension | Config Key | Purpose | Backend |
|-----------|-----------|---------|---------|
| Tensor Parallel (TP) | `tensor_model_parallel_size` | Splits weight matrices across GPUs | Megatron |
| Pipeline Parallel (PP) | `pipeline_model_parallel_size` | Splits model layers into stages | Megatron |
| Expert Parallel (EP) | `expert_model_parallel_size` | Distributes MoE experts across GPUs | Megatron |
| Expert Tensor Parallel (TPE) | `expert_tensor_parallel_size` | TP within each expert | Megatron |
| Context Parallel (CP) | `context_parallel_size` | Splits sequence dimension | Megatron |
| Fully Sharded Data Parallel (FSDP) | `fsdp_config.sharding_strategy` | Shards parameters, grads, and optimizer states | FSDP |

### Backend Specifics

**Megatron Backend:**
The `MegatronWorker` and `MegatronActor` initialize distributed groups using Megatron Core's `parallel_state` [rlinf/workers/actor/megatron_actor_worker.py:19-21](). It handles complex 3D parallelism and specialized MoE configurations like `mg_ep_size` and `moe_grouped_gemm` [rlinf/workers/actor/megatron_actor_worker.py:105-107](). The system handles weight resharding between different TP/PP/EP configurations using `MegatronCoreWeightReshard` [rlinf/workers/actor/megatron_actor_worker.py:109-109]().

**FSDP Backend:**
The `FSDPModelManager` supports precision-aware `torch_dtype` selection for mixed precision [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py:68-77](). It provides two strategy implementations via `FSDPStrategyBase`: `FSDPStrategy` (classic `torch.distributed.fsdp`) and `FSDP2Strategy` (`fully_shard` API) [rlinf/hybrid_engines/fsdp/strategy/base.py:88-106](). It also supports `CPUOffload` for memory-constrained scenarios [rlinf/hybrid_engines/fsdp/strategy/fsdp.py:171-187](). The system uses `get_fsdp_wrap_policy` to handle both standard transformer models and VLA models [rlinf/hybrid_engines/fsdp/utils.py:151-209]().

### Context Parallelism (CP) and Sequence Packing
For reasoning tasks with long sequences, RLinf utilizes Context Parallelism. The `MAMegatronActor` supports multi-agent actor training with context parallel groups [rlinf/workers/actor/ma_megatron_actor_worker.py:107-112]().

For details, see [Model Parallelism Strategies](#9.1).

**Sources:** [rlinf/workers/actor/megatron_actor_worker.py:19-109](), [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py:68-106](), [rlinf/hybrid_engines/fsdp/strategy/base.py:88-106](), [rlinf/hybrid_engines/fsdp/strategy/fsdp.py:171-187](), [rlinf/hybrid_engines/fsdp/utils.py:151-209](), [rlinf/workers/actor/ma_megatron_actor_worker.py:107-112]()

---

## FUSCO MoE Optimization

FUSCO (FUSed Communication and COmputation) is a high-performance library that optimizes Mixture-of-Experts (MoE) all-to-all communication. RLinf integrates FUSCO to minimize the communication overhead of token dispatching.

### FUSCO Integration Logic
The system integrates FUSCO for optimized MoE all-to-all communication, which is particularly critical for models like Qwen3-MoE [tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml:1-1](). The `MegatronActor` configures MoE parameters such as `expert_model_parallel_size` and `expert_tensor_parallel_size` during worker initialization [rlinf/workers/actor/megatron_actor_worker.py:105-106]().

### 2D Dispatch and Token Routing
FUSCO optimizes token routing by using a 2D dispatch strategy. The `token_dispatcher.py` handles the underlying logic for routing tokens to appropriate experts across the distributed fabric [rlinf/hybrid_engines/megatron/token_dispatcher.py:1-1]().

For details, see [FUSCO MoE Optimization](#9.2).

**Sources:** [rlinf/workers/actor/megatron_actor_worker.py:105-106](), [rlinf/hybrid_engines/megatron/token_dispatcher.py:1-1](), [tests/e2e_tests/reasoning/qwen3-moe-2.5b-collocated-mg-sgl-ep-fusco-test.yaml:1-1]()

---

## Hybrid Execution and Dynamic Scheduling

RLinf features a hybrid execution engine that dynamically allocates GPU resources between environment interaction and model training.

### Resource Allocation Flow
The system supports complex placement modes for distributed components. This allows actors and rollouts to share or split nodes based on resource availability. The `PlacementMode` (e.g., `COLLOCATED`, `DISAGGREGATED`) determines how workers are mapped to hardware [rlinf/workers/actor/megatron_actor_worker.py:32-36]().

### System-to-Code Mapping: Hybrid Execution
The following diagram maps high-level hybrid execution concepts to specific code entities within the `rlinf` codebase.

| Diagram: Hybrid Execution Mapping |
| :--- |
| ```mermaid
graph TD
    subgraph "HybridExecutionEngine"
        SCHED["DynamicScheduler"]
        MODEL_MGR["ModelManager"]
        RUNNER["HybridRunner"]
    end

    subgraph "CodeEntities"
        DYN_SCHED["rlinf.scheduler.dynamic_scheduler.utils.get_scheduler_channel"]
        FSDP_MGR["rlinf.hybrid_engines.fsdp.fsdp_model_manager.FSDPModelManager"]
        AGENT_RUNNER["rlinf.runners.agentlightning_runner.AgentLightningRunner"]
    end

    SCHED --- DYN_SCHED
    MODEL_MGR --- FSDP_MGR
    RUNNER --- AGENT_RUNNER

    AGENT_RUNNER -- "RequestsResources" --> DYN_SCHED
    FSDP_MGR -- "ManagedBy" --> AGENT_RUNNER
``` |

For details, see [Hybrid Execution and Dynamic Scheduling](#9.3).

**Sources:** [rlinf/scheduler/dynamic_scheduler/utils.py:43-48](), [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py:53-106](), [rlinf/runners/agentlightning_runner.py:1-1]()

---

## Memory Optimization Techniques

Expert users can leverage several techniques to train large models on memory-constrained hardware.

### Gradient Checkpointing and CPU Offloading
RLinf supports gradient checkpointing and CPU offloading for weights and optimizer states.

*   **Weight Resharding:** `MegatronCoreWeightReshard` manages weight transformations between different parallelism configurations to optimize memory usage during initialization [rlinf/workers/actor/megatron_actor_worker.py:109-109]().
*   **Offloading in Backends:** `MegatronWorker` tracks offloading status for weights, gradients, and optimizer states [rlinf/workers/megatron_worker.py:149-151](). `FSDPModelManager` similarly manages `is_weight_offloaded` and `is_optimizer_offloaded` [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py:105-106]().
*   **Dynamic Batching:** The system uses `split_dynamic_batch_size` and `BatchResizingIterator` to handle variable sequence lengths and prevent OOM [rlinf/workers/megatron_worker.py:34-55]().

### DP Load Balancing
For reasoning tasks with highly variable response lengths, `MAMegatronActor` utilizes `enable_dp_load_balance` to ensure data parallel ranks receive a balanced amount of computation [rlinf/workers/actor/ma_megatron_actor_worker.py:77-79]().

### System-to-Code Mapping: Memory Optimization
This diagram bridges memory optimization strategies to the underlying implementation classes.

| Diagram: Memory Optimization Architecture |
| :--- |
| ```mermaid
graph LR
    subgraph "OptimizationStrategies"
        RESHARD["WeightResharding"]
        OFFLOAD["CPUOffloading"]
        LOAD_BAL["DPLoadBalancing"]
    end

    subgraph "ImplementationEntities"
        RESHARD_UTIL["rlinf.utils.resharding.mcore_weight_reshard.MegatronCoreWeightReshard"]
        FSDP_MGR["rlinf.hybrid_engines.fsdp.fsdp_model_manager.FSDPModelManager"]
        MA_ACTOR["rlinf.workers.actor.ma_megatron_actor_worker.MAMegatronActor"]
    end

    RESHARD --- RESHARD_UTIL
    OFFLOAD --- FSDP_MGR
    LOAD_BAL --- MA_ACTOR

    MA_ACTOR -- "Uses" --> RESHARD_UTIL
    FSDP_MGR -- "Implements" --> OFFLOAD
``` |

For details, see [Memory Optimization Techniques](#9.4).

**Sources:** [rlinf/workers/actor/megatron_actor_worker.py:109-109](), [rlinf/workers/megatron_worker.py:34-151](), [rlinf/hybrid_engines/fsdp/fsdp_model_manager.py:105-106](), [rlinf/workers/actor/ma_megatron_actor_worker.py:77-79]()

---

