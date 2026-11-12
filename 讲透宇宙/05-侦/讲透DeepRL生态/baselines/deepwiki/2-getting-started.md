> 来源: [https://deepwiki.com/openai/baselines/2-getting-started](https://deepwiki.com/openai/baselines/2-getting-started)
> DeepWiki openai/baselines | Last indexed: 18 April 2025 (ea25b9

# Getting Started

  Relevant source files 
 - [.travis.yml](https://github.com/openai/baselines/blob/ea25b9e8/.travis.yml)
 - [Dockerfile](https://github.com/openai/baselines/blob/ea25b9e8/Dockerfile)
 - [README.md](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1)
 - [setup.py](https://github.com/openai/baselines/blob/ea25b9e8/setup.py)
 
  This page provides instructions on how to install and begin using the OpenAI Baselines library, a collection of high-quality implementations of reinforcement learning algorithms. For detailed information on running experiments after installation, see [Running Experiments](https://deepwiki.com/openai/baselines/2.1-running-experiments).

 
## Prerequisites and Dependencies

 The OpenAI Baselines library requires several dependencies to function properly:

 
```

```

 Sources: [setup.py31-47](https://github.com/openai/baselines/blob/ea25b9e8/setup.py#L31-L47) [README.md11-23](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L11-L23)

 
### System Requirements

 
#### Ubuntu

 
```

```

 
#### Mac OS X

 
```

```

 Sources: [README.md15-16](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L15-L16) [README.md21-22](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L21-L22)

 
## Installation Process

 
### Virtual Environment Setup

 It's recommended to use a virtual environment to avoid package conflicts:

 
```

```

 
 - Install virtualenv:

 
```

```
 - Create a virtual environment:

 
```

```
 - Activate the virtual environment:

 
```

```
 
 Sources: [README.md25-39](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L25-L39)

 
### Installing Baselines

 With your virtual environment activated, follow these steps:

 
```

```

 
 - Clone the repository:

 
```

```
 - Install TensorFlow:

 
```

```
 - Install the Baselines package:

 
```

```
 - Test the installation:

 
```

```
 
 Sources: [README.md46-74](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L46-L74)

 
### MuJoCo (Optional)

 Some of the baselines examples use MuJoCo physics simulator, which requires a license and binaries:

 
 - Obtain a license (30-day temporary license available) from [www.mujoco.org](http://www.mujoco.org)
 - Set up MuJoCo following the instructions at [mujoco-py](https://github.com/openai/baselines/blob/ea25b9e8/mujoco-py)
 
 Sources: [README.md67-68](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L67-L68)

 
## Package Structure

 The Baselines package includes multiple reinforcement learning algorithm implementations and supporting infrastructure:

 
```

```

 Sources: [README.md132-142](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L132-L142)

 
## Basic Usage

 The main entry point for running algorithms is the `baselines.run` module. The following diagram shows how command-line arguments flow through the system:

 
```

```

 Sources: [README.md77-81](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L77-L81)

 
### Example Commands

 Basic command structure:

 
```

```

 Example 1: Training PPO on MuJoCo Humanoid

 
```

```

 Example 2: Training DQN on Atari Pong

 
```

```

 Example 3: Training with custom hyperparameters

 
```

```

 Sources: [README.md82-101](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L82-L101)

 
### Saving and Loading Models

 To save a trained model:

 
```

```

 To load and visualize a trained model:

 
```

```

 Sources: [README.md106-115](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L106-L115)

 
### Logging and Visualization

 By default, all summary data is saved to a unique directory in a temp folder. You can specify a custom log path:

 
```

```

 The environment variable `$OPENAI_LOGDIR` can also be used to set the log directory.

 Sources: [README.md119-129](https://github.com/openai/baselines/blob/ea25b9e8/README.md?plain=1#L119-L129)

 For more detailed information on running experiments and configuring algorithms, see [Running Experiments](https://deepwiki.com/openai/baselines/2.1-running-experiments).
