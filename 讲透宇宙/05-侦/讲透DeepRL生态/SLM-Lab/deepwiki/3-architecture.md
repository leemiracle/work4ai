> 来源: [https://deepwiki.com/kengz/SLM-Lab/3-architecture](https://deepwiki.com/kengz/SLM-Lab/3-architecture)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Architecture

  Relevant source files 
 - [README.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1)
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
 - [slm_lab/env/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/lib/viz.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 
  This page describes how SLM Lab's major subsystems connect: how a spec file drives an `Experiment`, how `Trial` and `Session` objects execute the RL loop, and how `Agent` and environment interact. It covers the full data flow from a JSON spec file to saved model checkpoints and analysis outputs.

 For installation and first-run steps, see [Getting Started](https://deepwiki.com/kengz/SLM-Lab/2-getting-started). For per-subsystem API references, see [Experiment System](https://deepwiki.com/kengz/SLM-Lab/4-experiment-system), [Agent](https://deepwiki.com/kengz/SLM-Lab/5-agent), [Environments](https://deepwiki.com/kengz/SLM-Lab/6-environments), and [Configuration and Spec Files](https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files).

 
---

 
## Layered Overview

 SLM Lab organizes code into four layers:

 
| Layer | Primary Classes/Modules | Location |
|---|---|---|
| Entry & Config | spec_util, spec JSON files | slm_lab/spec/ |
| Orchestration | Experiment, Trial, Session | slm_lab/experiment/control.py |
| RL Core | Agent, Algorithm, Memory, nets | slm_lab/agent/ |
| Environment | make_env, wrappers, ClockWrapper | slm_lab/env/ |
| Analysis | analyze_session, analyze_trial, viz | slm_lab/experiment/analysis.py, slm_lab/lib/viz.py |
| Infrastructure | math_util, net_util, policy_util, util | slm_lab/lib/, slm_lab/agent/net/ |

 Sources: [slm_lab/experiment/control.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L1-L20) [slm_lab/agent/__init__.py1-22](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L1-L22) [slm_lab/env/__init__.py1-48](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L1-L48) [slm_lab/experiment/analysis.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L1-L20)

 
---

 
## Spec-Driven Initialization

 All configuration enters the system through a JSON spec file and the `spec_util` module. No component is initialized without a `spec` dict.

 **Spec loading sequence:**

 
 - `spec_util.get(spec_file, spec_name)` reads and validates a spec dict — [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198)
 - `spec_util.extend_meta_spec(spec)` injects runtime fields (`experiment_ts`, `trial`, `session`, `git_sha`, `prepath`, etc.) — [slm_lab/spec/spec_util.py115-135](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L115-L135)
 - `spec_util.tick(spec, unit)` advances `experiment`/`trial`/`session` indices and creates output directories — [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330)
 - The `spec` dict is passed down to every class constructor.
 
 The `SPEC_FORMAT` constant in `spec_util` defines the required top-level keys (`agent`, `env`, `meta`, `name`). The `check()` function validates types before any experiment runs.

 **Minimum required spec shape:**

 
```

```

 Sources: [slm_lab/spec/spec_util.py21-38](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L21-L38) [slm_lab/spec/spec_util.py76-90](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L76-L90) [slm_lab/spec/spec_util.py115-135](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L115-L135) [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330)

 
---

 
## Three-Level Execution Hierarchy

 **Diagram: Experiment → Trial → Session class relationships**

 
```

```

 Sources: [slm_lab/experiment/control.py147-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L147-L235)

 
### Experiment

 `Experiment` [slm_lab/experiment/control.py211-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L211-L235) is the top-level unit. Its `run()` method invokes `search.run_ray_search(self.spec)`, which spawns one `Trial` per hyperparameter configuration. After all trials complete, it calls `analysis.analyze_experiment()` and optionally trims saved models with `search.cleanup_trial_models()`.

 
### Trial

 `Trial` [slm_lab/experiment/control.py147-208](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L147-L208) runs one or more sessions against the same spec.

 
 - **Single session:** Calls `Session(spec).run()` directly.
 - **Multiple sessions:** Calls `parallelize_sessions()`, which spawns one `mp.Process` per session using `mp_run_session()`.
 - **Distributed (A3C-style):** Calls `run_distributed_sessions()`, which first builds shared global nets via `init_global_nets()`, then passes them to each session process.
 
 After all sessions complete, it calls `analysis.analyze_trial()` and logs scalar trial metrics.

 
### Session

 `Session` [slm_lab/experiment/control.py36-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L36-L144) is where the RL loop runs.

 In `__init__`, it calls `make_agent_env(spec)` to create the `Agent` and environment. If `meta.rigorous_eval` is set, a separate `eval_env` is also created.

 `run_rl()` is the main loop [slm_lab/experiment/control.py105-129](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L129):

 
```

```

 `try_ckpt()` [slm_lab/experiment/control.py78-103](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L78-L103) fires at intervals defined by `log_frequency` and `eval_frequency`. At each checkpoint it: saves the model, records metrics to the training dataframe, optionally evaluates in `eval_env`, and triggers incremental session/trial plots.

 After the loop, `run()` calls `analysis.analyze_session()` on `agent.mt.eval_df` and returns the session metrics.

 Sources: [slm_lab/experiment/control.py21-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L21-L144) [slm_lab/experiment/control.py199-208](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L199-L208)

 
---

 
## Agent and Environment Interaction

 **Diagram: Agent internals and environment wiring**

 
```

```

 Sources: [slm_lab/agent/__init__.py24-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L24-L121) [slm_lab/env/__init__.py153-203](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L153-L203)

 
### Agent

 `Agent` [slm_lab/agent/__init__.py24-121](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L24-L121) is a thin coordinator. It holds references to `self.algorithm`, `self.memory`, and `self.mt` (a `MetricsTracker`). Its two primary API methods:

 
 - `act(state)` — delegates to `self.algorithm.act(state)` under `torch.no_grad()`.
 - `update(state, action, reward, next_state, done, terminated, truncated)` — updates `mt`, writes to `memory`, calls `algorithm.train()`, then `algorithm.update()` (for exploration variable decay).
 
 
### MetricsTracker

 `MetricsTracker` [slm_lab/agent/__init__.py123-413](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L123-L413) owns the `train_df` and `eval_df` dataframes that accumulate per-checkpoint rows. Key columns include `total_reward`, `total_reward_ma`, `loss`, `fps`, `frame`, `opt_step`, and `lr`. Its `ckpt(env, df_mode)` method appends a new row; `log_summary(df_mode)` prints a formatted summary.

 
### Algorithm

 All algorithms inherit from the `Algorithm` ABC [slm_lab/agent/algorithm/base.py12-136](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/algorithm/base.py#L12-L136) The required interface:

 
| Method | Purpose |
|---|---|
| init_algorithm_params() | Read spec values, set hyperparameters |
| init_nets(global_nets) | Instantiate neural networks and optimizers |
| calc_pdparam(x) | Forward pass to get action distribution parameters |
| act(state) | Select an action from the policy |
| sample() | Pull a batch from memory |
| train() | One training step; returns loss or nan |
| update() | Decay exploration variables; update target nets |
| save(ckpt) / load() | Model persistence |

 Concrete algorithms:

 
| Class | File | Family |
|---|---|---|
| SARSA | algorithm/sarsa.py | Value-based, on-policy |
| VanillaDQN, DQN, DoubleDQN | algorithm/dqn.py | Value-based, off-policy |
| Reinforce | algorithm/reinforce.py | Policy gradient |
| ActorCritic | algorithm/actor_critic.py | Actor-Critic |
| PPO | algorithm/ppo.py | Actor-Critic, clipped surrogate |
| SoftActorCritic | algorithm/sac.py | Actor-Critic, entropy-regularized |
| SIL, PPOSIL | algorithm/sil.py | Actor-Critic + self-imitation |
| Random | algorithm/random.py | Baseline |

 
### Environment

 `make_env(spec)` [slm_lab/env/__init__.py153-203](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L153-L203) creates a Gymnasium environment and wraps it:

 
 - Calls `_make_single_env()` or `_make_vector_env()` based on `env_spec['num_envs']`.
 - Applies normalization (`NormalizeObservation`, `NormalizeReward`), clipping (`ClipReward`, `ClipObservation`), and action rescaling (`RescaleAction`) as specified.
 - For Atari: applies `AtariPreprocessing` and `FrameStackObservation`.
 - Injects attributes onto the env object: `state_dim`, `action_dim`, `is_discrete`, `is_venv`, `max_frame`.
 - Wraps with `ClockWrapper` (single) or `VectorClockWrapper` (vector) to provide a frame counter accessible via `env.get()`.
 
 Sources: [slm_lab/env/__init__.py63-204](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/env/__init__.py#L63-L204)

 
---

 
## Data Flow: Spec to Results

 **Diagram: Full data flow through the system**

 
```

```

 Sources: [slm_lab/experiment/control.py105-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L144) [slm_lab/experiment/analysis.py264-313](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L264-L313) [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330)

 
### Output Directory Structure

 For an experiment named `ppo_cartpole` started at timestamp `2025_01_01_120000`:

 
```
data/ppo_cartpole_2025_01_01_120000/
├── ppo_cartpole_spec.json           # experiment spec snapshot
├── ppo_cartpole_t0_spec.json        # trial 0 spec
├── ppo_cartpole_t0_s0_spec.json     # session 0 of trial 0 spec
├── graph/
│   └── ppo_cartpole_t0_s0_session_graph_*.png
├── info/
│   ├── ppo_cartpole_t0_s0_session_df_train.csv
│   ├── ppo_cartpole_t0_s0_session_metrics_train.json
│   ├── ppo_cartpole_t0_trial_metrics.json
│   └── ppo_cartpole_trial_data_dict.json
├── log/
│   └── ppo_cartpole_t0_s0.log
└── model/
    ├── ppo_cartpole_t0_s0_net.pt
    └── ppo_cartpole_t0_s0_net_best.pt
```

 The path structure is computed by `util.get_prepath(spec, unit)` [slm_lab/lib/util.py195-209](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L195-L209) using the `trial` and `session` indices in `spec['meta']`.

 
### Analysis Pipeline

 Each level of the hierarchy triggers analysis when it completes:

 
 - `Session.run()` → `analysis.analyze_session(spec, mt.eval_df, 'eval')` — computes strength, efficiency, stability; saves session metrics JSON and session graph PNGs.
 - `Trial.run()` → `analysis.analyze_trial(spec, session_metrics_list)` — aggregates session metrics, computes consistency, saves trial metrics JSON and trial graph PNGs.
 - `Experiment.run()` → `analysis.analyze_experiment(spec, trial_data_dict)` — builds `experiment_df` sorted by strength, saves CSV and experiment scatter plots.
 
 Offline re-analysis is available via `retro_analyze()` in [slm_lab/experiment/retro_analysis.py68-80](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py#L68-L80) which reads saved spec and data files and re-runs the full analysis pipeline.

 Sources: [slm_lab/experiment/analysis.py264-313](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L264-L313) [slm_lab/experiment/retro_analysis.py16-80](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py#L16-L80)

 
---

 
## Checkpoint and Training Control

 `to_ckpt(env, mode)` [slm_lab/experiment/control.py65-76](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L65-L76) determines whether to run a checkpoint at the current frame. It fires when:

 
 - `frame % log_frequency < num_envs` (training log)
 - `frame % eval_frequency < num_envs` (eval, if `rigorous_eval` is set)
 - `frame == max_frame` (always at the final frame)
 
 The `frame_mod` helper in `util` handles the case where vectorized environments advance the frame counter by `num_envs` per step.

 Model saves happen inside `try_ckpt` [slm_lab/experiment/control.py78-103](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L78-L103):

 
 - `agent.save()` — saves the current model weights.
 - `agent.save(ckpt='best')` — saves an additional copy whenever `total_reward_ma` exceeds the previous best.
 
 Sources: [slm_lab/experiment/control.py65-103](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L65-L103) [slm_lab/lib/util.py110-115](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L110-L115)

 
---

 
## Distributed Training

 When `spec['meta']['distributed']` is not `False`, `Trial.run_distributed_sessions()` is used [slm_lab/experiment/control.py190-194](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L190-L194):

 
 - `init_global_nets()` creates a temporary `Session`, extracts its algorithm's nets, calls `net_util.init_global_nets()` to move them to shared memory, then closes the session.
 - `parallelize_sessions(global_nets)` spawns one `mp.Process` per session, each receiving the same `global_nets` dict.
 - Each session's algorithm uses the global nets for Hogwild-style asynchronous gradient updates.
 
 This supports algorithms like A3C where workers asynchronously update a shared parameter server.

 Sources: [slm_lab/experiment/control.py160-194](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L160-L194)

 
---

 
## Key Inter-Component Contracts

 **Diagram: Data contracts between components**

 
```

```

 Sources: [slm_lab/agent/__init__.py73-108](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L73-L108) [slm_lab/experiment/control.py105-129](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L129)

 The `Agent.act()` call runs under `torch.no_grad()`. The `Agent.update()` call stores the transition in memory and potentially triggers `algorithm.train()` if the algorithm's `to_train` flag is set (controlled by training frequency logic inside each algorithm's `update()` method).

 `batch` dictionaries from memory use plural keys (`states`, `actions`, etc.) as PyTorch tensors, moved to the network's device before loss computation.
