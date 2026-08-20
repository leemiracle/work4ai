# deepwiki torchrl §5 replay-buffers
> 来源: https://deepwiki.com/pytorch/rl/5-replay-buffers

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

## Replay Buffers

Relevant source files

  - docs/source/reference/data.rst

  - test/test_rb.py

  - torchrl/data/__init__.py

  - torchrl/data/replay_buffers/__init__.py

  - torchrl/data/replay_buffers/checkpointers.py

  - torchrl/data/replay_buffers/replay_buffers.py

  - torchrl/data/replay_buffers/samplers.py

  - torchrl/data/replay_buffers/storages.py

  - torchrl/data/replay_buffers/utils.py

  - torchrl/data/replay_buffers/writers.py

Replay buffers are memory structures that store experience data collected during reinforcement learning training. They enable experience replay, a fundamental technique in off-policy RL algorithms where the agent samples past experiences to update its policy. TorchRL implements replay buffers as composable systems built from three independent components: Storage (where data lives), Sampler (how data is selected), and Writer (how data is inserted).

This page provides an overview of the replay buffer system. For implementation details of the composable architecture, see ReplayBuffer Architecture. For advanced features like prioritization, trajectory storage, and checkpointing, see Advanced Replay Buffer Features.

### Purpose and Design Philosophy

The replay buffer system in TorchRL is designed around three principles:

  - Composability : Storage, sampling, and writing strategies are independent and can be mixed freely

  - Type Flexibility : Support for tensors, TensorDicts, PyTrees, and arbitrary Python objects

  - Efficiency : Memory-mapped storage, lazy initialization, and optimized C++ data structures

Sources: torchrl/data/replay_buffers/replay_buffers.py92-247

### Core Architecture

The replay buffer system follows a strategy pattern where three components collaborate:

```

```

Core Data Flow:

  - Environment/Collector produces experience → ReplayBuffer.add() / ReplayBuffer.extend()

  - Writer determines insertion location → Writer.add() / Writer.extend()

  - Storage persists the data → Storage.set()

  - Loss module requests batch → ReplayBuffer.sample()

  - Sampler selects indices → Sampler.sample()

  - Storage retrieves data → Storage.get()

Sources: torchrl/data/replay_buffers/replay_buffers.py92-247 Diagram 1 from architecture overview

### Component Types

TorchRL provides multiple implementations of each component that can be freely combined:

#### Storage Backends

| Storage Type | Description | Best For | File Reference |
| ListStorage | Python list storage | Arbitrary objects, small buffers | storages.py 234-429 |
| TensorStorage | Pre-allocated tensor | Fixed-size buffers, fast access | storages.py 504-971 |
| LazyTensorStorage | Lazy-initialized tensor | Unknown data shapes | storages.py 974-1091 |
| LazyMemmapStorage | Memory-mapped storage | Large buffers, disk persistence | storages.py 1094-1305 |
| LazyStackStorage | Heterogeneous structures | Variable-length trajectories | storages.py 431-502 |
| CompressedListStorage | Compressed storage | Memory-constrained environments | storages.py 1669-1931 |

#### Sampling Strategies

| Sampler Type | Description | Use Case | File Reference |
| RandomSampler | Uniform random sampling | Standard experience replay | samplers.py 120-151 |
| SamplerWithoutReplacement | Sequential no-replacement | Epoch-based training | samplers.py 153-295 |
| PrioritizedSampler | Priority-based sampling | Prioritized Experience Replay (PER) | samplers.py 297-733 |
| SliceSampler | Trajectory slice sampling | Recurrent networks, temporal structure | samplers.py 736-864 |
| PrioritizedSliceSampler | Prioritized trajectory slices | PER + recurrence | samplers.py 867-1010 |

#### Writing Policies

| Writer Type | Description | Behavior | File Reference |
| RoundRobinWriter | Circular buffer overwrite | FIFO replacement | writers.py 147-310 |
| TensorDictRoundRobinWriter | TensorDict-aware round-robin | Adds index tracking | writers.py 312-361 |
| TensorDictMaxValueWriter | Top-K based on priority | Keeps highest-priority samples | writers.py 363-636 |

Sources: torchrl/data/replay_buffers/storages.py57-2000 torchrl/data/replay_buffers/samplers.py45-1010 torchrl/data/replay_buffers/writers.py43-636

### Class Hierarchy and Code Entities

The following diagram maps the natural language concepts to concrete code classes:

```

```

Sources: torchrl/data/replay_buffers/__init__.py1-100 torchrl/data/replay_buffers/replay_buffers.py92-2200 torchrl/data/replay_buffers/storages.py57-2000 torchrl/data/replay_buffers/samplers.py45-1010 torchrl/data/replay_buffers/writers.py43-636

### Basic Usage Patterns

#### Simple Replay Buffer

The most basic usage combines default components:

```

```

Sources: torchrl/data/replay_buffers/replay_buffers.py180-246

#### TensorDict Replay Buffer

For structured RL data, use `TensorDictReplayBuffer`:

```

```

Sources: torchrl/data/replay_buffers/replay_buffers.py1244-1489

#### Prioritized Experience Replay

Use `PrioritizedSampler` for importance-weighted sampling:

