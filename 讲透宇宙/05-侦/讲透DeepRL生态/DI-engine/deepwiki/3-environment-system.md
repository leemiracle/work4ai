> 来源: [https://deepwiki.com/opendilab/DI-engine/3-environment-system](https://deepwiki.com/opendilab/DI-engine/3-environment-system)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Environment System

  Relevant source files 
 - [ding/bonus/config.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/bonus/config.py)
 - [ding/bonus/ppof.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/bonus/ppof.py)
 - [ding/data/level_replay/level_sampler.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/data/level_replay/level_sampler.py)
 - [ding/envs/env/default_wrapper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/default_wrapper.py)
 - [ding/envs/env/ding_env_wrapper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/ding_env_wrapper.py)
 - [ding/envs/env/tests/test_ding_env_wrapper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/tests/test_ding_env_wrapper.py)
 - [ding/envs/env_manager/base_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/base_env_manager.py)
 - [ding/envs/env_manager/gym_vector_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/gym_vector_env_manager.py)
 - [ding/envs/env_manager/subprocess_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py)
 - [ding/envs/env_manager/tests/conftest.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/tests/conftest.py)
 - [ding/envs/env_manager/tests/test_base_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/tests/test_base_env_manager.py)
 - [ding/envs/env_manager/tests/test_env_supervisor.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/tests/test_env_supervisor.py)
 - [ding/envs/env_manager/tests/test_gym_vector_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/tests/test_gym_vector_env_manager.py)
 - [ding/envs/env_manager/tests/test_subprocess_env_manager.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/tests/test_subprocess_env_manager.py)
 - [ding/envs/env_wrappers/env_wrappers.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_wrappers/env_wrappers.py)
 - [ding/example/dqn_nstep_gymnasium.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/example/dqn_nstep_gymnasium.py)
 - [ding/framework/middleware/functional/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/functional/__init__.py)
 - [ding/framework/middleware/functional/logger.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/functional/logger.py)
 - [ding/framework/middleware/tests/test_logger.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/tests/test_logger.py)
 - [ding/model/template/hpt.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/hpt.py)
 - [ding/model/template/tests/test_hpt.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/model/template/tests/test_hpt.py)
 - [ding/torch_utils/loss/tests/test_contrastive_loss.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/loss/tests/test_contrastive_loss.py)
 - [ding/torch_utils/optimizer_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/optimizer_helper.py)
 - [ding/torch_utils/tests/test_optimizer.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/tests/test_optimizer.py)
 - [ding/worker/collector/tests/speed_test/fake_env.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/tests/speed_test/fake_env.py)
 - [ding/worker/collector/tests/test_marine_parallel_collector.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/worker/collector/tests/test_marine_parallel_collector.py)
 
  The Environment System in DI-engine is responsible for managing and interfacing with reinforcement learning environments. It provides a standardized way to interact with various environments, handle environment parallelization, and implement custom wrappers to modify environment behavior.

 This page covers the core architecture and components of the environment system, explaining how environments are wrapped, managed, and used in reinforcement learning training pipelines. For information about configuring environments, see [Configuration System](https://deepwiki.com/opendilab/DI-engine/2.1-configuration-system), and for details on how environments integrate with the training pipeline, see [Pipeline System](https://deepwiki.com/opendilab/DI-engine/6-training-pipelines).

 
## Architecture Overview

 
```

```

 The Environment System consists of three main components:

 
 - **Environment Interface (BaseEnv)**: The base interface that all environments must implement
 - **Environment Wrapper (DingEnvWrapper)**: A wrapper that standardizes environment interfaces
 - **Environment Managers**: Components that manage multiple environments for parallel execution
 
 Sources: [ding/envs/env_manager/base_env_manager.py19-91](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/base_env_manager.py#L19-L91) [ding/envs/env/ding_env_wrapper.py17-24](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/ding_env_wrapper.py#L17-L24) [ding/envs/env_manager/subprocess_env_manager.py34-42](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py#L34-L42)

 
## Environment States

 
```

```

 Environments in DI-engine are managed through a state machine that tracks the status of each environment. The possible states are:

 
 - **VOID**: Initial state, environment resources not allocated
 - **INIT**: Environment initialized but not reset
 - **RESET**: Environment currently resetting
 - **RUN**: Environment active and ready for interaction
 - **DONE**: Environment completed all episodes
 - **ERROR**: Error occurred in the environment
 - **NEED_RESET**: Environment needs a manual reset
 
 Sources: [ding/envs/env_manager/base_env_manager.py20-27](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/base_env_manager.py#L20-L27)

 
## Environment Interface

 
### BaseEnv

 `BaseEnv` is the core interface that all environments must implement. It defines methods for interaction with reinforcement learning algorithms:

 
```

```

 `BaseEnvTimestep` is a namedtuple that contains the result of a step in the environment:

 
 - `obs`: The observation after taking the action
 - `reward`: The reward received from the action
 - `done`: Whether the episode is done
 - `info`: Additional information provided by the environment
 
 Sources: [ding/envs/env/ding_env_wrapper.py17-24](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/ding_env_wrapper.py#L17-L24)

 
### DingEnvWrapper

 `DingEnvWrapper` is a concrete implementation of `BaseEnv` that wraps both gym and gymnasium environments to provide a consistent interface. It handles various environment-specific details and provides additional functionality:

 
```

```

 Key features of `DingEnvWrapper`:

 
 - Supports both gym and gymnasium environments
 - Handles action scaling and reward clipping
 - Manages environment wrappers for preprocessing observations or modifying environment behavior
 - Creates separate environment configurations for collectors and evaluators
 - Supports saving replay videos for visualization
 
 Sources: [ding/envs/env/ding_env_wrapper.py26-370](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/ding_env_wrapper.py#L26-L370)

 
## Environment Managers

 Environment managers in DI-engine handle multiple environments for parallel execution, which is essential for efficient data collection in reinforcement learning.

 
### BaseEnvManager

 `BaseEnvManager` is an abstract class that defines the interface for environment managers. It handles environment creation, reset, step, seed, and close operations for multiple environments.

 
```

```

 Key features of `BaseEnvManager`:

 
 - Manages multiple environments with unique IDs
 - Tracks environment states
 - Handles environment resets and seeds
 - Provides access to ready observations for action selection
 - Supports automatic environment reset when episodes are done
 
 Sources: [ding/envs/env_manager/base_env_manager.py63-564](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/base_env_manager.py#L63-L564)

 
### AsyncSubprocessEnvManager

 `AsyncSubprocessEnvManager` runs environments in separate subprocesses for true parallel execution. It communicates with environment processes through pipes and can use shared memory for efficient data transfer.

 
```

```

 Key features of `AsyncSubprocessEnvManager`:

 
 - Runs environments in separate subprocesses for true parallelism
 - Uses pipes for communication between main process and subprocesses
 - Can use shared memory for efficient observation transfer
 - Supports environment timeouts to handle hanging environments
 - Provides robust error handling and environment recovery
 
 Sources: [ding/envs/env_manager/subprocess_env_manager.py34-651](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py#L34-L651)

 
### SyncSubprocessEnvManager

 `SyncSubprocessEnvManager` is a synchronous version of the subprocess environment manager. It also runs environments in separate processes but steps through them synchronously.

 
```

```

 The main difference between `AsyncSubprocessEnvManager` and `SyncSubprocessEnvManager` is in the `step` method:

 
 - `AsyncSubprocessEnvManager` allows collecting data from ready environments without waiting for all environments
 - `SyncSubprocessEnvManager` steps through all environments in lockstep
 
 Sources: [ding/envs/env_manager/subprocess_env_manager.py677-776](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py#L677-L776)

 
## Environment Wrappers

 DI-engine includes a variety of environment wrappers that modify environment behavior for different purposes. These wrappers can be composed to create complex preprocessing pipelines.

 
### Common Environment Wrappers

 
```

```

 Common environment wrappers in DI-engine include:

 
 - **Observation processing wrappers**:

 
 - `WarpFrameWrapper`: Resizes frames to a standard size (usually 84x84)
 - `ScaledFloatFrameWrapper`: Normalizes observations to [0,1]
 - `FrameStackWrapper`: Stacks multiple frames as a single observation
 - `ObsTransposeWrapper`: Transposes observation dimensions
 - **Reward processing wrappers**:

 
 - `ClipRewardWrapper`: Clips rewards to {-1, 0, +1}
 - `DelayRewardWrapper`: Accumulates rewards and returns them at intervals
 - **Episode management wrappers**:

 
 - `MaxAndSkipWrapper`: Skips frames for faster execution
 - `NoopResetWrapper`: Executes random no-ops on reset
 - `EpisodicLifeWrapper`: Treats loss of life as end of episode
 - `FireResetWrapper`: Executes 'fire' action on reset
 - `EvalEpisodeReturnWrapper`: Evaluates the episode return
 - **Compatibility wrappers**:

 
 - `GymToGymnasiumWrapper`: Adapts Gym environments to Gymnasium interface
 
 Sources: [ding/envs/env_wrappers/env_wrappers.py44-423](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_wrappers/env_wrappers.py#L44-L423) [ding/envs/env/default_wrapper.py7-47](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/default_wrapper.py#L7-L47)

 
### Default Wrapper Configurations

 DI-engine provides default wrapper configurations for common environment types:

 
 - **Atari environments**:

 
 - NoopReset → MaxAndSkip → EpisodicLife → FireReset → WarpFrame → ScaledFloat → ClipReward → FrameStack
 - **Mujoco environments**:

 
 - EvalEpisodeReturn
 - **Gymnasium environments**:

 
 - GymToGymnasium
 
 These default configurations can be accessed through the `get_default_wrappers` function:

 
```

```

 Sources: [ding/envs/env/default_wrapper.py8-43](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env/default_wrapper.py#L8-L43)

 
## Usage Examples

 
### Creating and Using Environments

 
```

```

 
### Using Environment Managers for Parallel Execution

 
```

```

 Sources: [ding/bonus/ppof.py239-266](https://github.com/opendilab/DI-engine/blob/c290a673/ding/bonus/ppof.py#L239-L266) [ding/example/dqn_nstep_gymnasium.py21-29](https://github.com/opendilab/DI-engine/blob/c290a673/ding/example/dqn_nstep_gymnasium.py#L21-L29)

 
## Integration with Training Pipeline

 The Environment System integrates with the Training Pipeline through environment managers and specialized middleware components. The typical workflow is:

 
 - Create an environment wrapper (`DingEnvWrapper`) for the target environment
 - Create environment manager(s) for collector and evaluator
 - Use middleware components like `StepCollector` and `interaction_evaluator` to interact with the environments
 - Process the collected data through the policy and update the model
 
 
```

```

 Sources: [ding/bonus/ppof.py240-266](https://github.com/opendilab/DI-engine/blob/c290a673/ding/bonus/ppof.py#L240-L266) [ding/framework/middleware/functional/__init__.py3-15](https://github.com/opendilab/DI-engine/blob/c290a673/ding/framework/middleware/functional/__init__.py#L3-L15)

 
## Best Practices

 
 - **Environment Selection**: Choose the appropriate environment for your task, ensuring it has the right observation and action spaces.
 - **Environment Wrappers**: Use environment wrappers to preprocess observations, modify rewards, or change episode termination conditions. Combine multiple wrappers to create a custom preprocessing pipeline.
 - **Environment Managers**: Use `AsyncSubprocessEnvManager` for efficient data collection with true parallelism. Use `SyncSubprocessEnvManager` when synchronization between environments is important.
 - **Reproducibility**: Set seeds for environments to ensure reproducible results using the `seed` method.
 - **Resource Management**: Always close environments and environment managers when they are no longer needed to free up resources.
 - **Visualization**: Use `enable_save_replay` to save videos of environment interactions for visualization and debugging.
 
 
## Advanced Features

 
### Shared Memory for Efficient Observation Transfer

 The subprocess environment managers support using shared memory for efficient observation transfer between processes, which can significantly improve performance for environments with large observations (like images).

 
```

```

 Sources: [ding/envs/env_manager/subprocess_env_manager.py106-122](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py#L106-L122)

 
### Error Handling and Recovery

 The environment managers include robust error handling and recovery mechanisms, including:

 
 - Timeout handling for environment steps and resets
 - Error recovery through environment reset or recreation
 - Detection of abnormal timesteps
 
 
```

```

 Sources: [ding/envs/env_manager/subprocess_env_manager.py403-444](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/subprocess_env_manager.py#L403-L444) [ding/envs/env_manager/base_env_manager.py30-62](https://github.com/opendilab/DI-engine/blob/c290a673/ding/envs/env_manager/base_env_manager.py#L30-L62)
