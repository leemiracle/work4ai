> 来源: [https://deepwiki.com/rlworkgroup/garage/3-rl-algorithms](https://deepwiki.com/rlworkgroup/garage/3-rl-algorithms)
> DeepWiki rlworkgroup/garage | Last indexed: 25 April 2025 (2d5948

# RL Algorithms

  Relevant source files 
 - [docs/index.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/index.md?plain=1)
 - [docs/user/algo_bc.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_bc.md?plain=1)
 - [docs/user/algo_cem.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_cem.md?plain=1)
 - [docs/user/algo_ddpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ddpg.md?plain=1)
 - [docs/user/algo_dqn.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_dqn.md?plain=1)
 - [docs/user/algo_erwr.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_erwr.md?plain=1)
 - [docs/user/algo_maml.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_maml.md?plain=1)
 - [docs/user/algo_mtppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mtppo.md?plain=1)
 - [docs/user/algo_mttrpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mttrpo.md?plain=1)
 - [docs/user/algo_pearl.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_pearl.md?plain=1)
 - [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1)
 - [docs/user/algo_rl2.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_rl2.md?plain=1)
 - [docs/user/algo_sac.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1)
 - [docs/user/algo_td3.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_td3.md?plain=1)
 - [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1)
 - [docs/user/algo_vpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_vpg.md?plain=1)
 - [docs/user/images/dqn_plots.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/dqn_plots.png)
 - [docs/user/images/numpy.png](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/images/numpy.png)
 - [docs/user/references.bib](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/references.bib)
 - [src/garage/np/algos/cem.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py)
 - [src/garage/np/algos/cma_es.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cma_es.py)
 - [src/garage/tf/algos/ddpg.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/ddpg.py)
 - [src/garage/tf/algos/dqn.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/dqn.py)
 - [src/garage/tf/algos/npo.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/npo.py)
 - [src/garage/tf/algos/reps.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/reps.py)
 - [src/garage/tf/algos/td3.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/td3.py)
 - [src/garage/tf/algos/te_npo.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/te_npo.py)
 - [src/garage/torch/__init__.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/__init__.py)
 - [src/garage/torch/_functions.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/_functions.py)
 - [src/garage/torch/algos/bc.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/bc.py)
 - [src/garage/torch/algos/ddpg.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/ddpg.py)
 - [src/garage/torch/algos/dqn.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/dqn.py)
 - [src/garage/torch/algos/sac.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py)
 - [src/garage/torch/algos/td3.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/td3.py)
 - [src/garage/torch/modules/cnn_module.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/modules/cnn_module.py)
 - [src/garage/torch/policies/discrete_qf_argmax_policy.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/policies/discrete_qf_argmax_policy.py)
 - [src/garage/torch/policies/stochastic_policy.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/policies/stochastic_policy.py)
 - [tests/garage/torch/algos/test_dqn.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/torch/algos/test_dqn.py)
 - [tests/garage/torch/test_functions.py](https://github.com/rlworkgroup/garage/blob/2d594803/tests/garage/torch/test_functions.py)
 
  This page provides an overview of the reinforcement learning algorithms implemented in garage. It covers the hierarchical organization of different algorithm families, their implementations across different frameworks (PyTorch, TensorFlow, and NumPy), and how they relate to one another. For information about the broader architecture and how algorithms integrate with other components, see [Core Architecture](https://deepwiki.com/rlworkgroup/garage/2-core-architecture).

 
## RL Algorithm Base Class

 All reinforcement learning algorithms in garage inherit from the `RLAlgorithm` abstract base class, which defines the common interface that all algorithm implementations must follow. This allows for a consistent training process regardless of the specific algorithm used.

 
```

```

 Sources: [src/garage/np/algos/rl_algorithm.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/rl_algorithm.py) [src/garage/tf/algos/npo.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/npo.py) [src/garage/torch/algos/sac.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py) [src/garage/np/algos/cem.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py)

 The `RLAlgorithm` base class requires implementations to provide:

 
 - A `train()` method that controls the overall training loop, working with the `Trainer` object
 - A `train_once()` method that performs a single training iteration using collected episode data
 
 
## Algorithm Taxonomy

 Garage implements a wide range of RL algorithms across multiple frameworks. The algorithms can be categorized in several ways:

 
### By Learning Type

 
```

```

 Sources: [docs/index.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/index.md?plain=1) [src/garage/torch/algos/sac.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py) [src/garage/tf/algos/ddpg.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/ddpg.py) [src/garage/np/algos/cma_es.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cma_es.py) [src/garage/np/algos/cem.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py)

 
### By Framework Implementation

 
```

```

 Sources: [docs/user/algo_sac.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1) [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1) [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1) [docs/user/algo_dqn.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_dqn.md?plain=1) [docs/user/algo_td3.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_td3.md?plain=1) [docs/user/algo_bc.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_bc.md?plain=1)

 
## On-Policy Algorithms

 On-policy methods learn a policy by directly interacting with the environment and using only the data collected from the current policy. They typically discard older samples after each policy update.

 
### Policy Gradient Methods

 Policy gradient methods directly optimize the policy by updating it in the direction that increases expected return:

 
```

```

 Sources: [src/garage/tf/algos/npo.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/npo.py) [docs/user/algo_ppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1) [docs/user/algo_trpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_trpo.md?plain=1) [docs/user/algo_vpg.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_vpg.md?plain=1)

 
#### VPG (REINFORCE)

 Vanilla Policy Gradient (also known as REINFORCE) is the most basic policy gradient algorithm. It updates the policy parameters directly in the direction of the gradient of the expected return.

 
#### NPO and TRPO

 Natural Policy Optimization (NPO) and Trust Region Policy Optimization (TRPO) use a trust region constraint to ensure stable policy updates. TRPO uses the natural gradient and a constraint on the KL divergence between the old and new policies to prevent large policy changes.

 
#### PPO

 Proximal Policy Optimization (PPO) is a simpler alternative to TRPO that also constrains policy updates but uses a clipped objective function. This makes it more computationally efficient while still offering good performance.

 
### Other On-Policy Methods

 
```

```

 Sources: [src/garage/tf/algos/reps.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/reps.py) [docs/user/algo_erwr.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_erwr.md?plain=1)

 
## Off-Policy Algorithms

 Off-policy methods can learn from data collected by different policies, typically using a replay buffer to store and reuse past experiences.

 
```

```

 Sources: [src/garage/torch/algos/sac.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py) [src/garage/torch/algos/ddpg.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/ddpg.py) [src/garage/tf/algos/td3.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/td3.py) [src/garage/torch/algos/dqn.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/dqn.py)

 
### Q-Learning Based Methods

 
#### DQN

 Deep Q-Network (DQN) is a value-based method that learns a Q-function network to estimate the value of state-action pairs. DQN uses techniques like experience replay and target networks to stabilize training.

 
### Actor-Critic Methods

 Actor-critic methods maintain both a policy (actor) and a value or Q-function (critic):

 
#### DDPG and TD3

 Deep Deterministic Policy Gradient (DDPG) is an actor-critic algorithm for continuous action spaces that combines ideas from DQN and deterministic policy gradients. TD3 (Twin Delayed DDPG) improves upon DDPG with several modifications:

 
 - Uses two Q-functions to reduce overestimation bias
 - Adds noise to target actions
 - Updates the policy less frequently than the Q-functions
 
 
#### SAC

 Soft Actor-Critic (SAC) is an actor-critic algorithm that incorporates entropy regularization to encourage exploration. It learns a policy, a value function, and a Q-function, and often includes automatic tuning of the temperature parameter that controls the entropy regularization.

 Example SAC implementation structure:

 
```

```

 Sources: [src/garage/torch/algos/sac.py19-196](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py#L19-L196) [src/garage/torch/algos/sac.py449-505](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py#L449-L505)

 
## Meta-RL Algorithms

 Meta-RL algorithms aim to learn policies that can quickly adapt to new tasks with minimal additional training.

 
```

```

 Sources: [docs/user/algo_maml.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_maml.md?plain=1) [docs/user/algo_rl2.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_rl2.md?plain=1) [docs/user/algo_pearl.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_pearl.md?plain=1) [docs/user/algo_mtppo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mtppo.md?plain=1) [docs/user/algo_mttrpo.md](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_mttrpo.md?plain=1)

 
### MAML

 Model-Agnostic Meta-Learning (MAML) optimizes for fast adaptation by explicitly training the model to be easily fine-tuned on new tasks.

 
### RL²

 RL² (RL-squared) treats the entire meta-RL problem as a single RL problem where the policy is implemented as a recurrent neural network that has memory of past episodes, allowing it to adapt based on experience.

 
### PEARL

 Probabilistic Embeddings for Actor-Critic RL (PEARL) is an off-policy meta-RL algorithm that learns a latent context variable to encode task information, enabling rapid adaptation to new tasks.

 
### Multi-Task Variants

 Multi-task variants of algorithms (MT-PPO, MT-TRPO, MT-SAC) are designed to simultaneously learn policies for multiple related tasks, sharing knowledge across tasks.

 
## Evolutionary Algorithms

 Evolutionary algorithms approach RL through population-based optimization rather than gradient-based learning.

 
```

```

 Sources: [src/garage/np/algos/cem.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py) [src/garage/np/algos/cma_es.py](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cma_es.py)

 
### CEM

 The Cross-Entropy Method (CEM) iteratively optimizes a policy by:

 
 - Sampling policies from a Gaussian distribution
 - Evaluating the policies on the environment
 - Updating the distribution parameters based on the top-performing policies
 
 
### CMA-ES

 Covariance Matrix Adaptation Evolution Strategy (CMA-ES) is a more sophisticated evolutionary algorithm that adapts the full covariance matrix of the sampling distribution, enabling more effective exploration in the policy space.

 
## Framework Implementations

 Garage provides implementations of algorithms across three frameworks: PyTorch, TensorFlow, and NumPy, allowing users to choose based on their familiarity and preferences.

 
### Common Implementation Patterns

 Despite the different frameworks, algorithms in garage follow common patterns:

 
```

```

 Sources: [src/garage/torch/algos/sac.py188-233](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/algos/sac.py#L188-L233) [src/garage/tf/algos/ddpg.py269-302](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/ddpg.py#L269-L302) [src/garage/np/algos/cem.py121-172](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py#L121-L172)

 
### PyTorch-Specific Features

 PyTorch implementations typically use the following patterns:

 
```

```

 Sources: [src/garage/torch/_functions.py25-43](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/_functions.py#L25-L43) [src/garage/torch/_functions.py284-302](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/torch/_functions.py#L284-L302)

 
### TensorFlow-Specific Features

 TensorFlow implementations typically use:

 
```

```

 Sources: [src/garage/tf/algos/ddpg.py133-178](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/tf/algos/ddpg.py#L133-L178)

 
### NumPy-Only Implementations

 Simpler algorithms like CEM and CMA-ES are implemented using NumPy without requiring deep learning frameworks:

 
```

```

 Sources: [src/garage/np/algos/cem.py156-158](https://github.com/rlworkgroup/garage/blob/2d594803/src/garage/np/algos/cem.py#L156-L158)

 
## Algorithm Selection Guide

 When choosing an algorithm for your RL task, consider:

 
| Algorithm Type | Use Case | Example Algorithms |
|---|---|---|
| On-policy | When recent experience is most relevant, when exploration is a key factor | PPO, TRPO, VPG |
| Off-policy | When sample efficiency is important, when learning from demonstrations | SAC, TD3, DQN |
| Meta-RL | When fast adaptation to new tasks is required | MAML, PEARL, RL² |
| Evolutionary | When gradient information is unavailable, or objective is non-differentiable | CEM, CMA-ES |

 For specific action space considerations:

 
| Action Space | Recommended Algorithms |
|---|---|
| Discrete | DQN, PPO, TRPO |
| Continuous | SAC, TD3, DDPG, PPO, TRPO |

 For balancing exploration and exploitation:

 
| Emphasis | Recommended Algorithms |
|---|---|
| Exploration | SAC (with automatic entropy tuning), CEM |
| Exploitation | TD3, DDPG |
| Balanced | PPO, TRPO |

 
## Common Usage Pattern

 A typical usage pattern for instantiating and training an algorithm in garage:

 
```

```

 Sources: [docs/user/algo_ppo.md38-48](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_ppo.md?plain=1#L38-L48) [docs/user/algo_sac.md25-64](https://github.com/rlworkgroup/garage/blob/2d594803/docs/user/algo_sac.md?plain=1#L25-L64)
