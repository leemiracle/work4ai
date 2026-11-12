> 来源: [https://deepwiki.com/facebookresearch/ReAgent/1-reagent-overview](https://deepwiki.com/facebookresearch/ReAgent/1-reagent-overview)
> DeepWiki facebookresearch/ReAgent | Last indexed: 21 April 2025 (9e707c

# ReAgent Overview

  Relevant source files 
 - [.circleci/config.yml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/.circleci/config.yml)
 - [.gitignore](https://github.com/facebookresearch/ReAgent/blob/9e707c09/.gitignore)
 - [CONTRIBUTING.md](https://github.com/facebookresearch/ReAgent/blob/9e707c09/CONTRIBUTING.md?plain=1)
 - [LICENSE](https://github.com/facebookresearch/ReAgent/blob/9e707c09/LICENSE)
 - [README.md](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1)
 - [docs/continuous_integration.rst](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/continuous_integration.rst)
 - [docs/installation.rst](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/installation.rst)
 - [docs/usage.rst](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst)
 - [pyproject.toml](https://github.com/facebookresearch/ReAgent/blob/9e707c09/pyproject.toml)
 - [rasp_requirements.txt](https://github.com/facebookresearch/ReAgent/blob/9e707c09/rasp_requirements.txt)
 - [setup.cfg](https://github.com/facebookresearch/ReAgent/blob/9e707c09/setup.cfg)
 - [tox.ini](https://github.com/facebookresearch/ReAgent/blob/9e707c09/tox.ini)
 
  ReAgent is an open-source end-to-end platform for applied reinforcement learning (RL) developed by Facebook/Meta. This document provides a comprehensive overview of the ReAgent system architecture, components, and workflows to help developers understand how the different parts fit together.

 
> **Note**: ReAgent is officially archived and no longer maintained. For latest support on production-ready reinforcement learning, refer to [Pearl](https://github.com/facebookresearch/ReAgent/blob/9e707c09/Pearl) - Production-ready Reinforcement Learning AI Agent Library.

 
## Purpose and Scope

 ReAgent is designed specifically for large-scale, distributed recommendation and optimization tasks. It addresses several challenging aspects of applied reinforcement learning:

 
 - Training on **offline batches** of data when simulators aren't available
 - Supporting **thousands of varying feature types** with different distributions
 - Providing **counterfactual policy evaluation** (CPE) to estimate policy performance before deployment
 - Enabling both **research experimentation** and **production deployment** from the same codebase
 
 The platform integrates data preprocessing, model training, evaluation, and serving into a unified workflow optimized for real-world applications.

 Sources: [README.md11-14](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1#L11-L14) [docs/usage.rst6-11](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L6-L11)

 
## System Architecture

 
### High-Level Architecture Overview

 The following diagram illustrates the key components of ReAgent and their relationships:

 
```

```

 Sources: [README.md11-14](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1#L11-L14) [docs/usage.rst6-11](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L6-L11)

 
### Data Flow in ReAgent

 The following diagram shows the typical data flow in a ReAgent workflow:

 
```

```

 Sources: [docs/usage.rst85-118](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L85-L118) [docs/usage.rst229-257](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L229-L257)

 
## Supported Algorithms

 ReAgent includes implementations of numerous reinforcement learning algorithms across different categories:

 
### Classic Off-Policy Algorithms

 
 - **Discrete-Action DQN**: Standard Deep Q-Networks for discrete action spaces
 - **Parametric-Action DQN**: DQN variant for parameterized action spaces
 - **Double DQN, Dueling DQN**: Enhanced DQN variants
 - **Distributional RL**: C51 and QR-DQN implementations
 - **TD3**: Twin Delayed Deep Deterministic Policy Gradient
 - **SAC**: Soft Actor-Critic for continuous control
 - **CRR**: Critic Regularized Regression
 - **PPO**: Proximal Policy Optimization
 
 
### RL for Recommender Systems

 
 - **Seq2Slate**: Sequence-to-Slate approach for ranking
 - **SlateQ**: Q-learning for slate recommendations
 
 
### Counterfactual Evaluation

 
 - **Doubly Robust** methods for both bandits and sequential decisions
 - **MAGIC**: More Advanced off-policy evaluation method
 
 
### Bandits

 
 - **UCB1** and **MetricUCB**: Upper Confidence Bound algorithms
 - **Thompson Sampling**: Probability matching approach
 - **LinUCB**: Linear UCB for contextual bandits
 
 Sources: [README.md16-47](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1#L16-L47)

 
## Core Components

 
### Training System Architecture

 ReAgent's training system is built around PyTorch Lightning, with a hierarchy of trainer classes:

 
```

```

 The `ReAgentLightningModule` serves as the base class for all trainers, providing standardized training loops and integration with PyTorch Lightning's distributed training capabilities.

 Sources: [tox.ini42-115](https://github.com/facebookresearch/ReAgent/blob/9e707c09/tox.ini#L42-L115)

 
### ModelManager Workflow

 ModelManager is a key abstraction that orchestrates the end-to-end training process:

 
```

```

 The ModelManager handles:

 
 - Feature identification and normalization
 - Data querying and preprocessing
 - Building trainer modules
 - Creating TorchScript serving modules
 
 Sources: [docs/usage.rst202-214](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L202-L214) [docs/usage.rst229-257](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L229-L257)

 
## Training Workflows

 ReAgent supports two primary training workflows:

 
### Online RL Training (with Simulators)

 When a simulator is available (like OpenAI Gym environments), ReAgent can train policies online where the latest version of the policy makes decisions in real-time:

 
```

```

 This approach is typically used for research experimentation.

 Sources: [docs/usage.rst54-65](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L54-L65)

 
### Offline RL Training (Batch RL)

 For most real-world applications, ReAgent uses batch RL, where data collection and policy learning are decoupled:

 
```

```

 This workflow handles large-scale data, feature preprocessing, and allows for offline evaluation of policies before deployment.

 Sources: [docs/usage.rst75-118](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L75-L118) [docs/usage.rst149-169](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L149-L169)

 
## Installation and Setup

 ReAgent can be installed via Docker or manually. The basic installation steps are:

 
 - Clone the repository
 - Install Python dependencies with pip
 - Optionally build the preprocessing JAR for Spark operations
 - Optionally build RASP (ReAgent Serving Platform) for deployment
 
 For detailed installation instructions, see [Installation and Setup](https://deepwiki.com/facebookresearch/ReAgent/1.1-installation-and-setup).

 Sources: [docs/installation.rst6-107](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/installation.rst#L6-L107) [setup.cfg11-37](https://github.com/facebookresearch/ReAgent/blob/9e707c09/setup.cfg#L11-L37)

 
## Key Use Cases

 ReAgent is particularly well-suited for:

 
 - **Recommendation systems** where RL can optimize for long-term user engagement
 - **Decision optimization** in complex environments with delayed rewards
 - **Large-scale batch learning** scenarios without simulators
 - **Production deployment** of RL policies with robust evaluation
 
 For situations where simulators are available and on-policy learning is feasible, ReAgent still provides strong support through its Gym integration.

 Sources: [README.md11-14](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1#L11-L14) [docs/usage.rst6-11](https://github.com/facebookresearch/ReAgent/blob/9e707c09/docs/usage.rst#L6-L11)

 
## Limitations and Alternatives

 It's important to note that ReAgent is officially archived and no longer maintained. For current production-ready reinforcement learning, Meta recommends [Pearl](https://github.com/facebookresearch/ReAgent/blob/9e707c09/Pearl) which builds on the lessons learned from ReAgent.

 Sources: [README.md3](https://github.com/facebookresearch/ReAgent/blob/9e707c09/README.md?plain=1#L3-L3)
