> 来源: [https://deepwiki.com/thu-ml/tianshou/3-policy-framework](https://deepwiki.com/thu-ml/tianshou/3-policy-framework)
> DeepWiki thu-ml/tianshou | Last indexed: 19 April 2025 (90846f

# Policy Framework

  Relevant source files 
 - [tianshou/policy/base.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py)
 - [tianshou/policy/modelfree/a2c.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/a2c.py)
 - [tianshou/policy/modelfree/ddpg.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ddpg.py)
 - [tianshou/policy/modelfree/dqn.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/dqn.py)
 - [tianshou/policy/modelfree/pg.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/pg.py)
 - [tianshou/policy/modelfree/ppo.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py)
 - [tianshou/policy/modelfree/sac.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/sac.py)
 - [tianshou/policy/modelfree/td3.py](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/td3.py)
 
  The Policy Framework in Tianshou is the core component that implements various reinforcement learning algorithms. It provides a unified interface for defining agent behaviors and learning methods through a hierarchy of policy classes. This document explains the architecture, components, and usage of the policy framework.

 For information about how policies interact with data collection, see [Data Handling System](https://deepwiki.com/thu-ml/tianshou/2-data-handling-system).

 
## Core Concepts

 In Tianshou, a policy defines how an agent acts in an environment and how it learns from experience. The Policy Framework provides:

 
 - A common interface for all RL algorithms
 - Utilities for common RL operations (calculating returns, handling exploration)
 - Implementations of popular algorithms (DQN, PPO, SAC, etc.)
 
 
### Policy Class Hierarchy

 
```

```

 Sources:

 
 - [tianshou/policy/base.py136-722](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L136-L722)
 - [tianshou/policy/modelfree/pg.py53-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/pg.py#L53-L236)
 - [tianshou/policy/modelfree/a2c.py33-207](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/a2c.py#L33-L207)
 - [tianshou/policy/modelfree/ppo.py52-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py#L52-L236)
 - [tianshou/policy/modelfree/dqn.py31-255](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/dqn.py#L31-L255)
 - [tianshou/policy/modelfree/ddpg.py34-225](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ddpg.py#L34-L225)
 - [tianshou/policy/modelfree/sac.py54-263](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/sac.py#L54-L263)
 - [tianshou/policy/modelfree/td3.py28-164](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/td3.py#L28-L164)
 
 
## BasePolicy

 The `BasePolicy` class is the foundation of all policy implementations in Tianshou. It inherits from `torch.nn.Module`, which enables seamless integration with PyTorch's features for model saving, loading, and gradient-based optimization.

 
### Key Methods

 
```

```

 Sources:

 
 - [tianshou/policy/base.py317-324](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L317-L324) - `forward` method
 - [tianshou/policy/base.py459-480](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L459-L480) - `learn` method
 - [tianshou/policy/base.py442-457](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L442-L457) - `process_fn` method
 - [tianshou/policy/base.py482-504](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L482-L504) - `post_process_fn` method
 - [tianshou/policy/base.py506-553](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L506-L553) - `update` method
 
 
#### Abstract Methods

 
 - **`forward`**: Computes action based on observation

 
 - **Input**: `batch` containing observations
 - **Output**: A batch with at least `act` (actions) and `state` (internal state)
 - The algorithm-specific output is defined by each policy implementation
 - **`learn`**: Updates policy with a batch of data

 
 - **Input**: Processed batch of data
 - **Output**: `TrainingStats` object containing metrics (losses, etc.)
 - Core learning logic for the specific algorithm
 
 
#### Update Cycle

 The update cycle in BasePolicy coordinates the learning process:

 
```

```

 Sources:

 
 - [tianshou/policy/base.py506-553](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L506-L553)
 
 
### Action Handling

 `BasePolicy` provides methods for handling actions:

 
 - **`map_action`**: Maps network output (typically in [-1, 1] range) to the environment's action space
 - **`map_action_inverse`**: Maps environment actions back to network's range
 - **`exploration_noise`**: Adds exploration noise to actions (overridden by specific policies)
 
 Sources:

 
 - [tianshou/policy/base.py367-400](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L367-L400) - `map_action` method
 - [tianshou/policy/base.py402-428](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L402-L428) - `map_action_inverse` method
 - [tianshou/policy/base.py269-285](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L269-L285) - `exploration_noise` method
 
 
### Returns Calculation

 The policy framework provides key methods for calculating returns and advantages:

 
 - **`compute_episodic_return`**: Calculates episodic returns using GAE (Generalized Advantage Estimation)

 
 - Used by on-policy algorithms like PPO
 - Can compute Monte Carlo returns when `gae_lambda=1.0`
 - **`compute_nstep_return`**: Computes n-step returns for Q-learning

 
 - Used by off-policy algorithms like DQN, DDPG, SAC
 
 Sources:

 
 - [tianshou/policy/base.py576-626](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L576-L626) - `compute_episodic_return` method
 - [tianshou/policy/base.py629-721](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L629-L721) - `compute_nstep_return` method
 - [tianshou/policy/base.py760-806](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L760-L806) - `_gae_return` function
 - [tianshou/policy/base.py827-887](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L827-L887) - `_nstep_return` function
 
 
## Policy Implementations

 Tianshou includes implementations of popular reinforcement learning algorithms, organized into several categories.

 
### Value-Based Policies

 Value-based methods focus on estimating the value of states and actions:

 
 - **DQNPolicy**: Deep Q-Network with variants 
 - Supports Double DQN, Dueling DQN architecture
 - Uses n-step returns and target networks
 
 Sources:

 
 - [tianshou/policy/modelfree/dqn.py31-255](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/dqn.py#L31-L255)
 
 
### Policy Gradient Methods

 Policy gradient methods directly optimize the policy:

 
 - **PGPolicy**: Basic policy gradient (REINFORCE)

 
 - Monte Carlo returns
 - No value function baseline
 - **A2CPolicy**: Advantage Actor-Critic

 
 - Uses a value function as baseline
 - Reduces variance with advantage calculation
 - **PPOPolicy**: Proximal Policy Optimization

 
 - Clip mechanism to limit policy updates
 - Better sample efficiency than A2C
 
 Sources:

 
 - [tianshou/policy/modelfree/pg.py53-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/pg.py#L53-L236)
 - [tianshou/policy/modelfree/a2c.py33-207](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/a2c.py#L33-L207)
 - [tianshou/policy/modelfree/ppo.py52-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py#L52-L236)
 
 
### Actor-Critic Methods for Continuous Action Spaces

 Specialized algorithms for continuous control tasks:

 
 - **DDPGPolicy**: Deep Deterministic Policy Gradient

 
 - Deterministic policy for continuous actions
 - Uses target networks and replay buffer
 - **TD3Policy**: Twin Delayed DDPG

 
 - Dual critics to reduce overestimation
 - Delayed policy updates
 - Target policy smoothing
 - **SACPolicy**: Soft Actor-Critic

 
 - Maximum entropy reinforcement learning
 - Stochastic policy with automatic temperature tuning
 - Dual critics like TD3
 
 Sources:

 
 - [tianshou/policy/modelfree/ddpg.py34-225](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ddpg.py#L34-L225)
 - [tianshou/policy/modelfree/td3.py28-164](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/td3.py#L28-L164)
 - [tianshou/policy/modelfree/sac.py54-263](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/sac.py#L54-L263)
 
 
## Data Flow in Policy Learning

 The following diagram shows the data flow during policy learning:

 
```

```

 Sources:

 
 - [tianshou/policy/base.py506-553](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L506-L553) - `update` method
 
 
## Training Statistics

 Policies in Tianshou return standardized training statistics through dataclass objects that inherit from `TrainingStats`:

 
| Policy Type | Training Statistics |
|---|---|
| DQN | loss |
| PG | loss |
| A2C | loss, actor_loss, vf_loss, ent_loss |
| PPO | loss, clip_loss, vf_loss, ent_loss |
| DDPG | actor_loss, critic_loss |
| TD3 | actor_loss, critic1_loss, critic2_loss |
| SAC | actor_loss, critic1_loss, critic2_loss, alpha, alpha_loss |

 Sources:

 
 - [tianshou/policy/base.py37-71](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L37-L71) - `TrainingStats` base class
 - [tianshou/policy/modelfree/dqn.py23-26](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/dqn.py#L23-L26) - `DQNTrainingStats`
 - [tianshou/policy/modelfree/pg.py45-48](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/pg.py#L45-L48) - `PGTrainingStats`
 - [tianshou/policy/modelfree/a2c.py21-27](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/a2c.py#L21-L27) - `A2CTrainingStats`
 - [tianshou/policy/modelfree/ppo.py21-45](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py#L21-L45) - `PPOTrainingStats`
 - [tianshou/policy/modelfree/ddpg.py25-28](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ddpg.py#L25-L28) - `DDPGTrainingStats`
 - [tianshou/policy/modelfree/td3.py17-22](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/td3.py#L17-L22) - `TD3TrainingStats`
 - [tianshou/policy/modelfree/sac.py41-47](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/sac.py#L41-L47) - `SACTrainingStats`
 
 
## Example: Policy Update Process

 The following example shows the key steps of a policy update in PPO:

 
```

```

 Sources:

 
 - [tianshou/policy/modelfree/ppo.py149-166](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py#L149-L166) - `process_fn` method
 - [tianshou/policy/modelfree/ppo.py169-235](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/ppo.py#L169-L235) - `learn` method
 - [tianshou/policy/base.py576-626](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L576-L626) - `compute_episodic_return` method
 
 
## Creating Custom Policies

 To create a custom policy, you need to inherit from `BasePolicy` and implement at minimum:

 
 - **`forward`**: Define how the policy computes actions from observations
 - **`learn`**: Define how the policy updates its parameters from experience data
 
 For most algorithms, you'll also need to override:

 
 - **`process_fn`**: Pre-process data before learning (e.g., computing returns)
 
 Example structure for a custom policy:

 
```

```

 Sources:

 
 - [tianshou/policy/base.py136-722](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L136-L722) - `BasePolicy` class
 - [tianshou/policy/modelfree/pg.py53-236](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/modelfree/pg.py#L53-L236) - Example of a simple policy implementation
 
 
## Integration with the Training Loop

 Policies in Tianshou are designed to work with the Trainer system, which handles the training loop:

 
```

```

 Sources:

 
 - [tianshou/policy/base.py506-553](https://github.com/thu-ml/tianshou/blob/90846f6b/tianshou/policy/base.py#L506-L553) - `update` method
 
 
## Conclusion

 The Policy Framework in Tianshou provides a flexible and extensible foundation for implementing reinforcement learning algorithms. By standardizing the interface and providing common utilities, it enables researchers and practitioners to focus on algorithm-specific components while leveraging the robust infrastructure for data handling, environment interaction, and training.

 For more details on specific policy implementations, see [Value-Based Algorithms](https://deepwiki.com/thu-ml/tianshou/3.2-value-based-algorithms), [Policy Gradient Algorithms](https://deepwiki.com/thu-ml/tianshou/3.3-policy-gradient-algorithms), and [Actor-Critic Algorithms](https://deepwiki.com/thu-ml/tianshou/3.4-actor-critic-algorithms).
