> 来源: [https://deepwiki.com/takuseno/d3rlpy/12-api-reference](https://deepwiki.com/takuseno/d3rlpy/12-api-reference)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# API Reference

  Relevant source files 
 - [docs/references/dataset.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst)
 - [docs/references/datasets.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/datasets.rst)
 - [docs/references/index.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst)
 - [docs/references/off_policy_evaluation.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/off_policy_evaluation.rst)
 - [docs/tips.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst)
 
  This page provides comprehensive API documentation for all public classes, methods, and functions in d3rlpy. The API is organized by functional area to help you quickly locate the components you need for your reinforcement learning projects.

 For algorithm usage examples and tutorials, see [Quick Start Tutorial](https://deepwiki.com/takuseno/d3rlpy/3-quick-start-tutorial). For architectural concepts behind these APIs, see [Core Architecture](https://deepwiki.com/takuseno/d3rlpy/4-core-architecture) and [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For data handling patterns, see [Data Management](https://deepwiki.com/takuseno/d3rlpy/6-data-management).

 
## API Organization

 The d3rlpy API is structured around several core modules that correspond to different aspects of reinforcement learning:

 
```

```

 **Sources:** [docs/references/index.rst7-21](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L7-L21)

 
## Core Algorithm API

 The algorithm API forms the heart of d3rlpy, providing configuration-based interfaces for all supported reinforcement learning algorithms.

 
### Algorithm Configuration Pattern

 All algorithms in d3rlpy follow a consistent configuration-creation pattern:

 
```

```

 **Sources:** [docs/references/index.rst10](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L10-L10)

 
### Q-Learning Algorithm Configurations

 The `d3rlpy.algos` module provides configuration classes for Q-learning based algorithms:

 
| Algorithm | Configuration Class | Description |
|---|---|---|
| DQN | DQNConfig | Deep Q-Network for discrete actions |
| CQL | CQLConfig | Conservative Q-Learning for offline RL |
| SAC | SACConfig | Soft Actor-Critic for continuous control |
| BEAR | BEARConfig | Bootstrapping Error Accumulation Reduction |
| BCQ | BCQConfig | Batch-Constrained Q-Learning |
| AWR | AWRConfig | Advantage-Weighted Regression |
| AWAC | AWACConfig | Advantage-Weighted Actor-Critic |
| TD3 | TD3Config | Twin Delayed Deep Deterministic Policy Gradient |
| TD3+BC | TD3PlusBCConfig | TD3 with Behavior Cloning |

 **Sources:** [docs/references/index.rst10](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L10-L10)

 
### Transformer Algorithm Configurations

 For sequence modeling approaches:

 
| Algorithm | Configuration Class | Description |
|---|---|---|
| Decision Transformer | DecisionTransformerConfig | Sequence modeling for RL |
| Trajectory Transformer | TrajectedTransformerConfig | Trajectory-based sequence modeling |

 **Sources:** [docs/references/index.rst10](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L10-L10)

 
### Algorithm Base Classes

 The inheritance hierarchy for algorithm implementations:

 
```

```

 **Sources:** [docs/references/index.rst10](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L10-L10)

 
## Data Management API

 
### Dataset Loading Functions

 The `d3rlpy.datasets` module provides functions to load standard RL datasets:

 
| Function | Purpose | Return Type |
|---|---|---|
| get_d4rl() | Load D4RL datasets | (ReplayBuffer, gym.Env) |
| get_atari() | Load Atari datasets | (ReplayBuffer, gym.Env) |
| get_minari() | Load Minari datasets | (ReplayBuffer, gym.Env) |
| get_cartpole() | Load CartPole dataset | (ReplayBuffer, gym.Env) |
| get_pendulum() | Load Pendulum dataset | (ReplayBuffer, gym.Env) |
| get_dataset() | Load custom datasets | (ReplayBuffer, gym.Env) |

 **Sources:** [docs/references/datasets.rst9-20](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/datasets.rst#L9-L20)

 
### Replay Buffer System

 The replay buffer API follows a modular design with interchangeable components:

 
```

```

 **Sources:** [docs/references/dataset.rst69-142](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst#L69-L142) [docs/references/dataset.rst144-156](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst#L144-L156) [docs/references/dataset.rst159-197](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst#L159-L197) [docs/references/dataset.rst199-268](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst#L199-L268)

 
### Data Structures

 Core data structures for representing RL experiences:

 
| Class | Purpose | Key Fields |
|---|---|---|
| Episode | Single episode container | observations, actions, rewards, terminated |
| Transition | Single transition | observation, action, reward, next_observation, terminal |
| PartialTrajectory | Trajectory slice | observations, actions, returns_to_go, timesteps, masks |
| TransitionMiniBatch | Batch of transitions | Batched transition data |
| TrajectoryMiniBatch | Batch of trajectories | Batched trajectory data |

 **Sources:** [docs/references/dataset.rst59-60](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/dataset.rst#L59-L60)

 
## Model Components API

 
### Encoder Factories

 The `d3rlpy.models` module provides encoder factories for feature extraction:

 
```

```

 **Sources:** [docs/references/index.rst16](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L16-L16) [docs/tips.rst65-78](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst#L65-L78)

 
### Q-Function Factories

 Q-function architectures for value estimation:

 
| Factory Class | Architecture | Use Case |
|---|---|---|
| MeanQFunctionFactory | Standard Q-network | Basic value estimation |
| QRQFunctionFactory | Quantile Regression | Distributional RL |
| IQNQFunctionFactory | Implicit Quantile Networks | Advanced distributional RL |
| FQFQFunctionFactory | Fully Parameterized Quantile Function | State-of-the-art distributional RL |

 **Sources:** [docs/references/index.rst11](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L11-L11) [docs/tips.rst69](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst#L69-L69)

 
### Policy Architectures

 Policy network implementations:

 
| Class | Algorithm Family | Action Space |
|---|---|---|
| DeterministicPolicy | DDPG, TD3 | Continuous |
| StochasticPolicy | SAC | Continuous |
| CategoricalPolicy | DQN variants | Discrete |
| SquashedNormalPolicy | SAC variants | Continuous with bounds |

 **Sources:** [docs/references/index.rst16](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L16-L16)

 
## Preprocessing API

 
### Scaler System

 The `d3rlpy.preprocessing` module provides data normalization:

 
```

```

 **Sources:** [docs/references/index.rst14](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L14-L14) [docs/tips.rst50](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst#L50-L50)

 
## Metrics and Evaluation API

 
### Evaluation Metrics

 The `d3rlpy.metrics` module provides comprehensive evaluation tools:

 
| Metric Category | Classes | Purpose |
|---|---|---|
| Environment Evaluation | EnvironmentEvaluator | Test in actual environment |
| Value Estimation | InitialStateValueEstimationEvaluator | Estimate state values |
| Policy Evaluation | SoftOPCEvaluator | Off-policy confidence intervals |
| Scoring Functions | scorer decorators | Custom evaluation metrics |

 **Sources:** [docs/references/index.rst17](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L17-L17) [docs/references/off_policy_evaluation.rst26-29](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/off_policy_evaluation.rst#L26-L29)

 
### Off-Policy Evaluation

 The `d3rlpy.ope` module provides methods to evaluate policies without environment interaction:

 
```

```

 **Sources:** [docs/references/off_policy_evaluation.rst37-51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/off_policy_evaluation.rst#L37-L51)

 
## Logging API

 
### Experiment Tracking

 The `d3rlpy.logging` module provides adapters for popular experiment tracking tools:

 
| Adapter Class | Platform | Features |
|---|---|---|
| FileAdapterFactory | Local files | CSV/JSON logging |
| TensorBoardAdapterFactory | TensorBoard | Scalar/histogram tracking |
| WandbAdapterFactory | Weights & Biases | Cloud-based tracking |

 **Sources:** [docs/references/index.rst19](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L19-L19)

 
## Utilities and CLI API

 
### Environment Utilities

 The `d3rlpy.envs` module provides environment management functions:

 
| Function | Purpose |
|---|---|
| seed_env() | Set environment random seed |
| AsyncBatchEnv | Parallel environment execution |

 **Sources:** [docs/tips.rst21](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst#L21-L21)

 
### Command Line Interface

 The `d3rlpy.cli` module provides command-line tools:

 
| Command | Purpose |
|---|---|
| d3rlpy plot | Generate training plots |
| d3rlpy export | Model format conversion |
| d3rlpy eval | Policy evaluation |

 **Sources:** [docs/references/index.rst20](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/index.rst#L20-L20)

 
### Core Utilities

 Top-level utility functions:

 
| Function | Purpose |
|---|---|
| seed() | Set global random seeds |
| load_learnable() | Load saved algorithms |
| save_learnable() | Save algorithm state |

 **Sources:** [docs/tips.rst17](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/tips.rst#L17-L17) [docs/references/off_policy_evaluation.rst14](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/off_policy_evaluation.rst#L14-L14)
