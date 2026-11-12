> 来源: [https://deepwiki.com/kengz/SLM-Lab/5-agent](https://deepwiki.com/kengz/SLM-Lab/5-agent)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Agent

  Relevant source files 
 - [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py)
 - [slm_lab/agent/algorithm/actor_critic.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/actor_critic.py)
 - [slm_lab/agent/algorithm/base.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py)
 - [slm_lab/agent/algorithm/dqn.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/dqn.py)
 - [slm_lab/agent/algorithm/policy_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/policy_util.py)
 - [slm_lab/agent/algorithm/ppo.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/ppo.py)
 - [slm_lab/agent/algorithm/random.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/random.py)
 - [slm_lab/agent/algorithm/reinforce.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/reinforce.py)
 - [slm_lab/agent/algorithm/sac.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/sac.py)
 - [slm_lab/agent/algorithm/sarsa.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/sarsa.py)
 - [slm_lab/agent/algorithm/sil.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/sil.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 
  This page describes the `Agent` module in SLM Lab: its structure, the three components it coordinates (algorithm, memory, and network), and the interface it exposes to the training loop. The `Agent` is the central abstraction that bridges the environment and the learning system.

 For detailed documentation on each sub-component, see:

 
 - [Agent and MetricsTracker](https://deepwiki.com/kengz/SLM-Lab/5.1-agent-and-metricstracker) — full `Agent` and `MetricsTracker` API
 - [Algorithms](https://deepwiki.com/kengz/SLM-Lab/5.2-algorithms) — algorithm implementations and base class
 - [Memory](https://deepwiki.com/kengz/SLM-Lab/5.3-memory) — memory buffer implementations
 - [Neural Networks](https://deepwiki.com/kengz/SLM-Lab/5.4-neural-networks) — network architectures and utilities
 
 For how `Agent` is created and called from the experiment lifecycle, see [Control Flow: Experiment, Trial, and Session](https://deepwiki.com/kengz/SLM-Lab/4.1-control-flow:-experiment-trial-and-session).

 
---

 
## Overview

 The `Agent` class ([slm_lab/agent/__init__.py24-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L24-L121)) is the coordinator between three internal components:

 
| Component | Instantiated From | Role |
|---|---|---|
| Algorithm | agent_spec["algorithm"]["name"] | Decides actions, computes loss, trains networks |
| Memory | agent_spec["memory"]["name"] | Stores and samples transitions |
| MetricsTracker | Passed in from Session | Tracks reward, loss, and logging data |

 The `Algorithm` in turn owns one or more `Net` (neural network) instances. The `Agent` itself holds references to all three and coordinates the flow of data between them during each environment step.

 **Agent Module Layout:**

 
```

```

 Sources: [slm_lab/agent/__init__.py1-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L1-L121) [slm_lab/agent/algorithm/base.py1-136](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L1-L136) [slm_lab/experiment/control.py21-26](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L21-L26)

 
---

 
## Agent Initialization

 `Agent` is constructed by `Session` through the `make_agent_env` helper ([slm_lab/experiment/control.py21-26](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L21-L26)):

 
```

```

 During `__init__`, `Agent` [slm_lab/agent/__init__.py30-71](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L30-L71):

 
 - Reads environment space attributes (`state_dim`, `action_dim`, `is_discrete`) directly from the wrapped env.
 - Determines the `ActionPD` class (probability distribution for sampling actions) by calling `policy_util.get_action_type()` and `policy_util.get_action_pd_cls()`.
 - Instantiates `Memory` via `getattr(memory, memory_name)(...)`.
 - Instantiates `Algorithm` via `getattr(algorithm, algorithm_name)(agent, global_nets)`. 
 - `Algorithm.__init__` immediately calls `init_algorithm_params()` then `init_nets()`, building and wiring all neural networks.
 
 **Initialization sequence:**

 
```

```

 Sources: [slm_lab/agent/__init__.py30-71](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L30-L71) [slm_lab/agent/algorithm/base.py15-26](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L15-L26) [slm_lab/experiment/control.py21-26](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L21-L26)

 
---

 
## The RL Loop Interface

 `Session.run_rl()` ([slm_lab/experiment/control.py105-129](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L129)) drives the interaction between `Agent` and `Env`. At each timestep:

 
 - `agent.act(state)` → returns `action`
 - `env.step(action)` → returns `next_state, reward, terminated, truncated, info`
 - `agent.update(state, action, reward, next_state, done, terminated, truncated)`
 
 **Data flow per timestep:**

 
```

```

 
### `act()`

 [slm_lab/agent/__init__.py73-78](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L73-L78)

 Wraps `algorithm.act(state)` inside `torch.no_grad()` for inference efficiency. Returns a numpy array (or scalar for single discrete envs) compatible with `gym.Env.step()`.

 
### `update()`

 [slm_lab/agent/__init__.py80-108](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L80-L108)

 Called every step after `env.step()`. Performs three sequential operations:

 
 - `mt.update(...)` — passes data to `MetricsTracker` for TensorBoard tracking.
 - `memory.update(...)` — stores the transition in the memory buffer. Skipped in eval mode.
 - `algorithm.train()` — triggers a training step if the memory is ready (controlled by `to_train` and `training_frequency` inside the algorithm). Returns loss.
 - `algorithm.update()` — updates decayable variables like `explore_var` (epsilon, tau).
 
 In eval mode (`util.in_eval_lab_mode()`), only `mt.update()` is called; memory and training are skipped.

 Sources: [slm_lab/agent/__init__.py73-108](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L73-L108) [slm_lab/experiment/control.py105-129](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L129)

 
---

 
## Algorithm Component

 The abstract base class `Algorithm` ([slm_lab/agent/algorithm/base.py12-136](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L12-L136)) defines the interface that all algorithm implementations must satisfy. It holds a reference to `agent` and reads `algorithm_spec`, `memory_spec`, and `net_spec` from the agent's spec.

 **Algorithm inheritance hierarchy:**

 
```

```

 All concrete algorithms are importable as `slm_lab.agent.algorithm.<ClassName>` and are selected by name from the spec field `agent.algorithm.name`.

 **Algorithm reference table:**

 
| Class | Module | Memory Type | Action Space |
|---|---|---|---|
| Random | random.py | any | discrete or continuous |
| SARSA | sarsa.py | OnPolicyBatchReplay | discrete |
| VanillaDQN | dqn.py | Replay | discrete |
| DQN | dqn.py | Replay | discrete |
| DoubleDQN | dqn.py | Replay | discrete |
| Reinforce | reinforce.py | OnPolicyReplay | discrete or continuous |
| ActorCritic | actor_critic.py | OnPolicyReplay / OnPolicyBatchReplay | discrete or continuous |
| PPO | ppo.py | OnPolicyBatchReplay | discrete or continuous |
| SIL | sil.py | OnPolicyReplay + Replay | discrete or continuous |
| PPOSIL | sil.py | OnPolicyBatchReplay + Replay | discrete or continuous |
| SoftActorCritic | sac.py | Replay | discrete or continuous |

 Sources: [slm_lab/agent/algorithm/base.py12-136](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L12-L136) [slm_lab/agent/algorithm/dqn.py1-10](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/dqn.py#L1-L10) [slm_lab/agent/algorithm/reinforce.py1-10](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/reinforce.py#L1-L10) [slm_lab/agent/algorithm/actor_critic.py61-70](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/actor_critic.py#L61-L70) [slm_lab/agent/algorithm/ppo.py14-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/ppo.py#L14-L20) [slm_lab/agent/algorithm/sac.py15-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/sac.py#L15-L20) [slm_lab/agent/algorithm/sil.py13-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/sil.py#L13-L20)

 
---

 
## Memory Component

 Memory classes are in `slm_lab/agent/memory/`. They all expose a common interface: `update(state, action, reward, next_state, done, ...)` to add transitions and `sample()` to return a batch dict. The class is selected by `agent_spec["memory"]["name"]`.

 
| Class | File | Mode |
|---|---|---|
| Replay | replay.py | off-policy circular buffer |
| OnPolicyReplay | replay.py | episodic, cleared after sample |
| OnPolicyBatchReplay | replay.py | flat batch, cleared after sample |
| OnPolicyCrossEntropy | replay.py | top-percentile episode filtering |
| PrioritizedReplay | prioritized.py | off-policy with SumTree priorities |

 For full details, see [Memory](https://deepwiki.com/kengz/SLM-Lab/5.3-memory).

 Sources: [slm_lab/agent/__init__.py68-69](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L68-L69)

 
---

 
## Neural Network Component

 Networks are in `slm_lab/agent/net/`. The Algorithm selects and instantiates them using `net_spec["type"]` and calling `getattr(net, NetClass)(net_spec, in_dim, out_dim)`. Networks expose a `forward()` and a `train_step(loss, optim, lr_scheduler)` method.

 
| Class | Architecture | Typical Use |
|---|---|---|
| MLPNet | fully connected MLP | most algorithms |
| HydraMLPNet | multi-head MLP | multi-task or separate actor/critic heads |
| DuelingMLPNet | dueling advantage streams | DQN variants |
| ConvNet | convolutional + MLP | pixel-based / Atari |
| DuelingConvNet | dueling convolutional | Atari DQN variants |
| RecurrentNet | LSTM + MLP | sequence / partial observability |

 For full details, see [Neural Networks](https://deepwiki.com/kengz/SLM-Lab/5.4-neural-networks).

 Sources: [slm_lab/agent/algorithm/base.py40-42](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L40-L42) [slm_lab/agent/algorithm/reinforce.py76-94](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/reinforce.py#L76-L94)

 
---

 
## MetricsTracker

 `MetricsTracker` ([slm_lab/agent/__init__.py123-414](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L123-L414)) is constructed by `Session` before `Agent` and passed in as `mt`. It accumulates per-step data into `train_df` and `eval_df` DataFrames, logs to console and TensorBoard, and provides data for the analysis pipeline.

 Key responsibilities:

 
 - **`ckpt(env, df_mode)`** — appends a row to `train_df` or `eval_df` with the current reward, loss, fps, frame, lr, and any registered algorithm variables.
 - **`log_summary(df_mode)`** — formats and logs the last row to the console.
 - **`register_algo_var(var_name, source_obj)`** — dynamically adds any algorithm variable (e.g., `explore_var`, `clip_eps`, `alpha`) to the logged columns. Called by algorithms during `init_algorithm_params()`.
 - **`calc_log_metrics(spec, df_mode)`** — computes session-level metrics (strength, efficiency, stability) from the current DataFrame and stores them for Ray Tune reporting.
 
 For full documentation, see [Agent and MetricsTracker](https://deepwiki.com/kengz/SLM-Lab/5.1-agent-and-metricstracker).

 Sources: [slm_lab/agent/__init__.py123-414](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L123-L414) [slm_lab/experiment/control.py78-103](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L78-L103)

 
---

 
## Spec-to-Component Mapping

 The agent spec block in a JSON spec file controls every component:

 
```

```

 **Spec field to class resolution:**

 
```

```

 Sources: [slm_lab/agent/__init__.py68-71](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L68-L71) [slm_lab/agent/algorithm/base.py20-25](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L20-L25) [slm_lab/spec/spec_util.py21-38](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L21-L38)

 
---

 
## `save()` and `close()`

 
 - `agent.save(ckpt=None)` ([slm_lab/agent/__init__.py110-115](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L110-L115)) delegates to `algorithm.save(ckpt=ckpt)`, which calls `net_util.save_algorithm()` to persist all networks listed in `algorithm.net_names`. Passing `ckpt="best"` saves a separate best-checkpoint copy.
 - `agent.close()` ([slm_lab/agent/__init__.py117-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L117-L121)) calls `save()` and is triggered at the end of `Session.close()`.
 
 Neither method runs in eval mode (`util.in_eval_lab_mode()` returns `True`), preventing eval runs from overwriting saved models.

 Sources: [slm_lab/agent/__init__.py110-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L110-L121) [slm_lab/agent/algorithm/base.py116-130](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L116-L130) [slm_lab/experiment/control.py131-137](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L131-L137)
