# deepwiki cleanrl §12 glossary
> 来源: https://deepwiki.com/vwxyzjn/cleanrl/12-glossary

$/$
$?

/$

DeepWiki

DeepWiki
vwxyzjn/cleanrl

$?

/$

Last indexed:  27 July 2026  (fe8d8a)

  - Overview
  - Getting Started
  - Installation
  - Basic Usage
  - Model Zoo and HuggingFace Integration
  - Core Algorithms
  - PPO (Proximal Policy Optimization)
  - DQN (Deep Q-Network)
  - SAC (Soft Actor-Critic)
  - DDPG and TD3
  - Advanced Algorithms
  - JAX Implementations
  - JAX Algorithm Implementations
  - EnvPool XLA Integration
  - Environment Integrations
  - Classic Control
  - Atari Games
  - MuJoCo and Continuous Control
  - Procgen and Generalization
  - Multi-agent Environments
  - Isaac Gym Integration
  - EnvPool Integration
  - Benchmarking and Evaluation
  - Running Benchmarks
  - Experiment Tracking
  - Hyperparameter Tuning with Optuna
  - Cloud Deployment
  - AWS Batch Setup
  - Docker Containers
  - Testing and CI/CD
  - Development Guide
  - Contributing
  - Glossary

Menu

## Glossary

Relevant source files

  - .github/workflows/pre-commit.yml

  - .github/workflows/tests.yaml

  - .github/workflows/utils_test.yaml

  - README.md

  - benchmark/ppg.sh

  - cleanrl/c51.py

  - cleanrl/c51_atari.py

  - cleanrl/ddpg_continuous_action.py

  - cleanrl/ddpg_continuous_action_jax.py

  - cleanrl/dqn.py

  - cleanrl/dqn_atari.py

  - cleanrl/dqn_atari_jax.py

  - cleanrl/dqn_jax.py

  - cleanrl/ppo.py

  - cleanrl/ppo_continuous_action.py

  - cleanrl/sac_continuous_action.py

  - cleanrl/td3_continuous_action.py

  - cleanrl/td3_continuous_action_jax.py

  - docs/get-started/installation.md

  - docs/index.md

  - pyproject.toml

  - requirements/requirements-cloud.txt

This glossary provides definitions for codebase-specific terms, abbreviations, and domain concepts used throughout the CleanRL project. It is designed to help onboarding engineers navigate the unique "single-file" architecture and reinforcement learning (RL) specific implementations.

### Core Project Concepts

#### Single-file Implementation

The central philosophy of CleanRL. Every detail of an algorithm variant is contained within one standalone script (e.g., `ppo_atari.py`). This includes the neural network architecture, environment setup, and the training loop README.md19-21 This approach prioritizes readability and easy debugging over modularity README.md40-41

#### Args Dataclass Pattern

CleanRL uses a `dataclass` named `Args` at the top of every script to define hyperparameters and experiment settings cleanrl/ppo.py17-80 These are automatically parsed from the command line using `tyro` cleanrl/ppo.py130

#### Track (WandB)

A boolean flag in the `Args` dataclass. When `--track` is toggled, the experiment logs metrics, hyperparameters, and system information to Weights & Biases (WandB) cleanrl/ppo.py27-32

#### SPS (Steps Per Second)

A common performance metric in CleanRL scripts, calculated by dividing the total global steps by the elapsed time. It measures the throughput of the training implementation cleanrl/ppo.py321

### RL Domain Concepts in Code

#### Vectorized Environments

CleanRL utilizes `gymnasium.vector` to run multiple environment instances in parallel. This is typically managed via `SyncVectorEnv` or `AsyncVectorEnv` cleanrl/ppo.py162-164

#### GAE (Generalized Advantage Estimation)

A method for calculating advantages used in policy gradient methods like PPO. It balances bias and variance using a `gae_lambda` hyperparameter cleanrl/ppo.py51-52

#### Replay Buffer

A data structure used in off-policy algorithms (DQN, SAC, DDPG) to store and sample past transitions `(s, a, r, s', done)`. In CleanRL, this is implemented in `cleanrl_utils.buffers.ReplayBuffer` cleanrl/dqn.py16

#### Target Network

A copy of the main neural network used in Q-learning (DQN, TD3) to stabilize training. It is updated periodically or via "soft" updates controlled by `tau` cleanrl/dqn.py57-60

#### Entropy Tuning (Autotune)

Specifically used in Soft Actor-Critic (SAC). It automatically adjusts the temperature parameter $\alpha$ to match a `target_entropy` cleanrl/sac_continuous_action.py65-66

### Code-to-Entity Mapping

The following diagram illustrates how high-level RL concepts map to specific classes and variables within a CleanRL script (using `ppo.py` and `dqn.py` as primary references).

#### Diagram: Algorithm Structure Mapping

```

```

#### Diagram: Data Flow in PPO Implementation

This diagram shows how data flows through the entities defined in `ppo.py`.

```

```

### Technical Abbreviations

| Abbreviation | Full Term | Context in Code |
| PPO | Proximal Policy Optimization | ppo.py , ppo_atari.py cleanrl/ppo.py 1 |
| DQN | Deep Q-Network | dqn.py , dqn_atari.py cleanrl/dqn.py 1 |
| SAC | Soft Actor-Critic | sac_continuous_action.py cleanrl/sac_continuous_action.py 1 |
| TD3 | Twin Delayed DDPG | td3_continuous_action.py cleanrl/td3_continuous_action.py 1 |
| GAE | Generalized Advantage Estimation | Advantage calculation logic cleanrl/ppo.py 218-235 |
| KL | Kullback–Leibler Divergence | Used for early stopping in PPO cleanrl/ppo.py 69-70 |
| VF | Value Function | Critic network coefficient vf_coef cleanrl/ppo.py 65-66 |

### Environment Wrappers

CleanRL uses several standard and custom wrappers to preprocess environment data, particularly for Atari games.

  - RecordEpisodeStatistics : Gym wrapper that tracks episodic return and length, logged via writer.add_scalar cleanrl/ppo.py 88

  - NoopResetEnv : Resets the environment with a random number of no-op actions to provide different starting states cleanrl/dqn_atari.py 91

  - MaxAndSkipEnv : Returns only every skip -th frame and the max of the last two frames cleanrl/dqn_atari.py 92

  - EpisodicLifeEnv : Signals "done" when a life is lost in Atari games cleanrl/dqn_atari.py 93

  - FrameStack : Stacks $N$ recent frames to provide temporal information to the agent cleanrl/dqn_atari.py 99

Sources:

  - README.md 1-41

  - cleanrl/ppo.py 17-195

  - cleanrl/dqn.py 16-188

  - cleanrl/dqn_atari.py 82-126

  - cleanrl/sac_continuous_action.py 19-151

  - cleanrl/td3_continuous_action.py 19-132



#### On this page

  - Glossary
  - Core Project Concepts
  - Single-file Implementation
  - Args Dataclass Pattern
  - Track (WandB)
  - SPS (Steps Per Second)
  - RL Domain Concepts in Code
  - Vectorized Environments
  - GAE (Generalized Advantage Estimation)
  - Replay Buffer
  - Target Network
  - Entropy Tuning (Autotune)
  - Code-to-Entity Mapping
  - Diagram: Algorithm Structure Mapping
  - Diagram: Data Flow in PPO Implementation
  - Technical Abbreviations
  - Environment Wrappers

$!/$$/$
