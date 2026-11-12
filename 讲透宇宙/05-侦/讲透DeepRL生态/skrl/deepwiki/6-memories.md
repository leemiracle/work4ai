> 来源: [https://deepwiki.com/Toni-SM/skrl/6-memories](https://deepwiki.com/Toni-SM/skrl/6-memories)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Memories

  Relevant source files 
 - [docs/source/api/agents.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/agents.rst)
 - [docs/source/api/memories.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/memories.rst)
 - [docs/source/api/memories/random.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/memories/random.rst)
 - [docs/source/api/resources/noises.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/resources/noises.rst)
 - [docs/source/snippets/memories.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/memories.py)
 - [docs/source/snippets/noises.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/noises.py)
 - [skrl/memories/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/__init__.py)
 - [skrl/memories/jax/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/__init__.py)
 - [skrl/memories/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py)
 - [skrl/memories/jax/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/random.py)
 - [skrl/memories/torch/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/__init__.py)
 - [skrl/memories/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py)
 - [skrl/memories/torch/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py)
 - [skrl/memories/warp/random.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/warp/random.py)
 - [skrl/models/jax/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/__init__.py)
 - [skrl/models/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/jax/base.py)
 - [skrl/models/torch/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/__init__.py)
 - [skrl/models/torch/tabular.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/models/torch/tabular.py)
 
  The Memories system provides experience replay functionality for reinforcement learning agents in skrl. This system stores and manages transitions (state, action, reward, next state, etc.) collected during environment interaction, enabling agents to learn from past experiences through batch sampling. The memory system supports PyTorch, JAX, and Warp backends with standardized APIs.

 For information about agents that use these memories, see [Agents](https://deepwiki.com/Toni-SM/skrl/2-agents). For details about models and neural networks, see [Models](https://deepwiki.com/Toni-SM/skrl/3-models).

 
## Architecture Overview

 The memory system follows a multi-backend architecture with shared interfaces and backend-specific implementations. All memory classes inherit from a `Memory` base class that provides core functionality for tensor storage, circular buffering, and data sampling.

 
```

```

 Sources: [skrl/memories/torch/base.py20-30](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L20-L30) [skrl/memories/jax/base.py38-48](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L38-L48) [skrl/memories/torch/random.py10-21](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L10-L21) [skrl/memories/jax/random.py11-22](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/random.py#L11-L22) [skrl/memories/warp/random.py11-22](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/warp/random.py#L11-L22)

 
## Base Memory Class

 The `Memory` base class implements a circular buffer mechanism. Buffers are allocated as tensors with shape `(memory_size, num_envs, data_size)` [skrl/memories/torch/base.py33-35](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L33-L35)

 
### Core Components

 
| Component | Purpose | Key Methods |
|---|---|---|
| Tensor Storage | Dynamic tensor creation and management | create_tensor(), get_tensor_by_name(), set_tensor_by_name() |
| Circular Buffering | Efficient memory usage with fixed-size buffers | add_samples(), reset() |
| Data Sampling | Batch generation for training | sample(), sample_by_index(), sample_all() |
| Export/Import | Persistence and data sharing | save(), load() |

 
### Tensor Management

 The `create_tensor` API allows agents to define the specific data fields they need to store (e.g., "states", "actions", "rewards"). It handles dimension flattening unless `keep_dimensions` is enabled [skrl/memories/torch/base.py121-171](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L121-L171)

 
```

```

 Sources: [skrl/memories/torch/base.py59-65](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L59-L65) [skrl/memories/torch/base.py162-166](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L162-L166) [skrl/memories/jax/base.py77-85](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L77-L85)

 
## Data Addition and Circular Buffering

 The `add_samples()` method supports multi-environment data collection. It automatically manages the transition between environments and memory slots. If the memory is full and `export=True`, it triggers an automatic export before overwriting data [skrl/memories/torch/base.py40-41](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L40-L41)

 Sources: [skrl/memories/torch/base.py202-283](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L202-L283) [skrl/memories/jax/base.py247-346](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L247-L346)

 
## RandomMemory Implementation

 `RandomMemory` is the standard implementation for experience replay. It supports sampling with or without replacement [skrl/memories/torch/random.py33-36](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L33-L36)

 
### Sampling Mechanisms

 
 - **Random Sampling**: Generates random indexes using `torch.randperm` (PyTorch) or `np.random.permutation` (JAX/Warp) [skrl/memories/torch/random.py75](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L75-L75) [skrl/memories/jax/random.py74](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/random.py#L74-L74)
 - **Sequence Sampling**: If `sequence_length > 1`, the memory generates contiguous blocks of indexes to support Recurrent Neural Networks (RNNs) [skrl/memories/torch/random.py77-79](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L77-L79)
 - **Mini-batches**: The `sample` method can return data partitioned into `mini_batches` for optimization loops [skrl/memories/torch/random.py58](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L58-L58)
 
 Sources: [skrl/memories/torch/random.py51-81](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/random.py#L51-L81) [skrl/memories/jax/random.py52-80](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/random.py#L52-L80) [skrl/memories/warp/random.py52-80](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/warp/random.py#L52-L80)

 
## Data Export and Import

 Memories can be exported to several formats for offline RL or debugging. Supported formats include:

 
 - **PyTorch (`.pt`)**: Saves the internal tensor dictionary using `torch.save` [skrl/memories/torch/base.py28](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L28-L28)
 - **NumPy (`.npz`)**: Exports as a compressed NumPy archive [skrl/memories/torch/base.py28](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L28-L28)
 - **CSV (`.csv`)**: A flattened comma-separated representation [skrl/memories/torch/base.py28](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L28-L28)
 
 Sources: [skrl/memories/torch/base.py365-414](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L365-L414) [skrl/memories/jax/base.py372](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L372-L372)

 
## Backend-Specific Implementations

 
### PyTorch Backend

 Uses `torch.Tensor` and supports `share_memory()` for multiprocessing scenarios, allowing tensors to be shared across processes without duplication [skrl/memories/torch/base.py86-90](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L86-L90)

 
### JAX Backend

 Uses `jax.Array` and `jax.jit` for performance. Since JAX arrays are immutable, updates are performed using functional helpers like `_copyto` which utilize the `.at[:].set()` syntax [skrl/memories/jax/base.py22-35](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L22-L35)

 
### Warp Backend

 Implements memory using `wp.array`. Sampling logic follows the NumPy-based index generation similar to JAX but returns Warp arrays for GPU-accelerated agents [skrl/memories/warp/random.py52-80](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/warp/random.py#L52-L80)

 
```

```

 Sources: [skrl/memories/jax/base.py22-35](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/jax/base.py#L22-L35) [skrl/memories/torch/base.py86-90](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L86-L90) [skrl/memories/torch/base.py118-119](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/memories/torch/base.py#L118-L119)
