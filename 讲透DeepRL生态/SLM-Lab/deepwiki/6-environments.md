> 来源: [https://deepwiki.com/kengz/SLM-Lab/6-environments](https://deepwiki.com/kengz/SLM-Lab/6-environments)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Environments

  Relevant source files 
 - [slm_lab/env/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py)
 
  This page provides an overview of the `env` module (`slm_lab/env/`): its purpose, the types of environments supported, and how the creation and wrapping pipeline fits into the broader SLM Lab system. For detailed documentation on individual topics, see:

 
 - [Environment Creation](https://deepwiki.com/kengz/SLM-Lab/6.1-environment-creation) — `make_env`, `_make_single_env`, `_make_vector_env`, spec-driven instantiation
 - [Environment Wrappers](https://deepwiki.com/kengz/SLM-Lab/6.2-environment-wrappers) — custom and standard Gymnasium wrappers applied during construction
 
 
---

 
## Role in the System

 The `env` module is the interface between the RL agent and the world it trains in. It wraps [Gymnasium](https://gymnasium.farama.org/) environments with a standardized set of preprocessing steps, metadata attributes, and timing machinery so that agent code can interact with any supported environment through a consistent API.

 During a `Session`, the environment and agent are created together from the same spec. The agent calls `env.step()` and reads attributes like `env.state_dim`, `env.action_dim`, and `env.is_discrete` to configure itself. The spec's `env` block fully determines what gets created — no environment-specific code lives outside this module.

 For how the `Session` coordinates agent and environment, see [Control Flow: Experiment, Trial, and Session](https://deepwiki.com/kengz/SLM-Lab/4.1-control-flow:-experiment-trial-and-session).

 Sources: [slm_lab/env/__init__.py1-48](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L1-L48)

 
---

 
## Supported Environment Types

 
| Type | Detection | Notes |
|---|---|---|
| Classic Control | classic_control in entry point | Single or vectorized (sync) |
| Box2D | box2d in entry point | Single or vectorized (sync) |
| Atari (ALE) | name.startswith("ALE/") | Uses AtariVectorEnv or sync+wrappers |
| MuJoCo / Continuous | Box action space, non-ALE | Async vectorization; normalization supported |
| Any registered Gym env | — | Passes unknown kwargs through to gym.make |

 Atari environments require the `ale_py` package. If it is installed, `gym.register_envs(ale_py)` is called automatically on module import [slm_lab/env/__init__.py39-46](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L39-L46)

 
---

 
## Module Structure

 **Environment creation pipeline** — `make_env` in `__init__.py` is the single public entry point. It dispatches to either `_make_single_env` or `_make_vector_env`, then applies `_set_env_attributes` and wraps the result in a clock wrapper.

 **Wrappers** — `slm_lab/env/wrappers.py` supplies custom wrapper classes that are applied inside both creation paths.

 The diagram below shows the module layout and how the public surface area maps to implementation functions.

 **Diagram: env module structure**

 
```

```

 Sources: [slm_lab/env/__init__.py153-335](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L153-L335)

 
---

 
## Environment Attributes

 After construction, every env (single or vector) carries a standard set of attributes set by `_set_env_attributes`. Agent and algorithm code reads these to configure networks, action distributions, and training loops.

 
| Attribute | Type | Description |
|---|---|---|
| state_dim | int or tuple | Observation dimensionality |
| action_dim | int or list | Number of actions or shape |
| is_discrete | bool | True for Discrete, MultiDiscrete, MultiBinary |
| is_multi | bool | True for multi-dimensional action spaces |
| is_venv | bool | True if the env is a VectorEnv |
| num_envs | int | Number of parallel environments |
| max_t | int | Max steps per episode |
| max_frame | int | Total training frames (adjusted for distributed runs) |
| eval_frequency | int | From spec["meta"] |
| log_frequency | int | From spec["meta"] |
| done | bool | Episode termination flag |

 Sources: [slm_lab/env/__init__.py90-151](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L90-L151)

 
---

 
## Creation Flow Overview

 The diagram below shows the full call sequence from spec to a ready-to-use environment.

 **Diagram: make_env call flow**

 
```

```

 Sources: [slm_lab/env/__init__.py153-335](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L153-L335)

 
---

 
## Spec-Driven Configuration

 The `env` block of a spec file controls every aspect of environment creation. Keys handled directly by `make_env` are listed in `RESERVED_KEYS`; all other keys are forwarded verbatim as `**kwargs` to `gym.make` or `gym.make_vec`.

 
```
RESERVED_KEYS = {
    "name", "num_envs", "max_t", "max_frame",
    "normalize_obs", "normalize_reward",
    "clip_obs", "clip_reward"
}
```

 
| Spec key | Effect |
|---|---|
| name | Gym environment ID (e.g. "CartPole-v1", "ALE/Pong-v5") |
| num_envs | 1 → single env; > 1 → vectorized env |
| max_t | Max steps per episode (falls back to spec.max_episode_steps) |
| max_frame | Total training frames |
| normalize_obs | Wraps with NormalizeObservation / VectorNormalizeObservation |
| normalize_reward | Wraps with NormalizeReward / VectorNormalizeReward |
| clip_obs | Clips observations to ±clip_obs; defaults to 10.0 if normalize_obs=True |
| clip_reward | Clips rewards; scalar or [min, max] pair |

 For the full spec format reference, see [Spec Format Reference](https://deepwiki.com/kengz/SLM-Lab/7.1-spec-format-reference).

 Sources: [slm_lab/env/__init__.py51-60](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L51-L60) [slm_lab/env/__init__.py159-203](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L159-L203)

 
---

 
## Vectorization Mode Selection

 For vector environments, `_get_vectorization_mode` selects one of three Gymnasium vectorization backends automatically:

 
| Mode | When used | Notes |
|---|---|---|
| "vector_entry_point" | ALE/Atari, not rendering | Native AtariVectorEnv; fastest for Atari |
| "sync" | ALE rendering, simple envs (classic_control, box2d), or num_envs < 8 | Synchronous parallel |
| "async" | Complex envs with num_envs >= 8 | AsyncVectorEnv; subprocess-based parallelism |

 Sources: [slm_lab/env/__init__.py74-87](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L74-L87)

 
---

 
## Relation to the Agent

 The environment object is passed to and stored by the `Session`. The `Agent` reads env attributes (`state_dim`, `action_dim`, `is_discrete`) during `__init__` to build its networks and configure its action distribution. During the RL loop the agent calls `env.reset()` and `env.step(action)` directly through the `Session`.

 For more on how the agent uses these attributes, see [Agent and MetricsTracker](https://deepwiki.com/kengz/SLM-Lab/5.1-agent-and-metricstracker).
