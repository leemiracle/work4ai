> 来源: [https://deepwiki.com/takuseno/d3rlpy/1-overview](https://deepwiki.com/takuseno/d3rlpy/1-overview)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Overview

  Relevant source files 
 - [README.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1)
 - [ROADMAP.md](https://github.com/takuseno/d3rlpy/blob/4f0956ba/ROADMAP.md?plain=1)
 - [d3rlpy/_version.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/_version.py)
 - [d3rlpy/algos/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/__init__.py)
 - [docker/Dockerfile](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docker/Dockerfile)
 - [docs/index.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/index.rst)
 - [docs/installation.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst)
 - [docs/references/algos.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst)
 - [docs/requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/requirements.txt)
 - [scripts/build-docker](https://github.com/takuseno/d3rlpy/blob/4f0956ba/scripts/build-docker)
 
  This document provides a high-level introduction to d3rlpy, covering its purpose, key features, and overall architecture. For specific algorithm implementations, see [Algorithm System](https://deepwiki.com/takuseno/d3rlpy/5-algorithm-system). For data handling details, see [Data Management](https://deepwiki.com/takuseno/d3rlpy/6-data-management). For installation instructions, see [Installation and Setup](https://deepwiki.com/takuseno/d3rlpy/2-installation-and-setup).

 
## Purpose and Scope

 d3rlpy is an offline deep reinforcement learning library designed for practitioners and researchers. It provides state-of-the-art offline RL algorithms with intuitive APIs that require minimal deep learning expertise. The library supports both offline training from static datasets and online training with environment interaction.

 The library's primary goals are:

 
 - **Practical offline RL**: Enable powerful offline RL when online interaction is not feasible (e.g., robotics, medical applications)
 - **User-friendly APIs**: Provide scikit-learn-style interfaces that abstract away deep learning complexity
 - **Beyond state-of-the-art performance**: Achieve superior results through distributional Q-functions and advanced optimization techniques
 - **Scalability**: Support large-scale training with data-parallel distributed computing and GPU acceleration
 
 Sources: [README.md11-12](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L11-L12) [README.md39-50](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L39-L50) [docs/index.rst6-19](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/index.rst#L6-L19)

 
## Key Features

 
| Feature Category | Description | Key Benefits |
|---|---|---|
| Algorithm Support | 25+ state-of-the-art algorithms including SAC, CQL, BCQ, Decision Transformer | Comprehensive coverage of offline and online RL methods |
| Distributional Q-Functions | First library to support distributional Q-functions across all algorithms | Enhanced performance and uncertainty estimation |
| Data-Parallel Training | Multi-GPU and multi-node distributed training support | Scalable training for large datasets |
| Performance Optimization | CudaGraph and torch.compile acceleration | Significant speedup in training and inference |
| Flexible Data Support | D4RL, Atari, Minari datasets plus custom data formats | Easy integration with existing datasets |

 Sources: [README.md37-50](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L37-L50) [README.md88-112](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L88-L112) [README.md114-117](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L114-L117)

 
## Overall Architecture

 The d3rlpy architecture follows a layered design with clear separation of concerns:

 
### High-Level System Architecture

 
```

```

 Sources: [README.md13-29](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L13-L29) [docs/references/algos.rst26-51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L26-L51) [d3rlpy/algos/__init__.py1-3](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/algos/__init__.py#L1-L3)

 
### Core Algorithm Framework

 The algorithm framework implements a three-layer architecture that separates configuration, algorithm logic, and PyTorch implementation:

 
```

```

 Sources: [docs/references/algos.rst29-51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L29-L51) [docs/references/algos.rst390-407](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L390-L407) [README.md18-19](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L18-L19)

 
## Supported Algorithms

 d3rlpy provides comprehensive algorithm coverage across different RL paradigms:

 
### Algorithm Categories

 
| Category | Algorithms | Action Spaces |
|---|---|---|
| Behavior Cloning | BC, DiscreteBC | Discrete, Continuous |
| Value-Based | NFQ, DQN, DoubleDQN | Discrete |
| Actor-Critic | DDPG, TD3, SAC, DiscreteSAC | Both |
| Offline RL | BCQ, BEAR, CQL, AWAC, CRR, IQL, CalQL | Both |
| Hybrid Methods | PLAS, TD3+BC, PRDC, ReBRAC | Continuous |
| Transformer-Based | Decision Transformer, QDT, TACR | Both |

 
### Q-Function Support

 d3rlpy is the first library to provide distributional Q-function support across all algorithms:

 
 - Standard Q-function
 - Quantile Regression
 - Implicit Quantile Network (IQN)
 
 Sources: [README.md88-117](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L88-L117) [docs/references/algos.rst54-462](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/references/algos.rst#L54-L462)

 
## Data Processing Pipeline

 The library implements a sophisticated data processing pipeline that handles various data sources and formats:

 
```

```

 Sources: [README.md131-143](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L131-L143) [README.md150-173](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L150-L173) [README.md16](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L16-L16)

 
## Usage Patterns

 The library supports both offline and online training workflows through consistent APIs:

 
### Offline Training Example

 
```

```

 
### Online Training Example

 
```

```

 
### Prediction and Deployment

 
```

```

 Sources: [README.md13-29](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L13-L29) [README.md179-195](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L179-L195)

 
## Development and Ecosystem

 d3rlpy includes comprehensive development infrastructure:

 
 - **Testing**: Automated CI/CD with GitHub Actions
 - **Documentation**: Full API documentation and tutorials
 - **Containerization**: Docker images for reproducible environments
 - **Benchmarking**: Reproduction scripts and benchmark results
 - **CLI Tools**: Command-line utilities for model management and evaluation
 
 The library integrates with popular ML tools and frameworks:

 
 - **Logging**: WandB, TensorBoard, file-based logging
 - **Environments**: Gymnasium, D4RL, custom environments
 - **Hardware**: CUDA acceleration, multi-GPU support
 
 Sources: [README.md82-86](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L82-L86) [README.md120-122](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L120-L122) [README.md197-203](https://github.com/takuseno/d3rlpy/blob/4f0956ba/README.md?plain=1#L197-L203) [docker/Dockerfile1-42](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docker/Dockerfile#L1-L42)
