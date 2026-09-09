> 来源: [https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/7-running-experiments](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/7-running-experiments)
> DeepWiki ikostrikov/pytorch-a2c-ppo-acktr-gail | Last indexed: 21 April 2025 (41332b

# Running Experiments

  Relevant source files 
 - [README.md](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/README.md?plain=1)
 - [a2c_ppo_acktr/arguments.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py)
 - [generate_tmux_yaml.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/generate_tmux_yaml.py)
 - [run_all.yaml](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/run_all.yaml)
 
  This page provides a comprehensive guide on configuring and executing training runs using the various reinforcement learning algorithms (A2C, PPO, ACKTR) and GAIL imitation learning in this codebase. It covers basic usage patterns, command-line arguments, and techniques for running multiple experiments in parallel. For information about evaluating trained agents, see [Evaluation and Visualization](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/8-evaluation-and-visualization).

 
## Basic Usage

 The main entry point for training reinforcement learning agents is the `main.py` script. This script initializes the environment, sets up the policy network, and executes the training loop according to the specified command-line arguments.

 
### Basic Command Structure

 
```

```

 Here's a basic workflow diagram showing how experiments are configured and executed:

 
```

```

 Sources: [main.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/main.py) [a2c_ppo_acktr/arguments.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py)

 
### Example Commands

 Here are some example commands for running common experiments:

 
#### A2C with Atari Environment

 
```

```

 
#### PPO with Atari Environment

 
```

```

 
#### PPO with MuJoCo Environment

 
```

```

 Sources: [README.md82-116](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/README.md?plain=1#L82-L116)

 
## Command-Line Arguments

 The framework offers a wide range of command-line arguments to configure experiments. These arguments control everything from the algorithm selection to hyperparameters and logging settings.

 
### Key Arguments by Category

 
```

```

 Sources: [a2c_ppo_acktr/arguments.py6-161](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L6-L161)

 
### Common Arguments Table

 The following table describes the most commonly used arguments:

 
| Argument | Description | Default Value |
|---|---|---|
| --algo | RL algorithm to use (a2c, ppo, acktr) | a2c |
| --env-name | Environment ID | PongNoFrameskip-v4 |
| --lr | Learning rate | 7e-4 |
| --gamma | Discount factor | 0.99 |
| --num-processes | Number of parallel environments | 16 |
| --num-steps | Number of forward steps in A2C | 5 |
| --num-env-steps | Total environment steps to train | 10e6 |
| --seed | Random seed | 1 |
| --log-dir | Directory for logs | /tmp/gym/ |
| --save-dir | Directory for saving models | ./trained_models/ |

 Sources: [a2c_ppo_acktr/arguments.py6-161](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L6-L161)

 
### Algorithm-Specific Arguments

 
#### PPO-Specific Arguments

 
| Argument | Description | Default Value |
|---|---|---|
| --clip-param | PPO clip parameter | 0.2 |
| --ppo-epoch | Number of PPO epochs | 4 |
| --num-mini-batch | Number of batches for PPO | 32 |
| --use-gae | Use Generalized Advantage Estimation | False |
| --gae-lambda | GAE lambda parameter | 0.95 |

 
#### GAIL-Specific Arguments

 
| Argument | Description | Default Value |
|---|---|---|
| --gail | Use GAIL | False |
| --gail-experts-dir | Directory with expert demonstrations | ./gail_experts |
| --gail-batch-size | GAIL batch size | 128 |
| --gail-epoch | GAIL epochs | 5 |

 Sources: [a2c_ppo_acktr/arguments.py11-25](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L11-L25) [a2c_ppo_acktr/arguments.py86-99](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L86-L99)

 
## Environment-Specific Configurations

 Different environments require different hyperparameters for optimal performance. Here are recommended configurations for common environment types:

 
### Atari Environments

 
```

```

 
### MuJoCo Environments

 
```

```

 Sources: [README.md82-116](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/README.md?plain=1#L82-L116)

 
## Logging and Monitoring

 The framework provides several options for logging training progress and saving trained models:

 
 - `--log-dir`: Directory for storing tensorboard logs
 - `--log-interval`: Frequency of logging (in number of updates)
 - `--save-interval`: Frequency of saving the model (in number of updates)
 - `--eval-interval`: Frequency of evaluating the model (in number of updates)
 
 The logs include metrics such as:

 
 - Episode rewards
 - Value loss
 - Action loss
 - Entropy
 - Learning rate
 
 Sources: [a2c_ppo_acktr/arguments.py100-114](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L100-L114)

 
## Running Parallel Experiments

 For comprehensive benchmarking, it's often necessary to run multiple experiments with different seeds or hyperparameters. This repository provides tools for running parallel experiments using tmux.

 
### Using generate_tmux_yaml.py

 The `generate_tmux_yaml.py` script generates a YAML configuration for running multiple experiments in parallel using tmux:

 
```

```

 This generates a YAML file (`run_all.yaml`) that can be used with tmuxp to create a tmux session with multiple panes, each running a different experiment.

 
```

```

 Sources: [generate_tmux_yaml.py1-37](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/generate_tmux_yaml.py#L1-L37) [run_all.yaml1-193](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/run_all.yaml#L1-L193)

 
### Workflow for Parallel Experiments

 
 - Generate the YAML configuration:

 
```

```
 - Install tmuxp if not already installed:

 
```

```
 - Start the tmux session:

 
```

```
 
 This will create a tmux session with multiple panes, each running a different experiment with a different seed and/or environment.

 Sources: [generate_tmux_yaml.py1-37](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/generate_tmux_yaml.py#L1-L37) [run_all.yaml1-193](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/run_all.yaml#L1-L193)

 
## Reproducibility Considerations

 Reinforcement learning experiments are often sensitive to initialization and can be difficult to reproduce. To ensure reproducibility:

 
 - Always set a specific seed with `--seed <SEED>`
 - For deterministic GPU operations, use `--cuda-deterministic` (note: this may slow down training)
 - Run multiple seeds to establish statistical significance
 - Use the exact hyperparameters recommended in the README for each environment/algorithm combination
 
 The repository follows these best practices to maintain reproducibility across experiments.

 Sources: [README.md67-69](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/README.md?plain=1#L67-L69) [a2c_ppo_acktr/arguments.py69-74](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/a2c_ppo_acktr/arguments.py#L69-L74)

 
## Environment Types Support

 The framework supports various environment types:

 
 - Atari Learning Environment (e.g., `PongNoFrameskip-v4`)
 - MuJoCo physics simulation (e.g., `Reacher-v2`, `HalfCheetah-v2`)
 - PyBullet (alternative to MuJoCo)
 - DeepMind Control Suite via dm_control2gym
 
 To use DeepMind Control Suite environments, use the format:

 
```

```

 Sources: [README.md30-40](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/README.md?plain=1#L30-L40)

 
## Next Steps

 After running your experiments and training models, you may want to:

 
 - Evaluate the trained models using the `enjoy.py` script (see [Evaluation and Visualization](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/8-evaluation-and-visualization))
 - Visualize training results using the `visualize.ipynb` notebook
 - Compare performance across different algorithms and environments
 
 Each of these is covered in other sections of this documentation.
