> 来源: [https://deepwiki.com/astooke/rlpyt/8-replay-buffers](https://deepwiki.com/astooke/rlpyt/8-replay-buffers)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Replay Buffers

  Relevant source files 
 - [rlpyt/replays/async_.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/async_.py)
 - [rlpyt/replays/frame.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/frame.py)
 - [rlpyt/replays/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py)
 - [rlpyt/replays/non_sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/non_sequence/prioritized.py)
 - [rlpyt/replays/sequence/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/n_step.py)
 - [rlpyt/replays/sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/prioritized.py)
 - [rlpyt/replays/sum_tree.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sum_tree.py)
 
  Replay Buffers are a core component in rlpyt that store agent experiences for off-policy reinforcement learning algorithms. They enable efficient data reuse by allowing algorithms to sample past experiences, breaking the temporal correlation between samples and improving data efficiency. This page covers the various replay buffer implementations in rlpyt, including standard buffers, prioritized experience replay, sequence-based storage for recurrent networks, and frame-based buffering for visual observations.

 For information about the algorithms that use these buffers, see [Algorithms](https://deepwiki.com/astooke/rlpyt/3-algorithms).

 
## Replay Buffer Architecture

 The replay buffer system in rlpyt follows a hierarchical structure with specialized implementations for different needs. The base functionality handles the core storage and sampling mechanics, with extensions for n-step returns, prioritized sampling, and sequence data.

 
### Replay Buffer Hierarchy

 
```

```

 Sources: [rlpyt/replays/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py) [rlpyt/replays/sequence/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/n_step.py) [rlpyt/replays/non_sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/non_sequence/prioritized.py) [rlpyt/replays/sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/prioritized.py) [rlpyt/replays/frame.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/frame.py) [rlpyt/replays/async_.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/async_.py)

 
## Basic Replay Buffer Implementation

 The foundation of the replay system is the `BaseNStepReturnBuffer` class, which handles storage and computation of n-step returns. This buffer stores experiences in a circular buffer with leading dimensions [T, B], where T is time and B is batch size.

 
### Key Components and Behavior

 
```

```

 Sources: [rlpyt/replays/n_step.py11-109](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py#L11-L109)

 The `BaseNStepReturnBuffer` manages:

 
 - **Sample Storage**: Maintains a ring buffer of experiences with dimensions [T,B]
 - **N-Step Returns**: Computes n-step returns using discounted rewards
 - **Cursor Management**: Tracks the current write position and handles wrapping
 - **Validity Tracking**: Manages which samples are valid for sampling based on: 
 - `off_backward`: Most recent n-step samples (incomplete returns)
 - `off_forward`: Current cursor position (overwritten previous action/reward)
 
 When new samples are appended to the buffer:

 
```

```

 Sources: [rlpyt/replays/n_step.py62-79](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py#L62-L79)

 
## Sequence Replay Buffer

 The `SequenceNStepReturnBuffer` extends the base buffer to handle sequential data, particularly for recurrent neural networks (RNNs). This buffer stores RNN states and can extract continuous sequences for training.

 
### RNN State Storage Strategies

 
```

```

 Sources: [rlpyt/replays/sequence/n_step.py17-106](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/n_step.py#L17-L106)

 Key features:

 
 - **RNN State Management**:

 
 - Can store RNN states at regular intervals (`rnn_state_interval`) to save memory
 - Only timesteps with saved RNN states are valid starting points for sequences
 - **Sequence Extraction**:

 
 - `extract_batch()` returns full sequences including all relevant fields
 - Handles the extraction of valid sequences based on RNN state availability
 
 
## Prioritized Experience Replay

 Prioritized Experience Replay (PER) samples experiences based on their TD errors, focusing learning on surprising or informative transitions. The implementation uses a Sum Tree data structure for efficient prioritized sampling.

 
### Prioritized Replay System

 
```

```

 Sources: [rlpyt/replays/non_sequence/prioritized.py15-88](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/non_sequence/prioritized.py#L15-L88) [rlpyt/replays/sequence/prioritized.py16-125](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/prioritized.py#L16-L125) [rlpyt/replays/sum_tree.py8-222](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sum_tree.py#L8-L222)

 Key components:

 
 - **Priority Management**:

 
 - Uses a `SumTree` for efficient storage and sampling of priorities
 - Priorities are raised to power α (alpha) to control prioritization strength
 - **Sampling Process**:

 
 - Samples based on priority weights
 - Computes importance sampling weights to correct for bias: (1/priority)^β
 - Supports unique sampling to avoid duplicates
 - **Priority Updates**:

 
 - Updates priorities after learning based on new TD errors
 - Propagates changes through the tree efficiently
 
 
### Sum Tree Implementation

 The `SumTree` class provides a binary tree structure for efficient prioritized sampling:

 
```

```

 Sources: [rlpyt/replays/sum_tree.py8-222](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sum_tree.py#L8-L222)

 The `SumTree` implements:

 
 - **Efficient Sampling**:

 
 - O(log n) sampling based on priority
 - Binary search through tree to find samples
 - **Priority Updates**:

 
 - Updates priorities efficiently
 - Propagates changes up the tree
 - **Cursor Management**:

 
 - Handles advancing the buffer cursor
 - Marks invalid regions around cursor
 
 
## Frame-Based Buffer

 The `FrameBufferMixin` provides memory-efficient storage for frame-based observations (e.g., in Atari games) by storing only unique frames instead of redundant stacked observations.

 
### Frame Buffer Operation

 
```

```

 Sources: [rlpyt/replays/frame.py10-59](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/frame.py#L10-L59)

 Key features:

 
 - **Memory Efficiency**:

 
 - Only stores unique/new frames instead of full stacked observations
 - Significantly reduces memory usage for visual observations
 - **Frame Organization**:

 
 - `samples_frames`: Stores all unique frames including duplicates at boundaries
 - `samples_new_frames`: View into samples_frames without duplicates
 - **Appending Process**:

 
 - Only the newest frame from each observation is stored
 - Handles duplication at buffer wrapping points
 
 
## Asynchronous Replay Support

 The `AsyncReplayBufferMixin` provides thread-safe operation for multi-process training scenarios using read-write locks.

 
### Asynchronous Operation

 
```

```

 Sources: [rlpyt/replays/async_.py8-47](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/async_.py#L8-L47) [rlpyt/replays/sum_tree.py225-249](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sum_tree.py#L225-L249)

 Key components:

 
 - **Synchronization Primitives**:

 
 - Uses read-write locks to allow multiple readers but exclusive writers
 - Maintains shared variables for buffer state across processes
 - **Thread-Safe Operations**:

 
 - `append_samples()`: Uses write lock to safely add new experiences
 - `sample_batch()`: Uses read lock to safely sample without interference
 - `update_batch_priorities()`: Uses write lock to update priorities
 - **State Synchronization**:

 
 - `_async_pull()`: Updates local state from shared memory
 - `_async_push()`: Updates shared memory from local state
 
 
## Usage Pattern Table

 
| Buffer Type | Use Case | Key Features | Algorithm Examples |
|---|---|---|---|
| NStepReturnBuffer | Basic off-policy RL | N-step returns, circular buffer | DQN, SAC, DDPG |
| PrioritizedReplayBuffer | Improved sample efficiency | Priority-based sampling | Prioritized DQN, Rainbow |
| SequenceNStepReturnBuffer | Recurrent networks | RNN state storage, sequence sampling | R2D2 |
| PrioritizedSequenceReplayBuffer | Recurrent with priorities | Sequence priorities, RNN states | Prioritized R2D2 |
| FrameBufferMixin | Visual observations | Memory-efficient frame storage | Visual DQN variants |
| Async variants | Multi-process training | Thread-safe operations | Any off-policy with parallelism |

 Sources: [rlpyt/replays/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py) [rlpyt/replays/non_sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/non_sequence/prioritized.py) [rlpyt/replays/sequence/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/n_step.py) [rlpyt/replays/sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/prioritized.py) [rlpyt/replays/frame.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/frame.py) [rlpyt/replays/async_.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/async_.py)

 
## Integration with Algorithms

 Replay buffers integrate with rlpyt's algorithm components as follows:

 
```

```

 Sources: [rlpyt/replays/n_step.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/n_step.py) [rlpyt/replays/non_sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/non_sequence/prioritized.py) [rlpyt/replays/sequence/prioritized.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/replays/sequence/prioritized.py)

 During training:

 
 - The **Sampler** collects experiences from environment interactions
 - The **Runner** appends these experiences to the replay buffer
 - The **Algorithm** samples batches from the buffer for optimization
 - For prioritized replay, the algorithm updates priorities based on TD errors
 
 This design allows for flexible replay strategies while maintaining a consistent interface for algorithms to interact with.
