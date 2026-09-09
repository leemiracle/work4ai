> 来源: [https://deepwiki.com/OpenRL-Lab/openrl/2-environment-system](https://deepwiki.com/OpenRL-Lab/openrl/2-environment-system)
> DeepWiki OpenRL-Lab/openrl | Last indexed: 28 April 2025 (4c92aa

# Environment System

  Relevant source files 
 - [openrl/envs/__init__.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/__init__.py)
 - [openrl/envs/common/build_envs.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/build_envs.py)
 - [openrl/envs/common/registration.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py)
 - [openrl/envs/mpe/rendering.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/mpe/rendering.py)
 - [openrl/envs/vec_env/async_venv.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/vec_env/async_venv.py)
 - [openrl/utils/callbacks/checkpoint_callback.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/utils/callbacks/checkpoint_callback.py)
 - [openrl/utils/evaluation.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/utils/evaluation.py)
 - [tests/test_env/test_vec_env/test_async_env.py](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/tests/test_env/test_vec_env/test_async_env.py)
 
  The Environment System in OpenRL provides a unified interface for creating, managing, and interacting with reinforcement learning environments. It serves as the foundation for agent-environment interactions in the framework, abstracting away the differences between various environment types and providing consistent vectorization capabilities for parallel execution.

 This document focuses on the core architecture and functionality of the environment system. For specific details on environment registration, see [Environment Registration](https://deepwiki.com/OpenRL-Lab/openrl/2.1-environment-registration). For information about vectorized environments implementation, see [Vectorized Environments](https://deepwiki.com/OpenRL-Lab/openrl/2.2-vectorized-environments).

 
## Core Architecture

 The Environment System in OpenRL follows a layered architecture that provides flexibility in supporting various environment types while maintaining a consistent interface for agent interaction.

 
```

```

 Sources: [openrl/envs/common/registration.py35-182](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L35-L182) [openrl/envs/common/build_envs.py11-72](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/build_envs.py#L11-L72)

 The central component of the environment system is the `make()` function, which serves as a factory method for creating environments based on their ID. It supports a wide range of environment types from various libraries and applies the appropriate vectorization and wrappers.

 
## Environment Types and Registry

 OpenRL supports multiple environment types through a registry-based approach. Environment IDs are mapped to specific environment creation functions based on their type.

 
```

```

 Sources: [openrl/envs/__init__.py1-29](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/__init__.py#L1-L29) [openrl/envs/common/registration.py64-165](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L64-L165)

 The environment registry is organized as lists of environment IDs grouped by their type. When creating an environment, the `make()` function checks which registry the environment ID belongs to and calls the appropriate creation function.

 
### Supported Environment Types

 OpenRL provides built-in support for a variety of environment types:

 
| Environment Type | Description | Examples |
|---|---|---|
| Gymnasium | Standard single-agent environments | CartPole, MuJoCo |
| PettingZoo | Multi-agent environments | TicTacToe, Snakes |
| MPE | Multi-agent Particle Environments | simple_spread |
| NLP | Natural Language Processing environments | daily_dialog, fake_dialog_data |
| Toy | Simple environments for testing | BitFlippingEnv, IdentityEnv |
| Gridworld | Grid-based environments | GridWorldEnv |
| Offline | Environments for offline RL | OfflineEnv |
| Custom | User-defined environments | Any custom implementation |

 Sources: [openrl/envs/__init__.py1-29](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/__init__.py#L1-L29) [openrl/envs/common/registration.py64-165](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L64-L165)

 
## Vectorized Environment Implementation

 One of the key features of OpenRL's environment system is its vectorization capability, which enables parallel execution of multiple environment instances. This is particularly useful for improving sample efficiency during training.

 
```

```

 Sources: [openrl/envs/vec_env/async_venv.py45-680](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/vec_env/async_venv.py#L45-L680) [openrl/envs/common/registration.py167-170](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L167-L170)

 OpenRL offers two types of vectorized environments:

 
 - **SyncVectorEnv**: Executes environments sequentially in a single process. Simpler implementation but does not leverage parallel processing.
 - **AsyncVectorEnv**: Executes environments in parallel using multiple processes. Provides improved performance but adds complexity due to inter-process communication.
 
 The `AsyncVectorEnv` implementation stands out for its sophistication in handling parallel execution:

 
 - Uses Python's `multiprocessing` module to create worker processes
 - Communication between the main process and worker processes happens through pipes
 - Implements an asynchronous API with separate `_send` and `_fetch` methods for operations
 - Handles shared memory for efficient observation transfer
 - Provides error handling for worker process failures
 
 The state machine for `AsyncVectorEnv` operations:

 
```

```

 Sources: [openrl/envs/vec_env/async_venv.py38-43](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/vec_env/async_venv.py#L38-L43) [openrl/envs/vec_env/async_venv.py186-190](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/vec_env/async_venv.py#L186-L190)

 
## Environment Creation Process

 The environment creation process in OpenRL follows a consistent pattern regardless of the environment type:

 
```

```

 Sources: [openrl/envs/common/registration.py35-182](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L35-L182) [openrl/envs/common/build_envs.py11-72](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/build_envs.py#L11-L72)

 The `make()` function serves as the entry point for environment creation:

 
```

```

 Sources: [openrl/envs/common/registration.py35-44](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L35-L44)

 
## Integration with Other Systems

 The Environment System integrates with several other components of the OpenRL framework:

 
```

```

 Sources: [openrl/envs/common/registration.py172-181](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L172-L181) [openrl/utils/evaluation.py13-165](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/utils/evaluation.py#L13-L165) [openrl/utils/callbacks/checkpoint_callback.py25-103](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/utils/callbacks/checkpoint_callback.py#L25-L103)

 Key integration points include:

 
 - **Agent Integration**: Agents interact with environments through the standard `reset()` and `step()` methods
 - **Reward System**: Custom reward functions can be applied through the `RewardWrapper`
 - **Monitoring**: Performance metrics are collected through the `VecMonitorWrapper`
 - **Callback System**: Environment states can trigger callbacks during training
 - **Evaluation**: The environment system is used by the `evaluate_policy()` function to evaluate agent performance
 
 
## Conclusion

 The Environment System in OpenRL provides a robust and flexible foundation for reinforcement learning experimentation. By abstracting away the differences between environment types and providing consistent vectorization capabilities, it enables researchers and practitioners to focus on algorithm development rather than environment management.

 Key strengths of the system include:

 
 - Unified interface for diverse environment types
 - Efficient parallelization through vectorized environments
 - Extensibility through custom environments and wrappers
 - Integration with monitoring and reward systems
 
 For extending the environment system with custom environments, see [Custom Environments](https://deepwiki.com/OpenRL-Lab/openrl/2.3-custom-environments).

 Sources: [openrl/envs/common/registration.py17-182](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/common/registration.py#L17-L182) [openrl/envs/vec_env/async_venv.py17-876](https://github.com/OpenRL-Lab/openrl/blob/4c92aa44/openrl/envs/vec_env/async_venv.py#L17-L876)
