> 来源: [https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files](https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Configuration and Spec Files

  Relevant source files 
 - [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py)
 - [slm_lab/agent/net/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/net/__init__.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/experiment/search.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py)
 - [slm_lab/lib/logger.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/logger.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/spec/demo.json](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/conftest.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/conftest.py)
 - [test/experiment/test_control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/experiment/test_control.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 - [test/spec/test_dist_spec.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/spec/test_dist_spec.py)
 - [test/spec/test_spec.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/spec/test_spec.py)
 
  This page explains the spec system end-to-end: what a spec file contains, how it is loaded and validated by `spec_util`, how runtime metadata is injected, and how the spec propagates through the Experiment → Trial → Session hierarchy to configure every subsystem.

 For the full field-by-field reference, see page [7.1](https://deepwiki.com/kengz/SLM-Lab/7.1-spec-format-reference). For the provided benchmark and experimental spec files, see page [7.2](https://deepwiki.com/kengz/SLM-Lab/7.2-benchmark-specifications). For how the search block drives hyperparameter optimization, see page [4.3](https://deepwiki.com/kengz/SLM-Lab/4.3-hyperparameter-search).

 
---

 
## What a Spec Is

 A **spec** is a plain JSON (or YAML) dictionary that fully describes one experiment configuration. It specifies what algorithm and network to use, what environment to run, how many sessions and trials to execute, and optionally a search space for hyperparameter sweeps.

 Every `Experiment`, `Trial`, and `Session` receives exactly one spec dict. The same spec travels down the hierarchy; `spec_util.tick` mutates the index fields in `spec["meta"]` to advance the run counter at each level.

 **Spec files live in `slm_lab/spec/`**, defined by the constant `SPEC_DIR` in [slm_lab/spec/spec_util.py13](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L13-L13)

 A single spec file can contain multiple named specs. Each top-level key is a spec name.

 
```
slm_lab/spec/
├── demo.json              ← tutorial/quickstart spec
├── benchmark/
│   ├── dqn/
│   ├── ppo/
│   ├── sac/
│   └── a2c/
└── experimental/
    ├── a2c/
    ├── dqn/
    ├── ppo/
    ├── sarsa/
    ├── sil/
    └── misc/
```

 Sources: [slm_lab/spec/spec_util.py13](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L13-L13) [slm_lab/spec/demo.json1-65](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json#L1-L65)

 
---

 
## Spec File Structure

 A valid spec has four required top-level blocks plus an optional `search` block.

 
```

```

 The `SPEC_FORMAT` dict in `spec_util.py` defines the required keys and their expected types:

 [slm_lab/spec/spec_util.py21-38](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L21-L38)

 
| Block | Required Keys | Purpose |
|---|---|---|
| agent | name, algorithm, memory, net | Algorithm, memory, and network configuration |
| env | name, max_t, max_frame | Environment name and time limits |
| meta | max_session, max_trial | Execution counts and behavior flags |
| name | (top-level string) | Spec identifier, injected at load time |
| search | (optional) | Hyperparameter search space for Ray Tune |

 
### The `agent` Block

 The agent block configures the three components of the Agent: algorithm, memory, and neural network.

 
```

```

 
 - `algorithm.name` must match a class in `slm_lab/agent/algorithm/`.
 - `memory.name` must match a class in `slm_lab/agent/memory/`.
 - `net.type` must match a class in `slm_lab/agent/net/`.
 - Decay specs (`clip_eps_spec`, `entropy_coef_spec`, `explore_var_spec`) are dicts with a `name` field (`no_decay`, `linear_decay`, `rate_decay`, `periodic_decay`) and `start_val`, `end_val`, `start_step`, `end_step`.
 
 
### The `env` Block

 
```

```

 
| Field | Type | Description |
|---|---|---|
| name | str | Gymnasium environment ID |
| max_frame | int or float | Training terminates at this global frame count |
| max_t | int or null | Per-episode step limit; null uses the environment default |
| num_envs | int | Number of vectorized environment instances (optional, default 1) |

 
### The `meta` Block

 
```

```

 
| Field | Type | Description |
|---|---|---|
| max_session | int | Sessions per trial (repeated runs for consistency measurement) |
| max_trial | int or null | Trials in an experiment (hyperparameter search iterations) |
| log_frequency | int | Checkpoint interval in frames |
| eval_frequency | int | Evaluation checkpoint interval in frames |
| distributed | bool or str | false for standard; "synced" for A3C/Hogwild |
| rigorous_eval | bool | If true, uses a separate eval env for evaluation checkpoints |

 
### The `search` Block

 The optional `search` block defines the hyperparameter search space for Ray Tune. Keys use the format `"path__distribution"` where `path` is a dot-separated path into the spec, and `distribution` is a Ray Tune sampling function name.

 
```

```

 This block is consumed by `build_param_space` in [slm_lab/experiment/search.py39-77](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L39-L77) and removed from the spec before it is passed to a `Trial`.

 Sources: [slm_lab/spec/demo.json1-65](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/demo.json#L1-L65) [slm_lab/spec/spec_util.py21-38](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L21-L38) [slm_lab/experiment/search.py39-77](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L39-L77)

 
---

 
## The `spec_util` Module

 All spec operations are in `slm_lab/spec/spec_util.py`. The diagram below maps each operation to the function that implements it.

 **spec_util function map**

 
```

```

 Sources: [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198)

 
### `spec_util.get`

 [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198)

 Loads a named spec from a file. Applies variable substitution, parses the JSON/YAML, injects the `name` field, calls `extend_meta_spec`, and validates with `check`.

 
```

```

 The `sets` parameter accepts strings like `"key=value"` and substitutes `${key}` placeholders in the raw JSON string before parsing. This allows one spec to be reused across multiple environments.

 
### `spec_util.check`

 [slm_lab/spec/spec_util.py76-90](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L76-L90)

 Validates that the spec contains all required top-level keys from `SPEC_FORMAT` and that each key's value is of the correct type. Calls `check_comp_spec` for `agent`, `env`, and `meta` sub-blocks.

 
### `extend_meta_spec`

 [slm_lab/spec/spec_util.py115-135](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L115-L135)

 Adds runtime fields to `spec["meta"]` that are not present in the user-written spec file. These are computed at load time:

 
| Field | Value |
|---|---|
| experiment | -1 (ticked to 0 on first use) |
| trial | -1 |
| session | -1 |
| experiment_ts | Timestamp string YYYY_MM_DD_HHMMSS |
| git_sha | Current repo git SHA |
| random_seed | None (set per-session later) |
| resume | True if experiment_ts was passed in |
| cuda_offset | From CUDA_OFFSET env var |

 
### `spec_util.tick`

 [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330)

 Advances the index of a given lab unit in `spec["meta"]` and creates the required output directories. Called before instantiating each `Experiment`, `Trial`, or `Session`.

 
 - `tick(spec, 'experiment')`: increments `experiment`, resets `trial` and `session` to -1.
 - `tick(spec, 'trial')`: increments `trial`, resets `session` to -1.
 - `tick(spec, 'session')`: increments `session`. In `enjoy` mode, calls `get_best_session` instead of incrementing.
 
 After ticking, `spec["meta"]` is populated with path fields:

 
| Field | Example Value |
|---|---|
| predir | data/ppo_cartpole_2024_01_15_120000 |
| prepath | data/.../ppo_cartpole_t0 |
| graph_prepath | data/.../graph/ppo_cartpole_t0 |
| info_prepath | data/.../info/ppo_cartpole_t0 |
| log_prepath | data/.../log/ppo_cartpole_t0 |
| model_prepath | data/.../model/ppo_cartpole_t0 |

 These paths are used throughout the codebase to write session data, model checkpoints, and plots.

 
### `spec_util.save`

 [slm_lab/spec/spec_util.py247-250](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L247-L250)

 Writes the current spec dict to `{prepath}_spec.json`. Called from `Trial.__init__` and `Experiment.__init__` so that each run's full configuration is persisted to disk alongside its results.

 
### `spec_util.override_spec`

 [slm_lab/spec/spec_util.py235-244](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L235-L244)

 Modifies the spec in place based on the current lab mode. Used in tests and development to reduce run times.

 
| Mode | What is overridden |
|---|---|
| test | Short max_frame, reduced frequencies, max_session=1, small batch sizes |
| dev | max_session=1, max_trial=2 |
| enjoy | max_session=1 |

 Sources: [slm_lab/spec/spec_util.py115-135](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L115-L135) [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198) [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330) [slm_lab/spec/spec_util.py235-244](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L235-L244)

 
---

 
## Spec Lifecycle

 The diagram below shows how a spec moves from a file on disk to each component that uses it.

 **Spec lifecycle through the execution hierarchy**

 
```

```

 Sources: [slm_lab/spec/spec_util.py278-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L278-L330) [slm_lab/experiment/control.py154-158](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L154-L158) [slm_lab/experiment/control.py43-53](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L43-L53)

 
---

 
## Variable Substitution

 Spec files can contain `${variable}` placeholders. These are substituted before JSON parsing, allowing a single spec to parameterize environment names, frame budgets, and other values via the `--set` CLI flag or the `sets` argument to `spec_util.get`.

 [slm_lab/spec/spec_util.py138-157](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L138-L157)

 Example spec excerpt using variables:

 
```

```

 Invocation:

 
```

```

 When `key=value` is numeric, `set_variables` replaces the quoted `"${key}"` token with an unquoted number to preserve JSON numeric type. String values replace the token inline. If the substituted key is `env`, the resolved short name (e.g., `hopper`) is appended to `spec["name"]` so output directories are distinct per environment.

 Sources: [slm_lab/spec/spec_util.py138-157](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L138-L157) [slm_lab/spec/spec_util.py160-198](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L160-L198)

 
---

 
## How Subsystems Read the Spec

 Each component receives the full spec dict and reads only its own sub-dict. The table below maps component to the spec path it uses.

 
| Component | Spec path accessed | Where |
|---|---|---|
| Agent | spec["agent"] | slm_lab/agent/__init__.py37 |
| Algorithm (via Agent) | spec["agent"]["algorithm"] | slm_lab/agent/__init__.py70-71 |
| Memory (via Agent) | spec["agent"]["memory"] | slm_lab/agent/__init__.py68-69 |
| Net (via Algorithm) | spec["agent"]["net"] | (within each algorithm's init_nets) |
| make_env | spec["env"] | slm_lab/env/__init__.py |
| Session | spec["meta"]["session"] for index | slm_lab/experiment/control.py45 |
| Trial | spec["meta"]["trial"] for index | slm_lab/experiment/control.py156 |
| Session.to_ckpt | spec["meta"]["log_frequency"], spec["meta"]["eval_frequency"] | slm_lab/experiment/control.py65-76 |
| search.build_param_space | spec["search"] | slm_lab/experiment/search.py69-76 |
| analysis.analyze_session | spec["meta"]["info_prepath"], spec["env"]["name"] | slm_lab/experiment/analysis.py266-271 |

 **Spec path to component mapping**

 
```

```

 Sources: [slm_lab/agent/__init__.py37-71](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L37-L71) [slm_lab/experiment/control.py43-53](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L43-L53) [slm_lab/experiment/search.py39-77](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/search.py#L39-L77) [slm_lab/experiment/analysis.py264-276](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L264-L276)

 
---

 
## Output Directory Layout

 After `tick` runs, every output file uses paths derived from the spec. The directory structure for a run named `ppo_cartpole` started at timestamp `2024_01_15_120000`:

 
```
data/ppo_cartpole_2024_01_15_120000/
├── graph/
│   └── ppo_cartpole_t0_s0_...png
├── info/
│   ├── ppo_cartpole_t0_s0_session_df_train.csv
│   ├── ppo_cartpole_t0_s0_session_metrics_train.json
│   └── ppo_cartpole_t0_trial_metrics.json
├── log/
│   └── ppo_cartpole_t0_s0.log
├── model/
│   ├── ppo_cartpole_t0_s0.pt
│   └── ppo_cartpole_t0_s0_best.pt
├── ppo_cartpole_spec.json          ← experiment spec
└── ppo_cartpole_t0_spec.json       ← trial spec
```

 `prepath` encodes trial and session indices as `_t{i}` and `_s{j}` suffixes. The `insert_folder` utility in `util.py` inserts the subfolder between the directory and the filename.

 Sources: [slm_lab/lib/util.py195-215](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L195-L215) [slm_lab/spec/spec_util.py319-329](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L319-L329)

 
---

 
## Checking All Specs

 `spec_util.check_all` iterates over every `.json`, `.yaml`, and `.yml` file in `SPEC_DIR` (excluding files whose names start with `_`), loads each named spec, and runs `check` on it. This is used as a validation step before committing new specs.

 [slm_lab/spec/spec_util.py93-112](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L93-L112)

 Sources: [slm_lab/spec/spec_util.py93-112](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L93-L112)
