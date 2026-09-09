> 来源: [https://deepwiki.com/chainer/chainerrl/5-examples-and-usage](https://deepwiki.com/chainer/chainerrl/5-examples-and-usage)
> DeepWiki chainer/chainerrl | Last indexed: 8 June 2025 (7eed37

# Examples and Usage

  Relevant source files 
 - [examples/atari/reproduction/a3c/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/a3c/README.md?plain=1)
 - [examples/atari/reproduction/dqn/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/dqn/README.md?plain=1)
 - [examples/atari/reproduction/iqn/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/iqn/README.md?plain=1)
 - [examples/atari/reproduction/rainbow/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/rainbow/README.md?plain=1)
 - [examples/gym/train_a3c_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py)
 - [examples/gym/train_acer_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_acer_gym.py)
 - [examples/gym/train_categorical_dqn_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_categorical_dqn_gym.py)
 - [examples/gym/train_dqn_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py)
 - [examples/gym/train_pcl_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_pcl_gym.py)
 - [examples/gym/train_reinforce_gym.py](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_reinforce_gym.py)
 - [examples/mujoco/reproduction/ddpg/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ddpg/README.md?plain=1)
 - [examples/mujoco/reproduction/ppo/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ppo/README.md?plain=1)
 - [examples/mujoco/reproduction/soft_actor_critic/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/soft_actor_critic/README.md?plain=1)
 - [examples/mujoco/reproduction/td3/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/td3/README.md?plain=1)
 - [examples/mujoco/reproduction/trpo/README.md](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/trpo/README.md?plain=1)
 
  This page provides practical guidance for using ChainerRL through its comprehensive collection of examples and reproduction scripts. The examples demonstrate how to train reinforcement learning agents on standard benchmarks and reproduce results from published research papers.

 For information about the underlying training infrastructure, see [Training and Evaluation Infrastructure](https://deepwiki.com/chainer/chainerrl/4-training-and-evaluation-infrastructure). For details about specific RL algorithms, see [Reinforcement Learning Agents](https://deepwiki.com/chainer/chainerrl/2-reinforcement-learning-agents).

 
## Overview of Examples Structure

 ChainerRL provides examples organized into three main categories: basic training examples for getting started, algorithm reproduction scripts that match paper results, and a pretrained models system for immediate evaluation.

 
### Example Categories and Code Structure

 
```

```

 Sources: [examples/gym/train_dqn_gym.py1-187](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L1-L187) [examples/gym/train_a3c_gym.py1-203](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py#L1-L203) [examples/atari/reproduction/a3c/README.md1-139](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/a3c/README.md?plain=1#L1-L139) [examples/mujoco/reproduction/ppo/README.md1-90](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ppo/README.md?plain=1#L1-L90)

 
### Common Command Line Interface

 All examples follow a consistent command line interface pattern with standard options for training, evaluation, and model management.

 
| Option | Purpose | Example |
|---|---|---|
| --env | Environment name | --env CartPole-v0 |
| --gpu | GPU device ID (-1 for CPU) | --gpu 0 |
| --seed | Random seed | --seed 42 |
| --outdir | Output directory | --outdir results |
| --demo | Evaluation mode | --demo |
| --load | Load saved model | --load model.pkl |
| --load-pretrained | Load pretrained model | --load-pretrained |
| --steps | Training steps | --steps 1000000 |
| --eval-interval | Evaluation frequency | --eval-interval 10000 |

 Sources: [examples/gym/train_dqn_gym.py37-69](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L37-L69) [examples/gym/train_a3c_gym.py91-116](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py#L91-L116)

 
## Basic Training Examples

 The basic examples in `examples/gym/` demonstrate how to train popular RL algorithms on OpenAI Gym environments. These examples are designed for learning and experimentation with straightforward configurations.

 
### Environment Setup Pattern

 All basic examples follow a consistent environment setup pattern using ChainerRL wrappers:

 
```

```

 Sources: [examples/gym/train_dqn_gym.py81-99](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L81-L99) [examples/gym/train_a3c_gym.py133-149](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py#L133-L149)

 
### Agent Configuration Patterns

 The examples demonstrate different agent configuration patterns based on action space types:

 **Discrete Action Spaces (DQN Example):**

 
 - Uses `FCStateQFunctionWithDiscreteAction` for Q-functions
 - Employs `LinearDecayEpsilonGreedy` exploration
 - Configures `ReplayBuffer` or `PrioritizedReplayBuffer`
 
 **Continuous Action Spaces (DQN with NAF):**

 
 - Uses `FCQuadraticStateQFunction` for continuous control
 - Employs `AdditiveOU` exploration noise
 - Handles action clipping with `make_action_filtered`
 
 Sources: [examples/gym/train_dqn_gym.py107-128](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L107-L128) [examples/gym/train_dqn_gym.py153-160](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L153-L160)

 
### Training Loop Integration

 Basic examples use the high-level training functions from the `experiments` module:

 
```

```

 Sources: [examples/gym/train_dqn_gym.py167-183](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L167-L183) [examples/gym/train_a3c_gym.py176-198](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py#L176-L198)

 
## Algorithm Reproductions

 The reproduction scripts in `examples/atari/reproduction/` and `examples/mujoco/reproduction/` are designed to match published paper results with carefully tuned hyperparameters and evaluation protocols.

 
### Atari Reproduction Structure

 
```

```

 Sources: [examples/atari/reproduction/a3c/README.md32-43](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/a3c/README.md?plain=1#L32-L43) [examples/atari/reproduction/dqn/README.md34-49](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/dqn/README.md?plain=1#L34-L49) [examples/atari/reproduction/rainbow/README.md35-46](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/rainbow/README.md?plain=1#L35-L46)

 
### MuJoCo Reproduction Structure

 
```

```

 Sources: [examples/mujoco/reproduction/ppo/README.md42-59](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ppo/README.md?plain=1#L42-L59) [examples/mujoco/reproduction/trpo/README.md42-55](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/trpo/README.md?plain=1#L42-L55) [examples/mujoco/reproduction/ddpg/README.md39-82](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ddpg/README.md?plain=1#L39-L82)

 
### Evaluation Protocols

 Reproduction scripts implement rigorous evaluation protocols that match the original papers:

 **Atari Evaluation Protocol:**

 
 - Evaluation frequency: Every 1 million frames (250K timesteps)
 - Evaluation duration: 500K frames (125K timesteps) per evaluation
 - Episode constraints: Random no-ops (up to 30), time limits vary by algorithm
 - Reporting: Best intermediate score across 200 evaluations
 
 **MuJoCo Evaluation Protocol:**

 
 - Training duration: 2M timesteps for most algorithms
 - Evaluation frequency: Every 5K-50K timesteps depending on algorithm
 - Episode evaluation: 100 episodes without exploration noise
 - Reporting: Average return ± standard error across multiple seeds
 
 Sources: [examples/atari/reproduction/a3c/README.md110-125](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/a3c/README.md?plain=1#L110-L125) [examples/mujoco/reproduction/ppo/README.md42-52](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ppo/README.md?plain=1#L42-L52)

 
## Pretrained Models System

 ChainerRL provides a pretrained models system that allows immediate evaluation of trained agents without running lengthy training procedures.

 
### Loading Pretrained Models

 The pretrained model system uses the `--load-pretrained` flag with optional `--pretrained-type` specification:

 
```

```

 
### Pretrained Model Types

 
| Type | Description | Use Case |
|---|---|---|
| best | Best intermediate network during training | Highest performance evaluation |
| final | Final network after training completion | End-of-training state |

 Sources: [examples/atari/reproduction/dqn/README.md16-30](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/dqn/README.md?plain=1#L16-L30) [examples/atari/reproduction/rainbow/README.md16-30](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/rainbow/README.md?plain=1#L16-L30)

 
### Model Availability

 Pretrained models are available for:

 
 - **Atari domains**: DQN, A3C, Rainbow, IQN across 50+ games
 - **MuJoCo domains**: PPO, TRPO, DDPG, TD3, SAC across standard continuous control tasks
 
 Each reproduction script includes pretrained models that represent the performance reported in the corresponding README files.

 Sources: [examples/atari/reproduction/a3c/README.md16-19](https://github.com/chainer/chainerrl/blob/7eed3756/examples/atari/reproduction/a3c/README.md?plain=1#L16-L19) [examples/mujoco/reproduction/ppo/README.md19-23](https://github.com/chainer/chainerrl/blob/7eed3756/examples/mujoco/reproduction/ppo/README.md?plain=1#L19-L23)

 
## Practical Usage Patterns

 
### Quick Start for New Environments

 
 - **Choose an appropriate base example** based on action space:

 
 - Discrete actions: Use `train_dqn_gym.py` as starting point
 - Continuous actions: Use DQN with NAF or actor-critic methods
 - **Modify environment creation**:

 
```

```
 - **Adjust hyperparameters** in the argument parser section
 - **Run training**:

 
```

```
 
 
### Reproducing Paper Results

 
 - **Use the appropriate reproduction script** from the paper you want to reproduce
 - **Check requirements** in the README (e.g., MuJoCo Pro, atari_py)
 - **Run with paper-matching hyperparameters**: 
```

```
 - **Compare results** with the benchmarks provided in the README
 
 
### Custom Algorithm Development

 
 - **Start with the closest existing example** to your algorithm type
 - **Replace the agent creation section** with your custom agent
 - **Maintain the environment setup and training loop patterns**
 - **Use the same evaluation infrastructure** for consistent comparisons
 
 Sources: [examples/gym/train_dqn_gym.py33-187](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_dqn_gym.py#L33-L187) [examples/gym/train_a3c_gym.py88-202](https://github.com/chainer/chainerrl/blob/7eed3756/examples/gym/train_a3c_gym.py#L88-L202)
