> 来源: [https://deepwiki.com/kengz/SLM-Lab/2-getting-started](https://deepwiki.com/kengz/SLM-Lab/2-getting-started)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Getting Started

  Relevant source files 
 - [Dockerfile](https://github.com/kengz/SLM-Lab/blob/d3128a8a/Dockerfile)
 - [README.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1)
 - [bin/setup](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup)
 - [bin/setup_arch](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_arch)
 - [bin/setup_macOS](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_macOS)
 - [bin/setup_ubuntu](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_ubuntu)
 - [slm_lab/lib/viz.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py)
 
  This page is the entry point for new users of SLM Lab. It covers the complete path from a fresh machine to a running experiment: obtaining the code, installing dependencies, and executing a basic training run locally or on cloud. For detailed step-by-step instructions on each phase, see the child pages: [Installation](https://deepwiki.com/kengz/SLM-Lab/2.1-installation) and [Running Your First Experiment](https://deepwiki.com/kengz/SLM-Lab/2.2-running-your-first-experiment). For an explanation of the broader system architecture (Experiments, Trials, Sessions, Agents), see [Architecture](https://deepwiki.com/kengz/SLM-Lab/3-architecture).

 
---

 
## Overview

 SLM Lab is a PyTorch-based deep RL framework. Getting it running requires:

 
 - Installing system-level dependencies (C build tools, SDL2, SWIG, etc.)
 - Installing the `uv` Python package manager
 - Syncing Python dependencies with `uv sync`
 - Installing the `slm-lab` CLI tool
 - Running an experiment via `slm-lab run`
 
 The framework ships with platform-specific setup scripts, a Docker image, and a `uv`-based Python environment. All experiments are driven by JSON spec files — no code modifications are required for common workflows.

 
---

 
## Setup Paths

 Three supported paths exist for getting the environment ready:

 **Setup path diagram:**

 
```

```

 Sources: [bin/setup1-48](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup#L1-L48) [bin/setup_macOS1-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_macOS#L1-L36) [bin/setup_ubuntu1-28](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_ubuntu#L1-L28) [bin/setup_arch1-26](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup_arch#L1-L26) [Dockerfile1-29](https://github.com/kengz/SLM-Lab/blob/d3128a8a/Dockerfile#L1-L29) [README.md64-119](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L119)

 
---

 
## Quick Install (Native)

 
```

```

 If `slm-lab` is not on `PATH` after installation, use `uv run slm-lab` as a fallback.

 See [Installation](https://deepwiki.com/kengz/SLM-Lab/2.1-installation) for platform-specific dependency details and Docker instructions.

 Sources: [bin/setup1-48](https://github.com/kengz/SLM-Lab/blob/d3128a8a/bin/setup#L1-L48) [README.md64-85](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L85)

 
---

 
## Quick Install (Docker)

 The Docker image is based on `ubuntu:22.04` and mirrors the Ubuntu native setup.

 
```

```

 The `Dockerfile` installs system packages (`build-essential`, `swig`, `libgl1`, `libglib2.0-0`), then `uv`, then runs `uv sync --frozen` to reproduce the exact locked dependency set.

 Sources: [Dockerfile1-29](https://github.com/kengz/SLM-Lab/blob/d3128a8a/Dockerfile#L1-L29)

 
---

 
## Running a First Experiment

 Once installed, the demo PPO CartPole experiment requires no additional configuration:

 
```

```

 To run a custom spec file:

 
```

```

 The `slm-lab` CLI is defined in `run_lab.py` and uses [Typer](https://typer.tiangolo.com/). The `run` command loads a spec file, instantiates an `Experiment` → `Trial` → `Session` chain, and executes the RL training loop.

 **CLI command map:**

 
```

```

 Sources: [README.md64-119](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L119)

 
---

 
## Cloud Training (dstack)

 SLM Lab integrates with [dstack](https://dstack.ai) for cloud GPU training and HuggingFace for result storage.

 
| Step | Command |
|---|---|
| Copy env config | cp .env.example .env (add HF_TOKEN) |
| Install dstack | uv tool install dstack |
| CPU training | slm-lab run-remote spec.json spec_name train |
| GPU training | slm-lab run-remote --gpu spec.json spec_name train |
| Download results | slm-lab pull spec_name |
| List experiments | slm-lab list |

 Cloud configuration files live in `.dstack/`:

 
| Config file | Purpose |
|---|---|
| run-cpu-train.yml | CPU training job |
| run-cpu-search.yml | CPU hyperparameter search |
| run-gpu-train.yml | GPU training job |
| run-gpu-search.yml | GPU hyperparameter search |

 Sources: [README.md87-119](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L87-L119)

 
---

 
## Minimal Install (Orchestration Only)

 For a machine that only needs to dispatch cloud jobs, sync results, and generate plots — without local ML training:

 
```

```

 Sources: [README.md109-119](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L109-L119)

 
---

 
## What Happens After You Run

 The following diagram maps CLI invocation to the key code entities that execute:

 
```

```

 Outputs are saved under `data/<spec_name>_<timestamp>/` and include training curves, metrics, and a copy of the spec used.

 For an explanation of the full data flow through these components, see [Architecture](https://deepwiki.com/kengz/SLM-Lab/3-architecture). For details on the spec file format, see [Configuration and Spec Files](https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files).

 Sources: [README.md64-85](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L85)

 
---

 
## Supported Environments

 Any [Gymnasium](https://gymnasium.farama.org/)-compatible environment can be used by naming it in the spec file.

 
| Category | Examples | Dependency group |
|---|---|---|
| Classic Control | CartPole, Pendulum, Acrobot | gymnasium (default) |
| Box2D | LunarLander, BipedalWalker | gymnasium[box2d] |
| MuJoCo | Hopper, HalfCheetah, Humanoid | gymnasium[mujoco] |
| Atari | Breakout, MsPacman, 54 total | gymnasium[atari] |

 Sources: [README.md51-62](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L51-L62)
