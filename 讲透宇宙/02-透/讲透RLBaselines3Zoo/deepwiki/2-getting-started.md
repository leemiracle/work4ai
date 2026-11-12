<!-- source: DeepWiki mcp.deepwiki.com · repo DLR-RM/rl-baselines3-zoo · page 2 Getting Started · fetched 2026-10-14 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This guide provides essential information for setting up and using RL-Baselines3-Zoo, a training framework for Reinforcement Learning (RL) agents based on Stable Baselines3. You'll learn how to install the framework, configure your environment, and execute basic training and evaluation workflows.

For more detailed information about specific components like the training system architecture, see [Training System](#3), or for hyperparameter management, see [Hyperparameter Management](#4).

## Installation Options

RL-Baselines3-Zoo offers multiple installation methods depending on your needs. Choose the approach that best fits your requirements.

### Minimal Installation

The minimal installation includes just the core functionality without additional environments or testing dependencies.

**From source:**
```bash
pip install -e .
```

**As a Python package:**
```bash
pip install rl_zoo3
```

After installation, you can access the command-line interface from any directory:
```bash
rl_zoo3 train  # Equivalent to python train.py
```

Sources: [README.md:37-50](), [setup.py:17-27]()

### Full Installation

For complete functionality including all supported environments and testing capabilities:

```bash
apt-get install swig cmake ffmpeg
pip install -r requirements.txt
pip install -e .[plots,tests]
```

This installs:
- Core dependencies from `setup.py`
- Additional environment dependencies from `requirements.txt`
- Visualization tools (`plots`) and testing utilities (`tests`)

Sources: [README.md:52-59](), [setup.py:17-34](), [requirements.txt:1-15]()

### Python Version Requirements

RL-Baselines3-Zoo requires Python 3.9 or later. The package is tested with Python versions 3.9, 3.10, 3.11, and 3.12.

Sources: [setup.py:59-75]()

## System Architecture

Below is a high-level overview of the RL-Baselines3-Zoo architecture, showing the main components and their relationships.

**RL-Baselines3-Zoo Framework Components**

```mermaid
graph TD
    subgraph "User Interface"
        CLI["Command Line Interface<br>(rl_zoo3.cli)"]
        Scripts["Script Entry Points<br>(train.py, enjoy.py, etc.)"]
    end

    subgraph "Core Training Framework"
        Train["train.py"] --> ExpManager["Experiment Manager<br>(exp_manager.py)"]
        ExpManager --> EnvUtils["Environment Creation<br>(utils.py)"]
        ExpManager --> ModelUtils["Model Creation<br>(utils.py)"]
        ExpManager --> Callbacks["Callback System"]
    end

    subgraph "Configuration"
        HyperFiles["Hyperparameter Files<br>(hyperparams/*.yml)"]
        CLI --> Train
        Scripts --> Train
        HyperFiles --> Train
    end

    subgraph "Evaluation & Analysis"
        Enjoy["enjoy.py"]
        Benchmark["benchmark.py"]
        RecordVideo["record_video.py"]
        Plotting["plots/"]
    end

    subgraph "External Libraries"
        SB3["Stable-Baselines3<br>(RL Algorithms)"]
        Gym["Gymnasium<br>(Environments)"]
    end

    Train --> SB3
    EnvUtils --> Gym
    ExpManager --> "Evaluation & Analysis"
```

Sources: [README.md:12-16](), [setup.py:38-46]()

## Basic Usage Workflow

The typical workflow in RL-Baselines3-Zoo follows these stages:

**RL-Baselines3-Zoo Workflow**

```mermaid
flowchart LR
    subgraph "1. Setup"
        Install["Install RL-Zoo3"] --> ConfigEnv["Configure Environment"]
    end

    subgraph "2. Training"
        Train["Run train.py<br>with algorithm & environment"] --> TrainedModel["Trained Model (.zip)"]
    end

    subgraph "3. Evaluation"
        TrainedModel --> Enjoy["Run enjoy.py<br>to visualize agent"]
        TrainedModel --> Benchmark["Run benchmark.py<br>to measure performance"]
        TrainedModel --> Record["Run record_video.py<br>to create videos"]
    end

    subgraph "4. Analysis"
        Enjoy --> Analyze["Analyze results"]
        Benchmark --> Analyze
        Record --> Analyze
    end

    "1. Setup" --> "2. Training"
    "2. Training" --> "3. Evaluation"
    "3. Evaluation" --> "4. Analysis"
```

Sources: [README.md:62-100]()

## Training an Agent

To train an agent, use the `train.py` script or the CLI command `rl_zoo3 train`. You need to specify the algorithm and environment.

Basic training command:
```bash
python train.py --algo ALGORITHM_NAME --env ENVIRONMENT_ID
```

For example, to train a SAC agent on the HalfCheetah environment:
```bash
python train.py --algo sac --env HalfCheetahBulletEnv-v0
```

You can customize the training process with additional parameters:
```bash
python train.py --algo sac --env HalfCheetahBulletEnv-v0 --eval-freq 10000 --eval-episodes 10 --n-eval-envs 1
```

The `--eval-freq` parameter specifies how often (in timesteps) to evaluate the agent, `--eval-episodes` sets the number of evaluation episodes, and `--n-eval-envs` determines the number of parallel environments for evaluation.

Sources: [README.md:62-76]()

## Evaluating Trained Agents

After training, you can visualize your agent's performance using the `enjoy.py` script:

```bash
python enjoy.py --algo ALGORITHM_NAME --env ENVIRONMENT_ID
```

For example, to watch an A2C agent play Breakout for 5000 timesteps:
```bash
python enjoy.py --algo a2c --env BreakoutNoFrameskip-v4 --folder rl-trained-agents/ -n 5000
```

Sources: [README.md:88-100]()

## Accessing Pre-trained Agents

RL-Baselines3-Zoo comes with over 200 pre-trained agents. To access them:

1. Clone the repository with submodules:
   ```bash
   git clone --recursive https://github.com/DLR-RM/rl-baselines3-zoo
   ```

2. Use the pre-trained agents with the `enjoy.py` script:
   ```bash
   python enjoy.py --algo ALGORITHM_NAME --env ENVIRONMENT_ID --folder rl-trained-agents/
   ```

Pre-trained agents are also available on Hugging Face: https://huggingface.co/sb3

Sources: [README.md:88-115]()

## Interactive Usage

While RL-Baselines3-Zoo is primarily designed for command-line usage, you can also use it in interactive sessions (Jupyter notebooks, IPython) by modifying `sys.argv`:

```python
import sys
from rl_zoo3.train import train

sys.argv = ["python", "--algo", "ppo", "--env", "MountainCar-v0"]

train()
```

Sources: [README.md:259-271]()

## System Requirements and Dependencies

RL-Baselines3-Zoo has the following key dependencies:

| Dependency | Purpose | Version Requirements |
|------------|---------|----------------------|
| stable-baselines3 | Core RL algorithms | >=2.6.0, <3.0 |
| sb3_contrib | Additional RL algorithms | >=2.6.0, <3.0 |
| gymnasium | Environment interface | >=0.29.1, <1.2.0 |
| pybullet_envs_gymnasium | PyBullet environments | >=0.6.0 |
| optuna | Hyperparameter optimization | >=3.0 |
| wandb (optional) | Experiment tracking | - |
| moviepy (optional) | Video recording | >=1.0.0 |

Sources: [requirements.txt:1-15](), [setup.py:17-27]()

## Next Steps

Once you've set up RL-Baselines3-Zoo and tried the basic training and evaluation workflows, you can explore more advanced features:

- [Training System](#3) - Learn about the training system architecture in detail
- [Hyperparameter Management](#4) - Understand how to configure and optimize hyperparameters
- [Evaluation and Benchmarking](#5) - Discover more advanced evaluation techniques
- [External Integrations](#7) - Explore integrations with Weights & Biases and Hugging Face Hub
- [Visualization and Analysis](#8) - Learn about tools for visualizing and analyzing results

---

