> 来源: [https://deepwiki.com/araffin/rl-baselines-zoo/3-configuration-system](https://deepwiki.com/araffin/rl-baselines-zoo/3-configuration-system)
> DeepWiki araffin/rl-baselines-zoo | Last indexed: 24 June 2025 (ff84f3

# Configuration System

  Relevant source files 
 - [benchmark.md](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/benchmark.md?plain=1)
 - [hyperparams/ddpg.yml](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ddpg.yml)
 - [hyperparams/ppo2.yml](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml)
 - [hyperparams/sac.yml](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/sac.yml)
 
  
## Purpose and Scope

 The Configuration System manages hyperparameters, environment settings, and algorithm-specific configurations across all reinforcement learning training and evaluation workflows in RL Baselines Zoo. This system enables reproducible training by storing algorithm-environment combinations with their optimized hyperparameters in structured YAML files.

 For detailed information about algorithm-specific hyperparameter configurations, see [Algorithm Configurations](https://deepwiki.com/araffin/rl-baselines-zoo/3.1-algorithm-configurations). For environment creation and wrapper management, see [Environment Management](https://deepwiki.com/araffin/rl-baselines-zoo/3.2-environment-management).

 
## Configuration Architecture

 The configuration system operates through a hierarchical structure that maps algorithms to environments with their respective hyperparameters:

 
```

```

 Sources: [hyperparams/ppo2.yml1-344](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L1-L344) [hyperparams/sac.yml1-184](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/sac.yml#L1-L184) [hyperparams/ddpg.yml1-87](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ddpg.yml#L1-L87)

 
## Configuration File Structure

 Each algorithm configuration file follows a consistent YAML structure mapping environment names to hyperparameter dictionaries:

 
```

```

 Sources: [hyperparams/ppo2.yml1-50](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L1-L50) [hyperparams/ppo2.yml68-103](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L68-L103) [hyperparams/ppo2.yml154-169](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L154-L169)

 
## Configuration Categories

 The system organizes configurations into distinct categories based on algorithm capabilities and environment types:

 
| Configuration Type | Description | Example Files |
|---|---|---|
| On-Policy Algorithms | Algorithms that learn from current policy | ppo2.yml, a2c.yml, acktr.yml, trpo.yml |
| Off-Policy Algorithms | Algorithms that learn from replay buffer | sac.yml, ddpg.yml, td3.yml, dqn.yml |
| Advanced Algorithms | Specialized algorithms with unique requirements | her.yml, acer.yml |

 
### Environment-Specific Adaptations

 Configurations adapt to environment characteristics through specialized parameters:

 
```

```

 Sources: [hyperparams/ppo2.yml1-12](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L1-L12) [hyperparams/sac.yml49-62](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/sac.yml#L49-L62) [hyperparams/ddpg.yml38-48](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ddpg.yml#L38-L48)

 
## Configuration Loading and Application

 The configuration system integrates with the training pipeline through a structured loading process:

 
```

```

 Sources: [hyperparams/ppo2.yml28-39](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L28-L39)

 
## Special Configuration Features

 
### Linear Schedule Parameters

 The system supports dynamic parameter scheduling using the `lin_` prefix:

 
| Parameter Format | Description | Example |
|---|---|---|
| lin_2.5e-4 | Linear decay from initial value to 0 | Learning rate scheduling |
| lin_0.1 | Linear decay for clipping parameters | Cliprange scheduling |

 
### Normalization Settings

 Environment normalization is configured through multiple approaches:

 
```

```

 
### Custom Environment Wrappers

 Configurations can specify environment modifications:

 
```

```

 Sources: [hyperparams/ppo2.yml155](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L155-L155) [hyperparams/sac.yml50](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/sac.yml#L50-L50) [hyperparams/ppo2.yml316](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/hyperparams/ppo2.yml#L316-L316)

 
## Performance-Driven Configuration

 The benchmark results demonstrate the effectiveness of the configuration system across algorithm-environment combinations:

 
| Algorithm | Best Performance Environments | Configuration Strategy |
|---|---|---|
| PPO2 | Atari, Bullet Physics | Balanced exploration-exploitation |
| SAC | Continuous Control | High sample efficiency |
| DDPG | Simple Continuous | Deterministic policies |
| TD3 | Complex Continuous | Improved critic training |

 The configuration system enables consistent performance across 9 algorithms and over 50 environments, with hyperparameters tuned for optimal results in each domain.

 Sources: [benchmark.md1-136](https://github.com/araffin/rl-baselines-zoo/blob/ff84f398/benchmark.md?plain=1#L1-L136)
