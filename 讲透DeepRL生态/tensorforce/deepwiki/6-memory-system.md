> 来源: [https://deepwiki.com/tensorforce/tensorforce/6-memory-system](https://deepwiki.com/tensorforce/tensorforce/6-memory-system)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Memory System

  Relevant source files 
 - [tensorforce/core/memories/memory.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/memory.py)
 - [tensorforce/core/memories/queue.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py)
 - [tensorforce/core/memories/replay.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py)
 
  The Memory System in Tensorforce is responsible for storing and retrieving agent experiences for reinforcement learning training. It implements efficient storage structures and sampling strategies that support different reinforcement learning algorithms.

 Sources: [tensorforce/core/memories/memory.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/memory.py) [tensorforce/core/memories/queue.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py) [tensorforce/core/memories/replay.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py)

 
## Memory Hierarchy and Components

 Tensorforce uses a hierarchical memory system with specialized components that build upon each other:

 
```

```

 Sources: [tensorforce/core/memories/memory.py19-174](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/memory.py#L19-L174) [tensorforce/core/memories/queue.py24-461](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L24-L461) [tensorforce/core/memories/replay.py22-92](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py#L22-L92)

 
### Memory Base Class

 The `Memory` class is the abstract base class that defines the interface for all memory implementations. It declares core methods that subclasses must implement:

 
 - `enqueue`: Stores experiences (states, internals, auxiliaries, actions, terminal, reward)
 - `retrieve`: Retrieves specific experiences by indices
 - `successors`: Retrieves experiences following given indices
 - `predecessors`: Retrieves experiences preceding given indices
 - `retrieve_timesteps`: Retrieves batches of timesteps
 - `retrieve_episodes`: Retrieves batches of complete episodes
 
 Sources: [tensorforce/core/memories/memory.py19-174](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/memory.py#L19-L174)

 
### Queue Implementation

 The `Queue` class implements a circular buffer for storing experiences. It serves as the foundation for more advanced memory implementations:

 
 - Maintains fixed-capacity buffers for storing experience components
 - Handles circular wrapping when capacity is reached
 - Tracks terminal states to identify episode boundaries
 - Supports efficient sequence retrieval through predecessor/successor methods
 
 The Queue implements its storage using TensorFlow variables and specialized tracking of terminal states (using values 0, 1, 2, and 3 to represent different terminal conditions).

 Sources: [tensorforce/core/memories/queue.py24-461](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L24-L461)

 
### Replay Memory

 The `Replay` class extends `Queue` to implement experience replay, which randomly samples experiences from the buffer. This approach helps break temporal correlations in sequential data, which is crucial for many reinforcement learning algorithms:

 
 - `retrieve_timesteps`: Randomly samples timesteps from the buffer
 - `retrieve_episodes`: Randomly samples complete episodes from the buffer
 
 Sources: [tensorforce/core/memories/replay.py22-92](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py#L22-L92)

 
## Memory Storage Structure

 The Queue-based memory uses a circular buffer structure to efficiently store experiences:

 
```

```

 The memory system tracks several key variables:

 
 - `buffer_index`: Points to the next position to write in the circular buffer
 - `terminal_indices`: Records indices of terminal states to track episode boundaries
 - `episode_count`: Tracks the number of complete episodes in memory
 
 Sources: [tensorforce/core/memories/queue.py62-98](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L62-L98)

 
## Integration with Agent and Training

 The Memory System is tightly integrated with other components in the Tensorforce framework:

 
```

```

 Sources: [tensorforce/core/memories/memory.py152-173](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/memory.py#L152-L173) [tensorforce/core/memories/queue.py161-318](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L161-L318)

 
## Memory Types and Sampling

 Tensorforce provides these key memory implementations:

 
| Memory Type | Class | Description | Key Methods |
|---|---|---|---|
| queue | Queue | Sequential circular buffer | enqueue, retrieve, predecessors, successors |
| replay | Replay | Random sampling memory | retrieve_timesteps, retrieve_episodes |

 
### Random Sampling in Replay Memory

 The Replay memory implements two main sampling strategies:

 
 - **Random Timestep Sampling**:

 
 - Randomly selects individual timesteps from the buffer
 - Ensures selected timesteps aren't terminal states
 - Respects horizon constraints for temporal difference learning
 - **Random Episode Sampling**:

 
 - Randomly selects complete episodes from the buffer
 - Uses terminal indices to identify episode boundaries
 - Returns complete episode sequences
 
 Sources: [tensorforce/core/memories/replay.py36-92](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py#L36-L92)

 
## Configuration

 The memory system is configured when creating an agent:

 
```

```

 Sources: [tensorforce/core/memories/queue.py38-59](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L38-L59) [tensorforce/core/memories/replay.py22-32](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py#L22-L32)

 
## Key Implementation Details

 
 - **Terminal State Handling**: The Queue memory uses special values to track different terminal states:

 
 - 0: Non-terminal state
 - 1: Terminal state (episode end)
 - 2: Abort terminal (forced episode termination)
 - 3: Terminal marker (last observation)
 - **Efficient Circular Buffer**: The implementation uses TensorFlow operations to efficiently handle circular buffer operations, including modulo-based indexing.
 - **Episode Boundaries**: The memory system carefully tracks episode boundaries to ensure that sampled sequences don't cross episode boundaries.
 - **Batch Retrieval**: The memory system supports efficient batch retrieval operations for timesteps and episodes.
 
 Sources: [tensorforce/core/memories/queue.py100-160](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/queue.py#L100-L160) [tensorforce/core/memories/replay.py36-61](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/memories/replay.py#L36-L61)
