> 来源: [https://deepwiki.com/Toni-SM/skrl/5-trainers](https://deepwiki.com/Toni-SM/skrl/5-trainers)
> DeepWiki Toni-SM/skrl | Last indexed: 17 August 2026 (3cdc7f

# Trainers

  Relevant source files 
 - [docs/source/api/trainers.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/trainers.rst)
 - [docs/source/api/trainers/parallel.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/trainers/parallel.rst)
 - [docs/source/api/trainers/sequential.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/trainers/sequential.rst)
 - [docs/source/api/trainers/step.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/trainers/step.rst)
 - [docs/source/api/utils/huggingface.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/utils/huggingface.rst)
 - [docs/source/api/utils/postprocessing.rst](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/api/utils/postprocessing.rst)
 - [docs/source/snippets/trainer.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/trainer.py)
 - [skrl/trainers/jax/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/__init__.py)
 - [skrl/trainers/jax/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/base.py)
 - [skrl/trainers/jax/sequential.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/sequential.py)
 - [skrl/trainers/jax/step.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/step.py)
 - [skrl/trainers/torch/__init__.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/__init__.py)
 - [skrl/trainers/torch/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py)
 - [skrl/trainers/torch/parallel.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py)
 - [skrl/trainers/torch/sequential.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py)
 - [skrl/trainers/torch/step.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py)
 - [skrl/trainers/warp/base.py](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/warp/base.py)
 
  Trainers are the orchestration components responsible for managing the complete reinforcement learning training and evaluation loops. They coordinate interactions between agents and environments, handle multi-agent scenarios, manage parallel execution, and provide different execution strategies (sequential, parallel, and step-by-step control).

 For information about the agents that trainers orchestrate, see [Agents](https://deepwiki.com/Toni-SM/skrl/2-agents). For environment integration details, see [Environments](https://deepwiki.com/Toni-SM/skrl/4-environments).

 
## Architecture Overview

 The trainer system is built around a base `Trainer` class with specialized implementations for different execution strategies. Each trainer type supports PyTorch, JAX, and Warp backends with consistent APIs.

 
### Trainer Class Hierarchy

 
```

```

 Sources: [skrl/trainers/torch/base.py38-130](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L38-L130) [skrl/trainers/torch/sequential.py17-54](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L17-L54) [skrl/trainers/torch/parallel.py135-167](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L135-L167) [skrl/trainers/torch/step.py19-64](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py#L19-L64)

 
### Backend Support Matrix

 
| Trainer Type | PyTorch | JAX | Warp | Key Features |
|---|---|---|---|---|
| SequentialTrainer | ✓ | ✓ | ✓ | Standard training loop |
| ParallelTrainer | ✓ | ✗ | ✗ | Multi-process execution |
| StepTrainer | ✓ | ✓ | ✗ | Manual step control |

 Sources: [skrl/trainers/torch/__init__.py1-5](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/__init__.py#L1-L5) [skrl/trainers/jax/__init__.py1-4](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/__init__.py#L1-L4) [docs/source/snippets/trainer.py1-112](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/trainer.py#L1-L112)

 
## Training Loop Orchestration

 All trainers follow a consistent interaction pattern that coordinates agents and environments through standardized phases. The base `Trainer` class provides the default `train()` and `eval()` logic for single-agent scenarios, while subclasses override these for multi-agent or parallel execution.

 
### Core Training Flow

 
```

```

 Sources: [skrl/trainers/torch/base.py177-245](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L177-L245) [skrl/trainers/jax/base.py176-241](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/base.py#L176-L241)

 
### Agent Scope Management

 Trainers support multiple simultaneous agents by partitioning environments using agent scopes. The `scopes` parameter defines the range of environment indices each agent operates on.

 
```

```

 The `generate_equally_spaced_scopes()` function automatically distributes environments when scopes are not explicitly provided:

 Sources: [skrl/trainers/torch/base.py18-35](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L18-L35) [skrl/trainers/torch/base.py131-171](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L131-L171)

 
## Trainer Types

 
### SequentialTrainer

 The `SequentialTrainer` executes agents sequentially within each timestep, processing all agents before stepping the environment.

 **Key characteristics:**

 
 - Agents process states and generate actions one after another.
 - Single environment step per timestep after all agents act [skrl/trainers/torch/sequential.py108](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L108-L108)
 - Supports both single-agent and multi-agent scenarios.
 - Available in PyTorch, JAX, and Warp backends.
 
 Sources: [skrl/trainers/torch/sequential.py22-47](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L22-L47) [skrl/trainers/torch/sequential.py55-152](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L55-L152)

 
### ParallelTrainer

 The `ParallelTrainer` uses multiprocessing to execute multiple agents in parallel, providing performance improvements for CPU-bound computations.

 
```

```

 **Key features:**

 
 - Uses `torch.multiprocessing` with `spawn` method [skrl/trainers/torch/parallel.py166](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L166-L166)
 - Agents share memory for models and experience buffers via `share_memory_()` [skrl/trainers/torch/parallel.py70](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L70-L70)
 - Synchronization via barriers and message passing pipes [skrl/trainers/torch/parallel.py36-132](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L36-L132)
 - PyTorch backend only.
 
 **Processor tasks (`fn_processor`):**

 
 - `"init"`: Initialize agent in worker process [skrl/trainers/torch/parallel.py44](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L44-L44)
 - `"pre_interaction"`: Execute pre-interaction phase [skrl/trainers/torch/parallel.py51](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L51-L51)
 - `"act"`: Compute actions [skrl/trainers/torch/parallel.py56](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L56-L56)
 - `"record_transition"`: Store experience [skrl/trainers/torch/parallel.py75](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L75-L75)
 - `"post_interaction"`: Execute post-interaction phase [skrl/trainers/torch/parallel.py102](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L102-L102)
 - `"terminate"`: Shutdown worker process [skrl/trainers/torch/parallel.py40](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L40-L40)
 
 Sources: [skrl/trainers/torch/parallel.py18-134](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L18-L134) [skrl/trainers/torch/parallel.py140-431](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/parallel.py#L140-L431)

 
### StepTrainer

 The `StepTrainer` provides manual control over the training loop, executing single iterations on demand.

 **Key characteristics:**

 
 - Single-step execution via `train()` and `eval()` methods [skrl/trainers/torch/step.py63-183](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py#L63-L183)
 - Manual timestep management with internal `_timestep` counter [skrl/trainers/torch/step.py57](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py#L57-L57)
 - Returns environment transition data (observations, rewards, terminated, truncated, info) for external processing [skrl/trainers/torch/step.py81](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py#L81-L81)
 - Suitable for custom training logic and debugging.
 
 Sources: [skrl/trainers/torch/step.py24-61](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/step.py#L24-L61) [skrl/trainers/jax/step.py27-65](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/step.py#L27-L65)

 
## Multi-Agent Support

 Trainers automatically detect and handle multi-agent environments through specialized logic in the base `Trainer` class and specific overrides in subclasses.

 
### Multi-Agent Interaction Sequence

 
```

```

 Sources: [skrl/trainers/torch/sequential.py87-143](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L87-L143) [skrl/trainers/torch/base.py313-363](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L313-L363)

 
## Configuration System

 All trainers use the `TrainerCfg` dataclass for parameter management.

 
### Common Configuration Parameters

 
| Parameter | Type | Default | Description |
|---|---|---|---|
| timesteps | int | 100000 | Total training/evaluation timesteps skrl/trainers/torch/base.py42 |
| headless | bool | False | Whether to disable environment rendering skrl/trainers/torch/base.py45 |
| render_interval | int | 1 | Timestep interval for rendering skrl/trainers/torch/base.py48 |
| disable_progressbar | bool | False | Whether to hide the progress bar skrl/trainers/torch/base.py51 |
| environment_info | str | "episode" | Key for logging environment info skrl/trainers/torch/base.py57 |
| stochastic_evaluation | bool | False | Use stochastic actions during evaluation skrl/trainers/torch/base.py60 |

 Sources: [skrl/trainers/torch/base.py38-70](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L38-L70) [skrl/trainers/jax/base.py37-68](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/base.py#L37-L68)

 
## Backend Differences

 
### PyTorch Implementation

 
 - Uses `torch.no_grad()` for inference [skrl/trainers/torch/sequential.py90](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/sequential.py#L90-L90)
 - Supports distributed training via `config.torch.is_distributed` [skrl/trainers/torch/base.py109](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L109-L109)
 - Includes `ParallelTrainer` using `torch.multiprocessing`.
 
 
### JAX Implementation

 
 - Uses `contextlib.nullcontext()` instead of `torch.no_grad()` [skrl/trainers/jax/sequential.py91](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/sequential.py#L91-L91)
 - Uses `jax.numpy` for array operations [skrl/trainers/jax/sequential.py105](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/sequential.py#L105-L105)
 - Supports distributed training via `config.jax.is_distributed` [skrl/trainers/jax/base.py108](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/base.py#L108-L108)
 
 
### Warp Implementation

 
 - Focused on `SequentialTrainer` for high-performance vectorized environments.
 - API mirrors the PyTorch implementation for consistency.
 
 Sources: [skrl/trainers/torch/base.py109-111](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/torch/base.py#L109-L111) [skrl/trainers/jax/base.py108-110](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/skrl/trainers/jax/base.py#L108-L110) [docs/source/snippets/trainer.py37-52](https://github.com/Toni-SM/skrl/blob/3cdc7f3b/docs/source/snippets/trainer.py#L37-L52)
