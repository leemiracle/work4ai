> 来源: [https://deepwiki.com/AgileRL/AgileRL/8-configuration-and-benchmarking](https://deepwiki.com/AgileRL/AgileRL/8-configuration-and-benchmarking)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Configuration and Benchmarking

  Relevant source files 
 - [benchmarking/benchmarking_bandits.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py)
 - [benchmarking/benchmarking_off_policy_distributed.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_off_policy_distributed.py)
 - [benchmarking/benchmarking_offline.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline.py)
 - [benchmarking/benchmarking_offline_distributed.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py)
 - [benchmarking/benchmarking_on_policy.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py)
 - [benchmarking/make_evolvable_benchmarking.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/make_evolvable_benchmarking.py)
 - [configs/training/td3.yaml](https://github.com/AgileRL/AgileRL/blob/03307c7b/configs/training/td3.yaml)
 
  This document covers AgileRL's configuration system and benchmarking framework. The configuration system uses YAML files to define hyperparameters, network architectures, and training settings with support for evolutionary optimization bounds. The benchmarking framework provides comprehensive scripts for evaluating different RL paradigms including on-policy, off-policy, offline, multi-agent, and contextual bandit algorithms.

 For information about the actual training implementations, see [Training Framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework). For details about the evolutionary optimization process, see [Evolutionary Hyperparameter Optimization](https://deepwiki.com/AgileRL/AgileRL/4-evolutionary-hyperparameter-optimization).

 
## Configuration Architecture

 AgileRL's configuration system is built around YAML files that define three main sections: initialization hyperparameters (`INIT_HP`), mutation parameters (`MUTATION_PARAMS`), and network configurations (`NET_CONFIG`). The system integrates with the evolutionary optimization framework through the `HyperparameterConfig` and `RLParameter` classes.

 
```

```

 Sources: [configs/training/td3.yaml1-65](https://github.com/AgileRL/AgileRL/blob/03307c7b/configs/training/td3.yaml#L1-L65) [benchmarking/benchmarking_on_policy.py78-94](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L78-L94) [benchmarking/benchmarking_bandits.py73-87](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L73-L87)

 
## Benchmarking Framework Architecture

 The benchmarking framework consists of specialized scripts for each RL paradigm, all following a consistent pattern of configuration loading, environment setup, population creation, and training execution. The framework supports both single-node and distributed training configurations.

 
```

```

 Sources: [benchmarking/benchmarking_bandits.py23-138](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L23-L138) [benchmarking/benchmarking_on_policy.py24-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L24-L143) [benchmarking/benchmarking_off_policy_distributed.py22-104](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_off_policy_distributed.py#L22-L104)

 
## Configuration Structure

 
### INIT_HP Section

 The `INIT_HP` section defines core training parameters including environment settings, algorithm selection, and training limits. These parameters are used directly by the training functions and remain constant during evolutionary optimization.

 
| Parameter | Purpose | Example Values |
|---|---|---|
| ENV_NAME | Gymnasium environment identifier | "LunarLanderContinuous-v3" |
| ALGO | Algorithm selection | "TD3", "PPO", "DQN" |
| MAX_STEPS | Maximum training steps | 1_000_000 |
| POP_SIZE | Population size for evolution | 4, 6 |
| BATCH_SIZE | Training batch size | 128, 256 |
| MEMORY_SIZE | Replay buffer capacity | 100000 |
| TARGET_SCORE | Early stopping threshold | 200.0 |

 Sources: [configs/training/td3.yaml3-32](https://github.com/AgileRL/AgileRL/blob/03307c7b/configs/training/td3.yaml#L3-L32) [benchmarking/benchmarking_offline_distributed.py101-124](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py#L101-L124)

 
### MUTATION_PARAMS Section

 The `MUTATION_PARAMS` section defines evolutionary optimization parameters including mutation probabilities and hyperparameter bounds. These parameters control how the evolutionary process modifies agents during training.

 
```

```

 Sources: [configs/training/td3.yaml34-49](https://github.com/AgileRL/AgileRL/blob/03307c7b/configs/training/td3.yaml#L34-L49) [benchmarking/benchmarking_offline_distributed.py126-137](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py#L126-L137)

 
### NET_CONFIG Section

 The `NET_CONFIG` section specifies network architecture parameters including layer configurations and architectural bounds for evolution. This section is used when creating networks through the configuration system rather than explicit network objects.

 
```

```

 Sources: [configs/training/td3.yaml51-65](https://github.com/AgileRL/AgileRL/blob/03307c7b/configs/training/td3.yaml#L51-L65) [benchmarking/benchmarking_offline_distributed.py139-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py#L139-L143)

 
## Hyperparameter Configuration Classes

 
### HyperparameterConfig

 The `HyperparameterConfig` class defines the structure for evolvable hyperparameters, specifying which parameters can be mutated and their bounds. Each hyperparameter is defined as an `RLParameter` with minimum and maximum values.

 
```

```

 Sources: [benchmarking/benchmarking_on_policy.py78-94](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L78-L94) [benchmarking/benchmarking_bandits.py73-87](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L73-L87)

 
### RLParameter

 The `RLParameter` class defines individual hyperparameters with their bounds, data types, and optional scaling factors. Parameters can specify growth and shrink factors for evolutionary mutations.

 
```

```

 Sources: [benchmarking/benchmarking_bandits.py80-86](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L80-L86)

 
## Benchmarking Script Patterns

 
### Standard Benchmarking Flow

 All benchmarking scripts follow a consistent pattern for setup, execution, and evaluation. The `main()` function in each script implements this standardized flow.

 
```

```

 Sources: [benchmarking/benchmarking_on_policy.py24-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L24-L143) [benchmarking/benchmarking_bandits.py23-138](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L23-L138)

 
### Environment Setup Patterns

 The benchmarking scripts handle different environment types through consistent setup patterns. Each script adapts to its specific environment requirements while maintaining the same interface.

 
| Environment Type | Setup Pattern | Key Components |
|---|---|---|
| Standard Gym | make_vect_envs() | Vectorized environments, observation space handling |
| Atari | AtariPreprocessing, ClipReward | Frame stacking, reward clipping |
| Multi-Agent | pettingzoo environments | Agent coordination, shared observation/action spaces |
| Bandit | BanditEnv wrapper | Context-action mapping, reward structure |

 Sources: [benchmarking/benchmarking_on_policy.py29-34](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L29-L34) [make_evolvable_benchmarking.py42-45](https://github.com/AgileRL/AgileRL/blob/03307c7b/make_evolvable_benchmarking.py#L42-L45) [benchmarking/benchmarking_bandits.py36-37](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L36-L37)

 
## Distributed Training Configuration

 
### Accelerator Integration

 Distributed benchmarking scripts use HuggingFace Accelerate for multi-GPU and multi-node training. The `Accelerator` class handles device management and process synchronization.

 
```

```

 The accelerator is passed to key components including `Mutations`, `create_population`, and training functions to enable distributed execution.

 Sources: [benchmarking/benchmarking_off_policy_distributed.py23-28](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_off_policy_distributed.py#L23-L28) [benchmarking/benchmarking_offline_distributed.py23-28](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py#L23-L28)

 
### Distributed Component Configuration

 Components in distributed training are configured to work with the accelerator device and synchronization mechanisms. The replay buffer, mutations, and agent population all receive the accelerator instance.

 
```

```

 Sources: [benchmarking/benchmarking_off_policy_distributed.py37-64](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_off_policy_distributed.py#L37-L64) [benchmarking/benchmarking_offline_distributed.py39-71](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_offline_distributed.py#L39-L71)

 
## MakeEvolvable Benchmarking

 
### Custom Network Integration

 The `make_evolvable_benchmarking.py` script demonstrates how to integrate custom PyTorch networks with AgileRL's evolutionary system using the `MakeEvolvable` wrapper. This approach allows users to evolve arbitrary network architectures.

 
```

```

 Sources: [make_evolvable_benchmarking.py101-108](https://github.com/AgileRL/AgileRL/blob/03307c7b/make_evolvable_benchmarking.py#L101-L108)

 
### Multi-Paradigm Support

 The MakeEvolvable benchmarking script supports multiple RL paradigms and environment types within a single script, demonstrating the flexibility of the wrapper approach.

 
```

```

 Sources: [make_evolvable_benchmarking.py356-489](https://github.com/AgileRL/AgileRL/blob/03307c7b/make_evolvable_benchmarking.py#L356-L489)

 
## Configuration Loading and Validation

 
### YAML Loading Pattern

 All benchmarking scripts use a consistent pattern for loading and validating YAML configurations. The configuration is loaded using `yaml.safe_load()` and unpacked into the required sections.

 
```

```

 Sources: [benchmarking/benchmarking_on_policy.py136-143](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_on_policy.py#L136-L143) [benchmarking/benchmarking_bandits.py131-138](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_bandits.py#L131-L138)

 
### Parameter Validation

 The benchmarking scripts include parameter validation and default value handling for optional parameters. This ensures robust execution across different configuration variations.

 
```

```

 Sources: [make_evolvable_benchmarking.py338-340](https://github.com/AgileRL/AgileRL/blob/03307c7b/make_evolvable_benchmarking.py#L338-L340) [benchmarking/benchmarking_off_policy_distributed.py81-83](https://github.com/AgileRL/AgileRL/blob/03307c7b/benchmarking/benchmarking_off_policy_distributed.py#L81-L83)
