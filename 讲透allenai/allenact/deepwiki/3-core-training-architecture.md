<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/allenact · page 3 Core Training Architecture · fetched 2026-10-26 -->

# Core Training Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [allenact/algorithms/onpolicy_sync/engine.py](allenact/algorithms/onpolicy_sync/engine.py)
- [allenact/algorithms/onpolicy_sync/runner.py](allenact/algorithms/onpolicy_sync/runner.py)
- [allenact/algorithms/onpolicy_sync/storage.py](allenact/algorithms/onpolicy_sync/storage.py)
- [allenact/algorithms/onpolicy_sync/vector_sampled_tasks.py](allenact/algorithms/onpolicy_sync/vector_sampled_tasks.py)
- [allenact/base_abstractions/callbacks.py](allenact/base_abstractions/callbacks.py)
- [allenact/base_abstractions/preprocessor.py](allenact/base_abstractions/preprocessor.py)
- [allenact/base_abstractions/task.py](allenact/base_abstractions/task.py)
- [allenact/embodiedai/mapping/mapping_utils/map_builders.py](allenact/embodiedai/mapping/mapping_utils/map_builders.py)
- [allenact/embodiedai/mapping/mapping_utils/point_cloud_utils.py](allenact/embodiedai/mapping/mapping_utils/point_cloud_utils.py)
- [allenact/main.py](allenact/main.py)
- [allenact/utils/experiment_utils.py](allenact/utils/experiment_utils.py)
- [allenact/utils/misc_utils.py](allenact/utils/misc_utils.py)
- [allenact_plugins/ithor_plugin/ithor_sensors.py](allenact_plugins/ithor_plugin/ithor_sensors.py)
- [allenact_plugins/robothor_plugin/robothor_sensors.py](allenact_plugins/robothor_plugin/robothor_sensors.py)

</details>



This document describes AllenAct's core training system, which is the framework's most critical component responsible for orchestrating reinforcement learning training, validation, and testing processes. The training architecture handles distributed execution, experience collection, model updates, and checkpoint management across multiple environments and workers.

