> 来源: [https://deepwiki.com/kengz/SLM-Lab/8-utilities](https://deepwiki.com/kengz/SLM-Lab/8-utilities)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Utilities

  Relevant source files 
 - [slm_lab/agent/__init__.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py)
 - [slm_lab/experiment/analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py)
 - [slm_lab/experiment/control.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py)
 - [slm_lab/experiment/retro_analysis.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/retro_analysis.py)
 - [slm_lab/lib/math_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/math_util.py)
 - [slm_lab/lib/util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py)
 - [slm_lab/spec/spec_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py)
 - [test/lib/test_math_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_math_util.py)
 - [test/lib/test_util.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/test/lib/test_util.py)
 
  This page provides an overview of the shared utility libraries in `slm_lab/lib/`. These modules supply common functionality — I/O, path management, lab-mode context switching, logging, and mathematical operations — that is used throughout the experiment, agent, and environment subsystems.

 For the math calculations specific to RL algorithms (returns, advantages, decay functions), see [Math Utilities](https://deepwiki.com/kengz/SLM-Lab/8.1-math-utilities). For the random baseline generation system used in metrics, see [Random Baselines](https://deepwiki.com/kengz/SLM-Lab/8.2-random-baselines).

 
---

 
## Module Map

 The `lib/` directory contains four main modules. The diagram below maps each module to its primary consumers.

 **Utility Layer: Module Relationships**

 
```

```

 Sources: [slm_lab/lib/util.py1-30](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L1-L30) [slm_lab/lib/math_util.py1-10](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/math_util.py#L1-L10) [slm_lab/experiment/control.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L1-L20) [slm_lab/agent/__init__.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L1-L20)

 
---

 
## `util.py`

 `slm_lab/lib/util.py` is the primary utility module. It is imported as `from slm_lab.lib import util` across almost every file in the codebase. It is split into two layers: pure-Python utilities defined directly in the file, and ML-dependent utilities re-exported from `ml_util.py`.

 
### Function Categories

 
| Category | Functions | Notes |
|---|---|---|
| I/O | read, write, read_as_df, read_as_plain, write_as_df, write_as_plain | Auto-detects format from extension (.csv, .json, .yml, .txt) |
| Path resolution | smart_path, get_prepath, get_predir, get_session_df_path, insert_folder, prepath_to_idxs | smart_path resolves relative paths from ROOT_DIR |
| Timestamps | get_ts, calc_ts_diff, get_experiment_ts | Uses FILE_TS_FORMAT = "%Y_%m_%d_%H%M%S" |
| Lab mode | ctx_lab_mode, in_eval_lab_mode, in_train_lab_mode | Context manager and predicates for lab_mode env var |
| Logging helpers | log_dict, log_self_desc, set_logger, format_metrics | set_logger configures per-unit loguru file sinks |
| Type casting | cast_df, cast_list, downcast_float32 | Supplements pydash for pandas interop |
| Introspection | get_class_name, get_fn_list, get_class_attr, get_git_sha | Used for self-description logging |
| Statistics | calc_srs_mean_std | Aligns and aggregates pandas Series lists |
| Misc | frame_mod, flatten_dict, set_attr, monkey_patch, sizeof | frame_mod handles vector env tick alignment |

 Sources: [slm_lab/lib/util.py25-545](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L25-L545)

 
---

 
### I/O: `read` and `write`

 `read` and `write` dispatch by file extension:

 
```
.csv   → pandas DataFrame (pd.read_csv / df.to_csv)
.json  → dict or list (ujson.load / json.dump with LabJsonEncoder)
.yml   → dict (yaml.load / yaml.dump)
*      → str (open().read() / open().write())
```

 Both call `smart_path` to normalize relative paths against `ROOT_DIR` before opening files. `write` also calls `os.makedirs(..., exist_ok=True)` to create intermediate directories automatically.

 Sources: [slm_lab/lib/util.py299-515](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L299-L515)

 
---

 
### Lab Mode Context: `ctx_lab_mode`

 The `lab_mode` environment variable controls runtime behavior (training, eval, dev, test, enjoy). `ctx_lab_mode` is a context manager that temporarily sets `lab_mode` and restores the prior value on exit.

 
```
with util.ctx_lab_mode('eval'):
    agent.algorithm.update()   # sets explore_var to end_val
```

 The predicates `in_eval_lab_mode()` and `in_train_lab_mode()` check `lab_mode` against the `EVAL_MODES` and `TRAIN_MODES` constants defined in `slm_lab/__init__.py`.

 Sources: [slm_lab/lib/util.py262-280](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L262-L280) [slm_lab/lib/util.py242-249](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L242-L249)

 
---

 
### Path Utilities

 The path system produces deterministic file locations keyed by spec name, experiment timestamp, trial index, and session index. The key functions are:

 **Path Construction Flow**

 
```

```

 `spec_util.tick` calls these functions and writes the resulting paths into `spec['meta']` as `prepath`, `info_prepath`, `log_prepath`, `model_prepath`, and `graph_prepath`.

 Sources: [slm_lab/lib/util.py181-215](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L181-L215) [slm_lab/spec/spec_util.py318-330](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/spec/spec_util.py#L318-L330)

 
---

 
### Logging: `set_logger` and `format_metrics`

 `set_logger(spec, logger, unit)` adds a per-unit loguru file sink at `data/{name}_{ts}/log/{name}[_tN][_sN].log`. It removes any prior file sinks (keeping stdout) before adding the new one, so each Session, Trial, and Experiment writes to its own log file.

 `format_metrics(metrics: dict) -> list[str]` converts a metrics dictionary to a list of formatted strings for console output. It applies type-specific formatting:

 
| Key | Format |
|---|---|
| frame | scientific notation (1.00e+07) |
| total_reward, total_reward_ma | 2 decimal places |
| other floats | 4 significant figures |

 Sources: [slm_lab/lib/util.py393-410](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L393-L410) [slm_lab/lib/util.py29-55](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L29-L55)

 
---

 
## `ml_util.py`

 ML-dependent functions are defined in `slm_lab/lib/ml_util.py` and re-exported from `util.py` for backward compatibility. They are only available when `torch`, `numpy`, and `cv2` are installed.

 **Key re-exported symbols:**

 
| Symbol | Purpose |
|---|---|
| set_random_seed(spec) | Seeds Python, NumPy, and PyTorch RNGs from spec['meta']['random_seed'] |
| set_cuda_id(spec) | Sets CUDA_VISIBLE_DEVICES based on trial index and cuda_offset |
| epi_done(done) | Returns True if any environment in a vector env done array is True |
| to_torch_batch(batch, device, ...) | Converts a memory sample dict to a device-placed tensor dict |
| split_minibatch(batch, num_splits) | Splits a tensor batch into minibatches |
| LabJsonEncoder | json.JSONEncoder subclass that handles numpy arrays and tensors |
| batch_get, concat_batches | Batch indexing and concatenation for memory samples |
| Image utilities | grayscale_image, normalize_image, resize_image, preprocess_image, to_opencv_image, to_pytorch_image |

 Sources: [slm_lab/lib/util.py519-544](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L519-L544)

 
---

 
## `logger.py`

 `slm_lab/lib/logger.py` wraps [loguru](https://github.com/kengz/SLM-Lab/blob/d3128a8a/loguru) and exposes a single function: `get_logger(__name__)`. Every module that needs logging calls this at module level:

 
```

```

 This returns a loguru logger instance pre-configured with `LOG_FORMAT`. File sinks are managed separately by `util.set_logger`, which is called at each Session, Trial, and Experiment initialization.

 
---

 
## `env_var.py`

 `slm_lab/lib/env_var.py` provides thin accessors for environment variables that control lab behavior:

 
 - `lab_mode()` — reads the `lab_mode` environment variable (`train`, `eval`, `dev`, `test`, `enjoy`)
 - `log_extra()` — reads `LOG_EXTRA` to enable verbose metric logging
 
 These are imported directly by `util.py` and `agent/__init__.py` to make per-step mode decisions without passing mode arguments down the call stack.

 Sources: [slm_lab/lib/util.py13-14](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L13-L14) [slm_lab/agent/__init__.py19](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L19-L19)

 
---

 
## Utility Dependency Map (Code-Level)

 The following diagram maps the code-level import relationships for the utility layer.

 **`lib/` Import Graph**

 
```

```

 Sources: [slm_lab/lib/util.py1-24](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/util.py#L1-L24) [slm_lab/experiment/analysis.py1-11](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/analysis.py#L1-L11) [slm_lab/experiment/control.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/experiment/control.py#L1-L20) [slm_lab/agent/__init__.py1-20](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/agent/__init__.py#L1-L20)

 
---

 
## Child Pages

 
| Page | Module | Coverage |
|---|---|---|
| Math Utilities | slm_lab/lib/math_util.py | calc_returns, calc_nstep_returns, calc_gaes, calc_q_value_logits, venv_pack, venv_unpack, decay functions |
| Random Baselines | slm_lab/spec/random_baseline.py | gen_random_baseline, get_random_baseline, _random_baseline.json storage |
