<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/robustnav · page 3 Training and Evaluation Engine · fetched 2026-10-26 -->

# Training and Evaluation Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [allenact/algorithms/onpolicy_sync/engine.py](allenact/algorithms/onpolicy_sync/engine.py)
- [allenact/algorithms/onpolicy_sync/runner.py](allenact/algorithms/onpolicy_sync/runner.py)

</details>



This document covers the core training and evaluation engine that orchestrates the reinforcement learning pipeline in RobustNav. The engine manages multi-process execution, coordinates data collection and model updates, handles checkpointing, and aggregates metrics across distributed workers.

For information about the data management systems used during training, see [Data Management](#3.1). For details about agent architectures and policy implementations, see [Agent Architecture](#4). For loss function implementations, see [Loss Functions](#5).

## Purpose and Scope

The Training and Evaluation Engine serves as the central orchestration system that:

- Manages multi-process execution of training and evaluation workers
- Coordinates communication between processes via message queues
- Handles model checkpointing and state management
- Aggregates metrics and manages logging across distributed processes
- Orchestrates the complete training pipeline from data collection through model updates
- Supports both on-policy training and evaluation modes with corruption testing

## Architecture Overview

The engine follows a multi-process architecture with clear separation between training, validation, and testing phases. The system uses message queues for inter-process communication and supports distributed execution across multiple devices.

### Core Engine Classes

```mermaid
classDiagram
    class OnPolicyRLEngine {
        +ExperimentConfig config
        +VectorSampledTasks vector_tasks
        +ActorCriticModel actor_critic
        +mp.Queue results_queue
        +mp.Queue checkpoints_queue
        +collect_rollout_step()
        +initialize_rollouts()
        +act()
        +checkpoint_load()
        +close()
    }
    
    class OnPolicyTrainer {
        +Optimizer optimizer
        +LRScheduler lr_scheduler
        +TrainingPipeline training_pipeline
        +Dict tracking_info
        +train()
        +run_pipeline()
        +update()
        +backprop_step()
        +checkpoint_save()
    }
    
    class OnPolicyInference {
        +run_eval()
        +process_checkpoints()
        +skip_to_latest()
    }
    
    class OnPolicyRunner {
        +Dict queues
        +Dict processes
        +ExperimentConfig config
        +start_train()
        +start_test()
        +log()
        +process_train_packages()
        +process_eval_package()
    }
    
    OnPolicyRLEngine <|-- OnPolicyTrainer
    OnPolicyRLEngine <|-- OnPolicyInference
    OnPolicyRunner --> OnPolicyTrainer : "creates"
    OnPolicyRunner --> OnPolicyInference : "creates"
```

Sources: [allenact/algorithms/onpolicy_sync/engine.py:69-624](), [allenact/algorithms/onpolicy_sync/engine.py:625-1373](), [allenact/algorithms/onpolicy_sync/engine.py:1375-1650](), [allenact/algorithms/onpolicy_sync/runner.py:50-994]()

## Multi-Process Execution Model

The engine uses a master-worker architecture where `OnPolicyRunner` spawns and manages multiple worker processes for training and evaluation.

### Process Communication Architecture

```mermaid
graph TB
    subgraph "Main Process"
        Runner["OnPolicyRunner"]
        ResultsQueue["results_queue"]
        CheckpointsQueue["checkpoints_queue"]
        Logger["Logging & Metrics"]
    end
    
    subgraph "Training Workers"
        T1["OnPolicyTrainer Process 0"]
        T2["OnPolicyTrainer Process 1"] 
        TN["OnPolicyTrainer Process N"]
    end
    
    subgraph "Evaluation Workers"
        V1["OnPolicyInference (valid)"]
        E1["OnPolicyInference (test) 0"]
        E2["OnPolicyInference (test) 1"]
    end
    
    subgraph "Task Samplers"
        VT1["VectorSampledTasks T1"]
        VT2["VectorSampledTasks T2"]
        VE1["VectorSampledTasks E1"]
    end
    
    Runner --> T1
    Runner --> T2
    Runner --> TN
    Runner --> V1
    Runner --> E1
    Runner --> E2
    
    T1 --> VT1
    T2 --> VT2
    E1 --> VE1
    
    T1 --> ResultsQueue
    T2 --> ResultsQueue
    TN --> ResultsQueue
    V1 --> ResultsQueue
    E1 --> ResultsQueue
    E2 --> ResultsQueue
    
    Runner --> CheckpointsQueue
    CheckpointsQueue --> V1
    CheckpointsQueue --> E1
    CheckpointsQueue --> E2
    
    ResultsQueue --> Logger
```

Sources: [allenact/algorithms/onpolicy_sync/runner.py:95-103](), [allenact/algorithms/onpolicy_sync/runner.py:242-331](), [allenact/algorithms/onpolicy_sync/runner.py:332-409](), [allenact/algorithms/onpolicy_sync/engine.py:83-86]()

### Process Lifecycle Management

The `OnPolicyRunner` manages the complete lifecycle of worker processes:

| Process Type | Creation Method | Termination Method | Communication |
|--------------|----------------|-------------------|---------------|
| Training | `start_train()` | Results queue signal | `results_queue`, `checkpoints_queue` |
| Validation | `start_train()` (if enabled) | Checkpoint completion | `results_queue`, `checkpoints_queue` |
| Testing | `start_test()` | All checkpoints processed | `results_queue`, `checkpoints_queue` |

Sources: [allenact/algorithms/onpolicy_sync/runner.py:242-330](), [allenact/algorithms/onpolicy_sync/runner.py:332-409]()

## Training Pipeline

The training pipeline implements on-policy reinforcement learning with support for distributed execution and advanced optimization techniques.

### Training Loop Architecture

```mermaid
sequenceDiagram
    participant Runner as "OnPolicyRunner"
    participant Trainer as "OnPolicyTrainer" 
    participant Storage as "RolloutStorage"
    participant Tasks as "VectorSampledTasks"
    participant Model as "ActorCriticModel"
    participant Optimizer as "Optimizer"
    
    Runner->>Trainer: start_train()
    Trainer->>Storage: initialize_rollouts()
    Trainer->>Tasks: get_observations()
    
    loop Training Steps
        Trainer->>Model: act(observations)
        Model-->>Trainer: actions, values
        Trainer->>Tasks: step(actions)
        Tasks-->>Trainer: observations, rewards, dones
        Trainer->>Storage: insert(rollout_data)
    end
    
    Trainer->>Storage: compute_returns()
    
    loop Update Repeats
        Trainer->>Storage: recurrent_generator()
        Storage-->>Trainer: training_batches
        Trainer->>Model: forward(batch)
        Model-->>Trainer: actor_critic_output
        Trainer->>Trainer: compute_losses()
        Trainer->>Optimizer: backprop_step()
    end
    
    Trainer->>Runner: send_package(metrics)
```

Sources: [allenact/algorithms/onpolicy_sync/engine.py:1186-1328](), [allenact/algorithms/onpolicy_sync/engine.py:880-954](), [allenact/algorithms/onpolicy_sync/engine.py:997-1020]()

### Training State Management

The `OnPolicyTrainer` maintains several critical pieces of state:

- **Training Pipeline**: Manages stages, learning rates, and optimization schedules via `TrainingPipeline`
- **Rollout Storage**: Buffers experience data via `RolloutStorage` 
- **Tracking Info**: Accumulates metrics and loss values for logging
- **Distributed State**: Coordinates across workers using `torch.distributed` stores

Sources: [allenact/algorithms/onpolicy_sync/engine.py:666-704](), [allenact/algorithms/onpolicy_sync/engine.py:1186-1328]()

## Evaluation Pipeline

The evaluation system supports both validation during training and comprehensive testing with corruption robustness analysis.

### Evaluation Process Flow

```mermaid
graph TD
    subgraph "Checkpoint Management"
        CheckpointQueue["checkpoints_queue"]
        SkipLatest["skip_to_latest()"]
        LoadModel["checkpoint_load()"]
    end
    
    subgraph "Evaluation Execution"
        InitRollouts["initialize_rollouts()"]
        CollectSteps["collect_rollout_step()"]
        ActorCritic["actor_critic.eval()"]
        TaskMetrics["aggregate_task_metrics()"]
    end
    
    subgraph "Results Processing"
        LoggingPkg["LoggingPackage"]
        ResultsQueue["results_queue"]
        Visualizer["VizSuite"]
    end
    
    CheckpointQueue --> SkipLatest
    SkipLatest --> LoadModel
    LoadModel --> InitRollouts
    InitRollouts --> ActorCritic
    ActorCritic --> CollectSteps
    CollectSteps --> TaskMetrics
    TaskMetrics --> LoggingPkg
    LoggingPkg --> Visualizer
    LoggingPkg --> ResultsQueue
```

Sources: [allenact/algorithms/onpolicy_sync/engine.py:1411-1525](), [allenact/algorithms/onpolicy_sync/engine.py:1562-1650]()

### Evaluation Modes

The system supports different evaluation modes with distinct behaviors:

| Mode | Purpose | Checkpoint Handling | Task Distribution |
|------|---------|-------------------|-------------------|
| `valid` | Training validation | Skip to latest | Single worker |
| `test` | Final evaluation | Process all specified | Multiple workers |

Sources: [allenact/algorithms/onpolicy_sync/engine.py:1590-1598](), [allenact/algorithms/onpolicy_sync/runner.py:774-790]()

## Communication and Coordination

The engine uses a queue-based communication system to coordinate between processes and aggregate results.

### Message Queue Architecture

```mermaid
graph LR
    subgraph "Message Types"
        TrainPkg["LoggingPackage (train)"]
        ValidPkg["LoggingPackage (valid)"]
        TestPkg["LoggingPackage (test)"]
        Signals["Control Signals"]
    end
    
    subgraph "Processing Logic"
        Aggregator["process_train_packages()"]
        EvalProcessor["process_eval_package()"]
        TestProcessor["process_test_packages()"]
        SignalHandler["Control Signal Handler"]
    end
    
    subgraph "Outputs"
        TensorBoard["TensorBoard Logs"]
        MetricsFile["metrics.json"]
        ConsoleLog["Console Logging"]
    end
    
    TrainPkg --> Aggregator
    ValidPkg --> EvalProcessor
    TestPkg --> TestProcessor
    Signals --> SignalHandler
    
    Aggregator --> TensorBoard
    Aggregator --> ConsoleLog
    EvalProcessor --> TensorBoard
    EvalProcessor --> ConsoleLog
    TestProcessor --> MetricsFile
    TestProcessor --> TensorBoard
```

Sources: [allenact/algorithms/onpolicy_sync/runner.py:555-629](), [allenact/algorithms/onpolicy_sync/runner.py:518-554](), [allenact/algorithms/onpolicy_sync/runner.py:631-690]()

### Distributed Training Coordination

For multi-worker training, the engine implements synchronization mechanisms:

- **Barrier Synchronization**: Uses `torch.distributed.barrier()` to synchronize workers at rollout boundaries
- **Gradient Aggregation**: Performs `all_reduce` operations for distributed gradient updates
- **Step Counting**: Maintains consistent step counts across workers using distributed stores
- **Preemption Handling**: Allows workers to finish early to prevent stragglers

Sources: [allenact/algorithms/onpolicy_sync/engine.py:1200-1265](), [allenact/algorithms/onpolicy_sync/engine.py:1002-1020](), [allenact/algorithms/onpolicy_sync/engine.py:679-698]()

## Checkpointing and State Management

The engine provides comprehensive checkpointing capabilities for training resumption and evaluation.

### Checkpoint Content Structure

Checkpoints contain complete training state:

```python
save_dict = {
    "model_state_dict": self.actor_critic.state_dict(),
    "total_steps": self.training_pipeline.total_steps,
    "optimizer_state_dict": self.optimizer.state_dict(),
    "training_pipeline_state_dict": self.training_pipeline.state_dict(),
    "trainer_seed": self.seed,
    "scheduler_state": self.lr_scheduler.state_dict()  # if present
}
```

Sources: [allenact/algorithms/onpolicy_sync/engine.py:731-755]()

### Checkpoint Management Workflow

```mermaid
stateDiagram-v2
    [*] --> Training
    Training --> SaveCheckpoint : save_interval reached
    SaveCheckpoint --> QueueCheckpoint : if validation enabled
    QueueCheckpoint --> Training : continue training
    Training --> LoadCheckpoint : resume from checkpoint
    LoadCheckpoint --> Training : restored state
    
    QueueCheckpoint --> ValidationWorker : checkpoint available
    ValidationWorker --> EvaluateCheckpoint : load checkpoint
    EvaluateCheckpoint --> ReportResults : evaluation complete
    ReportResults --> ValidationWorker : wait for next checkpoint
```

Sources: [allenact/algorithms/onpolicy_sync/engine.py:1300-1315](), [allenact/algorithms/onpolicy_sync/engine.py:1562-1625](), [allenact/algorithms/onpolicy_sync/runner.py:870-944]()

The Training and Evaluation Engine provides a robust, scalable foundation for conducting reinforcement learning experiments with comprehensive logging, distributed execution support, and seamless integration with corruption testing systems.

---

