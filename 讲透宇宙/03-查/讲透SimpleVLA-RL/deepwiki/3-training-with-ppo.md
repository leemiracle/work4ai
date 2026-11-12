<!-- source: DeepWiki mcp.deepwiki.com · repo PRIME-RL/SimpleVLA-RL · page 3 Training with PPO · fetched 2026-10-30 -->

# veRL Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [verl/trainer/config/ppo_trainer.yaml](verl/trainer/config/ppo_trainer.yaml)
- [verl/trainer/ppo/ray_trainer.py](verl/trainer/ppo/ray_trainer.py)

</details>



The veRL framework provides the core infrastructure for distributed reinforcement learning training in SimpleVLA-RL. It handles data serialization, distributed function execution, and worker coordination across multi-GPU and multi-node environments. The framework abstracts the complexity of distributed computing while maintaining high performance for large-scale VLA model training.

For information about the specific model architectures being trained, see [Model Architecture](#2). For details about training orchestration and the PPO implementation, see [Training Pipeline](#1.2).

## Architecture Overview

The veRL framework consists of three main subsystems that work together to enable distributed RL training:

### Core Framework Components

```mermaid
graph TB
    subgraph "veRL Framework Core"
        DataProto["DataProto<br/>TensorDict + Metadata"]
        DataProtoFuture["DataProtoFuture<br/>Async Data Handling"]
        RegisterDecorator["@register Decorator<br/>Distributed Function Dispatch"]
    end
    
    subgraph "Dispatch Modes"
        OneToAll["ONE_TO_ALL<br/>Broadcast Pattern"]
        AllToAll["ALL_TO_ALL<br/>Direct Mapping"]
        MegatronCompute["MEGATRON_COMPUTE<br/>DP-Aware Distribution"]
        DPCompute["DP_COMPUTE<br/>Data Parallel Split"]
    end
    
    subgraph "Execution Patterns"
        ExecuteAll["Execute.ALL<br/>All Workers"]
        ExecuteRankZero["Execute.RANK_ZERO<br/>Single Worker"]
    end
    
    subgraph "Data Flow"
        Dispatch["dispatch_fn()<br/>Split Input Data"]
        Collect["collect_fn()<br/>Gather Output Data"]
        MaterializeFutures["_materialize_futures()<br/>Resolve Async Data"]
    end
    
    RegisterDecorator --> OneToAll
    RegisterDecorator --> AllToAll
    RegisterDecorator --> MegatronCompute
    RegisterDecorator --> DPCompute
    
    RegisterDecorator --> ExecuteAll
    RegisterDecorator --> ExecuteRankZero
    
    DataProto --> Dispatch
    DataProtoFuture --> MaterializeFutures
    MaterializeFutures --> DataProto
    Dispatch --> Collect
    Collect --> DataProto
```

Sources: [verl/__init__.py:22-27](), [verl/protocol.py:98-109](), [verl/single_controller/base/decorator.py:25-38](), [verl/single_controller/base/decorator.py:394-410]()

## Data Protocol System

The `DataProto` class serves as the standardized data container for all distributed operations. It combines PyTorch tensors in a `TensorDict` with non-tensor metadata, enabling efficient serialization and transfer between workers.

### DataProto Class Hierarchy

```mermaid
graph TB
    subgraph "Data Protocol Classes"
        DataProto["DataProto<br/>batch: TensorDict<br/>non_tensor_batch: Dict<br/>meta_info: Dict"]
        DataProtoItem["DataProtoItem<br/>Single Batch Item"]
        DataProtoFuture["DataProtoFuture<br/>collect_fn: Callable<br/>futures: List[ObjectRef]<br/>dispatch_fn: Callable"]
    end
    
    subgraph "Core Operations"
        FromDict["from_dict()<br/>Create from tensors"]
        FromSingleDict["from_single_dict()<br/>Mixed tensor/numpy"]
        ToDevice["to(device)<br/>Move tensors"]
        Chunk["chunk(chunks)<br/>Split along dim=0"]
        Concat["concat(data_list)<br/>Merge DataProtos"]
    end
    
    subgraph "TensorDict Integration"
        TensorDict["TensorDict<br/>PyTorch TensorDict"]
        BatchOps["Batch Operations<br/>slice(), select(), union()"]
        Iteration["make_iterator()<br/>DataLoader Integration"]
    end
    
    DataProto --> DataProtoItem
    DataProto --> FromDict
    DataProto --> FromSingleDict
    DataProto --> ToDevice
    DataProto --> Chunk
    DataProto --> Concat
    
    DataProto --> TensorDict
    TensorDict --> BatchOps
    DataProto --> Iteration
    
    DataProtoFuture --> DataProto
```

Sources: [verl/protocol.py:90-109](), [verl/protocol.py:173-222](), [verl/protocol.py:458-503]()

The `DataProtoFuture` enables asynchronous data operations by containing Ray object references (`ray.ObjectRef`) instead of actual data, allowing for non-blocking distributed execution patterns.

For detailed information about the data protocol implementation, see [Data Protocol](#3.1).

## Distributed Execution System

The `@register` decorator provides a unified interface for distributed function execution. Functions decorated with `@register` are automatically dispatched across workers according to specified patterns.

### Register Decorator Dispatch Patterns

```mermaid
graph LR
    subgraph "Function Decoration"
        UserFunction["user_function()"]
        RegisterDecorator["@register(<br/>dispatch_mode,<br/>execute_mode,<br/>blocking<br/>)"]
        DecoratedFunction["Distributed Function"]
    end
    
    subgraph "Dispatch Functions"
        DispatchOneToAll["dispatch_one_to_all()<br/>Broadcast to all workers"]
        DispatchMegatronCompute["dispatch_megatron_compute()<br/>DP-aware distribution"]
        DispatchDPCompute["dispatch_dp_compute_data_proto()<br/>Split DataProto by world_size"]
    end
    
    subgraph "Collect Functions"
        CollectAllToAll["collect_all_to_all()<br/>Return as-is"]
        CollectMegatronCompute["collect_megatron_compute()<br/>TP=0, PP=last only"]
        CollectDPCompute["collect_dp_compute_data_proto()<br/>Concat DataProtos"]
    end
    
    UserFunction --> RegisterDecorator
    RegisterDecorator --> DecoratedFunction
    
    DecoratedFunction --> DispatchOneToAll
    DecoratedFunction --> DispatchMegatronCompute
    DecoratedFunction --> DispatchDPCompute
    
    DispatchOneToAll --> CollectAllToAll
    DispatchMegatronCompute --> CollectMegatronCompute
    DispatchDPCompute --> CollectDPCompute
```

Sources: [verl/single_controller/base/decorator.py:60-67](), [verl/single_controller/base/decorator.py:118-126](), [verl/single_controller/base/decorator.py:272-276](), [verl/single_controller/base/decorator.py:300-347]()

The framework provides predefined dispatch modes optimized for different parallelization strategies:

| Dispatch Mode | Purpose | Data Distribution | Collection Pattern |
|---------------|---------|-------------------|-------------------|
| `ONE_TO_ALL` | Broadcast | Same data to all workers | Return all outputs |
| `MEGATRON_COMPUTE` | Megatron integration | DP-aware, same data per DP rank | Only TP=0, PP=last |
| `DP_COMPUTE_PROTO` | Data parallel | Split `DataProto` by world size | Concatenate results |
| `MEGATRON_PP_AS_DP` | Pipeline as data parallel | PP ranks treated as DP | PP=0 only |

For complete details about the distributed execution mechanisms, see [Distributed Execution](#3.2).

## Integration with Training Pipeline

The veRL framework integrates seamlessly with the overall training system through standardized interfaces:

### Training Integration Points

```mermaid
graph TB
    subgraph "Training Components"
        PPOTrainer["PPO Trainer<br/>verl.trainer.main_ppo"]
        ModelWorkers["Model Workers<br/>Parallel Llama Models"]
        Environment["Environment<br/>LIBERO Tasks"]
    end
    
    subgraph "veRL Framework"
        DataProtoFlow["DataProto Flow<br/>Rollout Data"]
        RegisteredFunctions["@register Functions<br/>Model Inference<br/>Environment Steps"]
        WorkerCoordination["Worker Coordination<br/>Resource Management"]
    end
    
    subgraph "Data Flow Patterns"
        RolloutCollection["Rollout Collection<br/>Environment → DataProto"]
        ModelInference["Model Inference<br/>DataProto → Predictions"]
        PolicyUpdate["Policy Update<br/>Gradients → Model"]
    end
    
    PPOTrainer --> DataProtoFlow
    PPOTrainer --> RegisteredFunctions
    
    DataProtoFlow --> RolloutCollection
    DataProtoFlow --> ModelInference
    DataProtoFlow --> PolicyUpdate
    
    RegisteredFunctions --> ModelWorkers
    RegisteredFunctions --> Environment
    
    WorkerCoordination --> ModelWorkers
```

Sources: [verl/__init__.py:22](), [verl/protocol.py:98-109](), [verl/single_controller/base/decorator.py:394-410]()

The framework's `DataProto` protocol ensures consistent data handling across all training components, while the `@register` decorator enables transparent distribution of compute-intensive operations like model inference and environment simulation.

For information about worker management and resource allocation, see [Worker Management](#3.3). For details about how these components integrate with the model architecture, see [Megatron Integration](#2.3).

---

