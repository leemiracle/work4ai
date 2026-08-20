# deepwiki torchrl §4 data-collection
> 来源: https://deepwiki.com/pytorch/rl/4-data-collection

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Data Collection

Relevant source files

  - test/mocking_classes.py

  - test/test_collector.py

  - test/test_env.py

  - torchrl/collectors/collectors.py

  - torchrl/envs/batched_envs.py

  - torchrl/envs/common.py

  - torchrl/envs/env_creator.py

  - torchrl/envs/utils.py

Data collection is the core infrastructure component responsible for gathering experience from reinforcement learning environments using policies. This system provides the bridge between environment interaction and training data, handling rollout execution, data aggregation, and policy weight synchronization across both single-node and distributed setups.

For distributed collection strategies and backends, see Distributed Collection. For training orchestration that consumes collected data, see Training Orchestration.

### Purpose and Architecture

The data collection system serves as the equivalent of PyTorch DataLoaders for reinforcement learning, with the key difference that it collects data from dynamic, stateful environments rather than static datasets. The system executes policies in environments over specified numbers of steps and delivers structured batches of experience data.

Core Data Collection Architecture

```

```

Sources: docs/source/reference/collectors.rst1-343 torchrl/collectors/__init__.py8-14

### Data Collection Flow

The data collection process follows a standardized pattern across all collector implementations, with variations in parallelization and synchronization strategies.

Data Collection Execution Flow

```

```

Sources: docs/source/reference/collectors.rst8-61

### Collector Classes and Types

The system provides multiple collector implementations optimized for different execution patterns and parallelization strategies.

#### Core Collector Hierarchy

| Collector Class | Execution Model | Environment Support | Use Case |
| SyncDataCollector | Sequential | Single environment | Simple collection, debugging |
| MultiSyncDataCollector | Multi-process synchronous | Multiple environments | Parallel collection with sync |
| MultiaSyncDataCollector | Multi-process asynchronous | Multiple environments | High-throughput async collection |

Collector Configuration and Batch Sizes

The collectors handle different batch size configurations based on their execution model:

```

```

Sources: docs/source/reference/collectors.rst62-100 torchrl/collectors/collectors.py1-50

#### Key Configuration Parameters

Core Collection Parameters:

  - frames_per_batch : Total frames collected per iteration

  - total_frames : Maximum frames over collector lifetime (-1 for endless)

  - max_frames_per_traj : Maximum steps per trajectory before reset

  - reset_at_each_iter : Whether to reset environments between batches

Device Configuration:

  - device : Generic device for unspecified components

  - storing_device : Device for output TensorDict storage

  - env_device : Device for environment execution

  - policy_device : Device for policy execution

Sources: docs/source/reference/collectors.rst44-61

### Weight Synchronization System

Weight synchronization ensures policy consistency across distributed collection workers and between training and inference processes.

Weight Updater Architecture

```

```

The weight updater system supports automatic and manual weight synchronization:

  - Automatic Updates : Set update_after_each_batch=True for updates after each collection

  - Manual Updates : Call collector.update_policy_weights_() explicitly

  - Interval Updates : Use max_weight_update_interval for forced periodic updates

Sources: torchrl/collectors/weight_update.py19-307 docs/source/reference/collectors.rst120-151

### Post-processing and Utilities

#### Trajectory Processing

The `split_trajectories` function separates concatenated trajectory data into individual episodes with proper masking:

Trajectory Splitting Process

```

```

Sources: torchrl/collectors/utils.py37-259 test/test_postprocs.py266-427

#### Multi-step Processing

The `MultiStep` transform implements n-step return computation for temporal difference learning:

Multi-step Transform Flow

```

```

Sources: torchrl/data/postprocs/postprocs.py83-295 test/test_postprocs.py25-231

### Integration with Training Infrastructure

#### Replay Buffer Integration

Data collectors integrate seamlessly with replay buffers for experience storage and sampling:

```

```

#### Asynchronous Collection

Collectors support background data collection with replay buffer integration:

```

```

Sources: docs/source/reference/collectors.rst172-267

### Device and Resource Management

The system provides flexible device configuration for optimal resource utilization:

Device Configuration Strategy

```

```

Sources: docs/source/reference/collectors.rst105-119 torchrl/collectors/distributed/generic.py299-332



#### On this page

  - Data Collection
  - Purpose and Architecture
  - Data Collection Flow
  - Collector Classes and Types
  - Core Collector Hierarchy
  - Key Configuration Parameters
  - Weight Synchronization System
  - Post-processing and Utilities
  - Trajectory Processing
  - Multi-step Processing
  - Integration with Training Infrastructure
  - Replay Buffer Integration
  - Asynchronous Collection
  - Device and Resource Management

$!/$$/$
