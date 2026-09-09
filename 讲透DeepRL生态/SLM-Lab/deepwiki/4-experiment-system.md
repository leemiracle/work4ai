> 来源: [https://deepwiki.com/kengz/SLM-Lab/4-experiment-system](https://deepwiki.com/kengz/SLM-Lab/4-experiment-system)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Experiment System

  Relevant source files 
 - [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py)
 - [slm_lab/agent/net/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/net/__init__.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/experiment/search.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py)
 - [slm_lab/lib/logger.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/logger.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/conftest.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/conftest.py)
 - [test/experiment/test_control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/experiment/test_control.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 - [test/spec/test_dist_spec.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/spec/test_dist_spec.py)
 - [test/spec/test_spec.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/spec/test_spec.py)
 
  This page describes the experiment orchestration layer: the three-level execution hierarchy (`Experiment`, `Trial`, `Session`), and how it connects to the analysis, search, and visualization subsystems.

 For details on each subsystem, see the child pages:

 
 - Control flow mechanics: [Control Flow: Experiment, Trial, and Session](https://deepwiki.com/kengz/SLM-Lab/4.1-control-flow:-experiment-trial-and-session)
 - Metrics and analysis: [Metrics and Analysis](https://deepwiki.com/kengz/SLM-Lab/4.2-metrics-and-analysis)
 - Hyperparameter search: [Hyperparameter Search](https://deepwiki.com/kengz/SLM-Lab/4.3-hyperparameter-search)
 - Visualization: [Visualization](https://deepwiki.com/kengz/SLM-Lab/4.4-visualization)
 
 For information about the spec format that drives experiments, see [Configuration and Spec Files](https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files).

 
---

 
## Overview

 The experiment system translates a JSON spec file into a structured execution run and produces a set of metrics, plots, and saved models. All orchestration logic lives in `slm_lab/experiment/`, with three main modules:

 
| Module | File | Responsibility |
|---|---|---|
| control | slm_lab/experiment/control.py | Experiment, Trial, Session classes; RL loop |
| analysis | slm_lab/experiment/analysis.py | Metrics computation; session/trial/experiment analysis |
| search | slm_lab/experiment/search.py | Ray Tune hyperparameter search |
| retro_analysis | slm_lab/experiment/retro_analysis.py | Offline re-analysis from saved files |

 Sources: [slm_lab/experiment/control.py1-19](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L1-L19) [slm_lab/experiment/analysis.py1-21](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L1-L21) [slm_lab/experiment/search.py1-19](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L1-L19)

 
---

 
## Three-Level Hierarchy

 The experiment system is organized as a strict three-level nesting. Each level runs the level below it, collects results, and produces its own outputs.

 **Hierarchy diagram: Class relationships and responsibilities**

 
```

```

 Sources: [slm_lab/experiment/control.py211-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L211-L235) [slm_lab/experiment/control.py147-208](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L147-L208) [slm_lab/experiment/control.py36-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L36-L144)

 
### Level Summary

 
| Level | Class | Spec field | Runs | Produces |
|---|---|---|---|---|
| Experiment | Experiment | meta.experiment | N Trials via Ray Tune | experiment_df.csv, experiment plots |
| Trial | Trial | meta.trial | max_session Sessions | trial_metrics.json, trial plots |
| Session | Session | meta.session | RL loop to max_frame | session_df.csv, session_metrics.json, model checkpoints |

 Sources: [slm_lab/experiment/control.py36-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L36-L235)

 
---

 
## Indices and the `spec_util.tick` Contract

 Each level's index is stored in `spec["meta"]` and is advanced by calling `spec_util.tick(spec, unit)` before instantiating that level. The indices start at `-1` and are incremented by `tick`. Lower indices are reset when a higher level ticks.

 
```
spec["meta"]["experiment"] = -1  # initial value
spec["meta"]["trial"]      = -1
spec["meta"]["session"]    = -1
```

 Calling `spec_util.tick(spec, 'trial')` increments `trial` to `0` and resets `session` to `-1`. This ensures deterministic, monotonically-increasing indices throughout a run.

 `tick` also sets all path-related fields on `meta`:

 
| Field set by tick | Example value |
|---|---|
| meta.predir | data/ppo_cartpole_2024_01_15_120000 |
| meta.prepath | data/.../ppo_cartpole_t0 |
| meta.info_prepath | data/.../info/ppo_cartpole_t0 |
| meta.model_prepath | data/.../model/ppo_cartpole_t0 |
| meta.log_prepath | data/.../log/ppo_cartpole_t0 |

 Sources: [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330)

 
---

 
## Execution Flow

 **Diagram: Full execution flow from CLI to saved outputs**

 
```

```

 Sources: [slm_lab/experiment/control.py139-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L139-L144) [slm_lab/experiment/control.py199-208](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L199-L208) [slm_lab/experiment/control.py228-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L228-L235) [slm_lab/experiment/search.py185-236](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L185-L236)

 
---

 
## Session: The RL Loop

 A `Session` contains one `Agent` and one `Env`. The main loop in `Session.run_rl` runs until the environment clock reaches `max_frame`:

 
```
state, info = env.reset()
while env.get() < env.max_frame:
    action = agent.act(state)
    next_state, reward, terminated, truncated, info = env.step(action)
    agent.update(state, action, reward, next_state, done, ...)
    try_ckpt(agent, env)
    state = next_state  # or env.reset() if episode done
```

 `try_ckpt` fires at `log_frequency` intervals and at the final frame. At each checkpoint it:

 
 - Appends a row to `agent.mt.train_df`
 - Saves the model (and optionally a `best` checkpoint)
 - Calls `analyze_session` to update session plots and metrics
 
 Sources: [slm_lab/experiment/control.py105-144](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L105-L144) [slm_lab/experiment/control.py78-104](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L78-L104)

 
---

 
## Trial: Session Aggregation

 A `Trial` runs `max_session` sessions and aggregates their metrics.

 
 - **Single session** (`max_session == 1`): runs `Session` directly in the same process.
 - **Multiple sessions** (`max_session > 1`): spawns parallel processes via `torch.multiprocessing`.
 - **Distributed** (`meta.distributed` is set): initializes global shared nets first via `init_global_nets`, then passes them to each session process via `parallelize_sessions`.
 
 After all sessions complete, `analyze_trial` computes trial-level metrics (mean strength, consistency, etc.) from the collected `session_metrics_list`.

 Sources: [slm_lab/experiment/control.py147-208](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L147-L208)

 
---

 
## Experiment: Hyperparameter Search

 An `Experiment` runs multiple trials, each with a different hyperparameter configuration sampled by Ray Tune. The `search` block in the spec file defines the search space.

 `Experiment.run()` calls `search.run_ray_search(spec)`, which:

 
 - Builds the param space from `spec["search"]` using `build_param_space`
 - Wraps `Trial.run` in `build_run_trial` for Ray Tune
 - Uses `OptunaSearch` for sampling with optional `AsyncHyperBandScheduler` early stopping
 - Collects `trial_data_dict` from saved files after all trials finish
 - Calls `analyze_experiment` to produce the final `experiment_df`
 - Calls `cleanup_trial_models` to delete model files for low-performing trials (retaining top-N)
 
 If no `search` block is present, running at the `Trial` level directly is the typical single-configuration workflow.

 Sources: [slm_lab/experiment/control.py211-235](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L211-L235) [slm_lab/experiment/search.py185-236](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L185-L236)

 
---

 
## Analysis Integration

 Analysis functions are called at the end of each level. They are stateless — they take data and write files to the `info/` and `graph/` directories.

 **Diagram: Analysis function call sites**

 
```

```

 The `METRICS_COLS` list in `analysis.py` defines the canonical set of scalar metrics tracked at every level:

 
| Metric | Description |
|---|---|
| frame | Total environment frames at end of trial |
| total_reward_ma | Moving average of total reward |
| strength | Mean return above random baseline |
| max_strength | Maximum per-checkpoint strength |
| final_strength | Strength at final checkpoint |
| sample_efficiency | Strength weighted by inverse frame count |
| training_efficiency | Strength weighted by inverse optimizer step count |
| stability | 1 minus relative reward drops |
| consistency | 1 minus cross-session variance of strength |

 Sources: [slm_lab/experiment/analysis.py13-19](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L13-L19) [slm_lab/experiment/analysis.py264-313](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L264-L313) [slm_lab/experiment/control.py78-96](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L78-L96)

 
---

 
## Output Directory Structure

 All outputs are written under `data/{spec_name}_{experiment_ts}/`. The `spec_util.tick` function creates the subdirectories and sets the path fields in `spec["meta"]`.

 
```
data/ppo_cartpole_2024_01_15_120000/
├── model/
│   ├── ppo_cartpole_t0_s0.pt
│   └── ppo_cartpole_t0_s0_ckpt-best.pt
├── info/
│   ├── ppo_cartpole_t0_s0_session_df_train.csv
│   ├── ppo_cartpole_t0_s0_session_df_eval.csv
│   ├── ppo_cartpole_t0_s0_session_metrics_train.json
│   ├── ppo_cartpole_t0_s0_session_metrics_eval.json
│   ├── ppo_cartpole_t0_trial_metrics.json
│   ├── ppo_cartpole_t0_trial_metrics_scalar.json
│   └── ppo_cartpole_trial_data_dict.json
├── graph/
│   ├── ppo_cartpole_t0_s0_session_graph_train.png
│   ├── ppo_cartpole_t0_trial_graph.png
│   └── ppo_cartpole_experiment_graph.png
└── log/
    └── ppo_cartpole_t0_s0.log
```

 Sources: [slm_lab/lib/util.py181-215](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L181-L215) [slm_lab/spec/spec_util.py319-329](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L319-L329)

 
---

 
## Retro Analysis

 `slm_lab/experiment/retro_analysis.py` provides offline re-analysis when the original run has completed but plots or metrics need to be regenerated (e.g., after a code change to `viz.py`).

 The entry point is `retro_analyze(predir)`, which calls three sub-functions in order:

 
| Function | What it re-runs |
|---|---|
| retro_analyze_sessions(predir) | analyze_session for each _s*_spec.json |
| retro_analyze_trials(predir) | analyze_trial for each _t*_spec.json |
| retro_analyze_experiment(predir) | analyze_experiment using saved _trial_data_dict.json |

 Invoked via the CLI:

 
```
uv run slm-retro data/ppo_cartpole_2024_01_15_120000/
```

 Sources: [slm_lab/experiment/retro_analysis.py16-87](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py#L16-L87)
