> 来源: [https://deepwiki.com/rlworkgroup/garage/4-environment-integration](https://deepwiki.com/rlworkgroup/garage/4-environment-integration)
> DeepWiki rlworkgroup/garage | Last indexed: 25 April 2025 (2d5948

# Environment Integration

  Relevant source files 
 - [docs/Makefile](https://github.com/rlworkgroup/garage/blob/2d594803/docs/Makefile)
 - [docs/conf.py](https://github.com/rlworkgroup/garage/blob/2d594803/docs/conf.py)
 - [docs/user/custom_worker.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/custom_worker.md?plain=1)
 - [docs/user/experiments.rst](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/experiments.rst)
 - [docs/user/implement_algo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_algo.md?plain=1)
 - [docs/user/implement_env.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.md?plain=1)
 - [docs/user/implement_env.rst](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.rst)
 - [docs/user/implement_worker.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_worker.md?plain=1)
 - [docs/user/installation.rst](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/installation.rst)
 - [docs/user/setting_up_your_development_environment.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/setting_up_your_development_environment.md?plain=1)
 - [docs/user/testing.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/testing.md?plain=1)
 - [docs/user/training_a_policy.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/training_a_policy.md?plain=1)
 - [readthedocs.yml](https://github.com/rlworkgroup/garage/blob/2d594803/readthedocs.yml)
 - [src/garage/envs/bullet/__init__.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/bullet/__init__.py)
 - [src/garage/envs/bullet/bullet_env.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/bullet/bullet_env.py)
 - [src/garage/envs/gym_env.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py)
 - [tests/garage/envs/bullet/__init__.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/envs/bullet/__init__.py)
 - [tests/garage/envs/bullet/test_bullet_env.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/envs/bullet/test_bullet_env.py)
 - [tests/garage/envs/test_gym_env.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/envs/test_gym_env.py)
 - [tests/garage/tf/envs/test_gym_base.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/tf/envs/test_gym_base.py)
 - [tests/helpers.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/helpers.py)
 
  This page explains how Garage integrates with external reinforcement learning environments and how to use different environment types within the framework. Environment integration is a critical component of Garage, as it provides the interface between reinforcement learning algorithms and the simulation environments they interact with.

 Garage abstracts environment interfaces using the `Environment` class, which provides a uniform API for all supported environment types. This allows algorithms to work consistently regardless of the underlying environment implementation.

 For information about creating custom environments, see [Custom Environments](https://deepwiki.com/rlworkgroup/garage/4.2-custom-environments). For details on environment wrappers, see [Environment Wrappers](https://deepwiki.com/rlworkgroup/garage/4.1-environment-wrappers).

 
## Environment Interface

 At the core of Garage's environment integration is the `Environment` interface, which standardizes how algorithms interact with environments.

 
```

```

 All environment implementations in Garage must adhere to this interface, which consists of:

 
 - **Properties**:

 
 - `observation_space`: Defines the structure and bounds of observations
 - `action_space`: Defines the structure and bounds of actions
 - `spec`: Environment specifications (combining the spaces and max episode length)
 - `render_modes`: Supported visualization modes
 - **Methods**:

 
 - `reset()`: Resets the environment to an initial state, returning the first observation and episode info
 - `step(action)`: Takes an action and returns an `EnvStep` (observation, reward, done, info)
 - `render(mode)`: Renders the environment in the specified mode
 - `visualize()`: Creates a visualization of the environment
 - `close()`: Closes the environment and releases resources
 
 Sources: [src/garage/envs/gym_env.py62-394](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L62-L394)

 
## Supported Environment Types

 Garage integrates with several popular environment libraries through environment wrapper classes.

 
```

```

 
### Gym Environments

 The most common environment type is the OpenAI Gym environment, which is wrapped using the `GymEnv` class. This wrapper provides compatibility with the vast ecosystem of Gym-based environments.

 
```

```

 Sources: [src/garage/envs/gym_env.py62-394](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L62-L394) [docs/user/implement_env.rst10-21](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.rst#L10-L21)

 
### PyBullet Environments

 PyBullet environments, which are physics-based simulation environments, are supported through the `BulletEnv` class, which extends `GymEnv` with PyBullet-specific functionality.

 
```

```

 When you create a `GymEnv` with a PyBullet environment, the `GymEnv` class automatically detects it and returns a `BulletEnv` instance instead.

 Sources: [src/garage/envs/gym_env.py83-113](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L83-L113) [src/garage/envs/bullet/bullet_env.py22-147](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/bullet/bullet_env.py#L22-L147)

 
### DeepMind Control Environments

 DeepMind Control Suite environments are supported through the `DmControlEnv` wrapper.

 
```

```

 
### MetaWorld Environments

 Garage also supports MetaWorld environments for meta-reinforcement learning research.

 
## Environment Integration Flow

 The following diagram illustrates how environments are integrated into the reinforcement learning training loop in Garage:

 
```

```

 Sources: [docs/user/experiments.rst20-28](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/experiments.rst#L20-L28)

 
## Environment Spaces and Specs

 Garage uses a library called `akro` to represent action and observation spaces, which is an extension of OpenAI Gym's space API. When you wrap an environment, the Gym spaces are automatically converted to `akro` spaces.

 
```

```

 The `EnvSpec` class combines the action and observation spaces with other environment specifications, such as the maximum episode length.

 Key points about environment spaces:

 
 - `akro.Box`: Represents continuous spaces with lower and upper bounds
 - `akro.Discrete`: Represents discrete spaces with a finite number of possible values
 - `akro.Image`: Represents image observations (normalized pixel values)
 - Spaces define the structure of both observations and actions
 
 Sources: [src/garage/envs/gym_env.py155-160](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L155-L160)

 
## Using Environments in Experiments

 Here's a typical pattern for using environments in Garage experiments:

 
```

```

 When using TensorFlow, you would use `TFTrainer` instead:

 
```

```

 Sources: [docs/user/experiments.rst30-90](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/experiments.rst#L30-L90) [docs/user/training_a_policy.md37-41](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/training_a_policy.md?plain=1#L37-L41)

 
## Environment Serialization

 Garage implements serialization (pickling) support for environments to enable experiment snapshots and resuming training. This requires special handling for environments with non-serializable components (like rendering viewers or physics server connections).

 The `GymEnv` and `BulletEnv` classes implement custom `__getstate__` and `__setstate__` methods to handle serialization and deserialization properly.

 For `GymEnv`:

 
 - When serialized, rendering viewers are temporarily removed
 - When deserialized, the environment is recreated from its parameters
 
 For `BulletEnv`:

 
 - Serialization stores constructor arguments
 - Deserialization creates a new connection to the PyBullet physics server
 
 Sources: [src/garage/envs/gym_env.py337-371](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L337-L371) [src/garage/envs/bullet/bullet_env.py81-147](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/bullet/bullet_env.py#L81-L147)

 
## Time Limits and Episode Termination

 Garage enhances the environment interface with standardized handling of episode termination, including:

 
 - Natural termination (the environment reaches a terminal state)
 - Time limit termination (the maximum episode length is reached)
 
 The `StepType` enum is used to indicate the type of step:

 
 - `FIRST`: First step after reset
 - `MID`: Middle step of an episode
 - `TERMINAL`: Terminal step (environment termination)
 - `TIMEOUT`: Time limit reached
 
 This information is included in the `EnvStep` returned by the `step()` method, allowing algorithms to distinguish between natural termination and timeout.

 Sources: [src/garage/envs/gym_env.py204-274](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L204-L274)

 
## Creating Custom Environment Wrappers

 If you need to integrate a new environment type with Garage, you can create a custom environment wrapper. The most common approach is to:

 
 - Inherit from `garage.Environment` or `garage.envs.GymEnv`
 - Implement the required properties and methods
 - Handle serialization if needed
 
 Key points for implementation:

 
 - Convert native spaces to `akro` spaces
 - Implement the `reset()` and `step()` methods
 - Manage environment resources properly in `close()`
 - Implement `__getstate__` and `__setstate__` if needed for serialization
 
 Sources: [docs/user/implement_env.rst21-48](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.rst#L21-L48) [docs/user/implement_env.md48-94](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.md?plain=1#L48-L94)

 
## Implementing a New Environment from Scratch

 You can also implement a completely new environment for Garage from scratch:

 
 - Create a class that inherits from `garage.Environment`
 - Define observation and action spaces using `akro`
 - Implement the required methods and properties
 - Implement the environment dynamics in `step()`
 
 
```

```

 Sources: [docs/user/implement_env.rst51-159](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.rst#L51-L159) [docs/user/implement_env.md96-276](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/implement_env.md?plain=1#L96-L276)

 
## Testing Environments

 When developing custom environments or environment wrappers, it's important to test them thoroughly. Garage provides helper functions for testing environments:

 
 - `step_env`: Simulates stepping through an environment
 - `step_env_with_gym_quirks`: Handles gym-specific testing behaviors
 
 Example test:

 
```

```

 For integrating with the testing system, environment tests should be placed in the `tests/garage/envs/` directory.

 Sources: [tests/helpers.py11-63](https://github.com/rlworkgroup/garage/blob/2d594803/tests/helpers.py#L11-L63) [tests/garage/envs/test_gym_env.py1-161](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/envs/test_gym_env.py#L1-L161) [docs/user/testing.md1-250](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/testing.md?plain=1#L1-L250)

 
## Common Issues and Solutions

 
### 1. Environment Rendering and Visualization

 Some environments have issues with rendering, especially when used in headless environments or when multiple environments are rendered simultaneously:

 
 - Gym environments from certain packages don't close their viewer windows properly
 - PyBullet environments allow only one GUI connection at a time
 - Some environments don't implement all render modes
 
 Garage includes workarounds for these issues in the environment wrappers.

 Sources: [src/garage/envs/gym_env.py275-335](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L275-L335) [src/garage/envs/bullet/bullet_env.py57-79](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/bullet/bullet_env.py#L57-L79)

 
### 2. Time Limit Handling

 Environments wrapped with `TimeLimit` in Gym have specific behaviors for episode termination:

 
 - `done=True` can indicate either natural termination or time limit reached
 - Garage adds `GymEnv.TimeLimitTerminated` to `info` to distinguish these cases
 
 Sources: [src/garage/envs/gym_env.py236-250](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L236-L250)

 
### 3. Environment Observation Space Compatibility

 Ensure that your environment's observations match its declared observation space:

 
 - Discrete observations can be either in the space directly or one-hot encoded
 - Image observations may need normalization
 - Garage checks that observations conform to the observation space
 
 Sources: [src/garage/envs/gym_env.py258-267](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/envs/gym_env.py#L258-L267)

 
## Conclusion

 Garage's environment integration system provides a flexible and extensible way to work with various environment types. By standardizing the environment interface and handling common issues, it allows algorithms to work seamlessly with different environments.

 Whether you're using built-in environment wrappers, adapting existing environments, or creating new ones from scratch, understanding these integration patterns will help you effectively use environments in your reinforcement learning experiments with Garage.
