> 来源: [https://deepwiki.com/tensorforce/tensorforce/1-overview](https://deepwiki.com/tensorforce/tensorforce/1-overview)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Overview

  Relevant source files 
 - [.travis.yml](https://github.com/tensorforce/tensorforce/blob/d384bdc8/.travis.yml)
 - [README.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1)
 - [docs/basics/installation.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/installation.md?plain=1)
 - [docs/conf.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/conf.py)
 - [docs/index.rst](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/index.rst)
 - [docs/requirements.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/requirements.txt)
 - [requirements-all.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt)
 - [requirements.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt)
 - [setup.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py)
 - [tensorforce/__init__.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py)
 - [tensorforce/environments/environment.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py)
 - [tensorforce/environments/openai_gym.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/openai_gym.py)
 - [tensorforce/execution/runner.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py)
 - [test/test_environments.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py)
 
  Tensorforce is an open-source deep reinforcement learning framework built on top of TensorFlow. It provides a modular, flexible library design for applied reinforcement learning in research and practical applications. This page introduces the framework's purpose, design philosophy, and high-level architecture.

 **Note**: As indicated in the repository README, this project is no longer maintained.

 For specific implementation details about agents, see [Agent Implementations](https://deepwiki.com/tensorforce/tensorforce/3-agent-implementations). For environment integration details, see [Environment Interface](https://deepwiki.com/tensorforce/tensorforce/2.2-environment-interface).

 
## Core Design Philosophy

 Tensorforce follows three key design principles that differentiate it from other reinforcement learning frameworks:

 
 - **Modular component-based design**: Features are implemented to be as generally applicable and configurable as possible, potentially at some cost of faithfully resembling details from academic papers.
 - **Separation of RL algorithm and application**: Algorithms are agnostic to the type and structure of inputs (states/observations) and outputs (actions/decisions), as well as the interaction with the application environment.
 - **Full-on TensorFlow models**: The entire reinforcement learning logic, including control flow, is implemented in TensorFlow to enable portable computation graphs independent of application programming language, and to facilitate model deployment.
 
 Sources: [README.md16-25](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L16-L25)

 
## High-Level System Architecture

 
### Core Components Diagram

 
```

```

 The architecture revolves around three main abstractions:

 
 - **Agent**: Handles decision-making and learning, encapsulating various reinforcement learning algorithms
 - **Environment**: Defines the problem space and interaction interface
 - **Runner**: Orchestrates the training and evaluation process between agents and environments
 
 The Agent contains a Model, which integrates various components like Network, Memory, Policy, Distribution, Optimizer, and Reward Estimation.

 Sources: [tensorforce/__init__.py22-25](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py#L22-L25) [README.md144-149](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L144-L149)

 
### Training Loop Flow

 
```

```

 This diagram illustrates the basic training loop in Tensorforce:

 
 - The Runner initializes the environment
 - For each timestep, the Agent selects actions based on current state
 - The Environment executes actions and returns next states, terminal flags, and rewards
 - The Agent observes outcomes and periodically updates its policy
 
 Sources: [tensorforce/execution/runner.py25-699](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L25-L699) [README.md76-111](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L76-L111)

 
## Core Components

 
### Agent

 The Agent is the central component implementing reinforcement learning algorithms. It provides a standardized interface for interaction with environments through actions and observations.

 
```

```

 The framework implements various reinforcement learning algorithms:

 
 - **Policy Gradient**: VPG (Vanilla Policy Gradient), PPO (Proximal Policy Optimization), TRPO (Trust Region Policy Optimization)
 - **Value-Based**: DQN (Deep Q-Network), Double DQN, Dueling DQN
 - **Actor-Critic**: A2C (Advantage Actor-Critic), AC (Actor-Critic), DPG (Deterministic Policy Gradient)
 
 Sources: [tensorforce/__init__.py24](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py#L24-L24) [README.md146-149](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L146-L149)

 
### Environment

 The Environment interface defines how agents interact with problems. It provides methods to reset the environment, execute actions, and receive observations and rewards.

 
```

```

 Key environment interface methods:

 
 - `states()`: Returns state space specification
 - `actions()`: Returns action space specification
 - `reset()`: Resets environment for a new episode
 - `execute(actions)`: Executes actions and returns next state, terminal flag, and reward
 
 Tensorforce provides adapters for numerous environments including:

 
 - OpenAI Gym (standard RL environments)
 - Arcade Learning Environment (Atari games)
 - OpenAI Retro (classic video games)
 - ViZDoom (first-person shooters)
 - And more
 
 Sources: [tensorforce/environments/environment.py33-250](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py#L33-L250) [tensorforce/environments/openai_gym.py24-498](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/openai_gym.py#L24-L498) [README.md155-161](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L155-L161)

 
### Runner

 The Runner orchestrates the interaction between agents and environments, coordinating the training and evaluation process.

 Key Runner methods:

 
 - `__init__()`: Initialize with agent and environment(s)
 - `run()`: Execute specified number of episodes/timesteps/updates
 - `close()`: Clean up resources
 
 The Runner supports features like:

 
 - Parallel environment execution
 - Episode and evaluation callbacks
 - Progress tracking with tqdm
 - Customizable evaluation metrics
 
 Sources: [tensorforce/execution/runner.py25-699](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L25-L699)

 
## Support Subsystems

 
### Memory System

 
```

```

 The Memory system stores and retrieves agent experiences for training:

 
 - **Queue**: Simple batch buffer memory
 - **Replay**: Random replay memory
 - **PrioritizedReplay**: Prioritized experience replay
 
 Sources: [README.md133-134](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L133-L134)

 
### Distribution System

 
```

```

 The Distribution system handles probability distributions for action selection:

 
 - **Categorical**: For discrete actions (finite integer values)
 - **Gaussian**: For continuous actions (unbounded real values)
 - **Beta**: For range-constrained continuous actions
 - **Bernoulli**: For boolean actions
 
 Sources: [README.md133](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L133-L133)

 
### Network Architecture System

 
```

```

 The Network system defines neural network architectures for policies and value functions:

 
 - Support for various layer types (fully-connected, convolutions, embeddings, RNNs)
 - Multi-state inputs and layer reuse
 - Directed acyclic graph structures
 - Keras layer integration
 
 Sources: [README.md130-132](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L130-L132)

 
## Quickstart Example

 
```

```

 This example demonstrates how to:

 
 - Create an environment (CartPole)
 - Configure and instantiate an agent
 - Run a training loop for multiple episodes
 - Handle agent-environment interaction
 
 Sources: [README.md76-111](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L76-L111)

 
## Installation

 Tensorforce can be installed via pip:

 
```

```

 For the latest version, install directly from GitHub:

 
```

```

 Main dependencies:

 
 - TensorFlow (v2.12.1)
 - Gym (v0.21.0-0.22.x)
 - NumPy (~1.21.5)
 - tqdm
 
 Additional dependencies can be installed for specific environments (ALE, Gym, Retro, ViZDoom, CARLA).

 Sources: [requirements.txt1-9](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt#L1-L9) [requirements-all.txt1-21](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt#L1-L21) [setup.py132-169](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L132-L169)

 
## Dependencies

 
| Dependency Type | Required Packages |
|---|---|
| Core | tensorflow, numpy, gym, h5py, matplotlib, msgpack, Pillow, tqdm |
| Optional - Addons | tensorflow-addons |
| Optional - Tuning | hpbandster |
| Optional - Environments | ale-py, gym[box2d,classic_control], gym-retro, vizdoom |
| Optional - Documentation | m2r, recommonmark, sphinx, sphinx-rtd-theme |
| Optional - Testing | pytest |

 Sources: [requirements.txt1-9](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt#L1-L9) [requirements-all.txt1-21](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt#L1-L21) [setup.py152-169](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L152-L169)
