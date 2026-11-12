> 来源: [https://deepwiki.com/google/dopamine/3-environments](https://deepwiki.com/google/dopamine/3-environments)
> DeepWiki google/dopamine | Last indexed: 18 April 2025 (bec5f4

# Environments

  Relevant source files 
 - [dopamine/discrete_domains/__init__.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/__init__.py)
 - [dopamine/discrete_domains/atari_lib.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py)
 - [dopamine/discrete_domains/gym_lib.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py)
 - [dopamine/discrete_domains/legacy_networks.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/legacy_networks.py)
 - [dopamine/labs/environments/brax/__init__.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/__init__.py)
 - [dopamine/labs/environments/brax/brax_lib.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/brax_lib.py)
 - [dopamine/labs/environments/brax/sac_brax.gin](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/sac_brax.gin)
 - [dopamine/labs/environments/brax/train.py](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/train.py)
 
  This page documents the environment interfaces and wrappers in the Dopamine reinforcement learning framework. Environments represent the tasks or problems that reinforcement learning agents interact with. Dopamine provides a unified interface for working with various environment types, including specialized preprocessing and configuration options for each.

 For information about specific environment implementations like Atari, see [Atari Environments](https://deepwiki.com/google/dopamine/3.1-atari-environments). For other environment types, see [Other Environments](https://deepwiki.com/google/dopamine/3.2-other-environments).

 
## Environment Types and Creation

 Dopamine supports multiple environment types through dedicated creation functions, each providing appropriate preprocessing and wrappers to maintain a consistent interface across environment types.

 
```

```

 Sources: [dopamine/discrete_domains/atari_lib.py69-148](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L69-L148) [dopamine/discrete_domains/gym_lib.py59-101](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L59-L101) [dopamine/labs/environments/brax/brax_lib.py76-79](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/brax_lib.py#L76-L79)

 
### Supported Environment Types

 Dopamine provides specialized support for the following environment types:

 
| Environment Type | Creation Function | Wrapper Class | Action Space | Example Environments |
|---|---|---|---|---|
| Atari | create_atari_environment | AtariPreprocessing | Discrete | Pong, Breakout, Space Invaders |
| Gym | create_gym_environment | GymPreprocessing | Discrete/Continuous | CartPole, MountainCar, LunarLander |
| MuJoCo | create_gym_environment | GymPreprocessing | Continuous | Ant, HalfCheetah, Hopper, Humanoid |
| Brax | create_brax_environment | BraxEnv | Continuous | Ant, Humanoid, Fetch |

 Sources: [dopamine/discrete_domains/atari_lib.py69-148](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L69-L148) [dopamine/discrete_domains/gym_lib.py59-101](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L59-L101) [dopamine/labs/environments/brax/brax_lib.py76-79](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/brax_lib.py#L76-L79)

 
## Common Environment Interface

 All environment wrappers in Dopamine implement a consistent interface to standardize agent-environment interactions:

 
```

```

 Sources: [dopamine/discrete_domains/atari_lib.py458-667](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L458-L667) [dopamine/discrete_domains/gym_lib.py446-487](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L446-L487) [dopamine/labs/environments/brax/brax_lib.py30-73](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/labs/environments/brax/brax_lib.py#L30-L73)

 
## Environment Preprocessing

 Each environment type requires specific preprocessing to standardize observations and implement features like frame skipping.

 
### Atari Preprocessing

 The `AtariPreprocessing` class implements image preprocessing for Atari 2600 agents following the guidelines in Machado et al. (2018):

 
```

```

 Key preprocessing options:

 
 - **Frame skipping**: Default 4 frames, controls action frequency
 - **Terminal on life loss**: Optionally treats life loss as episode termination
 - **Observation processing**: Grayscale, max-pooling, and resizing to 84x84 pixels
 
 Sources: [dopamine/discrete_domains/atari_lib.py458-667](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L458-L667)

 
### Gym Preprocessing

 The `GymPreprocessing` class provides a simpler wrapper for Gym environments:

 
 - Handles API differences between legacy Gym and newer Gymnasium
 - Properly identifies true termination vs. time limit truncation
 - Maintains the `game_over` flag to identify true termination states
 
 Sources: [dopamine/discrete_domains/gym_lib.py446-487](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L446-L487)

 
## Environment Creation Process

 The environment creation functions encapsulate the process of creating and configuring environments with appropriate preprocessing.

 
### Atari Environment Creation

 
```

```

 Configuration options:

 
 - `game_name`: Name of the Atari 2600 domain
 - `sticky_actions`: Enable probabilistic action repetition (default: True)
 - `use_legacy_gym`: Use the legacy Gym API instead of Gymnasium (default: False)
 - `use_ppo_preprocessing`: Use PPO-specific preprocessing pipeline (default: False)
 - `continuous_action_threshold`: Optional threshold for continuous actions
 
 Sources: [dopamine/discrete_domains/atari_lib.py69-148](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L69-L148)

 
### Gym Environment Creation

 
```

```

 Configuration options:

 
 - `environment_name`: Name of the environment to run
 - `version`: Version of the environment to run (default: 'v0')
 - `use_legacy_gym`: Use the legacy Gym API (default: False)
 - `use_ppo_preprocessing`: Use PPO-specific preprocessing (default: False)
 
 Sources: [dopamine/discrete_domains/gym_lib.py59-101](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L59-L101)

 
## Integration with Agents

 Environments interact with agents following a standard interface pattern:

 
```

```

 Sources: [dopamine/discrete_domains/atari_lib.py577-629](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L577-L629) [dopamine/discrete_domains/gym_lib.py478-487](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L478-L487)

 
## Environment-Specific Network Architectures

 Different environment types often require specific network architectures to efficiently process their observations.

 
### Atari Observation Processing Networks

 Atari environments use convolutional network architectures to process image observations:

 
```

```

 Sources: [dopamine/discrete_domains/atari_lib.py179-249](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L179-L249)

 
### Gym Environment Networks

 Classic control environments use fully connected networks with optional normalization:

 
```

```

 Sources: [dopamine/discrete_domains/gym_lib.py104-164](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L104-L164)

 
## Environment Reference

 
### Atari Preprocessing Configuration

 
| Parameter | Default | Description |
|---|---|---|
| frame_skip | 4 | Number of frames to skip between agent actions |
| terminal_on_life_loss | False | Whether to treat life loss as episode termination |
| screen_size | 84 | Size of the resized observation (square) |
| use_legacy_gym | False | Whether to use legacy Gym API |

 Sources: [dopamine/discrete_domains/atari_lib.py475-492](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/atari_lib.py#L475-L492)

 
### MuJoCo Environments

 Dopamine supports the following MuJoCo environments via the Gym interface:

 
```

```

 Sources: [dopamine/discrete_domains/gym_lib.py56](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L56-L56)

 
### Network Type Constants

 Dopamine defines observation shape and data type constants for various environments:

 
```

```

 Sources: [dopamine/discrete_domains/gym_lib.py42-53](https://github.com/google/dopamine/blob/bec5f4e1/dopamine/discrete_domains/gym_lib.py#L42-L53)

 
## Conclusion

 Dopamine's environment interfaces provide a unified way to interact with various reinforcement learning environments. The framework includes specialized preprocessing and wrappers for different environment types, with particular emphasis on Atari games. The environment creation functions and wrapper classes ensure that all environments present a consistent interface to agents, simplifying the development of reinforcement learning algorithms.
