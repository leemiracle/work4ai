> 来源: [https://deepwiki.com/AgileRL/AgileRL/3-training-framework](https://deepwiki.com/AgileRL/AgileRL/3-training-framework)
> DeepWiki AgileRL/AgileRL | Last indexed: 25 June 2025 (03307c

# Training Framework

  Relevant source files 
 - [agilerl/algorithms/ilql.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/algorithms/ilql.py)
 - [agilerl/training/train_bandits.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_bandits.py)
 - [agilerl/training/train_off_policy.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py)
 - [agilerl/training/train_offline.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py)
 - [agilerl/training/train_on_policy.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py)
 - [agilerl/utils/log_utils.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/log_utils.py)
 - [demos/demo_bandit.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/demos/demo_bandit.py)
 - [docs/distributed_training/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/distributed_training/index.rst)
 - [docs/off_policy/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/off_policy/index.rst)
 - [docs/offline_training/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/offline_training/index.rst)
 - [docs/on_policy/index.rst](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/on_policy/index.rst)
 - [tutorials/Language/train_bc_lm.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/tutorials/Language/train_bc_lm.py)
 - [tutorials/Language/train_ilql.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/tutorials/Language/train_ilql.py)
 - [tutorials/PettingZoo/agilerl_dqn_curriculum.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/tutorials/PettingZoo/agilerl_dqn_curriculum.py)
 - [tutorials/Skills/agilerl_skills_curriculum.py](https://github.com/AgileRL/AgileRL/blob/03307c7b/tutorials/Skills/agilerl_skills_curriculum.py)
 
  AgileRL's Training Framework provides the core orchestration system that coordinates reinforcement learning training across different paradigms. It serves as the central hub that integrates algorithms, evolutionary hyperparameter optimization, neural networks, and data management components into unified training loops.

 This framework handles five main training paradigms: on-policy, off-policy, offline, multi-agent, and LLM fine-tuning. For specific algorithm implementations, see [Reinforcement Learning Algorithms](https://deepwiki.com/AgileRL/AgileRL/2-reinforcement-learning-algorithms). For evolutionary optimization details, see [Evolutionary Hyperparameter Optimization](https://deepwiki.com/AgileRL/AgileRL/4-evolutionary-hyperparameter-optimization).

 
## Training Framework Architecture

 The Training Framework consists of specialized training functions that orchestrate different RL paradigms while maintaining a consistent interface for evolutionary hyperparameter optimization.

 
### Core Training Functions

 
```

```

 Sources: [agilerl/training/train_on_policy.py28-52](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L28-L52) [agilerl/training/train_off_policy.py37-69](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L37-L69) [agilerl/training/train_offline.py30-58](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py#L30-L58) [agilerl/training/train_bandits.py31-57](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_bandits.py#L31-L57)

 
### Training Function Interface

 All training functions share a consistent interface that enables seamless integration with evolutionary hyperparameter optimization:

 
| Parameter | Type | Purpose |
|---|---|---|
| env | gym.Env | Training environment |
| env_name | str | Environment identifier |
| algo | str | Algorithm name |
| pop | List[Algorithm] | Population of agents |
| max_steps | int | Maximum training steps |
| evo_steps | int | Evolution frequency |
| tournament | TournamentSelection | Selection mechanism |
| mutation | Mutations | Mutation operators |
| accelerator | Accelerator | Distributed training support |

 Sources: [agilerl/training/train_on_policy.py28-52](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L28-L52) [agilerl/training/train_off_policy.py37-69](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L37-L69) [agilerl/training/train_offline.py30-58](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py#L30-L58)

 
## Training Paradigm Implementation

 
### Training Loop Structure

 Each training paradigm follows a consistent structure while adapting to specific requirements:

 
```

```

 Sources: [agilerl/training/train_on_policy.py199-444](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L199-L444) [agilerl/training/train_off_policy.py235-582](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L235-L582) [agilerl/training/train_offline.py245-369](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py#L245-L369)

 
### Experience Collection Patterns

 Different paradigms handle experience collection distinctly:

 
```

```

 Sources: [agilerl/training/train_on_policy.py212-296](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L212-L296) [agilerl/training/train_off_policy.py255-408](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L255-L408) [agilerl/training/train_offline.py173-207](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py#L173-L207) [agilerl/training/train_bandits.py208-239](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_bandits.py#L208-L239)

 
## Integration with Evolutionary Components

 
### Population Management Flow

 The training framework integrates evolutionary hyperparameter optimization through a standardized flow:

 
```

```

 Sources: [agilerl/training/train_on_policy.py386-398](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L386-L398) [agilerl/training/train_off_policy.py524-536](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L524-L536) [agilerl/utils/utils.py20-23](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L20-L23)

 
### Distributed Training Integration

 The framework supports distributed training through `HuggingFace Accelerate`:

 
```

```

 Sources: [agilerl/training/train_off_policy.py197-213](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L197-L213) [agilerl/training/train_offline.py208-215](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_offline.py#L208-L215) [docs/distributed_training/index.rst37-251](https://github.com/AgileRL/AgileRL/blob/03307c7b/docs/distributed_training/index.rst#L37-L251)

 
## Monitoring and Checkpointing

 
### Logging Integration

 The framework provides comprehensive logging through Weights & Biases and console output:

 
| Metric Category | Tracked Values |
|---|---|
| Training Progress | global_step, fps, train/mean_score |
| Evaluation | eval/mean_fitness, eval/best_fitness |
| Population Stats | Individual agent losses, entropy values |
| Evolution | Agent indices, mutation types, step counts |

 Sources: [agilerl/training/train_on_policy.py320-369](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L320-L369) [agilerl/training/train_off_policy.py448-507](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L448-L507)

 
### Checkpoint Management

 
```

```

 Sources: [agilerl/training/train_on_policy.py422-432](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_on_policy.py#L422-L432) [agilerl/training/train_off_policy.py560-570](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/training/train_off_policy.py#L560-L570) [agilerl/utils/utils.py425-476](https://github.com/AgileRL/AgileRL/blob/03307c7b/agilerl/utils/utils.py#L425-L476)
