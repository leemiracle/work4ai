> 来源: [https://deepwiki.com/ShangtongZhang/DeepRL/5-running-experiments](https://deepwiki.com/ShangtongZhang/DeepRL/5-running-experiments)
> DeepWiki ShangtongZhang/DeepRL | Last indexed: 23 April 2025 (c0968b

# Running Experiments

  Relevant source files 
 - [docker_batch.sh](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/docker_batch.sh)
 - [examples.py](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py)
 - [template_jobs.py](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py)
 
  This document explains how to run reinforcement learning experiments using the DeepRL framework. It covers configuring and executing single experiments, batch experiments, and using the Docker environment for reproducible results. For information about specific agents, see [Agents](https://deepwiki.com/ShangtongZhang/DeepRL/2-agents), and for neural network architectures, see [Neural Networks](https://deepwiki.com/ShangtongZhang/DeepRL/3-neural-networks).

 
## Experiment Configuration and Execution Overview

 The DeepRL framework provides a flexible system for running RL experiments. Experiments are configured using the `Config` class, which allows you to specify parameters for agents, environments, neural networks, and training procedures.

 
```

```

 Sources: [examples.py1-654](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L1-L654) [template_jobs.py1-127](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L1-L127)

 
## Single Experiments

 Single experiments are defined in `examples.py` and provide complete configurations for specific algorithm-environment combinations.

 
### Running a Single Experiment

 To run a single experiment, you can uncomment the desired function call at the bottom of `examples.py`:

 
 - Select the environment by setting the `game` variable
 - Uncomment the desired algorithm function
 - Run `examples.py`
 
 
```

```

 Sources: [examples.py620-654](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L620-L654)

 
### Example Algorithm Configuration

 Each algorithm function in `examples.py` follows a similar pattern:

 
 - Create a `Config` object
 - Set up task/environment with `config.task_fn`
 - Define network architecture with `config.network_fn`
 - Configure optimizer with `config.optimizer_fn`
 - Set hyperparameters for training
 - Call `run_steps()` with the appropriate agent
 
 Here's an example from DQN configuration for pixel-based environments:

 
| Parameter | Purpose | Example Value |
|---|---|---|
| task_fn | Function that creates environment | lambda: Task(config.game) |
| network_fn | Function that creates neural network | lambda: VanillaNet(config.action_dim, NatureConvBody()) |
| optimizer_fn | Function that creates optimizer | lambda params: torch.optim.RMSprop(params, lr=0.00025) |
| batch_size | Size of training batches | 32 |
| discount | Discount factor | 0.99 |
| exploration_steps | Number of random actions at start | 50000 |
| max_steps | Total training steps | int(2e7) |

 Sources: [examples.py55-97](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L55-L97)

 
## Batch Experiments

 For systematic evaluations across multiple algorithms and environments, the framework provides batch experiment functionality through `template_jobs.py`.

 
### Configuring Batch Experiments

 Batch experiments are defined in `template_jobs.py`. Two primary batch functions are available:

 
 - `batch_atari()` - For Atari game environments
 - `batch_mujoco()` - For MuJoCo continuous control environments
 
 These functions define:

 
 - A list of games to evaluate
 - A list of algorithms to use
 - Optional parameters for each algorithm
 - Run counts for statistical significance
 
 
```

```

 Sources: [template_jobs.py4-114](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L4-L114)

 
### Running Batch Experiments

 To run a batch experiment:

 
 - Modify the game list and algorithm list in the appropriate batch function
 - Execute the script with the index parameter: 
```

```

 where `[index]` selects which experiment from the parameter matrix to run
 
 For parallel execution, you can use the Docker batch script.

 Sources: [template_jobs.py117-127](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L117-L127)

 
## Docker Environment

 The DeepRL framework includes Docker scripts to ensure experiment reproducibility across different systems.

 
### Docker Scripts

 The repository includes several Docker scripts:

 
| Script | Purpose |
|---|---|
| docker_build.sh | Builds the Docker image with all dependencies |
| docker_shell.sh | Opens an interactive shell in the Docker container |
| docker_python.sh | Runs a Python script in the Docker container |
| docker_batch.sh | Runs multiple experiments in parallel using Docker |

 
### Running Parallel Experiments with Docker

 The `docker_batch.sh` script automates running multiple experiments in parallel:

 
```

```

 Sources: [docker_batch.sh1-27](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/docker_batch.sh#L1-L27)

 To run batch experiments with Docker:

 
 - Ensure Docker is installed and the image is built
 - Configure the GPU list in `docker_batch.sh`
 - Execute the script: 
```

```
 
 The script will run multiple experiments in parallel, assigning them to available GPUs.

 Sources: [docker_batch.sh11-17](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/docker_batch.sh#L11-L17)

 
## Experiment Configuration Details

 The configuration system is central to running experiments. The `Config` class manages all parameters for an experiment.

 
### Key Configuration Parameters

 
| Parameter Category | Common Parameters | Purpose |
|---|---|---|
| Environment | task_fn, eval_env | Define training and evaluation environments |
| Neural Network | network_fn | Define network architecture |
| Optimization | optimizer_fn, discount, gradient_clip | Control learning process |
| Exploration | random_action_prob, exploration_steps | Define exploration strategy |
| Training | max_steps, rollout_length, batch_size | Control training procedure |
| Evaluation | eval_interval, eval_episodes | Define evaluation schedule |

 
### Algorithm-Specific Configurations

 Different algorithms require specific configuration parameters:

 
 - **DQN Family:**

 
 - target_network_update_freq
 - double_q
 - categorical_n_atoms (for C51)
 - num_quantiles (for QR-DQN)
 - **Policy Gradient Methods:**

 
 - entropy_weight
 - use_gae
 - gae_tau
 - **Actor-Critic Methods:**

 
 - target_network_mix
 - random_process_fn
 
 Sources: [examples.py11-617](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L11-L617)

 
## Monitoring and Analyzing Results

 During experiment execution, the framework logs progress to both the console and TensorBoard.

 
### Logging System

 Training progress is logged to:

 
 - Console output
 - TensorBoard event files in the `tf_log` directory
 - Checkpoint files in the `data` directory
 
 
### Directories

 
| Directory | Purpose |
|---|---|
| log | Contains log files from training |
| tf_log | Contains TensorBoard event files |
| data | Contains saved model checkpoints |

 Sources: [examples.py621-622](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L621-L622) [template_jobs.py118-119](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L118-L119)

 
### Visualizing Results

 To visualize results, you can use TensorBoard:

 
```

```

 This will start a web server that displays training metrics over time.

 
## Common Experiment Tasks

 
### Setting Random Seeds

 For reproducibility, the framework provides functions to set random seeds:

 
```

```

 Sources: [examples.py624](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L624-L624) [template_jobs.py120](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L120-L120)

 
### Selecting Compute Device

 You can select whether to use CPU or GPU:

 
```

```

 Sources: [examples.py625-627](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L625-L627) [template_jobs.py125](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L125-L125)

 
### Creating Output Directories

 Before running experiments, ensure necessary directories exist:

 
```

```

 Sources: [examples.py621-622](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L621-L622) [template_jobs.py118-119](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L118-L119)

 
## Integration with Other Components

 The experiment system integrates with other components of the DeepRL framework:

 
```

```

 This diagram shows how the experiment system connects with other components of the framework, such as agents, neural networks, and utilities.

 Sources: [examples.py1-654](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/examples.py#L1-L654) [template_jobs.py1-127](https://github.com/ShangtongZhang/DeepRL/blob/c0968b5c/template_jobs.py#L1-L127)