```

```

Sources: torchrl/data/replay_buffers/samplers.py297-733 torchrl/data/replay_buffers/replay_buffers.py1713-1866

### Integration with Training Loop

Replay buffers integrate naturally with TorchRL's training infrastructure:

```

```

Typical training loop:

```

```

Sources: torchrl/data/replay_buffers/replay_buffers.py180-246 Diagram 5 from architecture overview

### Data Type Support

TorchRL replay buffers support multiple data formats through the storage abstraction:

| Data Type | Storage Support | Example Usage |
| torch.Tensor | All storages | Single tensor per transition |
| TensorDict | All storages | Structured RL transitions |
| @tensorclass | All storages | Custom structured data |
| PyTree (dict/list/tuple) | TensorStorage , LazyTensorStorage , LazyMemmapStorage | Nested Python structures |
| Arbitrary Python objects | ListStorage , CompressedListStorage | Custom classes, strings, etc. |

Example with PyTree:

```

```

Sources: torchrl/data/replay_buffers/replay_buffers.py211-246 torchrl/data/replay_buffers/storages.py504-971

### Advanced Features Overview

The replay buffer system supports several advanced features detailed in Advanced Replay Buffer Features:

  - Prioritized Experience Replay (PER) : Sample high-error transitions more frequently with importance sampling correction

  - Trajectory Storage : Store and sample multi-step sequences for recurrent policies or multi-step returns

  - Checkpointing : Save/load buffer state to disk with compression and efficient serialization

  - Transforms : Apply preprocessing (normalization, frame stacking) during sampling

  - Multithreading : Prefetch samples in background threads for throughput

  - Distributed Buffers : Share buffers across processes with RemoteTensorDictReplayBuffer and RayReplayBuffer

Sources: torchrl/data/replay_buffers/replay_buffers.py92-2200 torchrl/data/replay_buffers/samplers.py297-1010

### Performance Considerations

#### Storage Selection Guidelines

| Scenario | Recommended Storage | Reason |
| Small buffer (<10K transitions) | LazyTensorStorage | Fast in-memory access |
| Large buffer (>100K transitions) | LazyMemmapStorage | Disk-backed, avoids OOM |
| Unknown data shape at init | LazyTensorStorage or LazyMemmapStorage | Lazy initialization on first add |
| Variable-length trajectories | LazyStackStorage | Supports heterogeneous shapes |
| Memory-constrained | CompressedListStorage | Compression reduces memory footprint |

#### Sampler Selection Guidelines

| Scenario | Recommended Sampler | Reason |
| Standard off-policy | RandomSampler | Uniform IID sampling |
| High-variance gradients | PrioritizedSampler | Focus on high-error transitions |
| Epoch-based training | SamplerWithoutReplacement | Iterate through data once per epoch |
| Recurrent policies | SliceSampler | Sample contiguous trajectory segments |

Sources: torchrl/data/replay_buffers/storages.py57-2000 torchrl/data/replay_buffers/samplers.py45-1010

### Relationship to Other TorchRL Components

Replay buffers connect multiple TorchRL systems:

```

```

  - TensorDict ( #2.1 ): Universal data container for all replay buffer operations

  - TensorSpec ( #2.2 ): Validates data shapes and types during storage

  - Collectors ( #4 ): Produce batched data for extend() operations

  - Loss Modules ( #7 ): Consume sampled batches for policy updates

  - ValueEstimators ( #7.5 ): Compute advantages/returns on sampled data

Sources: Diagram 1 and Diagram 6 from architecture overview torchrl/data/replay_buffers/replay_buffers.py92-2200

### Summary

The TorchRL replay buffer system provides:

  - Composable Architecture : Independent Storage, Sampler, and Writer components that can be freely combined

  - Type Flexibility : Support for tensors, TensorDicts, PyTrees, and arbitrary objects

  - Multiple Implementations : 6 storage types, 5 sampler types, 3 writer types covering common RL scenarios

  - Efficient Memory Management : Memory-mapped storage, lazy initialization, compression options

  - Advanced Features : Prioritization, trajectory sampling, checkpointing, distributed support

For implementation details and code examples, see ReplayBuffer Architecture. For advanced usage including PER, checkpointing, and distributed buffers, see Advanced Replay Buffer Features.

Sources: torchrl/data/replay_buffers/replay_buffers.py92-2200 torchrl/data/replay_buffers/storages.py57-2000 torchrl/data/replay_buffers/samplers.py45-1010 torchrl/data/replay_buffers/writers.py43-636 docs/source/reference/data.rst1-59



#### On this page

  - Replay Buffers
  - Purpose and Design Philosophy
  - Core Architecture
  - Component Types
  - Storage Backends
  - Sampling Strategies
  - Writing Policies
  - Class Hierarchy and Code Entities
  - Basic Usage Patterns
  - Simple Replay Buffer
  - TensorDict Replay Buffer
  - Prioritized Experience Replay
  - Integration with Training Loop
  - Data Type Support
  - Advanced Features Overview
  - Performance Considerations
  - Storage Selection Guidelines
  - Sampler Selection Guidelines
  - Relationship to Other TorchRL Components
  - Summary

$!/$$/$
