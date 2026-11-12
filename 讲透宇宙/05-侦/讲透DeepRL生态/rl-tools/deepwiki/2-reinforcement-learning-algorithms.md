> 来源: [https://deepwiki.com/rl-tools/rl-tools/2-reinforcement-learning-algorithms](https://deepwiki.com/rl-tools/rl-tools/2-reinforcement-learning-algorithms)
> DeepWiki rl-tools/rl-tools | Last indexed: 2 February 2026 (a0aef4

# Reinforcement Learning Algorithms

  Relevant source files 
 - [include/rl_tools/nn/layers/sample_and_squash/layer.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/layer.h)
 - [include/rl_tools/nn/layers/sample_and_squash/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/operations_generic.h)
 - [include/rl_tools/rl/algorithms/ppo/loop/core/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/config.h)
 - [include/rl_tools/rl/algorithms/ppo/loop/core/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/operations_generic.h)
 - [include/rl_tools/rl/algorithms/ppo/loop/core/state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/loop/core/state.h)
 - [include/rl_tools/rl/algorithms/ppo/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/operations_generic.h)
 - [include/rl_tools/rl/algorithms/ppo/ppo.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/ppo/ppo.h)
 - [include/rl_tools/rl/algorithms/sac/loop/core/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/config.h)
 - [include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h)
 - [include/rl_tools/rl/algorithms/sac/loop/core/state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/state.h)
 - [include/rl_tools/rl/algorithms/sac/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/operations_generic.h)
 - [include/rl_tools/rl/algorithms/sac/sac.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/sac.h)
 - [include/rl_tools/rl/algorithms/td3/loop/core/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/config.h)
 - [include/rl_tools/rl/algorithms/td3/loop/core/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/operations_generic.h)
 - [include/rl_tools/rl/algorithms/td3/loop/core/state.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/state.h)
 - [include/rl_tools/rl/algorithms/td3/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/operations_generic.h)
 - [include/rl_tools/rl/algorithms/td3/td3.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/td3.h)
 - [include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h)
 - [include/rl_tools/rl/components/off_policy_runner/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/operations_generic.h)
 - [include/rl_tools/rl/components/off_policy_runner/operations_generic_per_env.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/operations_generic_per_env.h)
 - [include/rl_tools/rl/components/on_policy_runner/on_policy_runner.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/on_policy_runner.h)
 - [include/rl_tools/rl/components/on_policy_runner/operations_generic.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/operations_generic.h)
 - [include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/on_policy_runner/operations_generic_per_env.h)
 - [include/rl_tools/rl/components/running_normalizer/running_normalizer.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/running_normalizer/running_normalizer.h)
 - [src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/CMakeLists.txt)
 - [src/rl/environments/pendulum/ppo/cpu/config.h](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/config.h)
 - [src/rl/environments/pendulum/ppo/cpu/training.cpp](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cpu/training.cpp)
 - [src/rl/environments/pendulum/ppo/cuda/CMakeLists.txt](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/CMakeLists.txt)
 - [src/rl/environments/pendulum/ppo/cuda/training.cu](https://github.com/rl-tools/rl-tools/blob/a0aef476/src/rl/environments/pendulum/ppo/cuda/training.cu)
 
  This document covers the reinforcement learning algorithms implemented in RLtools, including their core components, training procedures, and modular training loop architecture. For neural network implementation details, see [Neural Network Components](https://deepwiki.com/rl-tools/rl-tools/3-neural-network-components). For environment interfaces, see [Environments](https://deepwiki.com/rl-tools/rl-tools/4-environments).

 
## Algorithm Overview

 RLtools implements several state-of-the-art deep reinforcement learning algorithms, with comprehensive support for off-policy actor-critic methods. The framework provides modular implementations that can be configured for different environments and computational backends.

 
```

```

 **Sources:** [include/rl_tools/rl/algorithms/sac/sac.h9-151](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/sac.h#L9-L151) [include/rl_tools/rl/algorithms/td3/loop/core/config.h16-94](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/config.h#L16-L94) [include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h18-226](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h#L18-L226)

 
## Actor-Critic Architecture

 All implemented algorithms use actor-critic architectures with separate networks for policy (actor) and value function estimation (critic). The `ActorCritic` data structure serves as the central container for network components and optimizers.

 
```

```

 The twin critic design (used in SAC and TD3) helps reduce overestimation bias by taking the minimum of two Q-value estimates. Target networks provide stable training targets through soft updates.

 **Sources:** [include/rl_tools/rl/algorithms/sac/sac.h127-149](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/sac.h#L127-L149) [include/rl_tools/rl/algorithms/sac/operations_generic.h449-453](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/operations_generic.h#L449-L453)

 
## SAC Implementation Details

 Soft Actor-Critic implements maximum entropy reinforcement learning with automatic temperature adjustment. The algorithm optimizes a stochastic policy while maintaining exploration through entropy regularization.

 
### Policy Parameterization

 SAC uses a `SampleAndSquash` layer to parameterize stochastic policies with bounded actions:

 
```

```

 The `SampleAndSquash` layer implements the reparameterization trick for gradient computation through stochastic policies.

 **Sources:** [include/rl_tools/nn/layers/sample_and_squash/operations_generic.h115-173](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/operations_generic.h#L115-L173) [include/rl_tools/rl/algorithms/sac/operations_generic.h227-251](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/operations_generic.h#L227-L251)

 
### Training Procedure

 SAC training alternates between critic and actor updates with automatic entropy temperature adjustment:

 
```

```

 **Sources:** [include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h112-140](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h#L112-L140) [include/rl_tools/rl/algorithms/sac/operations_generic.h210-283](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/operations_generic.h#L210-L283)

 
### Entropy Regularization

 SAC automatically adjusts the entropy coefficient α through a separate optimization objective:

 
| Component | Purpose | Implementation |
|---|---|---|
| log_alpha | Learnable temperature parameter | LayerGradient.log_alpha |
| alpha_optimizer | Updates entropy coefficient | ActorCritic.alpha_optimizer |
| Target entropy | Desired exploration level | PARAMETERS::TARGET_ENTROPY = -ACTION_DIM |

 **Sources:** [include/rl_tools/rl/algorithms/sac/sac.h26-32](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/sac.h#L26-L32) [include/rl_tools/nn/layers/sample_and_squash/operations_generic.h316-338](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/nn/layers/sample_and_squash/operations_generic.h#L316-L338)

 
## TD3 Implementation Details

 Twin Delayed Deep Deterministic Policy Gradient adds several stabilization techniques to the DDPG algorithm, including delayed policy updates and target action noise.

 
### Key Differences from SAC

 
| Feature | SAC | TD3 |
|---|---|---|
| Policy Type | Stochastic (Gaussian) | Deterministic |
| Action Space | Continuous | Continuous |
| Exploration | Entropy regularization | Target policy noise |
| Policy Updates | Every step | Delayed (every 2 steps) |
| Output Layer | SampleAndSquash | Standard Dense with tanh |

 
```

```

 **Sources:** [include/rl_tools/rl/algorithms/td3/loop/core/config.h20-88](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/config.h#L20-L88) [include/rl_tools/rl/algorithms/td3/loop/core/operations_generic.h85-115](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/td3/loop/core/operations_generic.h#L85-L115)

 
## Training Loop Architecture

 RLtools implements a modular training loop architecture where core algorithm loops are enhanced with additional capabilities through wrapper configurations.

 
```

```

 
### Training State Management

 The `State` structure contains all components needed for algorithm execution:

 
| Component | Type | Purpose |
|---|---|---|
| actor_critic | ACTOR_CRITIC_TYPE | Main algorithm networks |
| off_policy_runner | OffPolicyRunner | Environment interaction |
| critic_batch | SequentialBatch | Critic training data |
| actor_training_buffers | ActorTrainingBuffers | Gradient computation workspace |
| rng | Random number generator | Stochastic sampling |

 **Sources:** [include/rl_tools/rl/algorithms/sac/loop/core/state.h13-38](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/state.h#L13-L38) [include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h100-149](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/algorithms/sac/loop/core/operations_generic.h#L100-L149)

 
## Off-Policy Runner System

 The `OffPolicyRunner` manages environment interaction, experience collection, and replay buffer management for off-policy algorithms.

 
```

```

 
### Batch Collection

 The runner supports both standard and sequential batch collection for different algorithm requirements:

 
| Batch Type | Use Case | Key Features |
|---|---|---|
| Batch | Standard RL | Independent transitions |
| SequentialBatch | RNN policies | Temporal sequences with reset handling |

 **Sources:** [include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h74-154](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/off_policy_runner.h#L74-L154) [include/rl_tools/rl/components/off_policy_runner/operations_generic.h232-257](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/operations_generic.h#L232-L257) [include/rl_tools/rl/components/off_policy_runner/operations_generic_per_env.h8-88](https://github.com/rl-tools/rl-tools/blob/a0aef476/include/rl_tools/rl/components/off_policy_runner/operations_generic_per_env.h#L8-L88)
