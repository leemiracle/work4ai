> 来源: [https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/8-evaluation-and-visualization](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/8-evaluation-and-visualization)
> DeepWiki ikostrikov/pytorch-a2c-ppo-acktr-gail | Last indexed: 21 April 2025 (41332b

# Evaluation and Visualization

  Relevant source files 
 - [enjoy.py](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/enjoy.py)
 - [visualize.ipynb](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/visualize.ipynb)
 
  This page covers tools and methods for evaluating trained reinforcement learning agents and visualizing their performance in the PyTorch A2C/PPO/ACKTR/GAIL framework. Proper evaluation is critical for assessing how well trained agents perform, while visualization helps in understanding agent behavior and comparing different algorithms. For information about training the agents, see [Training System](https://deepwiki.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/2-training-system).

 
## Agent Evaluation with enjoy.py

 The primary tool for evaluating trained agents is `enjoy.py`, which loads a trained model and visualizes its performance in the environment. This script allows you to see how your trained agent behaves and can be used to create videos or analyze qualitative aspects of the learned policy.

 
```

```

 
### Command-Line Arguments

 The `enjoy.py` script accepts several command-line arguments to configure the evaluation:

 
| Argument | Default | Description |
|---|---|---|
| --seed | 1 | Random seed for reproducibility |
| --log-interval | 10 | Log interval, one log per n updates |
| --env-name | 'PongNoFrameskip-v4' | Environment to evaluate on |
| --load-dir | './trained_models/' | Directory where trained models are stored |
| --non-det | False | Whether to use a non-deterministic policy |

 
### Basic Usage

 To evaluate a trained agent, run:

 
```

```

 This will load the trained model from `./trained_models/PongNoFrameskip-v4.pt` and run it in the environment with visualization.

 
### Evaluation Process

 The evaluation process in `enjoy.py` follows these steps:

 
 - **Environment Setup**: The script first creates the environment specified by `--env-name` using the same wrappers as in training.
 - **Model Loading**: The trained actor-critic model is loaded from the specified directory:
 
 
```

```

 
 - **Evaluation Loop**: The script enters an infinite loop where the agent interacts with the environment: 
 - The agent selects actions based on the current observation
 - The environment advances one step
 - The environment is rendered to visualize the agent's behavior
 - Special handling is implemented for PyBullet environments to control the camera
 
 Sources: [enjoy.py1-97](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/enjoy.py#L1-L97)

 
## Visualizing Training Results

 The repository includes a Jupyter notebook `visualize.ipynb` for analyzing and visualizing the performance of trained agents over time. This notebook uses functionality from OpenAI Baselines to generate learning curves from logs generated during training.

 
### Using visualize.ipynb

 The visualization notebook provides tools to:

 
 - Load training logs from specified directories
 - Plot learning curves showing how performance evolves during training
 - Average results across multiple random seeds to produce more reliable estimates
 
 
```

```

 
### Log File Structure

 The visualization tool expects log directories to follow a specific format for averaging results across seeds:

 
 - For experiment with name `name_exp0` and seeds 0 and 1, folders should be named `name_exp0-0` and `name_exp0-1`
 - This allows the tool to identify which logs belong to the same experiment with different random seeds
 
 
### Plotting Options

 The notebook uses `plot_results` function from Baselines with several customization options:

 
| Option | Description |
|---|---|
| average_group | Whether to average results within the same group (experiments with different seeds) |
| split_fn | Function that splits data into different groups for plotting |
| shaded_std | Whether to show standard deviation as a shaded region |

 
### Example Usage

 
```

```

 Sources: [visualize.ipynb1-100](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/visualize.ipynb#L1-L100)

 
## Best Practices for Evaluation

 When evaluating reinforcement learning agents and visualizing results, consider the following best practices:

 
### For Agent Evaluation

 
 - **Multiple Seeds**: Evaluate agents trained with multiple random seeds to account for variance in training.
 - **Deterministic vs. Stochastic Policies**: Use the `--non-det` flag to control whether the policy is deterministic or stochastic during evaluation:

 
 - Deterministic (default): Always takes the highest probability action
 - Non-deterministic: Samples from the action distribution (closer to training behavior)
 - **Environment Differences**: Note that some environments like PyBullet require special handling for visualization, which is implemented in `enjoy.py`.
 - **Normalization Consistency**: The script ensures that the same normalization statistics from training are used during evaluation.
 
 
```

```

 
### For Visualizing Results

 
 - **Log Organization**: Organize logs in a consistent format to enable proper averaging across seeds.
 - **Comparison Plot Setup**: When comparing different algorithms or hyperparameters, use the same environment and evaluation metrics.
 - **Statistical Significance**: Look at the variance across seeds to determine if differences between algorithms are significant.
 - **Render with Care**: When using `enjoy.py` for rendering, be aware that some environments require a display. For headless servers, consider using a virtual display.
 
 Sources: [enjoy.py35-69](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/enjoy.py#L35-L69) [visualize.ipynb13-24](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/visualize.ipynb#L13-L24)

 
## Creating Videos of Trained Agents

 You can record videos of your trained agents using the environment's built-in recording functionality. While not directly implemented in the codebase, this can be achieved with minimal modifications to `enjoy.py`.

 
### Steps to Record Videos:

 
 - **Add a monitor wrapper** to the environment creation process in `enjoy.py`:
 
 
```

```

 
 - **Run the agent** with the `enjoy.py` script as normal.
 - **Process the videos** if needed (e.g., convert to a more common format).
 
 This approach will save video files for each episode that the agent completes during evaluation.

 Sources: [enjoy.py39-47](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail/blob/41332b78/enjoy.py#L39-L47)

 
## Advanced Visualization Techniques

 Beyond the basic visualization provided by `visualize.ipynb`, you might want to perform more advanced analyses of your agents' behavior.

 
### State Visitation Analysis

 Analyzing which states the agent visits can provide insights into its exploration strategy and learned policy. This can be implemented by recording the observations during `enjoy.py` evaluation.

 
### Action Distribution Analysis

 Understanding the distribution of actions chosen by the agent can help diagnose issues with the policy. This can be achieved by modifying `enjoy.py` to record actions taken by the agent.

 
### Value Function Visualization

 For environments with low-dimensional state spaces, it can be helpful to visualize the learned value function. This requires extracting the value function from the trained model and plotting it across the state space.

 
```

```