For information about experiment configuration and setup, see [Experiment Configuration](#4). For details about specific simulation environments, see [Simulation Environments](#5). For model architecture details, see [Models and Algorithms](#6).

## System Overview

AllenAct's training architecture is built around a hierarchical system where `OnPolicyRunner` serves as the main orchestrator, spawning and managing multiple `OnPolicyRLEngine` worker processes. Each worker specializes in either training (`OnPolicyTrainer`) or inference (`OnPolicyInference`) tasks.

```mermaid
graph TB
    subgraph "Main Process"
        Main["main.py"]
        Runner["OnPolicyRunner"]
        ResultsQ["results_queue"]
        CheckpointsQ["checkpoints_queue"]
    end
    
    subgraph "Training Workers"
        Trainer1["OnPolicyTrainer Worker 0"]
        Trainer2["OnPolicyTrainer Worker 1"]
        TrainerN["OnPolicyTrainer Worker N"]
    end
    
    subgraph "Validation Worker"
        Validator["OnPolicyInference Worker"]
    end
    
    subgraph "Distributed Communication"
        TCPStore["TCPStore"]
        DistComm["Distributed Backend (NCCL/Gloo)"]
    end
    
    Main --> Runner
    Runner --> ResultsQ
    Runner --> CheckpointsQ
    Runner -->|"spawn processes"| Trainer1
    Runner -->|"spawn processes"| Trainer2
    Runner -->|"spawn processes"| TrainerN
    Runner -->|"spawn process"| Validator
    
    Trainer1 --> TCPStore
    Trainer2 --> TCPStore
    TrainerN --> TCPStore
    
    Trainer1 -->|"metrics"| ResultsQ
    Trainer2 -->|"metrics"| ResultsQ
    TrainerN -->|"metrics"| ResultsQ
    Validator -->|"metrics"| ResultsQ
    
    Validator <-->|"checkpoints"| CheckpointsQ
    
    TCPStore --> DistComm
```

**Training System Architecture Overview**

Sources: [allenact/algorithms/onpolicy_sync/runner.py:80-141](), [allenact/algorithms/onpolicy_sync/engine.py:93-101](), [allenact/main.py:463-525]()

## OnPolicyRunner - Training Orchestration

The `OnPolicyRunner` class serves as the primary controller for the entire training system. It handles process spawning, resource management, and coordination between training and validation workers.

### Runner Initialization and Process Management

```mermaid
graph TD
    Config["ExperimentConfig"]
    Runner["OnPolicyRunner"]
    
    subgraph "Initialization"
        InitCtx["init_context()"]
        WorkerDevices["worker_devices()"]
        LocalWorkerIds["local_worker_ids()"]
        GetPort["get_port()"]
    end
    
    subgraph "Process Spawning"
        TrainLoop["train_loop()"]
        ValidLoop["valid_loop()"]
        TestLoop["test_loop()"]
    end
    
    subgraph "Process Management"
        Queues["MP Queues"]
        ProcessDict["processes Dict"]
        LogAndClose["log_and_close()"]
    end
    
    Config --> Runner
    Runner --> InitCtx
    Runner --> WorkerDevices
    Runner --> LocalWorkerIds
    Runner --> GetPort
    
    Runner --> TrainLoop
    Runner --> ValidLoop
    Runner --> TestLoop
    
    TrainLoop --> Queues
    ValidLoop --> Queues
    TestLoop --> Queues
    
    Queues --> ProcessDict
    ProcessDict --> LogAndClose
```

**OnPolicyRunner Process Management Flow**

The `OnPolicyRunner` manages the following key responsibilities:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **Process Spawning** | Creates worker processes for training/validation | `start_train()`, `start_test()` methods |
| **Queue Management** | Handles inter-process communication | `mp.Queue` for results and checkpoints |
| **Resource Allocation** | Distributes GPU/CPU devices across workers | `worker_devices()`, `local_worker_ids()` |
| **Distributed Coordination** | Sets up TCP communication for multi-machine training | `get_port()`, distributed IP/port management |

Sources: [allenact/algorithms/onpolicy_sync/runner.py:495-669](), [allenact/algorithms/onpolicy_sync/runner.py:671-769]()

### Training and Validation Process Coordination

```mermaid
sequenceDiagram
    participant Main as Main Process
    participant Runner as OnPolicyRunner
    participant Trainer as OnPolicyTrainer
    participant Validator as OnPolicyInference
    participant Queue as Message Queues
    
    Main->>Runner: start_train()
    Runner->>Runner: spawn training processes
    Runner->>Trainer: train_loop()
    Runner->>Validator: valid_loop()
    
    loop Training Cycle
        Trainer->>Queue: training metrics
        Trainer->>Queue: checkpoint
        Queue->>Validator: checkpoint for validation
        Validator->>Queue: validation metrics
    end
    
    Queue->>Runner: collect results
    Runner->>Main: aggregated metrics
```

**Training and Validation Coordination Sequence**

Sources: [allenact/algorithms/onpolicy_sync/runner.py:404-429](), [allenact/algorithms/onpolicy_sync/runner.py:432-442](), [allenact/algorithms/onpolicy_sync/runner.py:445-453]()

## OnPolicyRLEngine Architecture

The `OnPolicyRLEngine` serves as the base class for all training and inference workers. It provides the core RL functionality and is specialized into `OnPolicyTrainer` and `OnPolicyInference` subclasses.

### Engine Class Hierarchy

```mermaid
graph TB
    Engine["OnPolicyRLEngine"]
    Trainer["OnPolicyTrainer"]
    Inference["OnPolicyInference"]
    
    subgraph "Core Components"
        ActorCritic["ActorCriticModel"]
        VectorTasks["VectorSampledTasks"]
        Storage["RolloutStorage"]
        Pipeline["TrainingPipeline"]
    end
    
    subgraph "Training Specific"
        Optimizer["optimizer"]
        LRScheduler["lr_scheduler"]
        Updates["compute_losses_track_them_and_backprop()"]
    end
    
    subgraph "Distributed Training"
        TCPStore["TCPStore"]
        DistBackend["Distributed Backend"]
        AllReduce["distributed_weighted_sum()"]
    end
    
    Engine --> Trainer
    Engine --> Inference
    
    Engine --> ActorCritic
    Engine --> VectorTasks
    Engine --> Storage
    Engine --> Pipeline
    
    Trainer --> Optimizer
    Trainer --> LRScheduler
    Trainer --> Updates
    
    Engine --> TCPStore
    TCPStore --> DistBackend
    Engine --> AllReduce
```

**OnPolicyRLEngine Class Architecture**

### Core Engine Functionality

The `OnPolicyRLEngine` implements several critical systems:

| System | Purpose | Key Methods |
|--------|---------|-------------|
| **Experience Collection** | Manages interaction with environments | `collect_step_across_all_task_samplers()` |
| **Model Management** | Handles neural network operations | `act()`, model loading/saving |
| **Storage Integration** | Coordinates with experience storage | `initialize_storage_and_viz()` |
| **Distributed Communication** | Handles multi-worker coordination | `distributed_weighted_sum()`, `distributed_reduce()` |

Sources: [allenact/algorithms/onpolicy_sync/engine.py:103-281](), [allenact/algorithms/onpolicy_sync/engine.py:532-547]()

### Training vs Inference Specialization

```mermaid
graph LR
    subgraph "OnPolicyTrainer"
        TrainMethod["train()"]
        BackpropStep["backprop_step()"]
        LossComputation["compute_losses_track_them_and_backprop()"]
        OptimStep["optimizer.step()"]
    end
    
    subgraph "OnPolicyInference"
        ProcessCheckpoints["process_checkpoints()"]
        RunEval["run_eval()"]
        EvalLoop["evaluation loop"]
    end
    
    subgraph "Shared Base"
        CollectStep["collect_step_across_all_task_samplers()"]
        AggregateLogs["aggregate_and_send_logging_package()"]
        ModelAct["act()"]
    end
    
    TrainMethod --> CollectStep
    ProcessCheckpoints --> CollectStep
    CollectStep --> AggregateLogs
    CollectStep --> ModelAct
```

**Training vs Inference Specialization**

Sources: [allenact/algorithms/onpolicy_sync/engine.py:823-966]()

## Experience Collection and Storage

The training system uses `VectorSampledTasks` to manage multiple environment instances and `RolloutStorage` to accumulate experience for training updates.

### VectorSampledTasks Architecture

```mermaid
graph TB
    subgraph "Main Process"
        VST["VectorSampledTasks"]
        ConnectionReads["connection_read_fns"]
        ConnectionWrites["connection_write_fns"]
    end
    
    subgraph "Worker Processes"
        Worker1["Worker Process 1"]
        Worker2["Worker Process 2"]
        WorkerN["Worker Process N"]
    end
    
    subgraph "SingleProcess Components"
        SPVST["SingleProcessVectorSampledTasks"]
        TaskSamplers["TaskSampler instances"]
        Tasks["Task instances"]
    end
    
    VST --> ConnectionReads
    VST --> ConnectionWrites
    
    ConnectionWrites -->|"commands"| Worker1
    ConnectionWrites -->|"commands"| Worker2
    ConnectionWrites -->|"commands"| WorkerN
    
    Worker1 -->|"results"| ConnectionReads
    Worker2 -->|"results"| ConnectionReads
    WorkerN -->|"results"| ConnectionReads
    
    Worker1 --> SPVST
    Worker2 --> SPVST
    WorkerN --> SPVST
    
    SPVST --> TaskSamplers
    TaskSamplers --> Tasks
```

**VectorSampledTasks Multiprocess Architecture**

The `VectorSampledTasks` system handles:

- **Process Management**: Spawns worker processes using `_spawn_workers()`
- **Command Distribution**: Sends actions via `step()`, `call_at()`, etc.
- **Result Aggregation**: Collects observations and rewards from all workers
- **Task Lifecycle**: Manages task completion and resampling via `auto_resample_when_done`

Sources: [allenact/algorithms/onpolicy_sync/vector_sampled_tasks.py:116-259](), [allenact/algorithms/onpolicy_sync/vector_sampled_tasks.py:329-422]()

### RolloutStorage and Experience Management

```mermaid
graph TD
    subgraph "Storage Components"
        Storage["RolloutStorage"]
        Observations["observations"]
        Actions["actions"]
        Rewards["rewards"]
        Values["value_preds"]
        Masks["masks"]
        Memory["memory_first_last"]
    end
    
    subgraph "Update Process"
        BeforeUpdates["before_updates()"]
        ComputeReturns["compute_returns()"]
        ComputeAdvantages["compute advantages"]
        BatchGenerator["batched_experience_generator()"]
        AfterUpdates["after_updates()"]
    end
    
    subgraph "Data Flow"
        Add["add()"]
        SamplerSelect["sampler_select()"]
        AgentInput["agent_input_for_next_step()"]
    end
    
    Storage --> Observations
    Storage --> Actions
    Storage --> Rewards
    Storage --> Values
    Storage --> Masks
    Storage --> Memory
    
    Add --> Storage
    Storage --> SamplerSelect
    Storage --> AgentInput
    
    Storage --> BeforeUpdates
    BeforeUpdates --> ComputeReturns
    BeforeUpdates --> ComputeAdvantages
    Storage --> BatchGenerator
    Storage --> AfterUpdates
```

**RolloutStorage Experience Management**

The `RolloutStorage` provides:

| Function | Purpose | Key Features |
|----------|---------|-------------|
| **Experience Accumulation** | Stores agent trajectories | Dynamic storage sizing, multi-sampler support |
| **Advantage Computation** | Calculates GAE advantages | Configurable γ and λ parameters |
| **Batch Generation** | Creates mini-batches for training | Supports both mini-batch and streaming modes |
| **Memory Management** | Handles recurrent model states | First/last memory storage for RNNs |

Sources: [allenact/algorithms/onpolicy_sync/storage.py:130-567](), [allenact/algorithms/onpolicy_sync/storage.py:438-501]()

## Distributed Training System

AllenAct supports distributed training across multiple machines and GPUs using PyTorch's distributed backend with `TCPStore` for coordination.

### Distributed Communication Architecture

```mermaid
graph TB
    subgraph "Machine 0 (Master)"
        Master["OnPolicyRunner machine_id=0"]
        MasterWorkers["Training Workers 0-N"]
        TCPServer["TCPStore Server"]
    end
    
    subgraph "Machine 1"
        Worker1["OnPolicyRunner machine_id=1"]
        M1Workers["Training Workers"]
        TCPClient1["TCPStore Client"]
    end
    
    subgraph "Machine K"
        WorkerK["OnPolicyRunner machine_id=K"]
        MKWorkers["Training Workers"]
        TCPClientK["TCPStore Client"]
    end
    
    subgraph "Communication Layer"
        DistBackend["PyTorch Distributed Backend"]
        AllReduce["All-Reduce Operations"]
        Barrier["Barrier Synchronization"]
    end
    
    Master --> TCPServer
    Worker1 --> TCPClient1
    WorkerK --> TCPClientK
    
    TCPServer <--> TCPClient1
    TCPServer <--> TCPClientK
    
    MasterWorkers --> DistBackend
    M1Workers --> DistBackend
    MKWorkers --> DistBackend
    
    DistBackend --> AllReduce
    DistBackend --> Barrier
```

**Distributed Training Communication Architecture**

### Distributed Training Coordination

The distributed training system coordinates through several mechanisms:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **TCPStore** | Shared key-value store for coordination | `torch.distributed.TCPStore` with master/worker setup |
| **Process Groups** | Grouped communication for workers | NCCL for GPU, Gloo for CPU/testing |
| **All-Reduce** | Gradient synchronization | `distributed_weighted_sum()`, `distributed_reduce()` |
| **Barriers** | Synchronization points | Used before loss computation and updates |

```mermaid
sequenceDiagram
    participant M as Machine 0 (Master)
    participant W1 as Machine 1 Worker
    participant W2 as Machine 2 Worker
    participant Store as TCPStore
    
    M->>Store: Initialize TCPStore server
    W1->>Store: Connect as client
    W2->>Store: Connect as client
    
    loop Training Step
        M->>Store: Barrier sync
        W1->>Store: Barrier sync  
        W2->>Store: Barrier sync
        
        Note over M,W2: Collect experiences in parallel
        
        M->>Store: All-reduce gradients
        W1->>Store: All-reduce gradients
        W2->>Store: All-reduce gradients
        
        Note over M,W2: Apply synchronized updates
    end
```

**Distributed Training Synchronization Sequence**

Sources: [allenact/algorithms/onpolicy_sync/engine.py:242-274](), [allenact/algorithms/onpolicy_sync/engine.py:776-802]()

## Training Pipeline and Configuration

The training system is configured through `TrainingPipeline` and `PipelineStage` objects that define losses, learning schedules, and training progression.

### Pipeline Architecture

```mermaid
graph TB
    subgraph "TrainingPipeline"
        Pipeline["TrainingPipeline"]
        Stages["pipeline_stages[]"]
        Losses["named_losses Dict"]
        Storage["storage_uuid_to_storage"]
    end
    
    subgraph "PipelineStage"
        Stage["PipelineStage"]
        LossNames["loss_names"]
        MaxSteps["max_stage_steps"]
        TrainingSettings["training_settings"]
        StageComponents["stage_components"]
    end
    
    subgraph "StageComponent"
        Component["StageComponent"]
        ComponentUUID["uuid"]
        ComponentLosses["loss_names"]
        ComponentSettings["training_settings"]
    end
    
    subgraph "Training Execution"
        CurrentStage["current_stage"]
        StepsTaken["steps_taken_in_stage"]
        EarlyStop["early_stopping_criterion"]
    end
    
    Pipeline --> Stages
    Pipeline --> Losses
    Pipeline --> Storage
    
    Stages --> Stage
    Stage --> LossNames
    Stage --> MaxSteps
    Stage --> TrainingSettings
    Stage --> StageComponents
    
    StageComponents --> Component
    Component --> ComponentUUID
    Component --> ComponentLosses
    Component --> ComponentSettings
    
    Pipeline --> CurrentStage
    Stage --> StepsTaken
    Stage --> EarlyStop
```

**Training Pipeline Configuration Architecture**

### Pipeline Execution Flow

The training pipeline executes in stages with configurable loss functions and training settings:

| Stage Element | Purpose | Configuration |
|---------------|---------|---------------|
| **Loss Functions** | Define training objectives | PPO, A2C, auxiliary losses |
| **Training Settings** | Control update parameters | Learning rate, batch size, update repeats |
| **Early Stopping** | Terminate stages early | Custom criteria based on metrics |
| **Stage Components** | Custom training components | Override settings per component |

Sources: [allenact/utils/experiment_utils.py:612-814](), [allenact/utils/experiment_utils.py:469-494](), [allenact/utils/experiment_utils.py:570-610]()

## Process Lifecycle and Error Handling

The training system includes robust process management with graceful shutdown and error recovery mechanisms.

### Process Management and Cleanup

```mermaid
graph TD
    subgraph "Process Initialization"
        InitProcess["init_process()"]
        SignalHandlers["SIGTERM/SIGINT handlers"]
        ProcessTitle["setproctitle()"]
    end
    
    subgraph "Normal Operation"
        TrainingLoop["Training/Validation Loop"]
        QueueComm["Queue Communication"]
        ResultsCollection["Results Collection"]
    end
    
    subgraph "Error Handling"
        ExceptionCatch["Exception Handling"]
        RestartLogic["try_restart_after_task_error"]
        ErrorLogging["Error Logging"]
    end
    
    subgraph "Cleanup"
        GracefulClose["Graceful Shutdown"]
        ResourceCleanup["Resource Cleanup"]
        ProcessExit["Process Exit"]
    end
    
    InitProcess --> SignalHandlers
    InitProcess --> ProcessTitle
    SignalHandlers --> TrainingLoop
    
    TrainingLoop --> QueueComm
    QueueComm --> ResultsCollection
    
    TrainingLoop --> ExceptionCatch
    ExceptionCatch --> RestartLogic
    ExceptionCatch --> ErrorLogging
    
    SignalHandlers --> GracefulClose
    GracefulClose --> ResourceCleanup
    ResourceCleanup --> ProcessExit
```

**Process Lifecycle and Error Handling**

The system provides comprehensive process management including:

- **Signal Handling**: Graceful shutdown on SIGTERM/SIGINT
- **Error Recovery**: Optional restart after task errors
- **Resource Cleanup**: Proper cleanup of multiprocessing resources
- **Logging Integration**: Comprehensive error logging and debugging support

Sources: [allenact/algorithms/onpolicy_sync/runner.py:342-377](), [allenact/algorithms/onpolicy_sync/runner.py:379-392](), [allenact/algorithms/onpolicy_sync/engine.py:125-157]()

---

