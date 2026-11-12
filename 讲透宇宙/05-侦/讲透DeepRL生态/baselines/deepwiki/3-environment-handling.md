> 来源: [https://deepwiki.com/openai/baselines/3-environment-handling](https://deepwiki.com/openai/baselines/3-environment-handling)
> DeepWiki openai/baselines | Last indexed: 18 April 2025 (ea25b9

# Environment Handling

  Relevant source files 
 - [baselines/common/cmd_util.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py)
 - [baselines/common/vec_env/__init__.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/__init__.py)
 - [baselines/common/vec_env/dummy_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py)
 - [baselines/common/vec_env/shmem_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/shmem_vec_env.py)
 - [baselines/common/vec_env/subproc_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py)
 - [baselines/common/vec_env/test_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/test_vec_env.py)
 - [baselines/her/her.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/her/her.py)
 - [baselines/logger.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/logger.py)
 
  
## Purpose and Scope

 This document describes how environments are managed, parallelized, and preprocessed in the OpenAI Baselines library. It covers the core infrastructure for environment creation, vectorization for parallel execution, environment wrappers for preprocessing, and monitoring for performance tracking. For detailed information about vectorized environments specifically, see [Vectorized Environments](https://deepwiki.com/openai/baselines/3.1-vectorized-environments).

 
## Overview

 The environment handling system in Baselines provides a flexible infrastructure for working with reinforcement learning environments. It includes utilities for creating environments, running multiple environments in parallel, preprocessing observations and rewards, and standardizing environment interfaces across different domains.

 
```

```

 Sources: [baselines/common/cmd_util.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py) [baselines/common/vec_env/\_\_init\_\_.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/\_\_init\_\_.py) [baselines/common/vec_env/dummy_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py) [baselines/common/vec_env/subproc_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py) [baselines/common/vec_env/shmem_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/shmem_vec_env.py)

 
## Environment Creation

 The environment creation process in Baselines is handled by a set of utility functions that create and configure environments based on their type (Atari, MuJoCo, Robotics, or standard Gym environments).

 
### Key Environment Creation Functions

 The main functions for environment creation are:

 
| Function | Purpose | Location |
|---|---|---|
| make_vec_env() | Creates a vectorized environment for parallel execution | baselines/common/cmd_util.py22-59 |
| make_env() | Creates a single environment with appropriate wrappers | baselines/common/cmd_util.py62-105 |
| make_atari() | Creates an Atari environment | baselines/common/atari_wrappers.py |
| make_mujoco_env() | Creates a MuJoCo environment | baselines/common/cmd_util.py108-122 |
| make_robotics_env() | Creates a Robotics environment (e.g., Fetch) | baselines/common/cmd_util.py124-135 |

 
### Environment Creation Flow

 The environment creation process typically follows this sequence:

 
```

```

 Sources: [baselines/common/cmd_util.py22-135](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L22-L135)

 
### Example Environment Creation

 When an algorithm needs an environment, it typically calls `make_vec_env()` with appropriate parameters:

 
```

```

 `make_vec_env()` creates a set of environment-creation functions, then passes them to the appropriate vectorized environment implementation.

 Sources: [baselines/common/cmd_util.py22-59](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L22-L59)

 
## Vectorized Environments

 Vectorized environments allow multiple environment instances to be run in parallel, which can significantly improve training throughput. Baselines implements this concept through the `VecEnv` abstract base class and three concrete implementations.

 
### VecEnv Class Hierarchy

 
```

```

 Sources: [baselines/common/vec_env/\_\_init\_\_.py1-10](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/\_\_init\_\_.py#L1-L10) [baselines/common/vec_env/dummy_vec_env.py5-81](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py#L5-L81) [baselines/common/vec_env/subproc_vec_env.py39-121](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py#L39-L121) [baselines/common/vec_env/shmem_vec_env.py20-104](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/shmem_vec_env.py#L20-L104)

 
### VecEnv Implementations

 Baselines provides three different implementations of the `VecEnv` interface:

 
 - **DummyVecEnv**: Runs environments sequentially in a single process. Useful for debugging and when `num_env == 1`.

 
```

```
 - **SubprocVecEnv**: Runs environments in parallel using multiple processes with pipe-based communication. Recommended when `num_env > 1` for improved throughput.

 
```

```
 - **ShmemVecEnv**: Optimized version of SubprocVecEnv that uses shared memory for observation communication, reducing overhead for large observations.
 
 
```

```

 Sources: [baselines/common/vec_env/dummy_vec_env.py5-81](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py#L5-L81) [baselines/common/vec_env/subproc_vec_env.py39-121](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py#L39-L121) [baselines/common/vec_env/shmem_vec_env.py20-104](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/shmem_vec_env.py#L20-L104)

 
## Environment Wrappers

 Environment wrappers modify the behavior of environments by intercepting and potentially transforming the interactions between an agent and an environment. Baselines includes numerous wrappers for common preprocessing tasks.

 
### Common Environment Wrappers

 
| Wrapper | Purpose | Applied To |
|---|---|---|
| Monitor | Records episode statistics (length, rewards) | All environments |
| ClipActionsWrapper | Clips actions to environment action space | Environments with Box action spaces |
| wrap_deepmind | Applies Atari-specific preprocessing | Atari environments |
| VecFrameStack | Stacks consecutive frames | Vectorized environments |
| VecNormalize | Normalizes observations and rewards | Vectorized environments |
| FlattenObservation | Flattens dictionary observations | Environments with Dict observation spaces |
| FilterObservation | Filters dictionary observations | Environments with Dict observation spaces |
| RewardScaler | Scales rewards by a constant factor | Any environment |

 
```

```

 Sources: [baselines/common/cmd_util.py62-105](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L62-L105) [baselines/common/vec_env/\_\_init\_\_.py1-10](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/\_\_init\_\_.py#L1-L10)

 
### Wrapper Application in Environment Creation

 The `make_env` function in `cmd_util.py` applies appropriate wrappers based on the environment type:

 
```

```

 Sources: [baselines/common/cmd_util.py62-105](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L62-L105)

 
## Monitoring and Logging

 Baselines includes a monitoring system to track environment performance metrics during training and evaluation.

 
### Monitoring Components

 The monitoring system consists of several key components:

 
 - **Monitor Wrapper**: Records episode statistics like length and rewards.
 - **VecMonitor**: Vectorized version of the Monitor wrapper.
 - **Logger**: Central logging system for recording and visualizing statistics.
 
 
```

```

 Sources: [baselines/logger.py1-502](https://github.com/openai/baselines/blob/ea25b9e8/baselines/logger.py#L1-L502) [baselines/common/cmd_util.py86-89](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L86-L89)

 
### Monitoring Workflow

 
 - The `Monitor` wrapper is applied to each environment during creation.
 - The `Monitor` records episode statistics when episodes terminate.
 - Statistics are aggregated and passed to the logger.
 - The logger outputs statistics to various formats (console, CSV, JSON, TensorBoard).
 
 
```

```

 Sources: [baselines/logger.py193-218](https://github.com/openai/baselines/blob/ea25b9e8/baselines/logger.py#L193-L218) [baselines/her/her.py53-63](https://github.com/openai/baselines/blob/ea25b9e8/baselines/her/her.py#L53-L63)

 
## End-to-End Environment Handling Example

 This section illustrates how the different components of the environment handling system interact during a typical reinforcement learning training process.

 
```

```

 Sources: [baselines/common/cmd_util.py22-105](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py#L22-L105) [baselines/common/vec_env/dummy_vec_env.py31-57](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py#L31-L57) [baselines/common/vec_env/subproc_vec_env.py75-88](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py#L75-L88) [baselines/logger.py193-218](https://github.com/openai/baselines/blob/ea25b9e8/baselines/logger.py#L193-L218)

 
## Summary

 The environment handling system in OpenAI Baselines provides a comprehensive infrastructure for creating, configuring, and managing reinforcement learning environments. Key features include:

 
 - **Environment Creation**: Functions like `make_vec_env` and `make_env` streamline the creation of different environment types.
 - **Vectorized Environments**: The `VecEnv` class hierarchy enables parallel environment execution for improved throughput.
 - **Environment Wrappers**: Various wrappers modify and standardize environment behavior for different domains.
 - **Monitoring**: The monitoring system tracks and logs performance metrics during training.
 
 This infrastructure allows algorithms to interact with environments in a consistent way, regardless of the underlying environment type or implementation details, while optimizing for performance and flexibility.

 Sources: [baselines/common/cmd_util.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/cmd_util.py) [baselines/common/vec_env/\_\_init\_\_.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/\_\_init\_\_.py) [baselines/common/vec_env/dummy_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/dummy_vec_env.py) [baselines/common/vec_env/subproc_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/subproc_vec_env.py) [baselines/common/vec_env/shmem_vec_env.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/common/vec_env/shmem_vec_env.py) [baselines/logger.py](https://github.com/openai/baselines/blob/ea25b9e8/baselines/logger.py)
