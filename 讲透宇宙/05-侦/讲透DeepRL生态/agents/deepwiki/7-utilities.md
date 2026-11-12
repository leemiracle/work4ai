> 来源: [https://deepwiki.com/tensorflow/agents/7-utilities](https://deepwiki.com/tensorflow/agents/7-utilities)
> DeepWiki tensorflow/agents | Last indexed: 24 April 2025 (2a236d

# Utilities

  Relevant source files 
 - [tf_agents/networks/network.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/networks/network.py)
 - [tf_agents/networks/network_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/networks/network_test.py)
 - [tf_agents/replay_buffers/replay_buffer.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/replay_buffers/replay_buffer.py)
 - [tf_agents/replay_buffers/replay_buffer_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/replay_buffers/replay_buffer_test.py)
 - [tf_agents/replay_buffers/tf_uniform_replay_buffer.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/replay_buffers/tf_uniform_replay_buffer.py)
 - [tf_agents/replay_buffers/tf_uniform_replay_buffer_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/replay_buffers/tf_uniform_replay_buffer_test.py)
 - [tf_agents/utils/common.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py)
 - [tf_agents/utils/common_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common_test.py)
 - [tf_agents/utils/nest_utils.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils.py)
 - [tf_agents/utils/nest_utils_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils_test.py)
 - [tf_agents/utils/numpy_storage.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/numpy_storage.py)
 - [tf_agents/utils/numpy_storage_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/numpy_storage_test.py)
 - [tf_agents/utils/session_utils_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/session_utils_test.py)
 - [tf_agents/utils/tensor_normalizer.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer.py)
 - [tf_agents/utils/tensor_normalizer_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer_test.py)
 
  This page documents the utility functions and classes in the TF-Agents library that provide common operations used throughout the codebase. These utilities simplify common tasks like manipulating nested tensor structures, normalizing tensors, periodically executing operations, and managing variables and checkpoints.

 For information about policy saving and loading, see [Policy Saving and Loading](https://deepwiki.com/tensorflow/agents/6.2-policy-saving-and-loading). For information about Reverb integration, see [Reverb Integration](https://deepwiki.com/tensorflow/agents/7.3-reverb-integration).

 
## Utility Components Overview

 TF-Agents provides several utility modules that simplify reinforcement learning implementations:

 
```

```

 Sources: [tf_agents/utils/common.py1-100](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L1-L100) [tf_agents/utils/nest_utils.py1-70](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils.py#L1-L70) [tf_agents/utils/tensor_normalizer.py1-50](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer.py#L1-L50) [tf_agents/utils/numpy_storage.py1-50](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/numpy_storage.py#L1-L50)

 
## Common Utilities

 The `common.py` module provides general-purpose utilities that help with routine tasks in reinforcement learning implementations.

 
### Variable Creation and Management

 Functions to simplify variable creation in both eager and graph modes:

 
```

```

 The `create_variable` function creates TensorFlow variables with proper initialization and resource handling:

 
```

```

 Sources: [tf_agents/utils/common.py204-247](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L204-L247) [tf_agents/utils/common.py127-150](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L127-L150) [tf_agents/utils/common_test.py38-82](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common_test.py#L38-L82)

 
### Soft Updates

 The `soft_variables_update` function performs a crucial operation for many reinforcement learning algorithms - the "soft update" of network weights:

 
```

```

 This function handles updating target networks in algorithms like SAC, DDPG, and TD3:

 
```

```

 Sources: [tf_agents/utils/common.py250-346](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L250-L346) [tf_agents/utils/common_test.py83-142](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common_test.py#L83-L142)

 
### Periodically Executed Operations

 The `Periodically` class and the `periodically` function allow executing operations at specified intervals:

 
```

```

 This is particularly useful for operations like:

 
 - Target network updates
 - Evaluation runs
 - Logging and checkpointing
 
 
```

```

 Sources: [tf_agents/utils/common.py414-545](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L414-L545) [tf_agents/utils/common_test.py230-331](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common_test.py#L230-L331)

 
### Tensor Manipulation Functions

 The common module provides functions for working with tensors:

 
| Function | Purpose |
|---|---|
| clip_to_spec | Clips a tensor to the bounds specified by a BoundedTensorSpec |
| scale_to_spec | Scales a tensor to match the bounds in a BoundedTensorSpec |
| index_with_actions | Selects values from a Q-value tensor using action indices |
| log_probability | Computes log probability of actions given distributions |
| entropy | Computes entropy of distributions |
| compute_returns | Calculates returns from rewards and discounts |

 Sources: [tf_agents/utils/common.py548-1023](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L548-L1023) [tf_agents/utils/common_test.py164-566](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common_test.py#L164-L566)

 
### Checkpointing

 The `Checkpointer` class simplifies saving and loading training state:

 
```

```

 The Checkpointer handles storing all relevant agent state:

 
```

```

 Sources: [tf_agents/utils/common.py1045-1101](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L1045-L1101) [tf_agents/networks/network.py341-356](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/networks/network.py#L341-L356)

 
## Nest Utilities

 The `nest_utils.py` module provides functions for working with nested tensor structures, which are common in reinforcement learning for handling complex observations, actions, and other data.

 
### Structure and Type Validation

 
```

```

 These functions ensure that data structures conform to the expected formats:

 
```

```

 Sources: [tf_agents/utils/nest_utils.py67-470](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils.py#L67-L470) [tf_agents/utils/nest_utils_test.py139-237](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils_test.py#L139-L237)

 
### Batching Operations

 Functions for handling batched tensors and adding/removing batch dimensions:

 
```

```

 These batching operations are particularly useful for processing observations and transitions:

 
```

```

 Sources: [tf_agents/utils/nest_utils.py472-835](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils.py#L472-L835) [tf_agents/utils/nest_utils_test.py238-388](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils_test.py#L238-L388)

 
### Fast Mapping Operations

 Optimized functions for mapping operations over nested structures:

 
| Function | Purpose |
|---|---|
| fast_map_structure | Efficiently maps function over nested structures |
| fast_map_structure_flatten | Maps function over pre-flattened structures |
| flatten_with_joined_paths | Flattens structure with paths joined as strings |
| map_structure_with_paths | Maps function with access to path information |
| prune_extra_keys | Removes keys from nested structures not in template |

 Sources: [tf_agents/utils/nest_utils.py145-320](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils.py#L145-L320) [tf_agents/utils/nest_utils_test.py389-650](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/nest_utils_test.py#L389-L650)

 
## Tensor Normalization

 The `tensor_normalizer.py` module provides classes for normalizing tensor values, which is important for stabilizing neural network inputs:

 
```

```

 
### How Normalizers Work

 Tensor normalizers maintain statistics (mean and variance) about input tensors and use these statistics to normalize values:

 
```

```

 Sources: [tf_agents/utils/tensor_normalizer.py46-206](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer.py#L46-L206) [tf_agents/utils/tensor_normalizer_test.py78-146](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer_test.py#L78-L146)

 
### EMATensorNormalizer

 The `EMATensorNormalizer` updates statistics using exponential moving averages, allowing for online updates that gradually adapt to changing data distributions:

 
```

```

 Sources: [tf_agents/utils/tensor_normalizer.py208-286](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer.py#L208-L286) [tf_agents/utils/tensor_normalizer_test.py147-200](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer_test.py#L147-L200)

 
### StreamingTensorNormalizer

 The `StreamingTensorNormalizer` tracks the full historical statistics of tensors:

 
```

```

 Sources: [tf_agents/utils/tensor_normalizer.py289-402](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer.py#L289-L402) [tf_agents/utils/tensor_normalizer_test.py476-525](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/tensor_normalizer_test.py#L476-L525)

 
## NumPy Storage

 The `numpy_storage.py` module provides utilities for checkpointing NumPy arrays:

 
```

```

 The `NumpyState` class is particularly useful for checkpointing replay buffers or other data structures that use NumPy arrays:

 
```

```

 Sources: [tf_agents/utils/numpy_storage.py34-107](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/numpy_storage.py#L34-L107) [tf_agents/utils/numpy_storage_test.py31-55](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/numpy_storage_test.py#L31-L55)

 
## Session Utilities

 For TensorFlow 1.x compatibility, TF-Agents provides session management utilities in `session_utils.py`:

 
```

```

 While TensorFlow 2.x uses eager execution by default, these utilities help with code that needs to operate in both modes:

 
```

```

 Sources: [tf_agents/utils/session_utils_test.py26-105](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/session_utils_test.py#L26-L105)

 
## Integration with Other Components

 The utilities described on this page are used throughout the TF-Agents library and provide the foundation for many higher-level features:

 
```

```

 The utilities described in this page serve as building blocks for many TF-Agents components. For instance:

 
 - The `soft_variables_update` function is used in DQN, DDPG, SAC, and other agents to update target networks
 - The `Periodically` class is used to execute operations like training, evaluation, and logging at specified intervals
 - Nest utilities are used throughout the codebase to handle nested tensor structures like observations and time steps
 - Tensor normalizers are used to stabilize inputs to neural networks
 - The `Checkpointer` class is used to save and restore agent state
 
 Sources: [tf_agents/utils/common.py16-45](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/utils/common.py#L16-L45) [tf_agents/networks/network.py110-147](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/networks/network.py#L110-L147) [tf_agents/replay_buffers/tf_uniform_replay_buffer.py47-101](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/replay_buffers/tf_uniform_replay_buffer.py#L47-L101)
