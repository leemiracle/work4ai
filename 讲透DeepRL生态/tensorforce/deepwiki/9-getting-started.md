> 来源: [https://deepwiki.com/tensorforce/tensorforce/9-getting-started](https://deepwiki.com/tensorforce/tensorforce/9-getting-started)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Getting Started

  Relevant source files 
 - [docs/basics/features.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/features.md?plain=1)
 - [docs/basics/getting-started.md](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1)
 - [examples/quickstart.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/examples/quickstart.py)
 - [test/test_documentation.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py)
 - [test/test_examples.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py)
 
  This document provides a practical introduction to using the Tensorforce library, a modular reinforcement learning framework. You'll learn how to set up environments, create agents, and train/evaluate your reinforcement learning models. For advanced features like parallel execution or action masking, see [Advanced Features](https://deepwiki.com/tensorforce/tensorforce/10-advanced-features).

 
## Framework Overview

 Tensorforce is built around three core abstractions that work together to implement reinforcement learning algorithms:

 
```

```

 Sources: [examples/quickstart.py57-61](https://github.com/tensorforce/tensorforce/blob/d384bdc8/examples/quickstart.py#L57-L61) [test/test_examples.py101-107](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L101-L107)

 
## Installation

 Install Tensorforce using pip:

 
```

```

 For the latest development version, you can install directly from GitHub:

 
```

```

 
## Creating Environments

 Environments define the reinforcement learning problem by providing states, accepting actions, and returning rewards.

 
### Using OpenAI Gym

 The simplest way to get started is with OpenAI Gym environments:

 
```

```

 Sources: [test/test_documentation.py25-35](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py#L25-L35) [docs/basics/getting-started.md8-28](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L8-L28)

 
### Custom Environments

 You can implement custom environments by extending the `Environment` class:

 
```

```

 When implementing a custom environment, you need to define:

 
 - `states()`: Returns the state space specification
 - `actions()`: Returns the action space specification
 - `reset()`: Resets the environment and returns the initial state
 - `execute(actions)`: Performs one step and returns next_state, terminal flag, and reward
 
 Example custom environment implementation:

 
```

```

 Sources: [docs/basics/getting-started.md49-93](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L49-L93)

 
## Creating Agents

 Agents implement reinforcement learning algorithms that learn to solve the problem defined by the environment.

 
```

```

 
### Basic Agent Creation

 You can create an agent using the `Agent.create()` function:

 
```

```

 Sources: [test/test_documentation.py53-69](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py#L53-L69) [docs/basics/getting-started.md105-129](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L105-L129)

 
### Agent Configuration via JSON

 You can also define agents via JSON configuration files:

 
```

```

 Then load the configuration:

 
```

```

 Sources: [docs/basics/getting-started.md131-152](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L131-L152)

 
## Training and Evaluation

 Tensorforce provides multiple ways to train and evaluate agents:

 
### Using the Runner Utility

 The recommended approach for training and evaluation is using the `Runner` utility:

 
```

```

 Sources: [examples/quickstart.py57-62](https://github.com/tensorforce/tensorforce/blob/d384bdc8/examples/quickstart.py#L57-L62) [test/test_documentation.py75-85](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py#L75-L85) [docs/basics/getting-started.md166-181](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L166-L181)

 
### Manual Training Loop (Act-Observe Pattern)

 For more control, you can implement a custom training loop:

 
```

```

 Sources: [test/test_documentation.py95-109](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_documentation.py#L95-L109) [docs/basics/getting-started.md202-217](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L202-L217)

 
### Advanced: Act-Experience-Update Pattern

 For maximum flexibility, Tensorforce offers an alternative interaction pattern:

 
```

```

 Sources: [test/test_examples.py214-246](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L214-L246) [docs/basics/getting-started.md219-250](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L219-L250)

 
### Evaluation

 To evaluate your trained agent:

 
```

```

 Sources: [test/test_examples.py247-258](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L247-L258) [docs/basics/getting-started.md254-271](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/basics/getting-started.md?plain=1#L254-L271)

 
## Quickstart Example

 Here's a complete example that trains a PPO agent on the CartPole environment:

 
```

```

 Sources: [examples/quickstart.py16-62](https://github.com/tensorforce/tensorforce/blob/d384bdc8/examples/quickstart.py#L16-L62)

 
## Saving and Loading Models

 You can save and load your trained agents:

 
```

```

 Sources: [examples/quickstart.py44-52](https://github.com/tensorforce/tensorforce/blob/d384bdc8/examples/quickstart.py#L44-L52) [test/test_examples.py673-686](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_examples.py#L673-L686)

 
## Next Steps

 After getting comfortable with the basics, you can explore:

 
 - Different agent implementations like PPO, DQN, or A2C
 - Advanced environment configurations
 - Custom network architectures
 - Optimizers and hyperparameter tuning
 - [Advanced features](https://deepwiki.com/tensorforce/tensorforce/10-advanced-features) like action masking, parallel execution, and more
