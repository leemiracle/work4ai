> 来源: [https://deepwiki.com/chainer/chainerrl/1-overview](https://deepwiki.com/chainer/chainerrl/1-overview)
> DeepWiki chainer/chainerrl | Last indexed: 8 June 2025 (7eed37

# Overview

  Relevant source files 
 - [README.md](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1)
 - [assets/ChainerRL.png](https://github.com/chainer/chainerrl/blob/7eed3756/assets/ChainerRL.png)
 - [assets/breakout.gif](https://github.com/chainer/chainerrl/blob/7eed3756/assets/breakout.gif)
 - [assets/grasping.gif](https://github.com/chainer/chainerrl/blob/7eed3756/assets/grasping.gif)
 - [assets/humanoid.gif](https://github.com/chainer/chainerrl/blob/7eed3756/assets/humanoid.gif)
 - [chainerrl/links/mlp_bn.py](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/links/mlp_bn.py)
 - [docs/install.rst](https://github.com/chainer/chainerrl/blob/7eed3756/docs/install.rst)
 
  
## Purpose and Scope

 ChainerRL is a deep reinforcement learning library that implements various state-of-the-art deep reinforcement learning algorithms in Python using the Chainer deep learning framework. This document provides an architectural overview of the ChainerRL codebase, covering its core components, algorithm implementations, and system organization.

 For detailed information about specific RL algorithms, see [Reinforcement Learning Agents](https://deepwiki.com/chainer/chainerrl/2-reinforcement-learning-agents). For implementation details of neural network components, see [Core Components](https://deepwiki.com/chainer/chainerrl/3-core-components). For guidance on training agents and evaluation, see [Training and Evaluation Infrastructure](https://deepwiki.com/chainer/chainerrl/4-training-and-evaluation-infrastructure).

 
## Library Architecture

 ChainerRL is organized into several key subsystems that work together to provide a comprehensive deep RL framework:

 
```

```

 Sources: [README.md1-134](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L1-L134) [chainerrl/links/mlp_bn.py1-83](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/links/mlp_bn.py#L1-L83)

 
## Algorithm Portfolio

 ChainerRL implements a comprehensive set of modern RL algorithms across different paradigms:

 
### Algorithm Support Matrix

 
| Algorithm | Discrete Actions | Continuous Actions | Recurrent Models | Batch Training | Async Training |
|---|---|---|---|---|---|
| DQN (including DoubleDQN) | ✓ | ✓ (NAF) | ✓ | ✓ | ✗ |
| CategoricalDQN | ✓ | ✗ | ✓ | ✓ | ✗ |
| Rainbow | ✓ | ✗ | ✓ | ✓ | ✗ |
| IQN | ✓ | ✗ | ✓ | ✓ | ✗ |
| DDPG | ✗ | ✓ | ✓ | ✓ | ✗ |
| A3C | ✓ | ✓ | ✓ | ✓ (A2C) | ✓ |
| ACER | ✓ | ✓ | ✓ | ✗ | ✓ |
| NSQ | ✓ | ✓ (NAF) | ✓ | ✗ | ✓ |
| PCL | ✓ | ✓ | ✓ | ✗ | ✓ |
| PPO | ✓ | ✓ | ✓ | ✓ | ✗ |
| TRPO | ✓ | ✓ | ✓ | ✓ | ✗ |
| TD3 | ✗ | ✓ | ✗ | ✓ | ✗ |
| SAC | ✗ | ✓ | ✗ | ✓ | ✗ |

 Sources: [README.md40-54](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L40-L54)

 
### Algorithm Organization by Approach

 
```

```

 Sources: [README.md56-86](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L56-L86)

 
## Core Neural Network Components

 ChainerRL provides reusable neural network building blocks that agents compose for different tasks:

 
```

```

 Sources: [chainerrl/links/mlp_bn.py22-82](https://github.com/chainer/chainerrl/blob/7eed3756/chainerrl/links/mlp_bn.py#L22-L82) [README.md88-98](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L88-L98)

 
## Training Infrastructure

 ChainerRL provides multiple training paradigms to accommodate different algorithm requirements:

 
```

```

 Sources: [README.md32-36](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L32-L36)

 
## Integration and Usage Patterns

 ChainerRL integrates with standard RL environments and provides comprehensive examples:

 
```

```

 Sources: [README.md34-36](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L34-L36) [README.md58-86](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L58-L86)

 
## Installation and Dependencies

 ChainerRL requires Python 3.6+ and depends primarily on the Chainer deep learning framework. Installation is available via PyPI or from source:

 
```

```

 Or for development:

 
```

```

 Key dependencies include `chainer`, `numpy`, and `gym` for environment interfaces.

 Sources: [README.md16-30](https://github.com/chainer/chainerrl/blob/7eed3756/README.md?plain=1#L16-L30) [docs/install.rst1-26](https://github.com/chainer/chainerrl/blob/7eed3756/docs/install.rst#L1-L26)
