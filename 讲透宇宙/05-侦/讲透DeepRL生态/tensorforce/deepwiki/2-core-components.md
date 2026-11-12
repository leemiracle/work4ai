> 来源: [https://deepwiki.com/tensorforce/tensorforce/2-core-components](https://deepwiki.com/tensorforce/tensorforce/2-core-components)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Core Components

  Relevant source files 
 - [README.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1)
 - [UPDATE_NOTES.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/UPDATE_NOTES.md?plain=1)
 - [docs/basics/installation.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/installation.md?plain=1)
 - [tensorforce/agents/agent.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py)
 - [tensorforce/agents/tensorforce.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/tensorforce.py)
 - [tensorforce/core/models/model.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/model.py)
 - [tensorforce/core/models/tensorforce.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/tensorforce.py)
 - [tensorforce/core/module.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/module.py)
 - [tensorforce/environments/environment.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py)
 - [tensorforce/environments/openai_gym.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/openai_gym.py)
 - [tensorforce/execution/runner.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py)
 - [tensorforce/util.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/util.py)
 - [test/unittest_base.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/unittest_base.py)
 
  This page provides an overview of the main abstractions and components in the Tensorforce framework and how they work together. Tensorforce is built around three primary components: Agent, Environment, and Runner, which form the foundation for implementing reinforcement learning algorithms.

 For detailed information about specific agent implementations, see [Agent Implementations](https://deepwiki.com/tensorforce/tensorforce/3-agent-implementations). For more details on the neural network architecture system, see [Neural Network Architecture](https://deepwiki.com/tensorforce/tensorforce/4-neural-network-architecture).

 
## Key Components and Their Relationships

 The following diagram illustrates the core components of Tensorforce and their relationships:

 
```

```

 Sources: [tensorforce/agents/agent.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py) [tensorforce/core/models/tensorforce.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/tensorforce.py) [tensorforce/execution/runner.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py) [tensorforce/environments/environment.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py)

 
## Agent

 The Agent is the central component that interacts with the environment and learns from experiences. It provides the primary interface for users to implement reinforcement learning algorithms.

 
### Agent Interface

 The base `Agent` class defines the common interface for all agents:

 
```

```

 Key methods:

 
 - `act(states, ...)`: Selects actions based on observed states
 - `observe(terminal, reward)`: Processes feedback from environment
 - `initialize()`: Initializes the agent
 - `save()/load()`: Handles model persistence
 
 Sources: [tensorforce/agents/agent.py31-747](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L31-L747)

 
### TensorforceAgent

 The `TensorforceAgent` extends the base `Agent` class and provides a highly configurable implementation:

 
```

```

 The TensorforceAgent uses a `TensorforceModel` that encapsulates:

 
 - Neural network architecture
 - Optimization routines
 - Memory management
 - Distribution functions
 - Reward estimation
 
 Sources: [tensorforce/agents/tensorforce.py28-299](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/tensorforce.py#L28-L299) [tensorforce/agents/agent.py31-163](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L31-L163)

 
## Environment

 The Environment provides the interface for the agent to interact with:

 
```

```

 Key methods:

 
 - `states()`: Returns state space specification
 - `actions()`: Returns action space specification
 - `reset()`: Resets environment to start a new episode
 - `execute(actions)`: Executes actions and returns next state, terminal flag, and reward
 
 The Environment interface supports various environments through adapters, including:

 
 - OpenAI Gym
 - CARLA
 - OpenAI Retro
 - OpenSim
 - PyGame Learning Environment
 - ViZDoom
 
 Sources: [tensorforce/environments/environment.py33-366](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py#L33-L366) [tensorforce/environments/openai_gym.py24-137](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/openai_gym.py#L24-L137)

 
## Runner

 The Runner manages the interaction between Agent and Environment:

 
```

```

 The Runner handles:

 
 - Running episodes
 - Collecting statistics
 - Reporting progress
 - Parallel environment execution
 
 Sources: [tensorforce/execution/runner.py25-572](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L25-L572)

 
## Training Loop Flow

 The following diagram illustrates the basic training loop in Tensorforce:

 
```

```

 Sources: [tensorforce/execution/runner.py226-572](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L226-L572) [tensorforce/agents/agent.py374-500](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L374-L500) [tensorforce/agents/agent.py502-568](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L502-L568)

 
## Memory System

 Memory components store and retrieve experiences for agent updates:

 
```

```

 Sources: [tensorforce/core/models/tensorforce.py129-200](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/tensorforce.py#L129-L200)

 
## Model Architecture

 The Model is the internal component of the Agent that handles the learning algorithms:

 
```

```

 The Model contains:

 
 - State/action specifications
 - Neural network policy
 - Memory for experience storage
 - Optimizer for updates
 - Objective function
 - Reward estimation routines
 
 Sources: [tensorforce/core/models/model.py31-343](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/model.py#L31-L343) [tensorforce/core/models/tensorforce.py29-494](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/tensorforce.py#L29-L494)

 
## Component Interaction Example

 The following diagram shows how these components interact during a typical interaction cycle:

 
```

```

 Sources: [tensorforce/execution/runner.py226-572](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L226-L572) [tensorforce/agents/agent.py374-500](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L374-L500) [tensorforce/agents/agent.py502-568](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L502-L568)

 
## Configuration and Initialization

 To create an agent, the framework uses the `Agent.create()` static method, which accepts various configuration options. The code snippet below shows a minimal example of agent creation:

 
```

```

 The initialization process:

 
 - Creates the agent based on the configuration
 - Initializes the model with state/action specifications from the environment
 - Constructs the network, policy, memory, and optimizer components
 - Prepares the reward estimation pipeline
 - Sets up tracking, saving, and summarizing capabilities if configured
 
 Sources: [tensorforce/agents/agent.py36-135](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L36-L135) [tensorforce/core/models/tensorforce.py31-200](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/core/models/tensorforce.py#L31-L200)

 
## Summary

 The core components of Tensorforce form a modular, flexible architecture for reinforcement learning. Key concepts to understand:

 
 - **Agent**: The main interface for implementing RL algorithms
 - **Environment**: The interface for the agent to interact with
 - **Runner**: Manages the interaction between agent and environment
 - **Model**: Handles the learning algorithms within the agent
 - **Policy**: Determines how actions are selected
 - **Memory**: Stores experiences for training
 - **Optimizer**: Updates model parameters based on experiences
 
 These components are designed to be modular, allowing for customization and extension to implement various reinforcement learning algorithms.

 Sources: [README.md16-150](https://github.com/tensorforce/tensorforce/blob/d384bdc8/README.md?plain=1#L16-L150) [UPDATE_NOTES.md1-10](https://github.com/tensorforce/tensorforce/blob/d384bdc8/UPDATE_NOTES.md?plain=1#L1-L10) [tensorforce/agents/agent.py31-100](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/agents/agent.py#L31-L100) [tensorforce/environments/environment.py33-130](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/environments/environment.py#L33-L130) [tensorforce/execution/runner.py25-150](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/execution/runner.py#L25-L150)
