> 来源: [https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/2-training-system](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/2-training-system)
> DeepWiki ikostrikov/pytorch-a2c-ppo-acktr-gail | Last indexed: 21 April 2025 (41332b

# Training System

  Relevant source files 
 - [a2c_ppo_acktr/storage.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/storage.py)
 - [main.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py)
 
  
## Purpose and Scope

 The Training System is the core component of the PyTorch A2C/PPO/ACKTR/GAIL implementation that orchestrates the reinforcement learning process. This document explains the primary training loop structure, experience collection mechanisms, and how different components interact during training. For information about specific reinforcement learning algorithms, see [Reinforcement Learning Algorithms](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/5-reinforcement-learning-algorithms).

 The training system is responsible for:

 
 - Setting up environments and agents
 - Collecting experiences through environment interaction
 - Computing returns and advantages
 - Updating policy networks based on collected data
 - Integrating optional components like GAIL for imitation learning
 
 
## Training Process Overview

 The training system follows a standard actor-critic reinforcement learning approach where agents interact with environments to collect experiences, then use these experiences to improve their policies.

 
```

```

 Sources: [main.py23-196](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L23-L196) [a2c_ppo_acktr/storage.py9-64](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/storage.py#L9-L64)

 
## Training Loop Architecture

 The training system is constructed as a loop that iteratively collects experiences and updates policies. Below is a detailed look at the components and their interactions:

 
```

```

 Sources: [main.py23-104](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L23-L104) [main.py105-162](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L105-L162)

 
## Experience Collection

 The experience collection process is a critical part of the training system, where the agent interacts with the environment and gathers data for learning.

 
### RolloutStorage System

 The `RolloutStorage` class is the central data structure that manages experience collection. It stores:

 
 - Observations
 - Actions and action log probabilities
 - Recurrent hidden states (if using recurrent policies)
 - Value predictions
 - Rewards
 - Masks (for episode termination)
 - Returns (computed advantages)
 
 
```

```

 Sources: [a2c_ppo_acktr/storage.py9-33](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/storage.py#L9-L33)

 
### Experience Collection Process

 The experience collection process follows these steps during each training iteration:

 
 - Sample actions from the current policy
 - Execute actions in the environment
 - Store transitions (state, action, reward, next state) in the RolloutStorage
 - Track episode rewards for logging
 
 The code structure for experience collection is as follows:

 
```

```

 Sources: [main.py113-134](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L113-L134) [main.py136-158](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L136-L158)

 
## Return Computation

 The `compute_returns` method in `RolloutStorage` calculates returns and advantages from collected experiences. This is a critical step before policy updates.

 Two methods are supported:

 
 - **Generalized Advantage Estimation (GAE)**: Provides a trade-off between bias and variance in advantage estimation
 - **Simple discounted returns**: Traditional approach using discounted rewards
 
 The system also handles proper time limits by distinguishing between true terminal states and artificial terminations due to episode time limits.

 
```

```

 Sources: [a2c_ppo_acktr/storage.py66-105](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/storage.py#L66-L105)

 
## Policy Update Process

 After collecting experiences and computing returns, the training system updates the policy network. The update process varies slightly depending on the algorithm (A2C, PPO, or ACKTR).

 
### Batch Generation

 The `RolloutStorage` provides two methods for generating training batches:

 
 - `feed_forward_generator`: For standard feed-forward networks
 - `recurrent_generator`: For recurrent policies
 
 These methods prepare mini-batches of experiences for efficient training, handling different network architectures appropriately.

 
| Generator | Purpose | When Used |
|---|---|---|
| feed_forward_generator | Creates randomized mini-batches by flattening and shuffling experiences | Used with standard feed-forward policies |
| recurrent_generator | Creates mini-batches that preserve sequential information | Used with recurrent policies (LSTM, GRU) |

 Sources: [a2c_ppo_acktr/storage.py107-202](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/storage.py#L107-L202)

 
### Update Flow

 The policy update process follows these steps:

 
 - Generate batches of experiences from the RolloutStorage
 - Feed the batches to the respective algorithm's update method
 - Optimize the policy and value networks
 - Reset the RolloutStorage for the next iteration
 
 
```

```

 Sources: [main.py160-162](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L160-L162)

 
## GAIL Integration (Optional)

 When GAIL (Generative Adversarial Imitation Learning) is enabled, the training system incorporates additional components for imitation learning:

 
 - Expert dataset loading from demonstrations
 - Discriminator network to distinguish agent behavior from expert behavior
 - Reward modification based on the discriminator's output
 
 
```

```

 Sources: [main.py74-90](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L74-L90) [main.py141-155](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L141-L155)

 
## Logging and Evaluation

 The training system includes facilities for tracking progress and evaluating performance:

 
 - Regular logging of training statistics (rewards, update count, FPS)
 - Periodic policy evaluation in separate environments
 - Model saving at specified intervals
 
 These components help monitor training progress and maintain the best models.

 Sources: [main.py165-194](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L165-L194)

 
## Complete Training Flow

 The overall training flow combines all the components described above into a cohesive system:

 
```

```

 Sources: [main.py105-194](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L105-L194)

 
## Key Configuration Parameters

 The training system behavior can be customized through various parameters:

 
| Parameter | Description | Impact on Training |
|---|---|---|
| num_steps | Number of steps to run per update | Controls the trade-off between learning frequency and data efficiency |
| num_processes | Number of parallel environments | Affects experience collection speed and diversity |
| gamma | Discount factor | Controls the importance of future rewards |
| use_gae | Whether to use Generalized Advantage Estimation | Affects the bias-variance trade-off in advantage estimation |
| gae_lambda | GAE parameter | Controls the bias-variance trade-off when using GAE |
| use_proper_time_limits | Handle environment time limits properly | Prevents treating time limit terminations as true episode endings |
| use_linear_lr_decay | Decay learning rate linearly | Helps stabilize learning in later stages |
| algo | Algorithm to use (a2c, ppo, acktr) | Determines the policy update mechanism |
| gail | Whether to use GAIL | Enables imitation learning mode |

 Sources: [main.py24](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L24-L24) [main.py103-111](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py#L103-L111)
