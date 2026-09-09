> 来源: [https://deepwiki.com/kengz/SLM-Lab/1-overview](https://deepwiki.com/kengz/SLM-Lab/1-overview)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Overview

  Relevant source files 
 - [README.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1)
 - [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/lib/viz.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py)
 - [slm_lab/spec/demo.json](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 
  This page introduces SLM Lab: its purpose, the algorithms it provides, its core abstractions, and a map of the codebase. For installation steps, see [Getting Started](https://deepwiki.com/kengz/SLM-Lab/2-getting-started). For a deep-dive into how the subsystems connect at runtime, see [Architecture](https://deepwiki.com/kengz/SLM-Lab/3-architecture).

 
---

 
## What SLM Lab Is

 SLM Lab is a **modular deep reinforcement learning framework built in PyTorch**. It is the companion library to the book *Foundations of Deep Reinforcement Learning* and is designed so that RL experiments can be fully specified via JSON configuration files with no code changes required.

 Every run saves its spec file and git SHA, making experiments reproducible. Training metrics, plots, and TensorBoard logs are produced automatically. The framework supports cloud training via `dstack` and result sharing via HuggingFace.

 The entry point is the `slm-lab` CLI, implemented in `run_lab.py`. The demo command `slm-lab run` runs a PPO agent on CartPole using the spec at [slm_lab/spec/demo.json](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json)

 Sources: [README.md1-65](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L1-L65) [slm_lab/spec/demo.json1-65](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json#L1-L65)

 
---

 
## Supported Algorithms

 
| Algorithm | Class Name | Type | Typical Use |
|---|---|---|---|
| REINFORCE | REINFORCE | On-policy policy gradient | Learning / teaching |
| SARSA | SARSA | On-policy TD control | Tabular-like problems |
| DQN / DoubleDQN | DQN, DoubleDQN | Off-policy value-based | Discrete actions, Atari |
| A2C | ActorCritic | On-policy actor-critic | Fast iteration, Atari |
| PPO | PPO | On-policy clipped surrogate | General purpose, MuJoCo, Atari |
| SAC | SoftActorCritic | Off-policy maximum entropy | Continuous control, MuJoCo |

 All algorithm classes live under `slm_lab/agent/algorithm/`. The `Agent` class in [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py) instantiates the correct algorithm by reading `agent_spec["algorithm"]["name"]` from the spec.

 Sources: [README.md40-49](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L40-L49) [slm_lab/agent/__init__.py68-71](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L68-L71)

 
---

 
## Supported Environments

 SLM Lab uses [Gymnasium](https://gymnasium.farama.org/) as its environment interface. Any Gymnasium-compatible environment can be used by specifying its name in the `env.name` field of the spec.

 
| Category | Examples |
|---|---|
| Classic Control | CartPole, Pendulum, Acrobot |
| Box2D | LunarLander, BipedalWalker |
| MuJoCo | Hopper, HalfCheetah, Humanoid |
| Atari | Breakout, MsPacman, and 54+ others |

 Environment creation and wrapping is handled by `make_env` in `slm_lab/env/__init__.py`. See [Environments](https://deepwiki.com/kengz/SLM-Lab/6-environments) for details.

 Sources: [README.md52-62](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L52-L62)

 
---

 
## Core Abstractions

 The framework is organized around five layered abstractions. The top three form the **experiment hierarchy**; the bottom two are the **RL runtime pair**.

 
### Experiment Hierarchy Diagram

 
```

```

 Sources: [slm_lab/experiment/control.py36-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L36-L235)

 
| Abstraction | Class | Responsibility |
|---|---|---|
| Experiment | Experiment | Runs hyperparameter search over a grid of Trials via Ray Tune |
| Trial | Trial | Runs max_session repeated sessions of one spec; aggregates results |
| Session | Session | Runs one full RL loop from frame 0 to max_frame; produces session metrics |
| Agent | Agent | Holds algorithm, memory, MetricsTracker; exposes act() and update() |
| Environment | Gymnasium env + wrappers | Wraps a Gymnasium env; tracks clock state, rewards, and episode info |

 Sources: [slm_lab/experiment/control.py36-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L36-L235) [slm_lab/agent/__init__.py24-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L24-L121)

 
---

 
## The RL Loop

 The innermost loop, run by `Session.run_rl()`, follows this sequence at every timestep:

 **Session RL Loop Diagram**

 
```

```

 Sources: [slm_lab/experiment/control.py105-129](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L129)

 
---

 
## Spec-Driven Configuration

 Every experiment is fully defined by a **spec** — a JSON (or YAML) dictionary loaded by `spec_util.get()`. Specs live in `slm_lab/spec/`. The demo spec at [slm_lab/spec/demo.json](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json) is the canonical starting point.

 A spec has four top-level blocks:

 
```
spec
├── name        (str)         experiment name
├── agent
│   ├── algorithm             algorithm class name + hyperparameters
│   ├── memory                memory class name + parameters
│   └── net                   network type + architecture + optimizer
├── env
│   ├── name                  Gymnasium environment ID
│   ├── max_frame             training budget in environment steps
│   └── num_envs              (optional) number of parallel envs
└── meta
    ├── max_session           number of repeated sessions per trial
    ├── max_trial             number of trials in a search experiment
    ├── log_frequency         how often to log/checkpoint
    └── distributed           whether to use Hogwild / async training
```

 `spec_util.tick()` advances the experiment/trial/session index in `meta` and creates output directories. `spec_util.check()` validates the spec structure on load. For full spec field reference, see [Spec Format Reference](https://deepwiki.com/kengz/SLM-Lab/7.1-spec-format-reference).

 Sources: [slm_lab/spec/spec_util.py21-38](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L21-L38) [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198) [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330) [slm_lab/spec/demo.json1-65](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json#L1-L65)

 
---

 
## Agent Internals

 The `Agent` class is composed of three components, all instantiated from the spec:

 **Agent Component Diagram**

 
```

```

 
 - `Algorithm` handles action selection (`act`), network training (`train`), and exploration variable updates (`update`).
 - `Memory` stores and samples transitions.
 - `MetricsTracker` records per-checkpoint metrics into `train_df` and `eval_df` DataFrames, and writes them to disk.
 
 Sources: [slm_lab/agent/__init__.py24-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L24-L121) [slm_lab/agent/__init__.py123-414](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L123-L414)

 
---

 
## Analysis Pipeline

 After each `Session`, `Trial`, and `Experiment`, `slm_lab/experiment/analysis.py` computes standardized metrics and generates plots.

 
| Metric | Description | Function |
|---|---|---|
| strength | Mean return above random baseline | calc_strength |
| sample_efficiency | Strength gained per environment frame | calc_efficiency |
| training_efficiency | Strength gained per optimizer step | calc_efficiency |
| stability | Penalizes drops in strength over time | calc_stability |
| consistency | Cross-session agreement in strength | calc_consistency |

 The entry points are `analyze_session`, `analyze_trial`, and `analyze_experiment` in [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py) Plots are produced by `viz.plot_session`, `viz.plot_trial`, and `viz.plot_experiment` in [slm_lab/lib/viz.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py) Offline re-analysis of saved data is possible via `retro_analyze` in [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)

 For a full description of these metrics, see [Metrics and Analysis](https://deepwiki.com/kengz/SLM-Lab/4.2-metrics-and-analysis).

 Sources: [slm_lab/experiment/analysis.py13-313](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L13-L313) [slm_lab/lib/viz.py136-277](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py#L136-L277) [slm_lab/experiment/retro_analysis.py1-91](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py#L1-L91)

 
---

 
## Codebase Map

 
```

```

 Sources: [slm_lab/experiment/control.py1-19](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L1-L19) [slm_lab/agent/__init__.py1-21](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L1-L21) [slm_lab/lib/util.py1-10](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L1-L10)

 
---

 
## Output Directory Layout

 Each run produces a timestamped directory under `data/`:

 
```
data/{spec_name}_{experiment_ts}/
├── {spec_name}_spec.json           experiment spec
├── {spec_name}_t0_spec.json        trial spec
├── graph/                          PNG plots
├── info/                           metrics JSON and session CSV files
├── log/                            loguru log files
└── model/                          saved PyTorch model weights
```

 The `prepath`, `info_prepath`, `graph_prepath`, `log_prepath`, and `model_prepath` keys in `spec["meta"]` all resolve to paths inside this directory and are set by `spec_util.tick()`.

 Sources: [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330) [slm_lab/lib/util.py181-215](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L181-L215)
