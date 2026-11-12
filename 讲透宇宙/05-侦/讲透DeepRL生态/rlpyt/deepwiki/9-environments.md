> 来源: [https://deepwiki.com/astooke/rlpyt/9-environments](https://deepwiki.com/astooke/rlpyt/9-environments)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Environments

  Relevant source files 
 - [rlpyt/envs/atari/atari_env.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/atari/atari_env.py)
 - [rlpyt/envs/gym.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/gym.py)
 - [rlpyt/samplers/collectors.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/samplers/collectors.py)
 - [rlpyt/spaces/composite.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/composite.py)
 - [rlpyt/spaces/float_box.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/float_box.py)
 - [rlpyt/spaces/gym_wrapper.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/gym_wrapper.py)
 - [rlpyt/spaces/gym_wrapper_schema.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/gym_wrapper_schema.py)
 - [rlpyt/spaces/int_box.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/int_box.py)
 - [rlpyt/utils/tensor.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/utils/tensor.py)
 - [tests/__init__.py](https://github.com/astooke/rlpyt/blob/f04f23db/tests/__init__.py)
 - [tests/test_gym_wrapper.py](https://github.com/astooke/rlpyt/blob/f04f23db/tests/test_gym_wrapper.py)
 - [tests/test_serial_sampler.py](https://github.com/astooke/rlpyt/blob/f04f23db/tests/test_serial_sampler.py)
 
  
## Overview

 The environment system in rlpyt provides a standardized interface for reinforcement learning environments, supporting both custom implementations and wrappers for existing environment libraries like OpenAI Gym. This page documents the environment interfaces, built-in environments, and wrappers available in rlpyt.

 Environments in rlpyt form a critical bridge between agents and the reinforcement learning problem. They define the observation and action spaces, implement the dynamics of the task, and provide feedback in the form of rewards.

 For information about how samplers interact with environments to collect experience, see [Samplers](https://deepwiki.com/astooke/rlpyt/6-samplers).

 
## Environment Interface

 
```

```

 Sources: [rlpyt/envs/atari/atari_env.py33-228](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/atari/atari_env.py#L33-L228) [rlpyt/envs/gym.py13-89](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/gym.py#L13-L89)

 The core environment interface in rlpyt is defined by the `Env` class. All environments must implement:

 
 - `reset()`: Resets the environment to an initial state and returns the initial observation
 - `step(action)`: Takes an action, advances the environment, and returns an `EnvStep`
 - `spaces`: Property returning an `EnvSpaces` instance containing the observation and action spaces
 
 The `EnvStep` is a container with four elements:

 
 - `observation`: The new observation after taking the action
 - `reward`: The reward received for the action
 - `done`: A boolean indicating if the episode has ended
 - `env_info`: Additional information as a namedtuple (environment-specific)
 
 
## Space Types

 
```

```

 Sources: [rlpyt/spaces/int_box.py7-49](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/int_box.py#L7-L49) [rlpyt/spaces/float_box.py7-51](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/float_box.py#L7-L51) [rlpyt/spaces/composite.py6-45](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/composite.py#L6-L45)

 Spaces define the format and constraints of observations and actions. The main space types are:

 
### IntBox

 `IntBox` represents a box of discrete integers with specificiable bounds. It's typically used for:

 
 - Discrete action spaces (e.g., selecting one of N actions)
 - Pixel observations in environments like Atari (as uint8 arrays)
 
 
```

```

 
### FloatBox

 `FloatBox` represents a box of continuous values with specificiable bounds. It's typically used for:

 
 - Continuous action spaces (e.g., joint torques in robotics tasks)
 - Processed observations (e.g., normalized sensor readings)
 
 
```

```

 
### Composite

 `Composite` combines multiple spaces into a single space, using named tuples to organize the components. It's useful for:

 
 - Complex observation spaces with multiple modalities
 - Action spaces that combine discrete and continuous components
 
 
## Built-in Environments

 
### Atari Environments

 
```

```

 Sources: [rlpyt/envs/atari/atari_env.py20-251](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/atari/atari_env.py#L20-L251)

 rlpyt provides a custom implementation of Atari environments using the Arcade Learning Environment (ALE). The `AtariEnv` class includes:

 
 - **Frame skipping**: Repeating the same action for multiple frames to improve efficiency
 - **Frame stacking**: Combining multiple frames to represent the observation to capture temporal information
 - **Observation processing**: Max pooling between frames, cropping, and downsampling to (80, 104)
 - **Game options**: Support for episodic lives, reward clipping, and random start noops
 - **Diagnostics**: Tracking of raw game score separate from clipped rewards
 
 Key parameters:

 
 - `game`: The Atari game to play (e.g., "pong", "breakout")
 - `frame_skip`: Number of frames to repeat each action
 - `num_img_obs`: Number of frames to stack in each observation
 - `clip_reward`: Whether to clip rewards to {-1, 0, 1}
 - `episodic_lives`: Whether losing a life ends the episode (while continuing the game)
 
 The `AtariTrajInfo` class tracks trajectory information specific to Atari games, such as the raw game score.

 
## Environment Wrappers

 
```

```

 Sources: [rlpyt/envs/gym.py13-172](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/envs/gym.py#L13-L172) [rlpyt/spaces/gym_wrapper.py10-138](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/spaces/gym_wrapper.py#L10-L138)

 
### OpenAI Gym Integration

 rlpyt provides wrappers to use environments from OpenAI Gym. The main components are:

 
#### GymEnvWrapper

 The `GymEnvWrapper` converts Gym environments to the rlpyt interface:

 
 - Wraps Gym's observation and action spaces with `GymSpaceWrapper`
 - Converts Gym's dictionary-based `info` to namedtuples for consistency and efficiency
 - Detects time limits in Gym environments and adds `timeout` flags to `env_info`
 - Provides conversion methods for observations and actions
 
 
```

```

 
#### GymSpaceWrapper

 The `GymSpaceWrapper` adapts Gym spaces to rlpyt spaces:

 
 - Handles conversion between Gym's dictionary spaces and rlpyt's namedtuples
 - Provides methods for sampling and generating null values
 - Ensures correct data types (e.g., converting float64 to float32)
 
 
### EnvInfoWrapper

 The `EnvInfoWrapper` ensures consistent information dictionaries:

 
 - Fills in missing keys in the environment info dictionary
 - Useful for environments that provide inconsistent information between steps
 - Helps prevent errors in samplers that expect specific keys
 
 
## Environment Interaction

 
```

```

 Sources: [rlpyt/samplers/collectors.py10-119](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/samplers/collectors.py#L10-L119)

 Environments in rlpyt are primarily interacted with through collectors, which gather batches of experience:

 
### BaseCollector

 The `BaseCollector` defines the interface for collectors:

 
 - `start_envs()`: Initializes environments, typically by calling `reset()`
 - `collect_batch()`: Collects a batch of transitions by stepping environments
 - `reset_if_needed()`: Resets environments when episodes end
 
 
### DecorrelatingStartCollector

 The `DecorrelatingStartCollector` extends the base collector with the ability to decorrelate initial states:

 
 - Takes random actions at the start of data collection to decorrelate states across parallel environments
 - Useful for preventing correlations in batch updates that could destabilize learning
 - Configurable with the `max_decorrelation_steps` parameter
 
 
## Example Usage

 Here's a simple example of how to create and use an environment in rlpyt:

 
```

```

 
```

```

 
## Environment Design Considerations

 When implementing custom environments for rlpyt, consider:

 
 - **Interface Compliance**: Ensure your environment implements the required `reset()` and `step()` methods with correct return types
 - **Space Definitions**: Define appropriate observation and action spaces using rlpyt's space classes
 - **Information Structure**: Use namedtuples for `env_info` to ensure consistency
 - **Timeout Handling**: Include a `timeout` field in `env_info` if your environment has a maximum episode length
 - **Observation Format**: Consider the dimensionality and type of observations (uint8 for pixels to save memory, float32 for continuous values)
 
 
## Environment Registration

 Unlike OpenAI Gym, rlpyt does not have a central environment registry. Instead:

 
 - For custom environments, define a class extending `Env` and instantiate it directly
 - For Gym environments, use the `make` function from `rlpyt.envs.gym`
 - For Atari environments, instantiate `AtariEnv` with the appropriate game name
