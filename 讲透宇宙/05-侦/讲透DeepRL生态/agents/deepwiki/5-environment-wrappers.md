> 来源: [https://deepwiki.com/tensorflow/agents/5-environment-wrappers](https://deepwiki.com/tensorflow/agents/5-environment-wrappers)
> DeepWiki tensorflow/agents | Last indexed: 24 April 2025 (2a236d

# Environment Wrappers

  Relevant source files 
 - [tf_agents/environments/batched_py_environment.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/batched_py_environment.py)
 - [tf_agents/environments/batched_py_environment_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/batched_py_environment_test.py)
 - [tf_agents/environments/gym_wrapper.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/gym_wrapper.py)
 - [tf_agents/environments/gym_wrapper_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/gym_wrapper_test.py)
 - [tf_agents/environments/parallel_py_environment.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/parallel_py_environment.py)
 - [tf_agents/environments/parallel_py_environment_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/parallel_py_environment_test.py)
 - [tf_agents/environments/py_environment.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/py_environment.py)
 - [tf_agents/environments/py_environment_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/py_environment_test.py)
 - [tf_agents/environments/random_py_environment.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/random_py_environment.py)
 - [tf_agents/environments/test_envs.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/test_envs.py)
 - [tf_agents/environments/test_envs_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/test_envs_test.py)
 - [tf_agents/environments/tf_py_environment.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/tf_py_environment.py)
 - [tf_agents/environments/tf_py_environment_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/tf_py_environment_test.py)
 - [tf_agents/environments/wrappers.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py)
 - [tf_agents/environments/wrappers_test.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers_test.py)
 - [tf_agents/examples/cql_sac/kumar20/dataset/dataset_generator.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/examples/cql_sac/kumar20/dataset/dataset_generator.py)
 - [tf_agents/examples/cql_sac/kumar20/dataset/dataset_utils.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/examples/cql_sac/kumar20/dataset/dataset_utils.py)
 - [tf_agents/examples/cql_sac/kumar20/dataset/file_utils.py](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/examples/cql_sac/kumar20/dataset/file_utils.py)
 
  Environment wrappers in TF-Agents provide a powerful mechanism to modify the behavior of reinforcement learning environments while maintaining a consistent interface. These wrappers follow a decorator pattern, allowing you to incrementally add, modify, or filter functionality of environments in a composable way. This document describes the environment wrapper architecture and the various wrappers available in TF-Agents.

 For information about Python environments directly, see [PyEnvironment](https://deepwiki.com/tensorflow/agents/2.2-environments), and for TensorFlow environments, see [TFEnvironment](https://deepwiki.com/tensorflow/agents/2.2-environments).

 
## Wrapper Architecture

 At the foundation of TF-Agents' wrapper system is the `PyEnvironmentBaseWrapper` class. This base class implements the `PyEnvironment` interface and forwards calls to the wrapped environment.

 
```

```

 Sources: [tf_agents/environments/wrappers.py45-96](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L45-L96) [tf_agents/environments/py_environment.py38-363](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/py_environment.py#L38-L363)

 The key method in `PyEnvironmentBaseWrapper` is `__getattr__`, which forwards all undefined attribute access to the wrapped environment:

 
```

```

 
## Time and Episode Management Wrappers

 
### TimeLimit

 The `TimeLimit` wrapper ends episodes after a specified number of steps, regardless of whether the environment would naturally terminate.

 
```

```

 Sources: [tf_agents/environments/wrappers.py98-134](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L98-L134)

 
### FixedLength

 The `FixedLength` wrapper ensures all episodes have the same length by truncating long episodes and padding short episodes (by repeating the last step with a discount of 0).

 Sources: [tf_agents/environments/wrappers.py136-188](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L136-L188)

 
## Action Manipulation Wrappers

 
### ActionRepeat

 The `ActionRepeat` wrapper repeats the same action multiple times and accumulates the rewards. This can reduce the effective number of decisions an agent needs to make.

 
```

```

 Sources: [tf_agents/environments/wrappers.py249-295](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L249-L295)

 
### FlattenActionWrapper

 The `FlattenActionWrapper` converts nested or multi-dimensional actions into a flat array, which is useful for algorithms that expect a simple action structure.

 Sources: [tf_agents/environments/wrappers.py298-387](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L298-L387)

 
### ActionDiscretizeWrapper

 The `ActionDiscretizeWrapper` converts continuous actions into discrete actions by dividing the continuous space into a specified number of discrete values.

 
```

```

 Sources: [tf_agents/environments/wrappers.py508-644](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L508-L644)

 
### ActionClipWrapper

 The `ActionClipWrapper` ensures actions stay within the bounds defined by the action spec, clipping any out-of-range values.

 Sources: [tf_agents/environments/wrappers.py647-672](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L647-L672)

 
### ActionOffsetWrapper

 The `ActionOffsetWrapper` shifts actions to be zero-based by subtracting the minimum value from the action, which is particularly useful for DQN agents that don't support negative-valued actions.

 Sources: [tf_agents/environments/wrappers.py677-711](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L677-L711)

 
### OneHotActionWrapper

 The `OneHotActionWrapper` converts discrete integer actions to one-hot format, which can be useful for certain neural network architectures.

 Sources: [tf_agents/environments/wrappers.py1124-1162](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L1124-L1162)

 
## Observation Manipulation Wrappers

 
### ObservationFilterWrapper

 The `ObservationFilterWrapper` selects only specific elements from the observation array based on provided indices.

 Sources: [tf_agents/environments/wrappers.py390-449](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L390-L449)

 
### FlattenObservationsWrapper

 The `FlattenObservationsWrapper` converts nested or multi-dimensional observations into a flat array.

 
```

```

 Sources: [tf_agents/environments/wrappers.py714-938](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L714-L938)

 
### HistoryWrapper

 The `HistoryWrapper` maintains a history of observations and optionally actions, appending them to the current observation. This is useful for environments where the agent benefits from temporal context.

 
```

```

 Sources: [tf_agents/environments/wrappers.py1020-1121](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L1020-L1121)

 
## Utility Wrappers

 
### RunStats

 The `RunStats` wrapper tracks statistics about environment interaction, such as episode count, step count, and reset count.

 
```

```

 Sources: [tf_agents/environments/wrappers.py452-506](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L452-L506)

 
### PerformanceProfiler

 The `PerformanceProfiler` wrapper uses Python's `cProfile` module to profile the performance of the environment, allowing you to identify bottlenecks in environment execution.

 Sources: [tf_agents/environments/wrappers.py190-247](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L190-L247)

 
### GoalReplayEnvWrapper

 The `GoalReplayEnvWrapper` is an abstract base class for implementing Hindsight Experience Replay (HER). It requires subclassing to implement environment-specific goal manipulation.

 Sources: [tf_agents/environments/wrappers.py941-1017](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L941-L1017)

 
## Gym Integration

 
### GymWrapper

 The `GymWrapper` adapts OpenAI Gym environments to the TF-Agents `PyEnvironment` interface, converting between the two APIs.

 
```

```

 Sources: [tf_agents/environments/gym_wrapper.py153-293](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/gym_wrapper.py#L153-L293)

 The `GymWrapper` handles:

 
 - Converting gym spaces to TF-Agents specs using `spec_from_gym_space`
 - Translating gym step method to TF-Agents time steps
 - Managing auto-reset behavior
 - Preserving additional gym environment methods like `render` and `seed`
 
 
## Batching and Parallelization

 
### BatchedPyEnvironment

 The `BatchedPyEnvironment` combines multiple environments into a single batched environment, which is useful for vectorized operations.

 
```

```

 Sources: [tf_agents/environments/batched_py_environment.py40-215](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/batched_py_environment.py#L40-L215)

 
### ParallelPyEnvironment

 The `ParallelPyEnvironment` runs multiple environments in parallel processes, offering better performance for computationally intensive environments.

 
```

```

 Sources: [tf_agents/environments/parallel_py_environment.py47-196](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/parallel_py_environment.py#L47-L196) [tf_agents/environments/parallel_py_environment.py230-503](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/parallel_py_environment.py#L230-L503)

 
## TF-Agents Environment Path

 This diagram shows the typical path from a raw environment to a TensorFlow-compatible environment:

 
```

```

 Sources: [tf_agents/environments/gym_wrapper.py153-293](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/gym_wrapper.py#L153-L293) [tf_agents/environments/wrappers.py45-96](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/wrappers.py#L45-L96) [tf_agents/environments/tf_py_environment.py68-388](https://github.com/tensorflow/agents/blob/2a236d30/tf_agents/environments/tf_py_environment.py#L68-L388)

 
## Wrapper Selection Guide

 
| When You Need To... | Use This Wrapper | Key Method to Override |
|---|---|---|
| Limit episode length | TimeLimit | _step |
| Make all episodes the same length | FixedLength | _step |
| Repeat actions multiple times | ActionRepeat | _step |
| Flatten nested actions | FlattenActionWrapper | action_spec, _step |
| Convert continuous to discrete actions | ActionDiscretizeWrapper | action_spec, _step |
| Ensure actions are within bounds | ActionClipWrapper | _step |
| Offset actions to be non-negative | ActionOffsetWrapper | action_spec, _step |
| Convert to one-hot actions | OneHotActionWrapper | action_spec, _step |
| Filter observation features | ObservationFilterWrapper | observation_spec, _step, _reset |
| Flatten nested observations | FlattenObservationsWrapper | observation_spec, _step, _reset |
| Add history to observations | HistoryWrapper | observation_spec, _step, _reset |
| Track environment statistics | RunStats | _step, _reset |
| Profile environment performance | PerformanceProfiler | _step, _reset |
| Implement Hindsight Experience Replay | GoalReplayEnvWrapper | get_trajectory_with_goal, get_goal_from_trajectory |
| Use OpenAI Gym environments | GymWrapper | N/A (not a wrapper) |
| Batch multiple environments | BatchedPyEnvironment | N/A (not a wrapper) |
| Run environments in parallel | ParallelPyEnvironment | N/A (not a wrapper) |

 
## Best Practices

 
 - **Wrapper Order Matters**: The order in which wrappers are applied impacts behavior. For example, applying a `TimeLimit` wrapper after a `HistoryWrapper` will limit the number of steps including the history.
 - **Choose Wrapper Combinations Carefully**: Different combinations of wrappers can interact in complex ways. Test your environment stack to ensure it behaves as expected.
 - **Custom Wrappers**: Create custom wrappers by inheriting from `PyEnvironmentBaseWrapper` and overriding the `_step` and/or `_reset` methods. Ensure you maintain the time step structure.
 - **Debugging**: Use the `RunStats` wrapper to track environment metrics during development and debugging.
 - **Performance Optimization**:

 
 - Use `BatchedPyEnvironment` when running on a single machine with multiple environments
 - Use `ParallelPyEnvironment` when environments are computationally intensive
 - Consider using `ActionRepeat` to reduce the effective number of decisions the agent needs to make
 
 By effectively using environment wrappers, you can tailor environments to your specific reinforcement learning needs, potentially improving learning efficiency and algorithm performance.
