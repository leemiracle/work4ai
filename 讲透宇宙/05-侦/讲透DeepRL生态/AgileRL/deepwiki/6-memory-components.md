> 来源: [https://deepwiki.com/AgileRL/AgileRL/6-memory-components](https://deepwiki.com/AgileRL/AgileRL/6-memory-components)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Memory Components

  Relevant source files 
 - [agilerl/components/replay_buffer.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py)
 - [agilerl/components/sampler.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/sampler.py)
 
  Memory components in AgileRL provide experience storage and sampling systems that enable off-policy reinforcement learning algorithms to learn from past experiences. These components implement various replay buffer strategies including standard experience replay, prioritized experience replay, and n-step returns, along with unified sampling interfaces that support both standard and distributed training configurations.

 For information about multi-agent specific replay buffers, see [Multi-Agent Replay Buffers](https://deepwiki.com/AgileRL/AgileRL/6.2-multi-agent-replay-buffers). For details on how these components integrate with training loops, see [Training Framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework).

 
## Architecture Overview

 The memory system in AgileRL is built around a modular design that separates storage from sampling logic. The core components include replay buffer implementations that handle experience storage, and a unified sampler that provides consistent interfaces across different buffer types and training configurations.

 
### Memory Component Class Hierarchy

 
```

```

 Sources: [agilerl/components/replay_buffer.py13-141](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L13-L141) [agilerl/components/replay_buffer.py143-258](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L143-L258) [agilerl/components/replay_buffer.py260-426](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L260-L426) [agilerl/components/sampler.py22-103](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/sampler.py#L22-L103)

 
## Core Replay Buffer Implementations

 
### Standard Replay Buffer

 The `ReplayBuffer` class provides the foundational circular buffer implementation for experience replay. It uses TensorDict for efficient storage and supports dynamic initialization based on the first transition added.

 
| Feature | Implementation |
|---|---|
| Storage Backend | TensorDict with circular indexing |
| Capacity Management | Fixed maximum size with overwriting |
| Device Support | CPU and GPU storage |
| Batch Sampling | Random uniform sampling |

 Key methods include:

 
 - `add(data: TensorDict)` - Adds transitions with automatic shape handling
 - `sample(batch_size: int)` - Returns randomly sampled batch
 - `storage` property - Provides access to underlying TensorDict
 
 Sources: [agilerl/components/replay_buffer.py13-141](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L13-L141)

 
### Multi-Step Replay Buffer

 The `MultiStepReplayBuffer` extends the base replay buffer to compute n-step returns, which can improve learning efficiency by incorporating longer-term rewards.

 
```

```

 The n-step return calculation follows the formula: `R_t = r_t + γ*r_{t+1} + γ²*r_{t+2} + ... + γ^{n-1}*r_{t+n-1}`

 Sources: [agilerl/components/replay_buffer.py143-258](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L143-L258)

 
### Prioritized Replay Buffer

 The `PrioritizedReplayBuffer` implements the prioritized experience replay algorithm, which samples transitions based on their temporal difference (TD) error magnitude, allowing the agent to learn more efficiently from important experiences.

 
| Component | Purpose |
|---|---|
| SumSegmentTree | Efficient priority-based sampling |
| MinSegmentTree | Importance sampling weight calculation |
| alpha parameter | Controls prioritization strength (0=uniform, 1=full prioritization) |
| beta parameter | Controls importance sampling correction |

 The sampling process involves:

 
 - Proportional sampling based on priorities stored in segment trees
 - Importance sampling weight calculation to correct for sampling bias
 - Priority updates based on TD errors from learning
 
 Sources: [agilerl/components/replay_buffer.py260-426](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L260-L426)

 
## Unified Sampling Interface

 The `Sampler` class provides a unified interface for sampling from different replay buffer types and supports both standard and distributed training configurations.

 
### Sampler Architecture and Data Flow

 
```

```

 
### Sampling Method Selection

 The sampler automatically selects the appropriate sampling method based on the buffer type:

 
```

```

 Sources: [agilerl/components/sampler.py84-102](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/sampler.py#L84-L102)

 
## Integration with Training Systems

 Memory components integrate with AgileRL's training framework through standardized interfaces. The key integration points include:

 
### TensorDict Integration

 All replay buffers use TensorDict as the standard data format, providing:

 
 - Efficient batched operations
 - Device-agnostic storage
 - Automatic shape handling for scalar observations
 - Seamless integration with PyTorch training loops
 
 
### Distributed Training Support

 The sampler supports distributed training through:

 
 - `ReplayDataset` integration for data sharding
 - Custom `tensordict_collate_fn` for proper TensorDict batching
 - DataLoader compatibility with distributed samplers
 
 
### Memory Buffer Selection Pattern

 
```

```

 The memory components are designed to be transparent to the training algorithms, with the sampler handling the complexity of different buffer types and training configurations.

 Sources: [agilerl/components/sampler.py22-208](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/sampler.py#L22-L208) [agilerl/components/replay_buffer.py73-114](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/components/replay_buffer.py#L73-L114)
