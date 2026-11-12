> 来源: [https://deepwiki.com/astooke/rlpyt/3-algorithms](https://deepwiki.com/astooke/rlpyt/3-algorithms)
> DeepWiki astooke/rlpyt | Last indexed: 25 April 2025 (f04f23

# Algorithms

  Relevant source files 
 - [docs/source/pages/util.rst](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/util.rst)
 - [rlpyt/algos/dqn/dqn.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/dqn.py)
 - [rlpyt/algos/dqn/r2d1.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/r2d1.py)
 - [rlpyt/algos/pg/a2c.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/a2c.py)
 - [rlpyt/algos/pg/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/base.py)
 - [rlpyt/algos/pg/ppo.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/ppo.py)
 - [rlpyt/algos/qpg/ddpg.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/ddpg.py)
 - [rlpyt/algos/qpg/sac.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py)
 - [rlpyt/algos/qpg/sac_v.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac_v.py)
 - [rlpyt/algos/qpg/td3.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/td3.py)
 - [rlpyt/algos/utils.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/utils.py)
 - [rlpyt/experiments/configs/mujoco/qpg/mujoco_sac_v.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/experiments/configs/mujoco/qpg/mujoco_sac_v.py)
 
  This page documents the reinforcement learning algorithms implemented in the rlpyt framework. Algorithms in rlpyt define the learning process - they determine how agent parameters are updated using collected experiences, implement optimization procedures, and manage replay buffers when needed. For information about Agents that use these algorithms, see [Agents](https://deepwiki.com/astooke/rlpyt/4-agents), and for how Runners coordinate the training process, see [Runners](https://deepwiki.com/astooke/rlpyt/5-runners).

 
## Algorithm Hierarchy and Categories

 Rlpyt organizes algorithms into three main families, all deriving from a common base class:

 
```

```

 Sources:

 
 - [rlpyt/algos/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py)
 - [rlpyt/algos/pg/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/base.py)
 - [rlpyt/algos/dqn/dqn.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/dqn.py)
 - [rlpyt/algos/qpg/ddpg.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/ddpg.py)
 - [rlpyt/algos/qpg/sac.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py)
 
 
## Common Algorithm Interface

 All algorithms in rlpyt implement a standardized interface for interacting with other framework components:

 
```

```

 Sources:

 
 - [rlpyt/algos/dqn/dqn.py158-190](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/dqn.py#L158-L190)
 - [rlpyt/algos/qpg/sac.py160-211](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py#L160-L211)
 - [rlpyt/algos/pg/a2c.py41-61](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/a2c.py#L41-L61)
 
 
## Base Algorithm Class

 The `RlAlgorithm` base class defines the interface that all algorithms must implement:

 
| Method | Purpose |
|---|---|
| initialize | Setup algorithm for standard training runs |
| async_initialize | Setup for parallel/async training |
| optimize_agent | Main training method that processes samples and updates agent |
| optim_initialize | Initialize optimizers |
| initialize_replay_buffer | Setup replay buffers for off-policy algorithms |

 Sources:

 
 - [rlpyt/algos/base.py](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/base.py)
 
 
## Policy Gradient Algorithms

 Policy gradient algorithms in rlpyt optimize the agent's policy directly by computing gradients of the expected return.

 
### Policy Gradient Base Class

 The `PolicyGradientAlgo` class provides common functionality for all policy gradient methods:

 
```

```

 Sources:

 
 - [rlpyt/algos/pg/base.py41-75](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/base.py#L41-L75)
 
 
### A2C (Advantage Actor-Critic)

 A2C is a synchronous version of Advantage Actor-Critic that performs one gradient update per batch of collected experiences.

 
```

```

 Sources:

 
 - [rlpyt/algos/pg/a2c.py63-103](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/a2c.py#L63-L103)
 
 
### PPO (Proximal Policy Optimization)

 PPO uses clipped surrogate objectives to improve stability by preventing too large policy updates.

 
```

```

 Sources:

 
 - [rlpyt/algos/pg/ppo.py117-154](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/ppo.py#L117-L154)
 
 
## Q-Learning Algorithms

 Q-learning algorithms learn action-value functions and derive policies from them, typically using experience replay.

 
### DQN (Deep Q-Network)

 DQN learns an action-value function by minimizing the temporal difference error.

 
```

```

 Sources:

 
 - [rlpyt/algos/dqn/dqn.py211-265](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/dqn.py#L211-L265)
 
 
### R2D1 (Recurrent Replay Distributed DQN)

 R2D1 extends DQN to recurrent networks with special handling for sequence data and priorities.

 
```

```

 Sources:

 
 - [rlpyt/algos/dqn/r2d1.py244-333](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/r2d1.py#L244-L333)
 
 
## Actor-Critic Algorithms

 Actor-critic algorithms combine policy optimization with value function learning.

 
### SAC (Soft Actor-Critic)

 SAC is an off-policy actor-critic method that uses entropy regularization and twin Q-functions.

 
```

```

 Sources:

 
 - [rlpyt/algos/qpg/sac.py227-283](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py#L227-L283)
 
 
### DDPG (Deep Deterministic Policy Gradient)

 DDPG is a deterministic policy gradient algorithm that uses an actor-critic architecture with off-policy learning.

 
```

```

 Sources:

 
 - [rlpyt/algos/qpg/ddpg.py188-204](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/ddpg.py#L188-L204)
 
 
### TD3 (Twin Delayed DDPG)

 TD3 improves DDPG with twin Q-functions, delayed policy updates, and target policy noise.

 
```

```

 Sources:

 
 - [rlpyt/algos/qpg/td3.py38-50](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/td3.py#L38-L50)
 
 
## Algorithm Optimization Flow

 The following diagram illustrates the optimization flow for different algorithm types:

 
```

```

 Sources:

 
 - [rlpyt/algos/pg/a2c.py41-61](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/pg/a2c.py#L41-L61)
 - [rlpyt/algos/dqn/dqn.py158-190](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/dqn.py#L158-L190)
 - [rlpyt/algos/qpg/sac.py160-211](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py#L160-L211)
 
 
## Algorithm Utility Functions

 Rlpyt provides utility functions for common RL algorithm operations:

 
| Function | Purpose |
|---|---|
| discount_return | Computes discounted returns from rewards |
| generalized_advantage_estimation | Computes GAE for policy gradient methods |
| discount_return_n_step | Computes n-step returns for Q-learning |
| valid_from_done | Creates a mask for valid timesteps in trajectories |

 
```

```

 Sources:

 
 - [rlpyt/algos/utils.py8-162](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/utils.py#L8-L162)
 - [docs/source/pages/util.rst83-96](https://github.com/astooke/rlpyt/blob/f04f23db/docs/source/pages/util.rst#L83-L96)
 
 
## Advanced Features

 
### Prioritized Experience Replay

 DQN and R2D1 support prioritized experience replay to more efficiently learn from important samples:

 
```

```

 Sources:

 
 - [rlpyt/algos/dqn/r2d1.py181-242](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/dqn/r2d1.py#L181-L242)
 
 
### Automatic Entropy Tuning

 SAC includes automatic tuning of the entropy coefficient to maintain a target entropy level:

 
```

```

 Sources:

 
 - [rlpyt/algos/qpg/sac.py277-283](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py#L277-L283)
 - [rlpyt/algos/qpg/sac.py179-183](https://github.com/astooke/rlpyt/blob/f04f23db/rlpyt/algos/qpg/sac.py#L179-L183)
 
 
## Implementing Custom Algorithms

 Custom algorithms can be implemented by subclassing one of the base algorithm classes and implementing the required methods:

 
 - Subclass `RlAlgorithm` or one of its derivatives like `PolicyGradientAlgo`
 - Implement `initialize` to set up your algorithm
 - Implement `optimize_agent` to define the update rule
 - Implement `loss` to compute your algorithm's loss function
 
 For off-policy algorithms, you'll also need to implement:

 
 - `initialize_replay_buffer` to set up your experience replay
 - `samples_to_buffer` to define how samples are stored
