> 来源: [https://deepwiki.com/AgileRL/AgileRL/4-evolutionary-hyperparameter-optimization](https://deepwiki.com/AgileRL/AgileRL/4-evolutionary-hyperparameter-optimization)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Evolutionary Hyperparameter Optimization

  Relevant source files 
 - [agilerl/hpo/mutation.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/mutation.py)
 - [agilerl/hpo/tournament.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/tournament.py)
 - [agilerl/utils/utils.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py)
 
  This document covers AgileRL's core evolutionary hyperparameter optimization (EvoHPO) system, which automatically optimizes neural network architectures, parameters, and RL hyperparameters during training. The system creates populations of agents, applies various mutations, and uses tournament selection to evolve better-performing agents over time.

 For information about specific training loops that use this system, see [Training Framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework). For details about the evolvable neural network architectures, see [Neural Network Architecture](https://deepwiki.com/AgileRL/AgileRL/5-neural-network-architecture).

 
## Overview

 AgileRL's evolutionary approach replaces traditional hyperparameter tuning by treating RL agents as individuals in an evolving population. During training, agents are periodically evaluated, selected based on fitness, and mutated to explore the hyperparameter space.

 
### EvoHPO System Architecture

 
```

```

 Sources: [agilerl/utils/utils.py154-552](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L154-L552) [agilerl/hpo/tournament.py11-191](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/tournament.py#L11-L191) [agilerl/hpo/mutation.py132-489](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/mutation.py#L132-L489)

 
## Population Creation and Management

 The evolutionary system begins by creating a population of identical agents using the `create_population` function. Each agent is assigned a unique index and can be configured with custom network architectures and hyperparameters.

 
### Population Creation Process

 
```

```

 The `create_population` function supports all major RL algorithms:

 
| Algorithm | Class | Key Parameters |
|---|---|---|
| DQN | DQN | batch_size, lr, learn_step, gamma, tau |
| Rainbow DQN | RainbowDQN | beta, prior_eps, num_atoms, v_min, v_max |
| DDPG | DDPG | lr_actor, lr_critic, O_U_noise, expl_noise |
| TD3 | TD3 | policy_freq, additional critic networks |
| PPO | PPO | gae_lambda, clip_coef, ent_coef, vf_coef |
| MADDPG | MADDPG | agent_ids, multi-agent specific parameters |
| MATD3 | MATD3 | Multi-agent TD3 parameters |
| IPPO | IPPO | Independent PPO for multi-agent |
| GRPO | GRPO | LLM-specific parameters, group_size, temperature |

 Sources: [agilerl/utils/utils.py154-552](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L154-L552)

 
## Tournament Selection

 The `TournamentSelection` class implements the selection mechanism that determines which agents survive and reproduce. It uses fitness-based selection with optional elitism to maintain the best-performing agent.

 
### Tournament Selection Components

 
```

```

 The selection process differs between standard RL algorithms and LLM algorithms:

 **Standard Agents**: Use `_select_standard_agents` which creates clones of selected agents with new indices.

 **LLM Agents**: Use `_select_llm_agents` which handles memory management more carefully due to the large size of language models, including cleanup of unwanted agents.

 Sources: [agilerl/hpo/tournament.py11-191](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/tournament.py#L11-L191)

 
## Mutation System

 The `Mutations` class implements five types of mutations that can be applied to agents. Each mutation type has a configurable probability and targets different aspects of the agent.

 
### Mutation Types and Implementation

 
```

```

 
### Mutation Type Details

 
| Mutation Type | Method | Target | Key Features |
|---|---|---|---|
| No Mutation | no_mutation | None | Returns agent unchanged, sets mut = "None" |
| Architecture | architecture_mutate | Network structure | Adds/removes layers/nodes, handles bandit algorithms |
| Parameters | parameter_mutation | Network weights | Applies noise to weight matrices, supports vectorized operations |
| Activation | activation_mutation | Activation functions | Changes activation layers, excluded for policy gradient methods |
| RL Hyperparameters | rl_hyperparam_mutation | Learning parameters | Mutates learning rates, batch sizes, etc. |

 **Architecture Mutations**: Use the evolvable module's `sample_mutation_method` to determine specific architectural changes. The same mutation is applied consistently across all evaluation networks (policy, critics, etc.).

 **Parameter Mutations**: Implement sophisticated weight perturbation with three strategies:

 
 - Normal mutation: Add noise proportional to current weight magnitude
 - Super mutation: Add larger noise with higher probability
 - Reset mutation: Completely reinitialize weights
 
 **RL Hyperparameter Mutations**: Sample from a configured `HyperparameterConfig` and apply multiplicative/additive changes to parameters like learning rates, batch sizes, and algorithm-specific parameters.

 Sources: [agilerl/hpo/mutation.py132-1006](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/mutation.py#L132-L1006)

 
## Integration with Training

 The evolutionary system integrates with training through the `tournament_selection_and_mutation` function, which orchestrates the complete evolutionary cycle.

 
### Training Integration Workflow

 
```

```

 
### Distributed Training Considerations

 The system handles distributed training through HuggingFace Accelerate:

 
 - **Model Unwrapping**: Models are unwrapped from the accelerator before selection/mutation
 - **Main Process Execution**: Selection and mutation occur only on the main process
 - **Model Synchronization**: Updated models are saved and loaded across processes
 - **LLM Special Handling**: Language models use `consolidate_mutations` to broadcast changes
 
 
### Configuration Parameters

 The evolutionary system accepts several configuration parameters:

 
```

```

 Sources: [agilerl/utils/utils.py605-696](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L605-L696) [agilerl/hpo/mutation.py163-177](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/mutation.py#L163-L177) [agilerl/hpo/tournament.py24-39](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/tournament.py#L24-L39)

 
## Fitness Evaluation and Tracking

 Agents track their performance through fitness scores stored in their `fitness` attribute. The tournament selection uses the mean of the last `eval_loop` fitness scores to determine agent ranking.

 
### Fitness Management

 
```

```

 Agents maintain several tracking attributes:

 
 - `fitness`: List of fitness scores over time
 - `steps`: List of training steps corresponding to fitness evaluations
 - `mut`: String indicating the last mutation applied
 - `index`: Unique identifier for the agent
 
 The system also provides utility functions like `print_hyperparams` and `plot_population_score` for monitoring evolutionary progress.

 Sources: [agilerl/utils/utils.py822-852](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L822-L852) [agilerl/hpo/tournament.py66-71](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/hpo/tournament.py#L66-L71)
