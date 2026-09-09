> 来源: [https://deepwiki.com/ray-project/ray/5-ray-rllib](https://deepwiki.com/ray-project/ray/5-ray-rllib)
> DeepWiki ray-project/ray | Last indexed: 25 June 2026 (bf1295

# Ray RLlib

  Relevant source files 
 - [.vale/styles/config/vocabularies/RLlib/accept.txt](https://github.com/ray-project/ray/blob/bf129559/.vale/styles/config/vocabularies/RLlib/accept.txt)
 - [doc/source/_includes/rllib/new_api_stack.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/_includes/rllib/new_api_stack.rst)
 - [doc/source/rllib/algorithm-config.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/algorithm-config.rst)
 - [doc/source/rllib/checkpoints.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/checkpoints.rst)
 - [doc/source/rllib/external-envs.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/external-envs.rst)
 - [doc/source/rllib/getting-started.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/getting-started.rst)
 - [doc/source/rllib/images/acrobot-v1.png](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/images/acrobot-v1.png)
 - [doc/source/rllib/images/scaling_axes_overview.svg](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/images/scaling_axes_overview.svg)
 - [doc/source/rllib/index.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/index.rst)
 - [doc/source/rllib/key-concepts.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/key-concepts.rst)
 - [doc/source/rllib/metrics-logger.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/metrics-logger.rst)
 - [doc/source/rllib/multi-agent-envs.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/multi-agent-envs.rst)
 - [doc/source/rllib/new-api-stack-migration-guide.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/new-api-stack-migration-guide.rst)
 - [doc/source/rllib/package_ref/algorithm.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/algorithm.rst)
 - [doc/source/rllib/package_ref/callback.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/callback.rst)
 - [doc/source/rllib/package_ref/index.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/index.rst)
 - [doc/source/rllib/package_ref/learner.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/learner.rst)
 - [doc/source/rllib/package_ref/rl_modules.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/rl_modules.rst)
 - [doc/source/rllib/package_ref/utils.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/package_ref/utils.rst)
 - [doc/source/rllib/rllib-advanced-api.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-advanced-api.rst)
 - [doc/source/rllib/rllib-algorithms.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-algorithms.rst)
 - [doc/source/rllib/rllib-callback.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-callback.rst)
 - [doc/source/rllib/rllib-dev.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-dev.rst)
 - [doc/source/rllib/rllib-env.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-env.rst)
 - [doc/source/rllib/rllib-examples.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-examples.rst)
 - [doc/source/rllib/rllib-fault-tolerance.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-fault-tolerance.rst)
 - [doc/source/rllib/rllib-learner.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/rllib-learner.rst)
 - [doc/source/rllib/user-guides.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/rllib/user-guides.rst)
 - [doc/source/train/distributed-tensorflow-keras.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/distributed-tensorflow-keras.rst)
 - [doc/source/train/doc_code/dl_guide.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/dl_guide.py)
 - [doc/source/train/doc_code/hvd_trainer.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/hvd_trainer.py)
 - [doc/source/train/doc_code/key_concepts.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/key_concepts.py)
 - [doc/source/train/doc_code/tuner.py](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/doc_code/tuner.py)
 - [doc/source/train/user-guides/results.rst](https://github.com/ray-project/ray/blob/bf129559/doc/source/train/user-guides/results.rst)
 - [rllib/algorithms/algorithm.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm.py)
 - [rllib/algorithms/algorithm_config.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py)
 - [rllib/algorithms/appo/utils.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/appo/utils.py)
 - [rllib/algorithms/impala/impala.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala.py)
 - [rllib/algorithms/impala/impala_learner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala_learner.py)
 - [rllib/algorithms/utils.py](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/utils.py)
 - [rllib/core/learner/learner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner.py)
 - [rllib/core/learner/learner_group.py](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner_group.py)
 - [rllib/core/learner/torch/torch_learner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/torch/torch_learner.py)
 - [rllib/env/env_runner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/env/env_runner.py)
 - [rllib/env/env_runner_group.py](https://github.com/ray-project/ray/blob/bf129559/rllib/env/env_runner_group.py)
 - [rllib/env/multi_agent_env_runner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/env/multi_agent_env_runner.py)
 - [rllib/env/single_agent_env_runner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/env/single_agent_env_runner.py)
 - [rllib/env/tests/test_env_runner_group.py](https://github.com/ray-project/ray/blob/bf129559/rllib/env/tests/test_env_runner_group.py)
 - [rllib/evaluation/rollout_worker.py](https://github.com/ray-project/ray/blob/bf129559/rllib/evaluation/rollout_worker.py)
 - [rllib/evaluation/tests/test_rollout_worker.py](https://github.com/ray-project/ray/blob/bf129559/rllib/evaluation/tests/test_rollout_worker.py)
 - [rllib/examples/algorithms/classes/vpg.py](https://github.com/ray-project/ray/blob/bf129559/rllib/examples/algorithms/classes/vpg.py)
 - [rllib/examples/learners/classes/vpg_torch_learner.py](https://github.com/ray-project/ray/blob/bf129559/rllib/examples/learners/classes/vpg_torch_learner.py)
 - [rllib/offline/estimators/tests/utils.py](https://github.com/ray-project/ray/blob/bf129559/rllib/offline/estimators/tests/utils.py)
 - [rllib/offline/tests/test_feature_importance.py](https://github.com/ray-project/ray/blob/bf129559/rllib/offline/tests/test_feature_importance.py)
 - [rllib/utils/actor_manager.py](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/actor_manager.py)
 - [rllib/utils/metrics/__init__.py](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/__init__.py)
 - [rllib/utils/test_utils.py](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/test_utils.py)
 
  
## Purpose and Scope

 Ray RLlib is a scalable reinforcement learning library built on Ray. It provides a unified framework for training RL agents across multiple algorithms (PPO, IMPALA, DQN, etc.) with support for distributed training, multi-agent scenarios, and various optimization techniques. This document covers RLlib's core architecture, including the training loop coordination, environment sampling, and model updating infrastructure.

 For detailed information about specific training configurations and algorithm implementations, see [Training Architecture and Configuration](https://deepwiki.com/ray-project/ray/5.1-training-architecture-and-configuration).

 
## Core Architecture

 RLlib follows a distributed actor-based architecture where independent components coordinate to collect experience data and train neural network policies.

 
### System Overview

 
```

```

 **Sources:** [rllib/algorithms/algorithm.py208-253](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm.py#L208-L253) [rllib/algorithms/algorithm_config.py109-138](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L109-L138)

 
### Key Components

 
| Component | Location | Purpose |
|---|---|---|
| Algorithm | rllib/algorithms/algorithm.py208 | Coordinates training, manages workers and learners |
| AlgorithmConfig | rllib/algorithms/algorithm_config.py109 | Configuration object for all settings |
| EnvRunner | rllib/env/env_runner.py36 | Base class for environment interaction |
| EnvRunnerGroup | rllib/env/env_runner_group.py70 | Manages distributed EnvRunners |
| Learner | rllib/core/learner/learner.py112 | Updates neural network weights |
| LearnerGroup | rllib/core/learner/learner_group.py100 | Manages distributed Learners |
| RLModule | rllib/core/rl_module/rl_module.py44 | Neural network policy/value functions |

 **Sources:** [rllib/algorithms/algorithm.py208-216](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm.py#L208-L216) [rllib/algorithms/algorithm_config.py109-138](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L109-L138)

 
## Algorithm Class

 The `Algorithm` class ([rllib/algorithms/algorithm.py208](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm.py#L208-L208)) is the central coordinator that orchestrates all RL training components. It inherits from `Trainable` and `Checkpointable`.

 
### Core Responsibilities

 
```

```

 
### Main API Methods

 
| Method | Line Reference | Description |
|---|---|---|
| __init__() | rllib/algorithms/algorithm.py405-583 | Initialize algorithm with config |
| setup() | rllib/algorithms/algorithm.py742-930 | Create workers, learners, replay buffers |
| train() | Inherited from Trainable | Run one training iteration |
| training_step() | rllib/algorithms/algorithm.py1330 | Execute one iteration of the algorithm's logic |
| evaluate() | rllib/algorithms/algorithm.py1662 | Run evaluation on eval workers |
| save_to_path() | rllib/algorithms/algorithm.py2451 | Save checkpoint to path |
| restore_from_path() | rllib/algorithms/algorithm.py2483 | Restore from checkpoint |

 **Sources:** [rllib/algorithms/algorithm.py208-1662](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm.py#L208-L1662)

 
## EnvRunner System

 EnvRunners are responsible for collecting experience data by interacting with environments. They run the current policy (RLModule) to generate actions and collect episodes.

 
### EnvRunner Hierarchy

 
```

```

 
### EnvRunner Data Flow

 
```

```

 
### SingleAgentEnvRunner

 The `SingleAgentEnvRunner` ([rllib/env/single_agent_env_runner.py68](https://github.com/ray-project/ray/blob/bf129559/rllib/env/single_agent_env_runner.py#L68-L68)) handles single-agent environments.

 **Key Methods:**

 
| Method | Line Reference | Description |
|---|---|---|
| sample() | rllib/env/single_agent_env_runner.py152-270 | Collect timesteps or episodes |
| _sample() | rllib/env/single_agent_env_runner.py272-477 | Internal sampling loop |
| make_env() | rllib/env/env_runner.py231 | Create vectorized environment |
| make_module() | rllib/env/env_runner.py265 | Create RLModule instance |

 **Sources:** [rllib/env/single_agent_env_runner.py68-477](https://github.com/ray-project/ray/blob/bf129559/rllib/env/single_agent_env_runner.py#L68-L477) [rllib/env/env_runner.py36-265](https://github.com/ray-project/ray/blob/bf129559/rllib/env/env_runner.py#L36-L265)

 
### MultiAgentEnvRunner

 The `MultiAgentEnvRunner` ([rllib/env/multi_agent_env_runner.py73](https://github.com/ray-project/ray/blob/bf129559/rllib/env/multi_agent_env_runner.py#L73-L73)) handles multi-agent environments with multiple policies.

 **Key Differences from Single-Agent:**

 
 - Manages `MultiAgentEpisode` objects ([rllib/env/multi_agent_episode.py25](https://github.com/ray-project/ray/blob/bf129559/rllib/env/multi_agent_episode.py#L25-L25)) with per-agent data.
 - Handles agent-to-module mapping via `config.multi_agent(policy_mapping_fn=...)` ([rllib/algorithms/algorithm_config.py1867](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1867-L1867)).
 - Uses `MultiRLModule` ([rllib/core/rl_module/multi_rl_module.py68](https://github.com/ray-project/ray/blob/bf129559/rllib/core/rl_module/multi_rl_module.py#L68-L68)) containing multiple policy modules.
 
 **Sources:** [rllib/env/multi_agent_env_runner.py73-166](https://github.com/ray-project/ray/blob/bf129559/rllib/env/multi_agent_env_runner.py#L73-L166) [rllib/algorithms/algorithm_config.py1867-1900](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1867-L1900)

 
### EnvRunnerGroup

 The `EnvRunnerGroup` ([rllib/env/env_runner_group.py70](https://github.com/ray-project/ray/blob/bf129559/rllib/env/env_runner_group.py#L70-L70)) manages a pool of EnvRunner actors (both local and remote).

 **Key Methods:**

 
| Method | Line Reference | Description |
|---|---|---|
| __init__() | rllib/env/env_runner_group.py76-227 | Create worker pool |
| foreach_worker() | rllib/env/env_runner_group.py605 | Execute function on all workers |
| sync_weights() | rllib/env/env_runner_group.py760 | Sync RLModule weights to workers |
| add_workers() | rllib/env/env_runner_group.py455-549 | Add new remote workers |

 **Fault Tolerance:** The `FaultTolerantActorManager` ([rllib/utils/actor_manager.py197](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/actor_manager.py#L197-L197)) handles worker failures and automatic restarts.

 **Sources:** [rllib/env/env_runner_group.py70-549](https://github.com/ray-project/ray/blob/bf129559/rllib/env/env_runner_group.py#L70-L549) [rllib/utils/actor_manager.py197-250](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/actor_manager.py#L197-L250)

 
## Learner System

 Learners are responsible for computing gradients and updating the neural network weights of RLModules.

 
### Learner Class

 The `Learner` class ([rllib/core/learner/learner.py112](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner.py#L112-L112)) is the base class for all learner implementations.

 **Key Methods:**

 
| Method | Line Reference | Description |
|---|---|---|
| build() | rllib/core/learner/learner.py320-356 | Build module, optimizers, connectors |
| update_from_episodes() | rllib/core/learner/learner.py535 | Train from episode data |
| compute_losses() | rllib/core/learner/learner.py1010 | Compute loss per module |
| compute_gradients() | rllib/core/learner/torch/torch_learner.py170 | Compute parameter gradients (Torch) |
| apply_gradients() | rllib/core/learner/torch/torch_learner.py214 | Apply gradients to parameters (Torch) |

 **Sources:** [rllib/core/learner/learner.py112-1010](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner.py#L112-L1010) [rllib/core/learner/torch/torch_learner.py67-214](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/torch/torch_learner.py#L67-L214)

 
### LearnerGroup

 The `LearnerGroup` ([rllib/core/learner/learner_group.py100](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner_group.py#L100-L100)) coordinates multiple Learner workers for distributed training.

 **Distributed Training:** When `num_learners > 1`, the `RLlibBackendExecutor` ([rllib/core/learner/learner_group.py85](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner_group.py#L85-L85)) manages the distributed learner actors using Ray Train's backend logic.

 **Sources:** [rllib/core/learner/learner_group.py100-220](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner_group.py#L100-L220)

 
## Training Loop Patterns

 
### Synchronous On-Policy (PPO)

 PPO collects a batch of episodes using the `EnvRunnerGroup`, performs multiple SGD passes via `LearnerGroup.update_from_episodes()`, and then synchronizes weights back to the sampling workers.

 **Sources:** [rllib/algorithms/ppo/ppo.py63-500](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/ppo/ppo.py#L63-L500)

 
### Asynchronous Off-Policy (IMPALA)

 IMPALA utilizes asynchronous sampling where `EnvRunner` actors continuously send episodes to a queue ([rllib/algorithms/impala/impala_learner.py155](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala_learner.py#L155-L155)). `Learner` actors pull from this queue and perform updates independently of the sampling rate ([rllib/algorithms/impala/impala_learner.py169](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala_learner.py#L169-L169)).

 **Sources:** [rllib/algorithms/impala/impala.py71-155](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala.py#L71-L155) [rllib/algorithms/impala/impala_learner.py56-177](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/impala/impala_learner.py#L56-L177)

 
## Configuration System

 The `AlgorithmConfig` class ([rllib/algorithms/algorithm_config.py109](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L109-L109)) provides a fluent API for configuring training.

 **Key Configuration Methods:**

 
 - `environment()`: Set env, env_config, and spaces ([rllib/algorithms/algorithm_config.py1107](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1107-L1107)).
 - `env_runners()`: Configure sampling workers ([rllib/algorithms/algorithm_config.py1510](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1510-L1510)).
 - `learners()`: Configure training workers ([rllib/algorithms/algorithm_config.py1765](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1765-L1765)).
 - `training()`: Set hyperparameters like `lr` and `gamma` ([rllib/algorithms/algorithm_config.py1205](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L1205-L1205)).
 
 **Sources:** [rllib/algorithms/algorithm_config.py109-1765](https://github.com/ray-project/ray/blob/bf129559/rllib/algorithms/algorithm_config.py#L109-L1765)

 
## Connectors and Preprocessing

 Connectors transform data between components.

 
 - **EnvToModule**: Preprocesses observations before the policy forward pass ([rllib/env/single_agent_env_runner.py107](https://github.com/ray-project/ray/blob/bf129559/rllib/env/single_agent_env_runner.py#L107-L107)).
 - **LearnerConnector**: Prepares episodes for training, including tensor conversion (`NumpyToTensor`) and value bootstrapping ([rllib/core/learner/learner.py348](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner.py#L348-L348)).
 
 **Sources:** [rllib/env/single_agent_env_runner.py106-127](https://github.com/ray-project/ray/blob/bf129559/rllib/env/single_agent_env_runner.py#L106-L127) [rllib/core/learner/learner.py320-356](https://github.com/ray-project/ray/blob/bf129559/rllib/core/learner/learner.py#L320-L356)

 
## Metrics and Monitoring

 The `MetricsLogger` ([rllib/utils/metrics/metrics_logger.py117](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/metrics_logger.py#L117-L117)) collects and reduces metrics across distributed workers.

 **Key Metrics Categories:**

 
 - `ENV_RUNNER_RESULTS`: Sampling stats like episode returns ([rllib/utils/metrics/__init__.py120](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/__init__.py#L120-L120)).
 - `LEARNER_RESULTS`: Training stats like loss and learning rate ([rllib/utils/metrics/__init__.py127](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/__init__.py#L127-L127)).
 - `TIMERS`: Performance breakdown for sampling and updates ([rllib/utils/metrics/__init__.py152](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/__init__.py#L152-L152)).
 
 **Sources:** [rllib/utils/metrics/metrics_logger.py117-152](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/metrics_logger.py#L117-L152) [rllib/utils/metrics/__init__.py1-155](https://github.com/ray-project/ray/blob/bf129559/rllib/utils/metrics/__init__.py#L1-L155)
