> 来源: [https://deepwiki.com/takuseno/d3rlpy/3-quick-start-tutorial](https://deepwiki.com/takuseno/d3rlpy/3-quick-start-tutorial)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Quick Start Tutorial

  Relevant source files 
 - [README.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1)
 - [ROADMAP.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/ROADMAP.md?plain=1)
 - [d3rlpy/algos/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/__init__.py)
 - [d3rlpy/notebook_utils.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/notebook_utils.py)
 - [docs/notebooks.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/notebooks.rst)
 - [docs/references/algos.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst)
 - [docs/requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/requirements.txt)
 - [tutorials/atari.ipynb](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/atari.ipynb)
 - [tutorials/cartpole.ipynb](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/cartpole.ipynb)
 - [tutorials/online.ipynb](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/online.ipynb)
 - [tutorials/tpu.ipynb](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/tpu.ipynb)
 
  This document provides hands-on examples demonstrating the core workflows of d3rlpy for both offline and online reinforcement learning. It covers the essential steps from dataset loading to algorithm training and evaluation, with practical examples for continuous and discrete control tasks.

 For comprehensive algorithm details, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For data management concepts, see [Data Management](https://deepwiki.com/takuseno/d3rlpy/6-data-management). For installation instructions, see [Installation and Setup](https://deepwiki.com/takuseno/d3rlpy/2-installation-and-setup).

 
## Overview

 d3rlpy follows a consistent pattern across all algorithms and domains:

 
```

```

 **Core Workflow Components**

 
 - **Configuration**: Algorithm parameters defined via config classes
 - **Creation**: Algorithm instances created with device specification
 - **Training**: Offline training via `fit()` or online training via `fit_online()`
 - **Inference**: Action prediction via `predict()`
 
 Sources: [README.md13-29](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L13-L29) [docs/references/algos.rst11-21](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L11-L21)

 
## Offline Reinforcement Learning

 
### Continuous Control Example

 This example demonstrates offline RL with continuous control using the SAC algorithm on D4RL datasets:

 
```

```

 **Key Components**:

 
 - `d3rlpy.datasets.get_dataset()`: Loads D4RL datasets
 - `SACConfig`: Configuration class for Soft Actor-Critic
 - `compile_graph=True`: Enables PyTorch compilation for speed
 - `fit()`: Offline training method
 
 Sources: [README.md16-22](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L16-L22) [README.md132-143](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L132-L143)

 
### Discrete Control Example

 For discrete action spaces like Atari games, use discrete algorithm variants:

 
```

```

 **Key Components**:

 
 - `get_atari_transitions()`: Loads Atari datasets with frame stacking
 - `DiscreteCQLConfig`: CQL variant for discrete actions
 - `PixelObservationScaler`: Preprocesses image observations
 - `EnvironmentEvaluator`: Evaluates policy during training
 
 Sources: [README.md154-173](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L154-L173) [tutorials/atari.ipynb35-77](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/atari.ipynb#L35-L77)

 
## Online Reinforcement Learning

 
### Basic Online Training

 Online RL requires environment interaction and replay buffer management:

 
```

```

 **Online Training Components**:

 
 - `create_fifo_replay_buffer()`: Creates FIFO replay buffer
 - `fit_online()`: Online training method with environment interaction
 - `eval_env`: Separate environment for evaluation
 
 Sources: [README.md183-195](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L183-L195)

 
### Online Training with Exploration

 For value-based methods, specify exploration strategy:

 
```

```

 **Exploration Components**:

 
 - `ConstantEpsilonGreedy`: Epsilon-greedy exploration strategy
 - `explorer` parameter: Required for value-based online algorithms
 - `target_update_interval`: Q-network target update frequency
 
 Sources: [tutorials/online.ipynb71-91](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/online.ipynb#L71-L91)

 
## Training Configuration

 
### Device Selection

 All algorithms support CPU, GPU, and TPU devices:

 
```

```

 Sources: [docs/references/algos.rst16-20](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L16-L20) [tutorials/tpu.ipynb84-89](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/tpu.ipynb#L84-L89)

 
### Training Monitoring

 
```

```

 **Evaluator Usage**:

 
```

```

 Sources: [tutorials/cartpole.ipynb76-79](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials/cartpole.ipynb#L76-L79) [README.md141-142](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L141-L142)

 
## Algorithm Selection Guide

 
| Task Type | Recommended Algorithms | Configuration Classes |
|---|---|---|
| Continuous Offline | CQL, SAC, IQL | CQLConfig, SACConfig, IQLConfig |
| Discrete Offline | DiscreteCQL, DiscreteSAC | DiscreteCQLConfig, DiscreteSACConfig |
| Continuous Online | SAC, TD3, DDPG | SACConfig, TD3Config, DDPGConfig |
| Discrete Online | DQN, DoubleDQN | DQNConfig, DoubleDQNConfig |
| Sequential Decision | DecisionTransformer | DecisionTransformerConfig |

 Sources: [README.md88-112](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L88-L112)

 
## Next Steps

 After completing these basic examples:

 
 - **Advanced Algorithms**: Explore specialized algorithms in [Algorithm Implementations](https://deepwiki.com/takuseno/d3rlpy/5.3-algorithm-implementations)
 - **Data Processing**: Learn about preprocessing and data management in [Data Management](https://deepwiki.com/takuseno/d3rlpy/6-data-management)
 - **Model Customization**: Understand neural network components in [Model Components](https://deepwiki.com/takuseno/d3rlpy/7-model-components)
 - **Evaluation Metrics**: Study comprehensive evaluation in [Training and Evaluation](https://deepwiki.com/takuseno/d3rlpy/8-training-and-evaluation)
 - **Production Deployment**: See CLI tools and utilities in [CLI and Utilities](https://deepwiki.com/takuseno/d3rlpy/9-cli-and-utilities)
 
 The [tutorials directory](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tutorials directory) contains interactive Jupyter notebooks for hands-on experimentation.

 Sources: [README.md198-203](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L198-L203) [docs/notebooks.rst4-7](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/notebooks.rst#L4-L7)
